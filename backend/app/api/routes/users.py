from typing import List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr

from app.api.deps import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


class UserBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None


class UserResponse(UserBase):
    id: int

    class Config:
        orm_mode = True


@router.get("/me", response_model=dict)
async def read_users_me(
    current_user: dict = Depends(get_current_user),
):
    """
    Get current user.
    """
    return current_user


@router.get("/", response_model=List[UserResponse])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user),
):
    """
    Retrieve users.
    """
    # In a real application, you would fetch users from the database
    # For this example, we'll just return a mock list
    return [
        {
            "id": 1,
            "username": "johndoe",
            "email": "johndoe@example.com",
            "full_name": "John Doe",
        }
    ]


@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate):
    """
    Create new user.
    """
    # In a real application, you would create a user in the database
    # For this example, we'll just return a mock response
    return {
        "id": 1,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
    }
