from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models import Movie, Actor, Director
from app.schemas import MovieShort, ActorResponse, DirectorResponse


router = APIRouter(prefix="/search", tags=["search"])


# ============================================
# ПОИСК ФИЛЬМОВ
# ============================================

@router.get("/movies", response_model=list[MovieShort])
def search_movies(
    query: str = Query(..., min_length=1, description="Название фильма (рус/ориг)"),
    limit: int = Query(30, ge=1, le=100, description="Максимум результатов"),
    db: Session = Depends(get_db)
):
    """
    Публичный поиск фильмов по названию.
    Ищет по rus_title, orig_title и title.
    """
    pattern = f"%{query}%"
    return (
        db.query(Movie)
        .filter(
            or_(
                Movie.rus_title.ilike(pattern),
                Movie.orig_title.ilike(pattern),
                Movie.title.ilike(pattern)
            )
        )
        .order_by(Movie.rus_title)
        .limit(limit)
        .all()
    )


# ============================================
# ПОИСК АКТЁРОВ
# ============================================

@router.get("/actors", response_model=list[ActorResponse])
def search_actors(
    query: str = Query(..., min_length=1, description="Имя или фамилия актёра"),
    limit: int = Query(30, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Публичный поиск актёров по имени или фамилии.
    Регистронезависимый.
    """
    pattern = f"%{query}%"
    return (
        db.query(Actor)
        .filter(
            or_(
                Actor.first_name.ilike(pattern),
                Actor.second_name.ilike(pattern)
            )
        )
        .order_by(Actor.first_name, Actor.second_name)
        .limit(limit)
        .all()
    )


# ============================================
# ПОИСК РЕЖИССЁРОВ
# ============================================

@router.get("/directors", response_model=list[DirectorResponse])
def search_directors(
    query: str = Query(..., min_length=1, description="Имя или фамилия режиссёра"),
    limit: int = Query(30, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Публичный поиск режиссёров по имени или фамилии.
    Регистронезависимый.
    """
    pattern = f"%{query}%"
    return (
        db.query(Director)
        .filter(
            or_(
                Director.first_name.ilike(pattern),
                Director.second_name.ilike(pattern)
            )
        )
        .order_by(Director.first_name, Director.second_name)
        .limit(limit)
        .all()
    )