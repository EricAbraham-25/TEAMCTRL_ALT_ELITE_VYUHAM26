from getpass import getpass

from app.database.connection import SessionLocal
from app.models.company import User, Employee
from app.core.security import hash_password


def main():
    db = SessionLocal()

    try:
        print("\n=== OrgMind AI - Create User ===")

        username = input("Username: ").strip()

        if not username:
            print("Username cannot be empty.")
            return

        if db.query(User).filter(User.username == username).first():
            print("Username already exists.")
            return

        role = input("Role (manager/employee): ").strip().lower()

        if role not in ["manager", "employee"]:
            print("Invalid role.")
            return

        employee_id = None

        if role == "employee":
            try:
                employee_id = int(input("Employee ID: "))
            except ValueError:
                print("Invalid employee ID.")
                return

            employee = db.query(Employee).filter(
                Employee.id == employee_id
            ).first()

            if not employee:
                print("Employee not found.")
                return

            existing_account = db.query(User).filter(
                User.employee_id == employee_id
            ).first()

            if existing_account:
                print("This employee already has a login account.")
                return

        password = getpass("Password (minimum 12 characters): ")

        if len(password) < 12:
            print("Password must contain at least 12 characters.")
            return

        confirm_password = getpass("Confirm password: ")

        if password != confirm_password:
            print("Passwords do not match.")
            return

        user = User(
            username=username,
            password_hash=hash_password(password),
            role=role,
            employee_id=employee_id
        )

        db.add(user)
        db.commit()

        print(f"\n{role.capitalize()} account created successfully!")

    except Exception as error:
        db.rollback()
        print("Could not create account:", error)

    finally:
        db.close()


if __name__ == "__main__":
    main()