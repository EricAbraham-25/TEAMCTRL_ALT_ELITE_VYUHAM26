
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.connection import SessionLocal
from app.models.company import (
    Project,
    ProjectMember,
    Employee,
    Task,
    User
)

from app.core.dependencies import (
    get_current_user,
    require_manager
)
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectMemberCreate,
    ProjectMemberResponse,
    TaskCreate,
    TaskUpdate,
    TaskResponse
)

router = APIRouter(
    prefix="/api/projects",
    tags=["Projects"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_accessible_project(
    project_id: int,
    db: Session,
    current_user: User
):
    project = db.query(Project).filter(
        Project.id == project_id
    ).first()

    if not project:
        raise HTTPException(404, "Project not found")

    # Managers can access every project.
    if current_user.role == "manager":
        return project

    # Employees can access only projects they belong to.
    if current_user.role == "employee":
        membership = db.query(ProjectMember).filter(
            ProjectMember.project_id == project_id,
            ProjectMember.employee_id == current_user.employee_id
        ).first()

        if not membership:
            raise HTTPException(403, "You are not assigned to this project")

        return project

    raise HTTPException(403, "Access denied")


# ---------------- PROJECT MANAGEMENT ----------------

@router.post("/", response_model=ProjectResponse, status_code=201)
def create_project(
    data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager)
):
    if data.project_manager_id is not None:
        manager = db.query(Employee).filter(
            Employee.id == data.project_manager_id
        ).first()

        if not manager:
            raise HTTPException(404, "Project manager not found")

    project = Project(**data.model_dump())

    db.add(project)
    db.commit()
    db.refresh(project)

    return project


@router.get("/", response_model=list[ProjectResponse])
def get_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Project)

    if current_user.role == "employee":
        query = query.join(
            ProjectMember,
            Project.id == ProjectMember.project_id
        ).filter(
            ProjectMember.employee_id == current_user.employee_id
        )

    return query.order_by(Project.id.desc()).all()

@router.get("/active", response_model=list[ProjectResponse])
def get_active_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Project).filter(
        Project.status == "ongoing"
    )

    if current_user.role == "employee":
        query = query.join(
            ProjectMember,
            Project.id == ProjectMember.project_id
        ).filter(
            ProjectMember.employee_id == current_user.employee_id
        )

    return query.all()


@router.get("/delayed", response_model=list[ProjectResponse])
def get_delayed_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from datetime import date

    query = db.query(Project).filter(
        Project.deadline < date.today(),
        Project.status.notin_(["completed", "cancelled"])
    )

    if current_user.role == "employee":
        query = query.join(
            ProjectMember,
            Project.id == ProjectMember.project_id
        ).filter(
            ProjectMember.employee_id == current_user.employee_id
        )

    return query.all()


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_accessible_project(
        project_id,
        db,
        current_user
    )


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    data: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager)
):
    project = db.query(Project).filter(
        Project.id == project_id
    ).first()

    if not project:
        raise HTTPException(404, "Project not found")

    updates = data.model_dump(exclude_unset=True)

    if updates.get("name") is None and "name" in updates:
        raise HTTPException(422, "Project name cannot be null")

    if updates.get("progress") is not None:
        if not 0 <= updates["progress"] <= 100:
            raise HTTPException(422, "Progress must be between 0 and 100")

    if updates.get("project_manager_id") is not None:
        manager = db.query(Employee).filter(
            Employee.id == updates["project_manager_id"]
        ).first()

        if not manager:
            raise HTTPException(404, "Project manager not found")

    for key, value in updates.items():
        setattr(project, key, value)

    db.commit()
    db.refresh(project)

    return project


@router.delete("/{project_id}")
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager)
):
    project = db.query(Project).filter(
        Project.id == project_id
    ).first()

    if not project:
        raise HTTPException(404, "Project not found")

    # Prevent accidental deletion of projects with records
    has_tasks = db.query(Task).filter(
        Task.project_id == project_id
    ).first()

    has_members = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id
    ).first()

    if has_tasks or has_members:
        raise HTTPException(
            409,
            "Remove project tasks and members before deleting this project"
        )

    db.delete(project)
    db.commit()

    return {"message": "Project deleted successfully"}


# ---------------- PROJECT MEMBERS ----------------

@router.post(
    "/{project_id}/members",
    response_model=ProjectMemberResponse,
    status_code=201
)
def add_project_member(
    project_id: int,
    data: ProjectMemberCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager)
):
    project = db.query(Project).filter(
        Project.id == project_id
    ).first()

    if not project:
        raise HTTPException(404, "Project not found")

    employee = db.query(Employee).filter(
        Employee.id == data.employee_id
    ).first()

    if not employee:
        raise HTTPException(404, "Employee not found")

    existing = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.employee_id == data.employee_id
    ).first()

    if existing:
        raise HTTPException(409, "Employee already assigned")

    member = ProjectMember(
        project_id=project_id,
        employee_id=data.employee_id,
        role=data.role
    )

    db.add(member)
    db.commit()
    db.refresh(member)

    return member


@router.get("/{project_id}/members")
def get_project_members(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager)
):
    project = db.query(Project).filter(
        Project.id == project_id
    ).first()

    if not project:
        raise HTTPException(404, "Project not found")

    members = db.query(
        ProjectMember,
        Employee
    ).join(
        Employee,
        ProjectMember.employee_id == Employee.id
    ).filter(
        ProjectMember.project_id == project_id
    ).all()

    return [
        {
            "employee_id": employee.id,
            "employee_name": employee.name,
            "email": employee.email,
            "designation": employee.designation,
            "role": member.role
        }
        for member, employee in members
    ]


@router.delete("/{project_id}/members/{employee_id}")
def remove_project_member(
    project_id: int,
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager)
):
    member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.employee_id == employee_id
    ).first()

    if not member:
        raise HTTPException(404, "Project member not found")

    db.delete(member)
    db.commit()

    return {"message": "Project member removed successfully"}


# ---------------- TASK MANAGEMENT ----------------

@router.post(
    "/{project_id}/tasks",
    response_model=TaskResponse,
    status_code=201
)
def create_task(
    project_id: int,
    data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager)
):
    project = db.query(Project).filter(
        Project.id == project_id
    ).first()

    if not project:
        raise HTTPException(404, "Project not found")

    if data.assigned_to is not None:
        employee = db.query(Employee).filter(
            Employee.id == data.assigned_to
        ).first()

        if not employee:
            raise HTTPException(404, "Employee not found")

        member = db.query(ProjectMember).filter(
            ProjectMember.project_id == project_id,
            ProjectMember.employee_id == data.assigned_to
        ).first()

        if not member:
            raise HTTPException(
                400,
                "Assign the employee to the project before assigning tasks"
            )

    task = Task(
        project_id=project_id,
        **data.model_dump()
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return task


@router.get("/{project_id}/tasks", response_model=list[TaskResponse])
def get_project_tasks(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    get_accessible_project(project_id, db, current_user)

    query = db.query(Task).filter(
        Task.project_id == project_id
    )

    if current_user.role == "employee":
        query = query.filter(
            Task.assigned_to == current_user.employee_id
        )

    return query.order_by(Task.id.desc()).all()


@router.get("/{project_id}/tasks/pending")
def get_pending_tasks(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    get_accessible_project(project_id, db, current_user)

    query = db.query(Task).filter(
        Task.project_id == project_id,
        Task.status == "pending"
    )

    if current_user.role == "employee":
        query = query.filter(
            Task.assigned_to == current_user.employee_id
        )

    return query.all()


@router.put(
    "/tasks/{task_id}",
    response_model=TaskResponse
)
def update_task(
    task_id: int,
    data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager)
):
    task = db.query(Task).filter(
        Task.id == task_id
    ).first()

    if not task:
        raise HTTPException(404, "Task not found")

    updates = data.model_dump(exclude_unset=True)

    if "title" in updates and updates["title"] is None:
        raise HTTPException(422, "Task title cannot be null")

    if updates.get("assigned_to") is not None:
        employee = db.query(Employee).filter(
            Employee.id == updates["assigned_to"]
        ).first()

        if not employee:
            raise HTTPException(404, "Employee not found")

        member = db.query(ProjectMember).filter(
            ProjectMember.project_id == task.project_id,
            ProjectMember.employee_id == updates["assigned_to"]
        ).first()

        if not member:
            raise HTTPException(400, "Employee is not a project member")

    for key, value in updates.items():
        setattr(task, key, value)

    db.commit()
    db.refresh(task)

    return task


@router.delete("/tasks/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager)
):
    task = db.query(Task).filter(
        Task.id == task_id
    ).first()

    if not task:
        raise HTTPException(404, "Task not found")

    db.delete(task)
    db.commit()

    return {"message": "Task deleted successfully"}


# ---------------- PROJECT SUMMARY ----------------

@router.get("/{project_id}/summary")
def get_project_summary(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager)
):
    project = db.query(Project).filter(
        Project.id == project_id
    ).first()

    if not project:
        raise HTTPException(404, "Project not found")

    total_members = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id
    ).count()

    total_tasks = db.query(Task).filter(
        Task.project_id == project_id
    ).count()

    completed_tasks = db.query(Task).filter(
        Task.project_id == project_id,
        Task.status == "completed"
    ).count()

    pending_tasks = db.query(Task).filter(
        Task.project_id == project_id,
        Task.status == "pending"
    ).count()

    return {
        "project_id": project.id,
        "project_name": project.name,
        "status": project.status,
        "progress": project.progress,
        "team_size": total_members,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "pending_tasks": pending_tasks,
        "deadline": project.deadline
    }
