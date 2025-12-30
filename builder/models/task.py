from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional
import uuid


class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"


class OrmGenerationResult(BaseModel):
    """ORM 生成结果"""
    xml: str = Field(..., description="生成的 MyBatis XML 配置")
    entity_name: str = Field(..., description="实体类名称")
    table_name: str = Field(..., description="数据库表名")


class Task(BaseModel):
    """任务模型"""
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="任务ID")
    file_name: str = Field(..., description="上传的文件名")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="任务状态")
    error_message: Optional[str] = Field(None, description="错误信息（失败时）")
    result: Optional[OrmGenerationResult] = Field(None, description="生成结果（成功时）")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")


class TaskSubmitResponse(BaseModel):
    """任务提交响应"""
    task_id: str = Field(..., description="任务ID")
    message: str = Field(default="任务已提交，请稍后查询", description="响应消息")
