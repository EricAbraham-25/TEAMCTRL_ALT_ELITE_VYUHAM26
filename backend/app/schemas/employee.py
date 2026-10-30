
from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional


class EmployeeCreate(BaseModel):
    employee_code: str
    name: str
    email: EmailStr
    designation: Optional[str] = None
    department_id: Optional[int] = None


class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    designation: Optional[str] = None
    department_id: Optional[int] = None
    employment_status: Optional[str] = None


class EmployeeResponse(BaseModel):
    id: int
    employee_code: str
    name: str
    email: str
    designation: Optional[str] = None
    department_id: Optional[int] = None
    employment_status: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
