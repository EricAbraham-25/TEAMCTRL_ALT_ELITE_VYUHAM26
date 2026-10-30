from app.database.connection import Base, engine

# Import models so SQLAlchemy registers all tables
from app.models import (
    Department,
    Employee,
    Attendance,
    Project,
    ProjectMember,
    Task
)

def create_tables():
    Base.metadata.create_all(bind=engine)
    print("All database tables created successfully!")


if __name__ == "__main__":
    create_tables()