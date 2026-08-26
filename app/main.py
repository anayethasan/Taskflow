from fastapi import FastAPI

app = FastAPI(
    title="Taskflow API",
    description="Team and project management api",
    version="1.0.0",
)

@app.get("/")
def root():
    return {"message": "Welcome our Taskflow"}

@app.get("/health")
def health_check():
    return {"message": "healthy"}

