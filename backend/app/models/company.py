
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Date,
    DateTime,
    ForeignKey,
    UniqueConstraint
)
from sqlalchemy.sql import func

from app.database.connection import Base


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    employee_code = Column(String(50), unique=True, nullable=False)
    name = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    designation = Column(String(100))
    department_id = Column(
        Integer,
        ForeignKey("departments.id")
    )
    employment_status = Column(String(30), default="active")

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(
        Integer,
        ForeignKey("employees.id"),
        nullable=False
    )
    attendance_date = Column(Date, nullable=False)
    check_in = Column(DateTime(timezone=True))
    check_out = Column(DateTime(timezone=True))
    status = Column(String(30), default="present")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    project_manager_id = Column(
        Integer,
        ForeignKey("employees.id")
    )
    start_date = Column(Date)
    deadline = Column(Date)
    status = Column(String(30), default="planned")
    progress = Column(Integer, default=0)


class ProjectMember(Base):
    __tablename__ = "project_members"

    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "employee_id",
            name="unique_project_employee"
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(
        Integer,
        ForeignKey("projects.id"),
        nullable=False
    )
    employee_id = Column(
        Integer,
        ForeignKey("employees.id"),
        nullable=False
    )
    role = Column(String(100))


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(
        Integer,
        ForeignKey("projects.id"),
        nullable=False
    )
    assigned_to = Column(
        Integer,
        ForeignKey("employees.id")
    )
    title = Column(String(200), nullable=False)
    description = Column(Text)
    status = Column(String(30), default="pending")
    priority = Column(String(30), default="medium")
    progress = Column(Integer, default=0)
    due_date = Column(Date)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
