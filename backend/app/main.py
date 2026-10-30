
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.project_intelligence import router as project_intelligence_router
from app.api.employees import router as employee_router
from app.api.departments import router as department_router
from app.api.attendance import router as attendance_router
from app.api.projects import router as project_router
from app.api.chat import router as chat_router
from app.api.employee_intelligence import router as employee_intelligence_router

app = FastAPI(
    title="OrgMind AI",
    description="AI-Powered Company Management System",
    version="1.0.0"
)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(employee_router)
app.include_router(department_router)
app.include_router(attendance_router)
app.include_router(project_router)
app.include_router(chat_router)
app.include_router(project_intelligence_router)
app.include_router(employee_intelligence_router)

@app.get("/")
def home():
    return {
        "message": "OrgMind AI Backend is running!"
    }
