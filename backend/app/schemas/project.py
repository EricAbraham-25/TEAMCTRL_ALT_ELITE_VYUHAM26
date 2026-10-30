
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import date


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    project_manager_id: Optional[int] = None
    start_date: Optional[date] = None
    deadline: Optional[date] = None
    status: str = "planned"


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    project_manager_id: Optional[int] = None
    start_date: Optional[date] = None
    deadline: Optional[date] = None
    status: Optional[str] = None
    progress: Optional[int] = Field(default=None, ge=0, le=100)


class ProjectResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    project_manager_id: Optional[int] = None
    start_date: Optional[date] = None
    deadline: Optional[date] = None
    status: str
    progress: int

    model_config = ConfigDict(from_attributes=True)


class ProjectMemberCreate(BaseModel):
    employee_id: int
    role: str


class ProjectMemberResponse(BaseModel):
    id: int
    project_id: int
    employee_id: int
    role: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    assigned_to: Optional[int] = None
    status: str = "pending"
    priority: str = "medium"
    progress: int = Field(default=0, ge=0, le=100)
    due_date: Optional[date] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    assigned_to: Optional[int] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    progress: Optional[int] = Field(default=None, ge=0, le=100)
    due_date: Optional[date] = None


class TaskResponse(BaseModel):
    id: int
    project_id: int
    assigned_to: Optional[int] = None
    title: str
    description: Optional[str] = None
    status: str
    priority: str
    progress: int
    due_date: Optional[date] = None

    model_config = ConfigDict(from_attributes=True)
