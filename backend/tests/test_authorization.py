import os
import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("JWT_SECRET_KEY", os.getenv("JWT_SECRET_KEY", ""))

from app.main import app
from app.core.security import create_access_token
from app.database.connection import SessionLocal
from app.models.company import User, Employee, Project, ProjectMember, Task

client = TestClient(app)


def _db():
    return SessionLocal()


@pytest.fixture(scope="module")
def manager_user():
    db = _db()
    user = db.query(User).filter(User.role == "manager").first()
    db.close()
    assert user is not None, "No manager account found in DB for testing"
    return user


@pytest.fixture(scope="module")
def employee_user():
    db = _db()
    user = db.query(User).filter(
        User.role == "employee", User.employee_id.isnot(None)
    ).first()
    db.close()
    assert user is not None, "No employee account found in DB for testing"
    return user


@pytest.fixture(scope="module")
def other_employee_id(employee_user):
    db = _db()
    other = db.query(Employee).filter(
        Employee.id != employee_user.employee_id
    ).first()
    db.close()
    assert other is not None, "Need a second employee record for IDOR tests"
    return other.id


@pytest.fixture(scope="module")
def employee_project_id(employee_user):
    db = _db()
    membership = db.query(ProjectMember).filter(
        ProjectMember.employee_id == employee_user.employee_id
    ).first()
    db.close()
    assert membership is not None, "Employee must belong to at least one project"
    return membership.project_id


@pytest.fixture(scope="module")
def unrelated_project_id(employee_user, employee_project_id):
    db = _db()
    project = db.query(Project).filter(
        Project.id != employee_project_id
    ).first()
    db.close()
    if project is None:
        pytest.skip("No second project exists to test unrelated-project denial")
    return project.id


@pytest.fixture(scope="module")
def employee_task(employee_user):
    db = _db()
    task = db.query(Task).filter(
        Task.assigned_to == employee_user.employee_id
    ).first()
    db.close()
    assert task is not None, "Employee must have at least one assigned task"
    return task.id


def auth_header(user):
    token = create_access_token(
        user_id=user.id, role=user.role, employee_id=user.employee_id
    )
    return {"Authorization": f"Bearer {token}"}


# ---------------- AUTHENTICATION ----------------

class TestAuthentication:
    def test_no_token_rejected_on_employee_intelligence(self):
        r = client.get("/api/employee-intelligence/overview")
        assert r.status_code == 401

    def test_no_token_rejected_on_project_intelligence(self):
        r = client.get("/api/project-intelligence/overview")
        assert r.status_code == 401

    def test_no_token_rejected_on_chat(self):
        r = client.post("/api/chat/", json={"question": "hello"})
        assert r.status_code == 401

    def test_invalid_token_rejected(self):
        r = client.get(
            "/api/employee-intelligence/overview",
            headers={"Authorization": "Bearer not-a-real-token"}
        )
        assert r.status_code == 401

    def test_manager_token_accepted(self, manager_user):
        r = client.get("/api/employee-intelligence/overview", headers=auth_header(manager_user))
        assert r.status_code == 200

    def test_employee_token_accepted(self, employee_user):
        r = client.get("/api/employee-intelligence/overview", headers=auth_header(employee_user))
        assert r.status_code == 200

# ---------------- EMPLOYEE INTELLIGENCE ----------------

class TestEmployeeIntelligence:
    def test_manager_can_access_any_employee_intelligence(self, manager_user, other_employee_id):
        r = client.get(f"/api/employee-intelligence/{other_employee_id}/analysis", headers=auth_header(manager_user))
        assert r.status_code == 200
        assert r.json()["employee_id"] == other_employee_id

    def test_employee_can_access_own_intelligence(self, employee_user):
        r = client.get(
            f"/api/employee-intelligence/{employee_user.employee_id}/analysis",
            headers=auth_header(employee_user)
        )
        assert r.status_code == 200
        assert r.json()["employee_id"] == employee_user.employee_id

    def test_employee_cannot_access_other_employee_intelligence(self, employee_user, other_employee_id):
        r = client.get(
            f"/api/employee-intelligence/{other_employee_id}/analysis",
            headers=auth_header(employee_user)
        )
        assert r.status_code == 403

    def test_nonexistent_employee_returns_404(self, manager_user):
        r = client.get("/api/employee-intelligence/999999/analysis", headers=auth_header(manager_user))
        assert r.status_code == 404

    def test_employee_overview_scoped_to_self(self, employee_user):
        r = client.get("/api/employee-intelligence/overview", headers=auth_header(employee_user))
        assert r.status_code == 200
        body = r.json()
        assert body["total_employees"] == 1
        assert body["employees"][0]["employee_id"] == employee_user.employee_id

    def test_manager_overview_sees_all(self, manager_user):
        r = client.get("/api/employee-intelligence/overview", headers=auth_header(manager_user))
        assert r.status_code == 200
        assert r.json()["total_employees"] >= 1


# ---------------- PROJECT INTELLIGENCE ----------------

class TestProjectIntelligence:
    def test_manager_can_access_all_project_intelligence(self, manager_user):
        r = client.get("/api/project-intelligence/overview", headers=auth_header(manager_user))
        assert r.status_code == 200

    def test_employee_can_access_assigned_project_intelligence(self, employee_user, employee_project_id):
        r = client.get(
            f"/api/project-intelligence/{employee_project_id}/analysis",
            headers=auth_header(employee_user)
        )
        assert r.status_code == 200
        assert r.json()["project_id"] == employee_project_id

    def test_employee_cannot_access_unrelated_project_intelligence(self, employee_user, unrelated_project_id):
        r = client.get(
            f"/api/project-intelligence/{unrelated_project_id}/analysis",
            headers=auth_header(employee_user)
        )
        assert r.status_code == 403

    def test_project_intelligence_nonexistent_returns_404(self, manager_user):
        r = client.get("/api/project-intelligence/999999/analysis", headers=auth_header(manager_user))
        assert r.status_code == 404

    def test_employee_overview_scoped_to_memberships(self, employee_user, employee_project_id):
        r = client.get("/api/project-intelligence/overview", headers=auth_header(employee_user))
        assert r.status_code == 200
        ids = [p["project_id"] for p in r.json()["projects"]]
        assert employee_project_id in ids


# ---------------- TASK PROGRESS ----------------

class TestTaskProgress:
    def test_employee_can_update_own_task_progress(self, employee_user, employee_task):
        r = client.patch(
            f"/api/projects/tasks/{employee_task}/progress",
            json={"progress": 55},
            headers=auth_header(employee_user)
        )
        assert r.status_code == 200
        assert r.json()["progress"] == 55

    def test_employee_cannot_change_title_via_progress_endpoint(self, employee_user, employee_task):
        r = client.patch(
            f"/api/projects/tasks/{employee_task}/progress",
            json={"progress": 60, "title": "Hacked title"},
            headers=auth_header(employee_user)
        )
        # Extra field is ignored by the restricted schema; request still succeeds
        # but the title must remain unchanged.
        assert r.status_code == 200
        assert r.json()["title"] != "Hacked title"

    def test_employee_cannot_update_another_employees_task(self, employee_user, manager_user, other_employee_id):
        db = _db()
        foreign_task = db.query(Task).filter(Task.assigned_to == other_employee_id).first()
        db.close()
        if foreign_task is None:
            pytest.skip("No task assigned to the other employee to test against")
        r = client.patch(
            f"/api/projects/tasks/{foreign_task.id}/progress",
            json={"progress": 10},
            headers=auth_header(employee_user)
        )
        assert r.status_code == 403

    def test_progress_out_of_range_rejected(self, employee_user, employee_task):
        r = client.patch(
            f"/api/projects/tasks/{employee_task}/progress",
            json={"progress": 150},
            headers=auth_header(employee_user)
        )
        assert r.status_code == 422

    def test_manager_retains_full_task_update(self, manager_user, employee_task):
        r = client.put(
            f"/api/projects/tasks/{employee_task}",
            json={"priority": "high"},
            headers=auth_header(manager_user)
        )
        assert r.status_code == 200
        assert r.json()["priority"] == "high"

    def test_employee_forbidden_from_full_task_update_endpoint(self, employee_user, employee_task):
        r = client.put(
            f"/api/projects/tasks/{employee_task}",
            json={"priority": "low"},
            headers=auth_header(employee_user)
        )
        assert r.status_code == 403


# ---------------- CHATBOT ----------------

class TestChatbotAuth:
    def test_chat_requires_authentication(self):
        r = client.post("/api/chat/", json={"question": "List all projects"})
        assert r.status_code == 401

    def test_chat_rejects_invalid_token(self):
        r = client.post(
            "/api/chat/",
            json={"question": "List all projects"},
            headers={"Authorization": "Bearer garbage"}
        )
        assert r.status_code == 401
