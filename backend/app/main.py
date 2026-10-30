
from fastapi import FastAPI
from app.api.employees import router as employee_router
from app.api.departments import router as department_router

app = FastAPI(
    title="OrgMind AI",
    description="AI-powered Organization Management and Intelligence System",
    version="1.0.0"
)

app.include_router(employee_router)
app.include_router(department_router)


@app.get("/")
def home():
    return {
        "application": "OrgMind AI",
        "message": "Organization Intelligence System is running!",
        "status": "success"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }
