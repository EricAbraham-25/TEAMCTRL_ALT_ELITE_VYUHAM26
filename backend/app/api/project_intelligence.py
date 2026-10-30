
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.models.company import Project
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


@router.get("/overview")
def project_intelligence_overview(db: Session = Depends(get_db)):
    projects = db.query(Project).all()

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
    db: Session = Depends(get_db)
):
    result = analyze_project(db, project_id)

    if result.get("error"):
        raise HTTPException(
            status_code=404,
            detail=result["error"]
        )

    return result
