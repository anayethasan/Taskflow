from fastapi import FastAPI
from app.api.routes import users
from app.api.routes import auth

app = FastAPI(
    title="Taskflow API",
    description="Team and project management api",
    version="1.0.0",
)

app.include_router(users.router)
app.include_router(auth.router)

@app.get("/")
def root():
    return {"message": "Welcome our Taskflow"}

@app.get("/health")
def health_check():
    return {"message": "healthy"}

