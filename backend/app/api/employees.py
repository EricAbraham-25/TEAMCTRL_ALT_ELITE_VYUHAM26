
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.models.company import Employee, User
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeResponse
)
from app.core.dependencies import (
    get_current_user,
    require_manager,
    require_employee
)

router = APIRouter(
    prefix="/api/employees",
    tags=["Employees"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# MANAGER: Create an employee
@router.post("/", response_model=EmployeeResponse, status_code=201)
def create_employee(
    employee: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager)
):
    existing_employee = db.query(Employee).filter(
        (Employee.email == employee.email) |
        (Employee.employee_code == employee.employee_code)
    ).first()

    if existing_employee:
        raise HTTPException(
            status_code=409,
            detail="Employee email or employee code already exists"
        )

    new_employee = Employee(**employee.model_dump())

    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)

    return new_employee


# MANAGER: View all employees
# EMPLOYEE: View only their own record
@router.get("/", response_model=list[EmployeeResponse])
def get_employees(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == "manager":
        return db.query(Employee).order_by(Employee.id).all()

    if not current_user.employee_id:
        raise HTTPException(
            status_code=403,
            detail="No employee record linked to this account"
        )

    employee = db.query(Employee).filter(
        Employee.id == current_user.employee_id
    ).first()

    return [employee] if employee else []


# MANAGER: View any employee
# EMPLOYEE: View only their own record
@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == "employee":
        if current_user.employee_id != employee_id:
            raise HTTPException(
                status_code=403,
                detail="You can only access your own employee record"
            )
    elif current_user.role != "manager":
        raise HTTPException(status_code=403, detail="Access denied")

    employee = db.query(Employee).filter(
        Employee.id == employee_id
    ).first()

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    return employee


# MANAGER ONLY: Update employee
@router.put("/{employee_id}", response_model=EmployeeResponse)
def update_employee(
    employee_id: int,
    employee_data: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager)
):
    employee = db.query(Employee).filter(
        Employee.id == employee_id
    ).first()

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    updates = employee_data.model_dump(exclude_unset=True)

    if "email" in updates and updates["email"] is None:
        raise HTTPException(status_code=422, detail="Email cannot be null")

    if "name" in updates and updates["name"] is None:
        raise HTTPException(status_code=422, detail="Name cannot be null")

    for key, value in updates.items():
        setattr(employee, key, value)

    db.commit()
    db.refresh(employee)

    return employee


# MANAGER ONLY: Delete employee
@router.delete("/{employee_id}")
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager)
):
    employee = db.query(Employee).filter(
        Employee.id == employee_id
    ).first()

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    db.delete(employee)
    db.commit()

    return {"message": "Employee deleted successfully"}
