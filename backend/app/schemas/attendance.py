
from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from typing import Optional


class AttendanceResponse(BaseModel):
    id: int
    employee_id: int
    attendance_date: date
    check_in: Optional[datetime] = None
    check_out: Optional[datetime] = None
    status: str

    model_config = ConfigDict(from_attributes=True)
