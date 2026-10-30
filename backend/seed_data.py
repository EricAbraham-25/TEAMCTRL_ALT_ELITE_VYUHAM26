
from datetime import date, datetime, timedelta

from app.database.connection import SessionLocal
from app.models.company import (
    Department,
    Employee,
    Project,
    ProjectMember,
    Task,
    Attendance,
)

db = SessionLocal()

try:
    # Prevent duplicate sample data
    existing_employee = db.query(Employee).filter(
        Employee.employee_code == "EMP001"
    ).first()

    if existing_employee:
        print("Sample data already exists. No changes made.")

    else:
        # 1. Departments
        ai = Department(
            name="AI & ML",
            description="Artificial Intelligence and Machine Learning"
        )

        dev = Department(
            name="Development",
            description="Software and application development"
        )

        hr = Department(
            name="Human Resources",
            description="Employee management and recruitment"
        )

        db.add_all([ai, dev, hr])
        db.flush()

        # 2. Employees
        employees = [
            Employee(
                employee_code="EMP001",
                name="Abin",
                email="abin@example.com",
                designation="AI Engineer",
                department_id=ai.id,
                employment_status="active"
            ),
            Employee(
                employee_code="EMP002",
                name="Rahul",
                email="rahul@example.com",
                designation="Backend Developer",
                department_id=dev.id,
                employment_status="active"
            ),
            Employee(
                employee_code="EMP003",
                name="Anjali",
                email="anjali@example.com",
                designation="Frontend Developer",
                department_id=dev.id,
                employment_status="active"
            ),
            Employee(
                employee_code="EMP004",
                name="Arjun",
                email="arjun@example.com",
                designation="Data Scientist",
                department_id=ai.id,
                employment_status="active"
            ),
            Employee(
                employee_code="EMP005",
                name="Meera",
                email="meera@example.com",
                designation="HR Manager",
                department_id=hr.id,
                employment_status="active"
            ),
        ]

        db.add_all(employees)
        db.flush()

        # 3. Projects
        project1 = Project(
            name="OrgMind AI",
            description="AI-powered company management platform",
            project_manager_id=employees[0].id,
            start_date=date.today() - timedelta(days=20),
            deadline=date.today() + timedelta(days=30),
            status="ongoing",
            progress=45
        )

        project2 = Project(
            name="Smart Analytics",
            description="Business analytics and reporting platform",
            project_manager_id=employees[3].id,
            start_date=date.today() - timedelta(days=10),
            deadline=date.today() + timedelta(days=45),
            status="ongoing",
            progress=25
        )

        db.add_all([project1, project2])
        db.flush()

        # 4. Project members
        members = [
            ProjectMember(
                project_id=project1.id,
                employee_id=employees[0].id,
                role="AI Developer"
            ),
            ProjectMember(
                project_id=project1.id,
                employee_id=employees[1].id,
                role="Backend Developer"
            ),
            ProjectMember(
                project_id=project1.id,
                employee_id=employees[2].id,
                role="Frontend Developer"
            ),
            ProjectMember(
                project_id=project2.id,
                employee_id=employees[3].id,
                role="Project Lead"
            ),
            ProjectMember(
                project_id=project2.id,
                employee_id=employees[1].id,
                role="Backend Developer"
            ),
            ProjectMember(
                project_id=project2.id,
                employee_id=employees[2].id,
                role="Frontend Developer"
            ),
        ]

        db.add_all(members)

        # 5. Tasks
        tasks = [
            Task(
                project_id=project1.id,
                assigned_to=employees[0].id,
                title="Build AI agent",
                description="Integrate Claude with database tools",
                status="in_progress",
                priority="high",
                progress=60,
                due_date=date.today() + timedelta(days=5)
            ),
            Task(
                project_id=project1.id,
                assigned_to=employees[1].id,
                title="Develop backend APIs",
                description="Build employee and project APIs",
                status="completed",
                priority="high",
                progress=100,
                due_date=date.today() - timedelta(days=2)
            ),
            Task(
                project_id=project1.id,
                assigned_to=employees[2].id,
                title="Design dashboard",
                description="Create company dashboard UI",
                status="pending",
                priority="medium",
                progress=0,
                due_date=date.today() + timedelta(days=10)
            ),
            Task(
                project_id=project2.id,
                assigned_to=employees[3].id,
                title="Build analytics model",
                description="Develop business analytics model",
                status="in_progress",
                priority="high",
                progress=40,
                due_date=date.today() + timedelta(days=7)
            ),
            Task(
                project_id=project2.id,
                assigned_to=employees[1].id,
                title="Create reporting API",
                description="Build reporting endpoints",
                status="pending",
                priority="medium",
                progress=0,
                due_date=date.today() + timedelta(days=15)
            ),
        ]

        db.add_all(tasks)

        # 6. Sample attendance records
        today = date.today()

        attendance = [
            Attendance(
                employee_id=employees[0].id,
                attendance_date=today,
                check_in=datetime.combine(today, datetime.min.time()).replace(
                    hour=9, minute=15
                ),
                status="present"
            ),
            Attendance(
                employee_id=employees[1].id,
                attendance_date=today,
                check_in=datetime.combine(today, datetime.min.time()).replace(
                    hour=9, minute=30
                ),
                status="present"
            ),
            Attendance(
                employee_id=employees[2].id,
                attendance_date=today,
                check_in=datetime.combine(today, datetime.min.time()).replace(
                    hour=9, minute=5
                ),
                status="present"
            ),
        ]

        db.add_all(attendance)

        # 7. Save everything
        db.commit()

        print("Sample company data inserted successfully!")
        print("3 departments created.")
        print("5 employees created.")
        print("2 projects created.")
        print("6 project members created.")
        print("5 tasks created.")
        print("3 attendance records created.")

except Exception:
    db.rollback()
    raise

finally:
    db.close()
