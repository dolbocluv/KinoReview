


# models.py

from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime, timezone

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String, unique=True)
    public_name: Mapped[str] = mapped_column(String, default="Никнейм не задан")
    hashed_password: Mapped[str] = mapped_column(String)
    avatar_url: Mapped[str] = mapped_column(String, default="/static/default.png")
    bio: Mapped[str] = mapped_column(String, default="Описание отсутствует")
    admin_profile: Mapped["Admin"] = relationship("Admin", back_populates="user")
    
    reviews: Mapped[list["Review"]] = relationship("Review", back_populates="author")

class Admin(Base):
    __tablename__ = "admins"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    user: Mapped["User"] = relationship("User", back_populates="admin_profile")

class Film(Base):
    __tablename__ = 'films'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    poster_url: Mapped[str] = mapped_column(String, default="/static/default-film.png")
    
    reviews: Mapped[list["Review"]] = relationship("Review", back_populates="film")

class Review(Base):
    __tablename__ = 'reviews'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(String)
    film_id: Mapped[int] = mapped_column(Integer, ForeignKey("films.id"))
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    film: Mapped["Film"] = relationship("Film", back_populates="reviews")
    author: Mapped["User"] = relationship("User", back_populates="reviews")