


# schemas.py

from pydantic import BaseModel, Field, model_validator
from fastapi import UploadFile
from typing import List, Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str


class User(UserBase):
    id: int
    avatar_url: str = "default.jpg"

    class Config:
        from_attributes = True  # Для совместимости с SQLAlchemy

# При регистрации
class UserCreate(BaseModel):
    username: str
    password: str

# Для ответа
class UserOut(BaseModel):
    id: int
    username: str
    public_name: Optional[str] = "Пользователь"
    bio: Optional[str] = "Описание отсутствует"
    avatar_url: Optional[str] = "/default.png"
    is_admin: bool = Field(default=False, description="Является ли пользователь администратором")

    class Config:
        from_attributes = True

    @model_validator(mode='before')
    def set_admin_status(cls, values):
        # Если передан объект SQLAlchemy
        if hasattr(values, 'admin_profile'):
            values.is_admin = values.admin_profile is not None
        # Если передан словарь
        elif 'admin_profile' in values:
            values.is_admin = values['admin_profile'] is not None
        return values

# Для обновления профиля
class UserUpdate(BaseModel):
    public_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None

    class Config:
        from_attributes = True

class PasswordChange(BaseModel):
    old_password: str
    new_password: str


class FilmBase(BaseModel):
    title: str
    description: str

class FilmCreateWithPoster(BaseModel):
    title: str
    description: Optional[str] = None
    poster: UploadFile

class Film(FilmBase):
    id: int
    reviews: List['Review'] = []

    class Config:
        from_attributes = True

class FilmOut(FilmBase):
    id: int
    poster_url: str

    class Config:
        from_attributes = True


class ReviewBase(BaseModel):
    text: str

class ReviewCreate(ReviewBase):
    pass

class Review(ReviewBase):
    id: int
    created_at: datetime
    author_id: int
    film_id: int

    class Config:
        from_attributes = True