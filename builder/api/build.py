"""构建命令执行 API"""

import json
import time
import uuid
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from ..models.task import BuildCommandRequest, BuildCommandResponse
from ..services.shell_service import ShellService
from ..services.process_manager import process_manager
from ..config import settings

router = APIRouter()
shell_service = ShellService()

# 存储活跃的流式任务
active_streams: dict = {}


@router.post(
    "/execute",
    response_model=BuildCommandResponse,
    summary="执行构建命令",
    description="异步执行 Maven/npm/Gradle 等构建命令并返回结果（非流式）"
)
async def execute_build(request: BuildCommandRequest):
    """
    执行构建命令（非流式）

    支持的构建类型：
    - **maven**: Maven 命令（如 'mvn clean install'）
    - **npm**: npm 命令（如 'npm run build'）
    - **gradle**: Gradle 命令（如 'gradle build'）
    - **custom**: 自定义命令

    参数：
    - **command**: 构建命令字符串
    - **cwd**: 工作目录（可选，默认为项目根目录）
    - **timeout**: 超时时间（秒），默认 300 秒
    - **command_type**: 命令类型标识
    """
    import logging
    logger = logging.getLogger(__name__)

    # 安全验证：防止命令注入
    _validate_command(request.command)

    # 设置默认工作目录
    cwd = request.cwd or settings.project_root

    logger.info(f"执行构建命令: {request.command} | cwd: {cwd} | timeout: {request.timeout}")

    # 执行构建（收集所有输出）
    start_time = time.time()
    output_lines = []

    try:
        async for line in shell_service.run_command_stream(
            command=request.command,
            cwd=cwd,
            timeout=request.timeout
        ):
            output_lines.append(line)

        execution_time = time.time() - start_time

        logger.info(f"命令执行成功，耗时 {execution_time:.2f}s，输出行数: {len(output_lines)}")

        return BuildCommandResponse(
            success=True,
            command=request.command,
            exit_code=0,
            stdout='\n'.join(output_lines),
            stderr="",
            execution_time=execution_time,
            message="构建成功"
        )

    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"命令执行失败: {str(e)}", exc_info=True)
        return BuildCommandResponse(
            success=False,
            command=request.command,
            exit_code=-1,
            stdout="",
            stderr=str(e),
            execution_time=execution_time,
            message=f"构建失败: {str(e)}"
        )


@router.post(
    "/stop",
    summary="停止构建服务",
    description="停止运行中的构建服务（通过杀死指定端口的进程）"
)
async def stop_service(port: int = 8080):
    """
    停止指定端口的服务

    参数：
    - **port**: 要停止的端口号，默认 8080
    """
    import logging
    import subprocess
    import platform
    import asyncio
    from fastapi import BackgroundTasks
    logger = logging.getLogger(__name__)

    logger.info(f"收到停止服务请求，端口: {port}")

    # 使用后台任务执行停止操作，立即返回
    def stop_port_process():
        try:
            if platform.system() == 'Windows':
                # Windows: 使用 taskkill 杀死占用端口的进程
                # 先查找占用端口的进程 PID
                find_cmd = f"netstat -ano | findstr :{port}"
                result = subprocess.run(
                    find_cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                if result.returncode == 0 and result.stdout:
                    # 解析 PID
                    for line in result.stdout.strip().split('\n'):
                        if 'LISTENING' in line:
                            parts = line.split()
                            if len(parts) >= 5:
                                pid = parts[-1]
                                # 杀死进程
                                kill_cmd = f"taskkill /F /PID {pid}"
                                subprocess.run(kill_cmd, shell=True, capture_output=True, timeout=10)
                                logger.info(f"已杀死进程 PID: {pid}")

            else:
                # Linux/Mac: 使用 lsof 和 kill
                subprocess.run(f"fuser -k {port}/tcp", shell=True, timeout=10)
                logger.info(f"已停止端口 {port} 的服务")

        except Exception as e:
            logger.error(f"停止服务失败: {str(e)}")

    # 在后台线程中执行停止操作
    import threading
    thread = threading.Thread(target=stop_port_process, daemon=True)
    thread.start()

    # 立即返回
    return {"success": True, "message": f"正在停止端口 {port} 的服务..."}


@router.post(
    "/execute/stream",
    summary="流式执行构建命令",
    description="流式执行 Maven/npm/Gradle 等构建命令，通过 SSE 实时返回输出"
)
async def execute_build_stream(request: BuildCommandRequest):
    """
    流式执行构建命令（SSE）

    返回 Server-Sent Events 格式的流式数据：
    - data: {"type": "log", "line": "输出行"}
    - data: {"type": "complete", "success": true/false, "message": "..."}

    参数：
    - **command**: 构建命令字符串
    - **cwd**: 工作目录（可选，默认为项目根目录）
    - **timeout**: 超时时间（秒），默认 300 秒
    - **command_type**: 命令类型标识
    """
    import logging
    logger = logging.getLogger(__name__)

    # 安全验证：防止命令注入
    _validate_command(request.command)

    # 设置默认工作目录
    cwd = request.cwd or settings.project_root

    logger.info(f"=== 流式执行构建命令 ===")
    logger.info(f"命令: {request.command}")
    logger.info(f"工作目录: {cwd}")
    logger.info(f"超时: {request.timeout}秒")

    async def event_generator():
        """SSE 事件生成器"""
        command_success = True
        error_message = "构建成功"
        exit_code = 0

        try:
            async for line in shell_service.run_command_stream(
                command=request.command,
                cwd=cwd,
                timeout=request.timeout
            ):
                # 检查是否是特殊的退出码行
                if line.startswith("__BUILD_EXIT_CODE:"):
                    exit_code = int(line.split("__BUILD_EXIT_CODE:")[1].split("__")[0])
                    command_success = (exit_code == 0)
                    error_message = f"命令执行完成 (退出码: {exit_code})" if command_success else f"命令执行失败 (退出码: {exit_code})"
                else:
                    # 发送日志行
                    yield f"data: {json.dumps({'type': 'log', 'line': line}, ensure_ascii=False)}\n\n"

                # 检查客户端是否断开（yield 会触发断开检测）
                # 如果客户端断开，下一次循环时 GeneratorExit 会被触发

        except GeneratorExit:
            # 客户端断开连接
            logger.warning("客户端断开连接，停止流式输出")
            command_success = False
            error_message = "客户端断开连接"
            raise

        except Exception as e:
            # 执行过程中发生异常（如超时）
            command_success = False
            error_message = str(e)
            # 发送错误事件
            try:
                yield f"data: {json.dumps({'type': 'complete', 'success': False, 'message': error_message}, ensure_ascii=False)}\n\n"
            except:
                pass  # 客户端可能已经断开
            return

        # 发送完成事件
        try:
            yield f"data: {json.dumps({'type': 'complete', 'success': command_success, 'message': error_message}, ensure_ascii=False)}\n\n"
        except:
            pass  # 客户端可能已经断开

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


def _validate_command(command: str) -> None:
    """
    验证命令安全性，防止命令注入

    Args:
        command: 命令字符串

    Raises:
        HTTPException: 命令不安全时抛出
    """
    # 危险字符黑名单
    dangerous_chars = ['|', '&', ';', '$', '`', '(', ')', '<', '>']

    for char in dangerous_chars:
        if char in command:
            raise HTTPException(
                status_code=400,
                detail=f"命令包含非法字符: {char}，可能存在命令注入风险"
            )
