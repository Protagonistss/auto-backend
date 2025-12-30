from fastapi import APIRouter, UploadFile, File, HTTPException
from ..models.task import TaskSubmitResponse
from ..services.task_service import TaskService
from ..storage.task_store import TaskStore

router = APIRouter()
task_store = TaskStore()
task_service = TaskService(task_store)


@router.post("/upload", response_model=TaskSubmitResponse)
async def upload_config(file: UploadFile = File(...)):
    """上传配置文件，异步生成 ORM"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="文件名不能为空")

    if not file.filename.endswith(".json"):
        raise HTTPException(status_code=400, detail="仅支持 JSON 格式文件")

    content = await file.read()
    content_str = content.decode("utf-8")

    task_id = await task_service.submit_task(file.filename, content_str)

    return TaskSubmitResponse(task_id=task_id)


@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """查询任务状态"""
    task = await task_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    return task


@router.get("/tasks/{task_id}/result")
async def get_result(task_id: str):
    """获取生成结果（仅成功时）"""
    task = await task_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    if task.status != TaskStatus.SUCCESS:
        raise HTTPException(
            status_code=400,
            detail=f"任务未完成，当前状态: {task.status.value}"
        )

    return task.result
