
from sqlalchemy import text
from app.database.connection import engine

try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))

        print("================================")
        print("Supabase connection successful!")
        print("Test result:", result.scalar())
        print("================================")

except Exception as error:
    print("Database connection failed!")
    print("Error:", error)
