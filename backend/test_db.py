
from sqlalchemy import text
from app.database.connection import engine

with engine.connect() as connection:
    result = connection.execute(text("""
        SELECT
            current_database(),
            current_schema(),
            current_user,
            COUNT(*) FILTER (WHERE table_name = 'employees') AS employee_table_exists
        FROM information_schema.tables
        WHERE table_schema = 'public'
    """))

    print("Database connection successful!")

    print("Database:", connection.execute(
        text("SELECT current_database()")
    ).scalar())

    print("Employee count:", connection.execute(
        text("SELECT COUNT(*) FROM public.employees")
    ).scalar())

    print("Project count:", connection.execute(
        text("SELECT COUNT(*) FROM public.projects")
    ).scalar())
