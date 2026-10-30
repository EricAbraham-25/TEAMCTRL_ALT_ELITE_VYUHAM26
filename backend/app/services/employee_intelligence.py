
from datetime import date
from sqlalchemy.orm import Session

from app.models.company import Employee, Task


def analyze_employee(db: Session, employee_id: int):
    employee = db.query(Employee).filter(
        Employee.id == employee_id
    ).first()

    if not employee:
        return {"error": "Employee not found"}

    tasks = db.query(Task).filter(
        Task.assigned_to == employee_id
    ).all()

    today = date.today()

    total_tasks = len(tasks)

    completed_tasks = [
        task for task in tasks
        if (task.status or "").lower() == "completed"
    ]

    pending_tasks = [
        task for task in tasks
        if (task.status or "").lower() in ["pending", "in_progress"]
    ]

    overdue_tasks = [
        task for task in tasks
        if task.due_date
        and task.due_date < today
        and (task.status or "").lower() != "completed"
    ]

    completion_percentage = (
        round(len(completed_tasks) / total_tasks * 100, 2)
        if total_tasks else 0
    )

    insights = []

    if len(pending_tasks) >= 5:
        insights.append("High pending task workload")

    if overdue_tasks:
        insights.append(
            f"{len(overdue_tasks)} task(s) are overdue"
        )

    if total_tasks > 0 and completion_percentage < 30:
        insights.append("Low task completion percentage")

    return {
        "employee_id": employee.id,
        "employee_name": employee.name,
        "designation": employee.designation,
        "department": (
            employee.department.name
            if employee.department else None
        ),
        "total_tasks": total_tasks,
        "completed_tasks": len(completed_tasks),
        "pending_tasks": len(pending_tasks),
        "overdue_tasks": [
            {
                "title": task.title,
                "due_date": task.due_date,
                "priority": task.priority
            }
            for task in overdue_tasks
        ],
        "completion_percentage": completion_percentage,
        "insights": insights,
        "insight_count": len(insights)
    }
