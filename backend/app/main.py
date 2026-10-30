from fastapi import FastAPI

app = FastAPI(
    title="OrgMind AI",
    description="AI-powered Organization Intelligence System",
    version="1.0.0"
)


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