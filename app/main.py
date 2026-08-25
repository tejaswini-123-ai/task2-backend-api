import os

from dotenv import load_dotenv
from fastapi import FastAPI, status, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.schemas import (
    UserCreate,
    UserUpdate,
    ProjectCreate,
    ProjectUpdate,
    TaskCreate,
    TaskUpdate
)

load_dotenv()

APP_NAME = os.getenv("APP_NAME")
APP_VERSION = os.getenv("APP_VERSION")

app = FastAPI(
    title="Users, Projects & Tasks API",
    description="REST API for managing users, projects, and tasks",
    version="1.0.0"
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
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": "Validation error",
            "details": exc.errors()
        }
    )


# =========================================================
# TEMPORARY STORAGE
# =========================================================

users = []
projects = []
tasks = []


# =========================================================
# ID COUNTERS
# =========================================================

user_id_counter = 1
project_id_counter = 1
task_id_counter = 1


# =========================================================
# HOME
# =========================================================

@app.get("/")
def home():
    return "Users, Projects & Tasks API is running"


# =========================================================
# USERS
# =========================================================

# CREATE USER
@app.post("/users", status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate):
    global user_id_counter

    new_user = {
        "id": user_id_counter,
        "name": user.name,
        "email": user.email
    }

    users.append(new_user)
    user_id_counter += 1

    return {
        "message": "User created successfully",
        "user": new_user
    }


# GET ALL USERS
@app.get("/users")
def get_users():
    return {
        "message": "Users retrieved successfully",
        "users": users
    }


# GET USER BY ID
@app.get("/users/{user_id}")
def get_user(user_id: int):

    for user in users:
        if user["id"] == user_id:
            return {
                "message": "User retrieved successfully",
                "user": user
            }

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found"
    )


# UPDATE USER
@app.put("/users/{user_id}")
def update_user(user_id: int, user: UserUpdate):

    for existing_user in users:
        if existing_user["id"] == user_id:

            existing_user["name"] = user.name
            existing_user["email"] = user.email

            return {
                "message": "User updated successfully",
                "user": existing_user
            }

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found"
    )


# DELETE USER
@app.delete("/users/{user_id}")
def delete_user(user_id: int):

    for user in users:
        if user["id"] == user_id:

            users.remove(user)

            return {
                "message": "User deleted successfully",
                "user": user
            }

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found"
    )


# =========================================================
# PROJECTS
# =========================================================

# CREATE PROJECT
@app.post("/projects", status_code=status.HTTP_201_CREATED)
def create_project(project: ProjectCreate):
    global project_id_counter

    # Check if user exists
    user_exists = False

    for user in users:
        if user["id"] == project.user_id:
            user_exists = True
            break

    if not user_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    new_project = {
        "id": project_id_counter,
        "name": project.name,
        "description": project.description,
        "user_id": project.user_id
    }

    projects.append(new_project)
    project_id_counter += 1

    return {
        "message": "Project created successfully",
        "project": new_project
    }


# GET ALL PROJECTS
@app.get("/projects")
def get_projects():
    return {
        "message": "Projects retrieved successfully",
        "projects": projects
    }


# GET PROJECT BY ID
@app.get("/projects/{project_id}")
def get_project(project_id: int):

    for project in projects:
        if project["id"] == project_id:
            return {
                "message": "Project retrieved successfully",
                "project": project
            }

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Project not found"
    )


# UPDATE PROJECT
@app.put("/projects/{project_id}")
def update_project(
    project_id: int,
    project: ProjectUpdate
):

    # Check if user exists
    user_exists = False

    for user in users:
        if user["id"] == project.user_id:
            user_exists = True
            break

    if not user_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    for existing_project in projects:
        if existing_project["id"] == project_id:

            existing_project["name"] = project.name
            existing_project["description"] = project.description
            existing_project["user_id"] = project.user_id

            return {
                "message": "Project updated successfully",
                "project": existing_project
            }

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Project not found"
    )


# DELETE PROJECT
@app.delete("/projects/{project_id}")
def delete_project(project_id: int):

    for project in projects:
        if project["id"] == project_id:

            projects.remove(project)

            return {
                "message": "Project deleted successfully",
                "project": project
            }

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Project not found"
    )


# =========================================================
# TASKS
# =========================================================

# CREATE TASK
@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate):
    global task_id_counter

    # Check if project exists
    project_exists = False

    for project in projects:
        if project["id"] == task.project_id:
            project_exists = True
            break

    if not project_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    new_task = {
        "id": task_id_counter,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "project_id": task.project_id
    }

    tasks.append(new_task)
    task_id_counter += 1

    return {
        "message": "Task created successfully",
        "task": new_task
    }


# GET ALL TASKS
@app.get("/tasks")
def get_tasks():
    return {
        "message": "Tasks retrieved successfully",
        "tasks": tasks
    }


# GET TASK BY ID
@app.get("/tasks/{task_id}")
def get_task(task_id: int):

    for task in tasks:
        if task["id"] == task_id:
            return {
                "message": "Task retrieved successfully",
                "task": task
            }

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Task not found"
    )


# UPDATE TASK
@app.put("/tasks/{task_id}")
def update_task(
    task_id: int,
    task: TaskUpdate
):

    # Check if project exists
    project_exists = False

    for project in projects:
        if project["id"] == task.project_id:
            project_exists = True
            break

    if not project_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    for existing_task in tasks:
        if existing_task["id"] == task_id:

            existing_task["title"] = task.title
            existing_task["description"] = task.description
            existing_task["status"] = task.status
            existing_task["project_id"] = task.project_id

            return {
                "message": "Task updated successfully",
                "task": existing_task
            }

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Task not found"
    )


# DELETE TASK
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):

    for task in tasks:
        if task["id"] == task_id:

            tasks.remove(task)

            return {
                "message": "Task deleted successfully",
                "task": task
            }

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Task not found"
    )