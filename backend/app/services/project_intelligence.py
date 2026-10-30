from datetime import date
from sqlalchemy.orm import Session

from app.models.company import Project, Task, Employee


def analyze_project(db: Session, project_id: int):
    project = db.query(Project).filter(
        Project.id == project_id
    ).first()

    if not project:
        return {"error": "Project not found"}

    tasks = db.query(Task).filter(
        Task.project_id == project_id
    ).all()

    today = date.today()
    total_tasks = len(tasks)

    completed_tasks = [
        t for t in tasks
        if (t.status or "").lower() == "completed"
    ]

    pending_tasks = [
        t for t in tasks
        if (t.status or "").lower() in ["pending", "in_progress"]
    ]

    overdue_tasks = [
        t for t in tasks
        if t.due_date
        and t.due_date < today
        and (t.status or "").lower() != "completed"
    ]

    remaining_days = (
        (project.deadline - today).days
        if project.deadline else None
    )

    completion_percentage = (
        round(len(completed_tasks) / total_tasks * 100, 2)
        if total_tasks else 0
    )

    risks = []

    if remaining_days is not None and remaining_days < 0:
        risks.append("Project deadline has passed")

    if overdue_tasks:
        risks.append(f"{len(overdue_tasks)} task(s) are overdue")

    if remaining_days is not None and 0 <= remaining_days <= 7 and project.progress < 90:
        risks.append("Deadline approaching but progress is below 90%")

    if project.progress < 30 and remaining_days is not None and remaining_days <= 14:
        risks.append("Low progress with limited remaining time")

    team_workload = {}

    for task in tasks:
        if task.assigned_to:
            employee = db.query(Employee).filter(
                Employee.id == task.assigned_to
            ).first()

            if employee:
                team_workload[employee.name] = (
                    team_workload.get(employee.name, 0) + 1
                )

    return {
        "project_id": project.id,
        "project_name": project.name,
        "status": project.status,
        "progress": project.progress,
        "deadline": project.deadline,
        "remaining_days": remaining_days,
        "total_tasks": total_tasks,
        "completed_tasks": len(completed_tasks),
        "pending_tasks": len(pending_tasks),
        "overdue_tasks": [
            {
                "task": t.title,
                "due_date": t.due_date,
                "assigned_to": t.assigned_to
            }
            for t in overdue_tasks
        ],
        "completion_percentage_from_tasks": completion_percentage,
        "risks": risks,
        "risk_count": len(risks),
        "team_workload": team_workload
    }
