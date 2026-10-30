
from sqlalchemy.orm import Session

from app.models.company import (
    Employee,
    Department,
    Attendance,
    Project,
    ProjectMember,
    Task,
)


def search_employees(db: Session, query: str):
    employees = (
        db.query(Employee)
        .filter(
            (Employee.name.ilike(f"%{query}%"))
            | (Employee.employee_code.ilike(f"%{query}%"))
        )
        .limit(10)
        .all()
    )

    return [
        {
            "id": e.id,
            "name": e.name,
            "employee_code": e.employee_code,
            "designation": e.designation,
            "employment_status": e.employment_status,
            "department": e.department.name if e.department else None,
        }
        for e in employees
    ]


def get_employee_attendance(db: Session, employee_name: str):
    employee = (
        db.query(Employee)
        .filter(Employee.name.ilike(f"%{employee_name}%"))
        .first()
    )

    if not employee:
        return {"error": "Employee not found"}

    records = (
        db.query(Attendance)
        .filter(Attendance.employee_id == employee.id)
        .order_by(Attendance.attendance_date.desc())
        .limit(7)
        .all()
    )

    return {
        "employee": employee.name,
        "attendance": [
            {
                "date": str(a.attendance_date),
                "check_in": str(a.check_in) if a.check_in else None,
                "check_out": str(a.check_out) if a.check_out else None,
                "status": a.status,
            }
            for a in records
        ],
    }


def get_employee_tasks(db: Session, employee_name: str):
    employee = (
        db.query(Employee)
        .filter(Employee.name.ilike(f"%{employee_name}%"))
        .first()
    )

    if not employee:
        return {"error": "Employee not found"}

    tasks = (
        db.query(Task)
        .filter(Task.assigned_to == employee.id)
        .order_by(Task.due_date.asc())
        .all()
    )

    return {
        "employee": employee.name,
        "tasks": [
            {
                "title": t.title,
                "description": t.description,
                "status": t.status,
                "priority": t.priority,
                "progress": t.progress,
                "due_date": str(t.due_date) if t.due_date else None,
            }
            for t in tasks
        ],
    }


def list_projects(db: Session, status: str = None):
    query = db.query(Project)

    if status:
        query = query.filter(Project.status.ilike(status))

    projects = query.order_by(Project.deadline.asc()).all()

    return [
        {
            "id": p.id,
            "name": p.name,
            "status": p.status,
            "progress": p.progress,
            "deadline": str(p.deadline) if p.deadline else None,
        }
        for p in projects
    ]


def get_project_details(db: Session, project_name: str):
    project = (
        db.query(Project)
        .filter(Project.name.ilike(f"%{project_name}%"))
        .first()
    )

    if not project:
        return {"error": "Project not found"}

    members = (
        db.query(ProjectMember)
        .filter(ProjectMember.project_id == project.id)
        .all()
    )

    tasks = (
        db.query(Task)
        .filter(Task.project_id == project.id)
        .all()
    )

    return {
        "project": project.name,
        "description": project.description,
        "status": project.status,
        "progress": project.progress,
        "start_date": str(project.start_date) if project.start_date else None,
        "deadline": str(project.deadline) if project.deadline else None,
        "team": [
            {
                "employee": m.employee.name if m.employee else None,
                "role": m.role,
            }
            for m in members
        ],
        "tasks": [
            {
                "title": t.title,
                "assigned_to": t.employee.name if t.employee else None,
                "status": t.status,
                "priority": t.priority,
                "progress": t.progress,
                "due_date": str(t.due_date) if t.due_date else None,
            }
            for t in tasks
        ],
    }


def get_department_employees(db: Session, department_name: str):
    department = (
        db.query(Department)
        .filter(Department.name.ilike(f"%{department_name}%"))
        .first()
    )

    if not department:
        return {"error": f"Department '{department_name}' not found"}

    employees = (
        db.query(Employee)
        .filter(Employee.department_id == department.id)
        .all()
    )

    return {
        "department": department.name,
        "employee_count": len(employees),
        "employees": [
            {
                "name": e.name,
                "employee_code": e.employee_code,
                "designation": e.designation,
                "employment_status": e.employment_status,
            }
            for e in employees
        ],
    }
