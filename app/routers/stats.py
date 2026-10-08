from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import FavouriteMovie, Movie, Genre, GenreMovie
from app.dependencies import get_current_user


router = APIRouter(prefix="/stats", tags=["stats"])


# ============================================
# ТОП ЖАНРОВ (публичный)
# ============================================

@router.get("/popular-genres")
def get_popular_genres(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Топ-N жанров по количеству добавлений в избранное"""
    result = (
        db.query(
            Genre.name_ru.label("genre"),
            func.count(FavouriteMovie.id_favourite_movies).label("count")
        )
        .join(GenreMovie, Genre.id_genre == GenreMovie.id_genre)
        .join(Movie, Movie.id_movie == GenreMovie.id_movie)
        .join(FavouriteMovie, FavouriteMovie.id_movie == Movie.id_movie)
        .group_by(Genre.name_ru)
        .order_by(func.count(FavouriteMovie.id_favourite_movies).desc())
        .limit(limit)
        .all()
    )

    return [{"genre": row.genre, "count": row.count} for row in result]


# ============================================
# ЛИЧНАЯ СТАТИСТИКА
# ============================================

@router.get("/my-summary")
def get_my_summary(
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Личная статистика пользователя"""
    total = (
        db.query(func.count(FavouriteMovie.id_favourite_movies))
        .filter(FavouriteMovie.id_user == current_user_id)
        .scalar()
    )

    if total == 0:
        return {
            "total_favourites": 0,
            "favourite_genre": None,
            "avg_length": None
        }

    favourite_genre_row = (
        db.query(
            Genre.name_ru,
            func.count(FavouriteMovie.id_favourite_movies).label("count")
        )
        .join(GenreMovie, Genre.id_genre == GenreMovie.id_genre)
        .join(Movie, Movie.id_movie == GenreMovie.id_movie)
        .join(FavouriteMovie, FavouriteMovie.id_movie == Movie.id_movie)
        .filter(FavouriteMovie.id_user == current_user_id)
        .group_by(Genre.name_ru)
        .order_by(func.count(FavouriteMovie.id_favourite_movies).desc())
        .first()
    )

    avg_length = (
        db.query(func.avg(Movie.length))
        .join(FavouriteMovie, FavouriteMovie.id_movie == Movie.id_movie)
        .filter(FavouriteMovie.id_user == current_user_id)
        .scalar()
    )

    return {
        "total_favourites": total,
        "favourite_genre": favourite_genre_row.name_ru if favourite_genre_row else None,
        "avg_length": round(float(avg_length), 1) if avg_length else None
    }