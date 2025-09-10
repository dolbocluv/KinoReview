


# crud.py

from typing import Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select
from security import get_password_hash
from models import User, Film, Review
from schemas import UserCreate, UserUpdate, FilmCreateWithPoster, ReviewCreate
from fastapi import HTTPException, Path, UploadFile
import os

import uuid

# === ПОЛЬЗОВАТЕЛИ ===

def get_user_by_username(db: Session, username: str):
    return db.query(User).options(joinedload(User.admin_profile)).filter(User.username == username).first()

def get_user_by_id(db: Session, user_id: int):
    """Получить пользователя по его ID"""
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, user: UserCreate):
    """Создать нового пользователя"""
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        hashed_password=hashed_password,
        avatar_url="/static/default.png"
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_update: UserUpdate):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    if user_update.username:
        db_user.username = user_update.username
    if user_update.avatar_url:
        db_user.avatar_url = user_update.avatar_url
    
    db.commit()
    db.refresh(db_user)
    return db_user


# === ФИЛЬМЫ ===

def get_film(db: Session, film_id: int):
    # Явно загружаем отзывы вместе с фильмом
    film = db.query(Film).options(joinedload(Film.reviews)).filter(Film.id == film_id).first()
    return film

def get_films(db: Session, skip: int = 0, limit: int = 100):
    """Получить список фильмов"""
    return db.query(Film).offset(skip).limit(limit).all()

async def create_film(
    db: Session,
    title: str,
    description: Optional[str],
    poster: UploadFile,
    current_user: User  # Изменили параметр с user на current_user
):
    if not current_user.admin_profile:
        raise HTTPException(status_code=403, detail="Требуются права администратора")
    
    # 1. Проверка типа файла
    allowed_types = ["image/jpeg", "image/png", "image/webp"]
    if poster.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Допустимы только JPG/PNG/WEBP изображения"
        )

    # 2. Создаем папку для постеров
    poster_dir = Path("static/posters")
    poster_dir.mkdir(exist_ok=True, parents=True)
    
    # 3. Генерируем уникальное имя файла
    file_ext = Path(poster.filename).suffix.lower()
    poster_filename = f"{uuid.uuid4()}{file_ext}"
    poster_path = poster_dir / poster_filename

    # 4. Сохраняем файл
    try:
        with open(poster_path, "wb") as buffer:
            content = await poster.read()
            buffer.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка сохранения файла: {str(e)}"
        )

    # 5. Создаем запись в БД
    try:
        db_film = Film(
            title=title,
            description=description,
            poster_url=f"/static/posters/{poster_filename}"
        )
        db.add(db_film)
        db.commit()
        db.refresh(db_film)
        return db_film
    except Exception as e:
        db.rollback()
        # Удаляем файл если не удалось сохранить в БД
        if poster_path.exists():
            poster_path.unlink()
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка создания фильма: {str(e)}"
        )


# === ОТЗЫВЫ ===

def get_reviews_by_film(db: Session, film_id: int):
    """Получить все отзывы к фильму"""
    return db.query(Review).options(joinedload(Review.author)).filter(Review.film_id == film_id).all()

def create_film_review(db: Session, review: ReviewCreate, film_id: int, user_id: int):
    """Создать отзыв к фильму от пользователя"""
    db_review = Review(
        text=review.text,
        film_id=film_id,
        author_id=user_id
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review
