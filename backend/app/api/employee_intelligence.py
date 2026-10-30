
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.models.company import Employee, User
from app.core.dependencies import get_current_user
from app.services.employee_intelligence import analyze_employee

router = APIRouter(
    prefix="/api/employee-intelligence",
    tags=["Employee Intelligence"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ensure_employee_access(
    employee_id: int,
    db: Session,
    current_user: User
):
    employee = db.query(Employee).filter(
        Employee.id == employee_id
    ).first()

    if not employee:
        raise HTTPException(404, "Employee not found")

    # Managers are global organization administrators.
    if current_user.role == "manager":
        return employee

    # Employees may only access their own intelligence.
    if current_user.role == "employee":
        if current_user.employee_id is None:
            raise HTTPException(
                403, "No employee profile linked to this account"
            )

        if current_user.employee_id != employee_id:
            raise HTTPException(
                403, "You can only access your own employee intelligence"
            )

        return employee

    raise HTTPException(403, "Access denied")


@router.get("/overview")
def employee_intelligence_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == "employee":
        if current_user.employee_id is None:
            raise HTTPException(
                403, "No employee profile linked to this account"
            )

        employees = db.query(Employee).filter(
            Employee.id == current_user.employee_id
        ).all()
    else:
        employees = db.query(Employee).all()

    analyses = [
        analyze_employee(db, employee.id)
        for employee in employees
    ]

    return {
        "total_employees": len(analyses),
        "employees_with_insights": sum(
            1 for item in analyses
            if item.get("insight_count", 0) > 0
        ),
        "employees": analyses
    }


@router.get("/{employee_id}/analysis")
def employee_analysis(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ensure_employee_access(employee_id, db, current_user)

    result = analyze_employee(db, employee_id)

    if result.get("error"):
        raise HTTPException(
            status_code=404,
            detail=result["error"]
        )

    return result
