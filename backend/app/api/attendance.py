
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from zoneinfo import ZoneInfo

from app.database.connection import SessionLocal
from app.models.company import Attendance, Employee, User
from app.schemas.attendance import AttendanceResponse
from app.core.dependencies import get_current_user, require_manager

router = APIRouter(
    prefix="/api/attendance",
    tags=["Attendance"]
)

TIMEZONE = ZoneInfo("Asia/Kolkata")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_today():
    return datetime.now(TIMEZONE).date()


def verify_employee_access(employee_id: int, current_user: User):
    if current_user.role == "employee":
        if current_user.employee_id != employee_id:
            raise HTTPException(
                status_code=403,
                detail="You can only access your own attendance"
            )
    elif current_user.role != "manager":
        raise HTTPException(status_code=403, detail="Access denied")


# CHECK IN
@router.post("/check-in/{employee_id}", response_model=AttendanceResponse)
def check_in(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    verify_employee_access(employee_id, current_user)

    employee = db.query(Employee).filter(
        Employee.id == employee_id
    ).first()

    if not employee:
        raise HTTPException(404, "Employee not found")

    today = get_today()

    record = db.query(Attendance).filter(
        Attendance.employee_id == employee_id,
        Attendance.attendance_date == today
    ).first()

    if record:
        raise HTTPException(409, "Employee has already checked in today")

    attendance = Attendance(
        employee_id=employee_id,
        attendance_date=today,
        check_in=datetime.now(TIMEZONE),
        status="present"
    )

    db.add(attendance)
    db.commit()
    db.refresh(attendance)

    return attendance


# CHECK OUT
@router.post("/check-out/{employee_id}", response_model=AttendanceResponse)
def check_out(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    verify_employee_access(employee_id, current_user)

    today = get_today()

    record = db.query(Attendance).filter(
        Attendance.employee_id == employee_id,
        Attendance.attendance_date == today
    ).first()

    if not record:
        raise HTTPException(404, "No check-in record found for today")

    if record.check_out:
        raise HTTPException(409, "Employee has already checked out")

    record.check_out = datetime.now(TIMEZONE)

    db.commit()
    db.refresh(record)

    return record


# MANAGER: VIEW TODAY'S ORGANIZATION ATTENDANCE
@router.get("/today")
def get_today_attendance(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager)
):
    today = get_today()

    records = db.query(Attendance, Employee).join(
        Employee,
        Attendance.employee_id == Employee.id
    ).filter(
        Attendance.attendance_date == today
    ).all()

    return [
        {
            "employee_id": employee.id,
            "employee_name": employee.name,
            "check_in": attendance.check_in,
            "check_out": attendance.check_out,
            "status": attendance.status,
            "work_status": (
                "Checked out"
                if attendance.check_out
                else "Currently checked in"
            )
        }
        for attendance, employee in records
    ]


# MANAGER OR EMPLOYEE'S OWN ATTENDANCE
@router.get("/employee/{employee_id}", response_model=list[AttendanceResponse])
def get_employee_attendance(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    verify_employee_access(employee_id, current_user)

    employee = db.query(Employee).filter(
        Employee.id == employee_id
    ).first()

    if not employee:
        raise HTTPException(404, "Employee not found")

    return db.query(Attendance).filter(
        Attendance.employee_id == employee_id
    ).order_by(
        Attendance.attendance_date.desc()
    ).all()


# MANAGER OR EMPLOYEE'S OWN TODAY STATUS
@router.get("/employee/{employee_id}/today")
def get_employee_today_status(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    verify_employee_access(employee_id, current_user)

    today = get_today()

    employee = db.query(Employee).filter(
        Employee.id == employee_id
    ).first()

    if not employee:
        raise HTTPException(404, "Employee not found")

    record = db.query(Attendance).filter(
        Attendance.employee_id == employee_id,
        Attendance.attendance_date == today
    ).first()

    if not record:
        return {
            "employee": employee.name,
            "attendance": "No attendance record",
            "check_in": None,
            "check_out": None
        }

    return {
        "employee": employee.name,
        "attendance": record.status,
        "check_in": record.check_in,
        "check_out": record.check_out,
        "work_status": (
            "Checked out"
            if record.check_out
            else "Currently checked in"
        )
    }
