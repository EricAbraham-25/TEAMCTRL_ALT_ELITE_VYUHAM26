
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.models.company import Project, ProjectMember, User
from app.core.dependencies import get_current_user
from app.services.project_intelligence import analyze_project

router = APIRouter(
    prefix="/api/project-intelligence",
    tags=["Project Intelligence"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ensure_project_access(
    project_id: int,
    db: Session,
    current_user: User
):
    project = db.query(Project).filter(
        Project.id == project_id
    ).first()

    if not project:
        raise HTTPException(404, "Project not found")

    # Managers are global organization administrators.
    if current_user.role == "manager":
        return project

    # Employees may only access projects they are assigned to.
    if current_user.role == "employee":
        if current_user.employee_id is None:
            raise HTTPException(
                403, "No employee profile linked to this account"
            )

        membership = db.query(ProjectMember).filter(
            ProjectMember.project_id == project_id,
            ProjectMember.employee_id == current_user.employee_id
        ).first()

        if not membership:
            raise HTTPException(
                403, "You are not assigned to this project"
            )

        return project

    raise HTTPException(403, "Access denied")


@router.get("/overview")
def project_intelligence_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Project)

    if current_user.role == "employee":
        if current_user.employee_id is None:
            raise HTTPException(
                403, "No employee profile linked to this account"
            )

        query = query.join(
            ProjectMember,
            Project.id == ProjectMember.project_id
        ).filter(
            ProjectMember.employee_id == current_user.employee_id
        )

    projects = query.all()

    analyses = [
        analyze_project(db, project.id)
        for project in projects
    ]

    return {
        "total_projects": len(analyses),
        "at_risk_projects": sum(
            1 for item in analyses
            if item.get("risk_count", 0) > 0
        ),
        "projects": analyses
    }


@router.get("/{project_id}/analysis")
def project_analysis(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ensure_project_access(project_id, db, current_user)

    result = analyze_project(db, project_id)

    if result.get("error"):
        raise HTTPException(
            status_code=404,
            detail=result["error"]
        )

    return result
