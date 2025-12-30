from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional
import uuid


class TaskStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"


class OrmGenerationResult(BaseModel):
    xml: str
    entity_name: str
    table_name: str


class Task(BaseModel):
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    file_name: str
    status: TaskStatus = TaskStatus.PENDING
    error_message: Optional[str] = None
    result: Optional[OrmGenerationResult] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


class TaskSubmitResponse(BaseModel):
    task_id: str
    message: str = "任务已提交，请稍后查询"
