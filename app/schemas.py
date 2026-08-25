from pydantic import BaseModel, EmailStr, Field
from typing import Literal


# =========================================================
# USER SCHEMAS
# =========================================================

class UserCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="User's full name"
    )

    email: EmailStr


class UserUpdate(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    email: EmailStr


# =========================================================
# PROJECT SCHEMAS
# =========================================================

class ProjectCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=150
    )

    description: str = Field(
        ...,
        min_length=5,
        max_length=500
    )

    user_id: int = Field(
        ...,
        gt=0
    )


class ProjectUpdate(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=150
    )

    description: str = Field(
        ...,
        min_length=5,
        max_length=500
    )

    user_id: int = Field(
        ...,
        gt=0
    )


# =========================================================
# TASK SCHEMAS
# =========================================================

class TaskCreate(BaseModel):
    title: str = Field(
        ...,
        min_length=2,
        max_length=200
    )

    description: str = Field(
        ...,
        min_length=5,
        max_length=1000
    )

    status: Literal["todo", "in-progress", "done"]

    project_id: int = Field(
        ...,
        gt=0
    )


class TaskUpdate(BaseModel):
    title: str = Field(
        ...,
        min_length=2,
        max_length=200
    )

    description: str = Field(
        ...,
        min_length=5,
        max_length=1000
    )

    status: Literal["todo", "in-progress", "done"]

    project_id: int = Field(
        ...,
        gt=0
    )