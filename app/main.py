import os

from dotenv import load_dotenv
from fastapi import FastAPI, status, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session

from app.database import SessionLocal, engine, Base
from app import models

from app.schemas import (
    UserCreate,
    UserUpdate,
    ProjectCreate,
    ProjectUpdate,
    TaskCreate,
    TaskUpdate
)


# =========================================================
# ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()

APP_NAME = os.getenv("APP_NAME")
APP_VERSION = os.getenv("APP_VERSION")


# =========================================================
# CREATE DATABASE TABLES
# =========================================================

Base.metadata.create_all(bind=engine)


# =========================================================
# DATABASE SESSION
# =========================================================

def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# =========================================================
# FASTAPI APP
# =========================================================

app = FastAPI(
    title="Users, Projects & Tasks API",
    description="REST API for managing users, projects, and tasks",
    version=APP_VERSION or "1.0.0"
)


# =========================================================
# CENTRALIZED ERROR HANDLING
# =========================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={
            "success": False,
            "error": "Validation error",
            "details": exc.errors()
        }
    )


# =========================================================
# HOME
# =========================================================

@app.get("/")
def home():

    return {
        "message": f"{APP_NAME or 'Users, Projects & Tasks API'} is running"
    }


# =========================================================
# USERS
# =========================================================

# CREATE USER
@app.post("/users", status_code=status.HTTP_201_CREATED)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):

    new_user = models.User(
        name=user.name,
        email=user.email
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User created successfully",
        "user": {
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email
        }
    }


# GET ALL USERS
@app.get("/users")
def get_users(db: Session = Depends(get_db)):

    users = db.query(models.User).all()

    return {
        "message": "Users retrieved successfully",
        "users": users
    }


# GET USER BY ID
@app.get("/users/{user_id}")
def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):

    user = db.query(models.User).filter(
        models.User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return {
        "message": "User retrieved successfully",
        "user": user
    }


# UPDATE USER
@app.put("/users/{user_id}")
def update_user(
    user_id: int,
    user: UserUpdate,
    db: Session = Depends(get_db)
):

    existing_user = db.query(models.User).filter(
        models.User.id == user_id
    ).first()

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    existing_user.name = user.name
    existing_user.email = user.email

    db.commit()
    db.refresh(existing_user)

    return {
        "message": "User updated successfully",
        "user": existing_user
    }


# DELETE USER
@app.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db)
):

    user = db.query(models.User).filter(
        models.User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    db.delete(user)
    db.commit()

    return {
        "message": "User deleted successfully"
    }


# =========================================================
# PROJECTS
# =========================================================

# CREATE PROJECT
@app.post("/projects", status_code=status.HTTP_201_CREATED)
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db)
):

    user = db.query(models.User).filter(
        models.User.id == project.user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    new_project = models.Project(
        name=project.name,
        description=project.description,
        user_id=project.user_id
    )

    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    return {
        "message": "Project created successfully",
        "project": new_project
    }


# GET ALL PROJECTS
@app.get("/projects")
def get_projects(db: Session = Depends(get_db)):

    projects = db.query(models.Project).all()

    return {
        "message": "Projects retrieved successfully",
        "projects": projects
    }


# GET PROJECT BY ID
@app.get("/projects/{project_id}")
def get_project(
    project_id: int,
    db: Session = Depends(get_db)
):

    project = db.query(models.Project).filter(
        models.Project.id == project_id
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    return {
        "message": "Project retrieved successfully",
        "project": project
    }


# UPDATE PROJECT
@app.put("/projects/{project_id}")
def update_project(
    project_id: int,
    project: ProjectUpdate,
    db: Session = Depends(get_db)
):

    existing_project = db.query(models.Project).filter(
        models.Project.id == project_id
    ).first()

    if not existing_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    user = db.query(models.User).filter(
        models.User.id == project.user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    existing_project.name = project.name
    existing_project.description = project.description
    existing_project.user_id = project.user_id

    db.commit()
    db.refresh(existing_project)

    return {
        "message": "Project updated successfully",
        "project": existing_project
    }


# DELETE PROJECT
@app.delete("/projects/{project_id}")
def delete_project(
    project_id: int,
    db: Session = Depends(get_db)
):

    project = db.query(models.Project).filter(
        models.Project.id == project_id
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    db.delete(project)
    db.commit()

    return {
        "message": "Project deleted successfully"
    }


# =========================================================
# TASKS
# =========================================================

# CREATE TASK
@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db)
):

    project = db.query(models.Project).filter(
        models.Project.id == task.project_id
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    new_task = models.Task(
        title=task.title,
        description=task.description,
        status=task.status,
        project_id=task.project_id
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return {
        "message": "Task created successfully",
        "task": new_task
    }


# GET ALL TASKS
@app.get("/tasks")
def get_tasks(db: Session = Depends(get_db)):

    tasks = db.query(models.Task).all()

    return {
        "message": "Tasks retrieved successfully",
        "tasks": tasks
    }


# GET TASK BY ID
@app.get("/tasks/{task_id}")
def get_task(
    task_id: int,
    db: Session = Depends(get_db)
):

    task = db.query(models.Task).filter(
        models.Task.id == task_id
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return {
        "message": "Task retrieved successfully",
        "task": task
    }


# UPDATE TASK
@app.put("/tasks/{task_id}")
def update_task(
    task_id: int,
    task: TaskUpdate,
    db: Session = Depends(get_db)
):

    existing_task = db.query(models.Task).filter(
        models.Task.id == task_id
    ).first()

    if not existing_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    project = db.query(models.Project).filter(
        models.Project.id == task.project_id
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    existing_task.title = task.title
    existing_task.description = task.description
    existing_task.status = task.status
    existing_task.project_id = task.project_id

    db.commit()
    db.refresh(existing_task)

    return {
        "message": "Task updated successfully",
        "task": existing_task
    }


# DELETE TASK
@app.delete("/tasks/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db)
):

    task = db.query(models.Task).filter(
        models.Task.id == task_id
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    db.delete(task)
    db.commit()

    return {
        "message": "Task deleted successfully"
    }