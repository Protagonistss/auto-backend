from fastapi import APIRouter, HTTPException
from ..models.orm import WriteEntityRequest, WriteEntityResponse
from ..services.orm_service import OrmXmlService

router = APIRouter()
orm_service = OrmXmlService()


@router.post("/orm/entity", response_model=WriteEntityResponse, summary="写入 Entity")
async def write_entity(request: WriteEntityRequest):
    """
    将 AI 生成的 entity 写入 app.orm.xml

    - **xml**: entity XML 片段（符合 orm.md 规范）
    - **source**: 来源标识（ai/chat/manual）
    - **task_id**: 关联任务ID（可选）

    返回操作结果
    """
    try:
        result = orm_service.write_entity(request.xml)
        return WriteEntityResponse(
            success=True,
            entity_name=result.entity_name,
            action=result.action,
            message=f"Entity {result.entity_name} 已成功{result.action}"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except (FileNotFoundError, IOError) as e:
        raise HTTPException(status_code=500, detail=str(e))
