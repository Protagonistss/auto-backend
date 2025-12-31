import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from fastapi import UploadFile, HTTPException

from ..models.conversation import (
    Conversation,
    Message,
    FileInfo,
    ConversationDetail,
    ChatResponse,
    MessageRole,
)
from ..config import settings
from .ai_service import AIService

logger = logging.getLogger(__name__)


class Session:
    """会话状态（内存存储）"""
    def __init__(self, session_id: str, title: str):
        self.id = session_id
        self.title = title
        self.messages: List[Message] = []
        self.files: Dict[str, FileInfo] = {}
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()


class ConversationStore:
    """会话存储（内存）"""
    def __init__(self):
        self._sessions: Dict[str, Session] = {}

    def create(self, title: str) -> Session:
        """创建新会话"""
        session_id = str(uuid.uuid4())
        session = Session(session_id, title)
        self._sessions[session_id] = session
        logger.info(f"创建会话: {session_id}, 标题: {title}")
        return session

    def get(self, session_id: str) -> Optional[Session]:
        """获取会话"""
        return self._sessions.get(session_id)

    def list_all(self) -> List[Session]:
        """列出所有会话"""
        return list(self._sessions.values())

    def delete(self, session_id: str) -> bool:
        """删除会话"""
        if session_id in self._sessions:
            del self._sessions[session_id]
            logger.info(f"删除会话: {session_id}")
            return True
        return False


# 全局会话存储实例
store = ConversationStore()


class ConversationService:
    def __init__(self):
        self.ai_service = AIService()
        self.upload_dir = Path(settings.upload_dir)
        # 确保上传目录存在
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def create_conversation(self, title: str) -> Conversation:
        """创建新会话"""
        session = store.create(title)
        return Conversation(
            id=session.id,
            title=session.title,
            created_at=session.created_at,
            updated_at=session.updated_at
        )

    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """获取会话"""
        session = store.get(conversation_id)
        if not session:
            return None
        return Conversation(
            id=session.id,
            title=session.title,
            created_at=session.created_at,
            updated_at=session.updated_at
        )

    def list_conversations(self) -> List[Conversation]:
        """列出所有会话"""
        sessions = store.list_all()
        return [
            Conversation(
                id=s.id,
                title=s.title,
                created_at=s.created_at,
                updated_at=s.updated_at
            )
            for s in sessions
        ]

    def get_conversation_detail(self, conversation_id: str) -> Optional[ConversationDetail]:
        """获取会话详情"""
        session = store.get(conversation_id)
        if not session:
            return None

        return ConversationDetail(
            conversation=Conversation(
                id=session.id,
                title=session.title,
                created_at=session.created_at,
                updated_at=session.updated_at
            ),
            messages=session.messages,
            files=list(session.files.values())
        )

    async def send_message(
        self,
        conversation_id: str,
        content: str,
        file_ids: List[str] = None
    ) -> ChatResponse:
        """发送消息并获取 AI 响应"""
        if file_ids is None:
            file_ids = []

        session = store.get(conversation_id)
        if not session:
            raise HTTPException(status_code=404, detail="会话不存在")

        # 1. 创建用户消息
        user_message = Message(
            role=MessageRole.USER,
            content=content,
            file_references=file_ids
        )
        session.messages.append(user_message)

        # 2. 构建对话上下文
        context_messages = []

        # 获取最近的消息（用于上下文）
        recent_messages = session.messages[-settings.max_context_messages:]

        for msg in recent_messages:
            # 如果消息有关联文件，读取文件内容
            file_content = ""
            if msg.file_references:
                file_contents = []
                for file_id in msg.file_references:
                    if file_id in session.files:
                        file_info = session.files[file_id]
                        file_text = await self._read_file_content(file_info.file_path)
                        if file_text:
                            file_contents.append(
                                f"\n[文件: {file_info.original_name}]\n{file_text}\n"
                            )
                file_content = "\n".join(file_contents)

            # 构建完整消息内容
            full_content = file_content + msg.content
            context_messages.append({
                "role": msg.role.value,
                "content": full_content
            })

        # 3. 调用 AI（使用系统提示词）
        try:
            ai_response = self.ai_service.chat(context_messages, use_system_prompt=True)
        except Exception as e:
            logger.error(f"AI 调用失败: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="AI 服务调用失败")

        # 4. 创建助手消息
        assistant_message = Message(
            role=MessageRole.ASSISTANT,
            content=ai_response
        )
        session.messages.append(assistant_message)
        session.updated_at = datetime.utcnow()

        logger.info(f"消息已发送: {conversation_id}, 用户消息: {user_message.id}")

        return ChatResponse(
            message_id=assistant_message.id,
            role=assistant_message.role,
            content=assistant_message.content,
            created_at=assistant_message.created_at
        )

    async def upload_file(self, conversation_id: str, file: UploadFile) -> FileInfo:
        """上传文件"""
        session = store.get(conversation_id)
        if not session:
            raise HTTPException(status_code=404, detail="会话不存在")

        # 读取文件内容
        content = await file.read()

        # 验证文件大小
        if len(content) > settings.max_file_size:
            raise HTTPException(
                status_code=400,
                detail=f"文件大小超过限制 ({settings.max_file_size} bytes)"
            )

        # 验证文件类型
        if file.content_type and file.content_type not in settings.allowed_file_types:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件类型: {file.content_type}"
            )

        # 创建会话目录
        conversation_dir = self.upload_dir / conversation_id
        conversation_dir.mkdir(parents=True, exist_ok=True)

        # 生成唯一文件名
        file_extension = Path(file.filename).suffix
        stored_name = f"{uuid.uuid4()}{file_extension}"
        file_path = conversation_dir / stored_name

        # 保存文件
        with open(file_path, "wb") as f:
            f.write(content)

        # 创建文件信息
        file_info = FileInfo(
            original_name=file.filename,
            stored_name=stored_name,
            file_path=str(file_path),
            file_size=len(content),
            mime_type=file.content_type
        )

        # 保存到会话
        session.files[file_info.id] = file_info

        logger.info(f"文件已上传: {file_info.id}, 原名: {file.filename}")

        return file_info

    def delete_conversation(self, conversation_id: str) -> bool:
        """删除会话"""
        session = store.get(conversation_id)
        if not session:
            return False

        # 删除磁盘上的文件
        conversation_dir = self.upload_dir / conversation_id
        if conversation_dir.exists():
            import shutil
            shutil.rmtree(conversation_dir)

        # 从内存中删除会话
        return store.delete(conversation_id)

    async def _read_file_content(self, file_path: str) -> Optional[str]:
        """读取文件内容"""
        try:
            path = Path(file_path)
            if not path.exists():
                logger.warning(f"文件不存在: {file_path}")
                return None

            # 根据文件扩展名决定读取方式
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()

        except Exception as e:
            logger.error(f"读取文件失败: {file_path}, 错误: {e}")
            return None
