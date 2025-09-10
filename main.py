# main.py

from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, Form, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session, joinedload
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os
import logging
import uuid

from auth import get_current_user, verify_password, create_access_token, get_current_admin
from models import User, Review, Film as bd_Film
from database import get_db
from schemas import UserCreate, FilmCreateWithPoster, ReviewCreate, Film, UserUpdate, UserOut, PasswordChange, FilmOut
from crud import create_user, get_user_by_username, get_film, create_film_review, get_reviews_by_film, get_films, update_user, create_film
from security import get_password_hash



logger = logging.getLogger(__name__)

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory="static"), name="static")

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# === ПОЛЬЗОВАТЕЛИ ===

@app.post("/register/", status_code=201)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Регистрация нового пользователя"""
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Пользователь с таким логином уже существует")
    return create_user(db=db, user=user)


@app.post("/login/")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = get_user_by_username(db, username=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=400,
            detail="Неверный логин или пароль"
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=UserOut)
def read_users_me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Явно загружаем связанные данные администратора
    user = db.query(User).options(joinedload(User.admin_profile)).filter(User.id == current_user.id).first()
    return user

@app.patch("/users/me")
def update_profile(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if user_update.public_name:
        current_user.public_name = user_update.public_name
    if user_update.bio:
        current_user.bio = user_update.bio
    if user_update.avatar_url:
        current_user.avatar_url = user_update.avatar_url

    db.commit()
    db.refresh(current_user)
    return current_user

@app.post("/users/me/avatar")
async def update_avatar(
    avatar: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # Проверка типа файла
        if not avatar.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Только изображения разрешены")

        # Создаем папку, если не существует
        avatar_dir = Path("static/avatars")
        avatar_dir.mkdir(exist_ok=True, parents=True)

        # Генерируем уникальное имя файла
        file_ext = Path(avatar.filename).suffix
        new_filename = f"{current_user.id}_{uuid.uuid4()}{file_ext}"
        file_path = avatar_dir / new_filename

        # Сохраняем файл
        with open(file_path, "wb") as buffer:
            content = await avatar.read()
            buffer.write(content)

        # Обновляем запись в БД
        current_user.avatar_url = f"http://localhost:8000/static/avatars/{new_filename}"
        db.commit()

        return {"avatar_url": current_user.avatar_url}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/users/me/password")
def change_password(
    password_change: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not verify_password(password_change.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Неверный текущий пароль")

    current_user.hashed_password = get_password_hash(password_change.new_password)
    db.commit()
    return {"detail": "Пароль изменён"}


# === ФИЛЬМЫ ===

from typing import List, Optional

@app.get("/films/", response_model=List[FilmOut])
def read_films(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    films = get_films(db, skip=skip, limit=limit)
    return films

@app.get("/films/{film_id}", response_model=FilmOut)
def read_film(film_id: int, db: Session = Depends(get_db)):
    film = get_film(db, film_id=film_id)
    if not film:
        raise HTTPException(status_code=404, detail="Фильм не найден")
    return film

@app.post("/films/with-poster/")
def create_film(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    poster: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    # Сохранение файла
    poster_dir = "static/posters"
    os.makedirs(poster_dir, exist_ok=True)
    poster_location = f"{poster_dir}/{title}_{poster.filename}"

    with open(poster_location, "wb") as buffer:
        buffer.write(poster.file.read())

    # Добавление фильма в БД
    new_film = bd_Film(
        title=title,
        description=description,
        poster_url=f"/{poster_location}"
    )
    db.add(new_film)
    db.commit()
    db.refresh(new_film)
    return {"detail": "Фильм успешно добавлен"}


# === ОТЗЫВЫ ===

@app.post("/films/{film_id}/reviews/", status_code=201)
def create_review_for_film(
    film_id: int,
    review: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return create_film_review(db=db, review=review, film_id=film_id, user_id=current_user.id)


# Предположим, Review и User уже импортированы
# get_current_user и get_db тоже

@app.get("/films/{film_id}/reviews/", status_code=200)
def get_reviews(film_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    reviews = db.query(Review).options(joinedload(Review.author)).filter(Review.film_id == film_id).all()

    user_review = None
    public_reviews = []

    for review in reviews:
        review_data = {
            "id": review.id,
            "text": review.text,
            "created_at": review.created_at,
            "author_id": review.author_id,
            "author_name": review.author.public_name
        }

        if review.author_id == current_user.id:
            user_review = review_data
        else:
            public_reviews.append(review_data)

    return {"user_review": user_review, "public_reviews": public_reviews}



@app.delete("/films/{film_id}/reviews/me", status_code=204)
def delete_my_review(film_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    review = db.query(Review).filter(
        Review.film_id == film_id,
        Review.author_id == current_user.id
    ).first()

    if not review:
        raise HTTPException(status_code=404, detail="Отзыв не найден")

    db.delete(review)
    db.commit()
