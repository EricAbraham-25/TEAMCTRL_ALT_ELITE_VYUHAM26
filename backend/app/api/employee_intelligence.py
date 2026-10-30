
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.models.company import Employee
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


@router.get("/overview")
def employee_intelligence_overview(
    db: Session = Depends(get_db)
):
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
    db: Session = Depends(get_db)
):
    result = analyze_employee(db, employee_id)

    if result.get("error"):
        raise HTTPException(
            status_code=404,
            detail=result["error"]
        )

    return result
