import asyncio
import logging
import os
import shlex
from pathlib import Path
from typing import List, Union, Optional

logger = logging.getLogger(__name__)


class ShellService:
    """Shell 命令执行服务"""

    async def run_command(
        self, 
        command: Union[str, List[str]], 
        cwd: Optional[Union[str, Path]] = None,
        timeout: Optional[int] = None
    ) -> str:
        """
        异步执行 Shell 命令

        Args:
            command: 命令字符串 (如 'mvn clean') 或列表 (如 ['mvn', 'clean'])
            cwd: 执行命令的工作目录
            timeout: 超时时间（秒）

        Returns:
            str: 命令的标准输出 (stdout)

        Raises:
            FileNotFoundError: 指定的工作目录不存在
            RuntimeError: 命令执行失败 (非0退出码)
            asyncio.TimeoutError: 命令执行超时
        """
        # 1. 处理命令参数
        if isinstance(command, str):
            # 使用 shlex 正确处理引号，例如: 'mvn -DskipTests' -> ['mvn', '-DskipTests']
            cmd_args = shlex.split(command)
        else:
            cmd_args = command

        # 2. 处理工作目录
        if cwd:
            cwd_path = Path(cwd)
            if not cwd_path.exists():
                raise FileNotFoundError(f"工作目录不存在: {cwd}")
            cwd_str = str(cwd_path)
        else:
            cwd_str = None

        logger.info(f"执行命令: {' '.join(cmd_args)} | 目录: {cwd_str or '.'}")

        try:
            # 3. 创建子进程
            process = await asyncio.create_subprocess_exec(
                *cmd_args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd_str,
                # 如果在 Windows 上遇到路径或命令找不到的问题，可能需要 shell=True (但在 asyncio 中通常不推荐)
                # 对于 .bat/.cmd 文件，Windows 上通常需要设为 shell=True 或者显式调用 cmd /c
                # 这里保持默认，假设调用的是可执行文件 (如 mvn.cmd)
            )

            # 4. 等待结果 (带超时控制)
            if timeout:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
            else:
                stdout, stderr = await process.communicate()

            stdout_str = stdout.decode('utf-8', errors='replace').strip()
            stderr_str = stderr.decode('utf-8', errors='replace').strip()

            # 5. 检查退出码
            if process.returncode != 0:
                error_msg = (
                    f"命令执行失败 (Exit Code: {process.returncode})\n"
                    f"Command: {' '.join(cmd_args)}\n"
                    f"Stderr: {stderr_str}\n"
                    f"Stdout: {stdout_str}" if stdout_str else f"Stderr: {stderr_str}"
                )
                logger.error(error_msg)
                raise RuntimeError(error_msg)

            logger.info("命令执行成功")
            return stdout_str

        except asyncio.TimeoutError:
            process.kill()
            logger.error(f"命令执行超时 ({timeout}s): {command}")
            raise

        except Exception as e:
            logger.error(f"命令执行发生异常: {str(e)}")
            raise
