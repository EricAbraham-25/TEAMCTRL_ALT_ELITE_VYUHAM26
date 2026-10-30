
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.models.company import Department, Employee, User
from app.schemas.department import (
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentResponse
)
from app.schemas.employee import EmployeeResponse
from app.core.dependencies import get_current_user, require_manager

router = APIRouter(
    prefix="/api/departments",
    tags=["Departments"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# MANAGER ONLY: Create department
@router.post("/", response_model=DepartmentResponse, status_code=201)
def create_department(
    department: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager)
):
    existing = db.query(Department).filter(
        Department.name == department.name
    ).first()

    if existing:
        raise HTTPException(409, "Department already exists")

    new_department = Department(**department.model_dump())
    db.add(new_department)
    db.commit()
    db.refresh(new_department)

    return new_department


# MANAGER ONLY: View all departments
@router.get("/", response_model=list[DepartmentResponse])
def get_departments(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager)
):
    return db.query(Department).order_by(Department.id).all()


# MANAGER ONLY: View department
@router.get("/{department_id}", response_model=DepartmentResponse)
def get_department(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager)
):
    department = db.query(Department).filter(
        Department.id == department_id
    ).first()

    if not department:
        raise HTTPException(404, "Department not found")

    return department


# MANAGER ONLY: Update department
@router.put("/{department_id}", response_model=DepartmentResponse)
def update_department(
    department_id: int,
    department_data: DepartmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager)
):
    department = db.query(Department).filter(
        Department.id == department_id
    ).first()

    if not department:
        raise HTTPException(404, "Department not found")

    updates = department_data.model_dump(exclude_unset=True)

    if "name" in updates and updates["name"] is None:
        raise HTTPException(422, "Department name cannot be null")

    if "name" in updates:
        duplicate = db.query(Department).filter(
            Department.name == updates["name"],
            Department.id != department_id
        ).first()

        if duplicate:
            raise HTTPException(409, "Department name already exists")

    for key, value in updates.items():
        setattr(department, key, value)

    db.commit()
    db.refresh(department)

    return department


# MANAGER ONLY: Delete department
@router.delete("/{department_id}")
def delete_department(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager)
):
    department = db.query(Department).filter(
        Department.id == department_id
    ).first()

    if not department:
        raise HTTPException(404, "Department not found")

    assigned_employees = db.query(Employee).filter(
        Employee.department_id == department_id
    ).count()

    if assigned_employees > 0:
        raise HTTPException(
            status_code=409,
            detail="Cannot delete department with assigned employees"
        )

    db.delete(department)
    db.commit()

    return {"message": "Department deleted successfully"}


# MANAGER ONLY: View department employees
@router.get("/{department_id}/employees", response_model=list[EmployeeResponse])
def get_department_employees(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager)
):
    department = db.query(Department).filter(
        Department.id == department_id
    ).first()

    if not department:
        raise HTTPException(404, "Department not found")

    return db.query(Employee).filter(
        Employee.department_id == department_id
    ).all()
