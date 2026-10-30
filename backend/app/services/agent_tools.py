
from sqlalchemy.orm import Session
from app.services.project_intelligence import analyze_project
from app.services.employee_intelligence import analyze_employee

from app.models.company import (
    Employee,
    Department,
    Attendance,
    Project,
    ProjectMember,
    Task,
    User,
)


def _is_member_of_project(db: Session, project_id: int, employee_id: int) -> bool:
    return db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.employee_id == employee_id
    ).first() is not None


def search_employees(db: Session, current_user: User, query: str):
    # Employees cannot browse the employee directory. Managers only.
    if current_user.role != "manager":
        return {"error": "You are not permitted to search other employees."}

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


def get_employee_attendance(db: Session, current_user: User, employee_name: str = None):
    # Employees can only ever see their own attendance, regardless of
    # what name is supplied in the prompt. Identity comes from the JWT.
    if current_user.role == "employee":
        if current_user.employee_id is None:
            return {"error": "No employee profile linked to this account."}
        employee = db.query(Employee).filter(
            Employee.id == current_user.employee_id
        ).first()
    else:
        if not employee_name:
            return {"error": "Please provide an employee name."}
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


def get_employee_tasks(db: Session, current_user: User, employee_name: str = None):
    if current_user.role == "employee":
        if current_user.employee_id is None:
            return {"error": "No employee profile linked to this account."}
        employee = db.query(Employee).filter(
            Employee.id == current_user.employee_id
        ).first()
    else:
        if not employee_name:
            return {"error": "Please provide an employee name."}
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


def list_projects(db: Session, current_user: User, status: str = None):
    query = db.query(Project)

    if current_user.role == "employee":
        if current_user.employee_id is None:
            return {"error": "No employee profile linked to this account."}
        query = query.join(
            ProjectMember,
            Project.id == ProjectMember.project_id
        ).filter(
            ProjectMember.employee_id == current_user.employee_id
        )

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


def get_project_details(db: Session, current_user: User, project_name: str):
    project = (
        db.query(Project)
        .filter(Project.name.ilike(f"%{project_name}%"))
        .first()
    )

    if not project:
        return {"error": "Project not found"}

    if current_user.role == "employee":
        if current_user.employee_id is None:
            return {"error": "No employee profile linked to this account."}
        if not _is_member_of_project(db, project.id, current_user.employee_id):
            return {"error": "You are not assigned to this project."}

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

    if current_user.role == "employee":
        # Employees see only their own tasks within the project, never
        # the full team task list.
        tasks = [t for t in tasks if t.assigned_to == current_user.employee_id]

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
        ] if current_user.role == "manager" else [],
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


def get_department_employees(db: Session, current_user: User, department_name: str):
    # Browsing an entire department's roster is manager-only, org-wide data.
    if current_user.role != "manager":
        return {"error": "You are not permitted to view department rosters."}

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


def get_project_intelligence(db: Session, current_user: User, project_name: str):
    project = db.query(Project).filter(
        Project.name.ilike(f"%{project_name}%")
    ).first()

    if not project:
        return {"error": f"Project '{project_name}' not found"}

    if current_user.role == "employee":
        if current_user.employee_id is None:
            return {"error": "No employee profile linked to this account."}
        if not _is_member_of_project(db, project.id, current_user.employee_id):
            return {"error": "You are not assigned to this project."}

    return analyze_project(db, project.id)


def get_employee_intelligence(db: Session, current_user: User, employee_name: str = None):
    # Identity always comes from the authenticated user, never from the
    # prompt, for employee-role callers.
    if current_user.role == "employee":
        if current_user.employee_id is None:
            return {"error": "No employee profile linked to this account."}
        employee = db.query(Employee).filter(
            Employee.id == current_user.employee_id
        ).first()
    else:
        if not employee_name:
            return {"error": "Please provide an employee name."}
        employee = db.query(Employee).filter(
            Employee.name.ilike(f"%{employee_name}%")
        ).first()

    if not employee:
        return {"error": f"Employee not found"}

    return analyze_employee(db, employee.id)
