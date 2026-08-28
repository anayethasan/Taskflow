from fastapi import FastAPI
from app.api.routes import users

app = FastAPI(
    title="Taskflow API",
    description="Team and project management api",
    version="1.0.0",
)

app.include_router(users.router)

@app.get("/")
def root():
    return {"message": "Welcome our Taskflow"}

@app.get("/health")
def health_check():
    return {"message": "healthy"}

