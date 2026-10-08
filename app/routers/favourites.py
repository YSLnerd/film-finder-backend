from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import FavouriteMovie, Movie
from app.schemas import MovieShort
from app.dependencies import get_current_user


router = APIRouter(prefix="/favourites", tags=["favourites"])


@router.get("/", response_model=list[MovieShort])
def get_favourites(
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Список избранных фильмов пользователя"""
    favourites = (
        db.query(FavouriteMovie)
        .filter(FavouriteMovie.id_user == current_user_id)
        .all()
    )

    movie_ids = [f.id_movie for f in favourites]
    if not movie_ids:
        return []

    movies = (
        db.query(Movie)
        .filter(Movie.id_movie.in_(movie_ids))
        .order_by(Movie.rus_title)
        .all()
    )
    return movies


@router.post("/{movie_id}", status_code=status.HTTP_201_CREATED)
def add_to_favourites(
    movie_id: int,
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Добавить фильм в избранное"""
    movie = db.query(Movie).filter(Movie.id_movie == movie_id).first()
    if not movie:
        raise HTTPException(404, "Фильм не найден")

    existing = (
        db.query(FavouriteMovie)
        .filter(
            FavouriteMovie.id_movie == movie_id,
            FavouriteMovie.id_user == current_user_id
        )
        .first()
    )
    if existing:
        raise HTTPException(400, "Фильм уже в избранном")

    favourite = FavouriteMovie(
        id_movie=movie_id,
        id_user=current_user_id
    )
    db.add(favourite)
    db.commit()

    return {
        "message": "Фильм добавлен в избранное",
        "id_movie": movie_id
    }


@router.delete("/{movie_id}")
def remove_from_favourites(
    movie_id: int,
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Удалить фильм из избранного"""
    favourite = (
        db.query(FavouriteMovie)
        .filter(
            FavouriteMovie.id_movie == movie_id,
            FavouriteMovie.id_user == current_user_id
        )
        .first()
    )

    if not favourite:
        raise HTTPException(404, "Фильм не найден в избранном")

    db.delete(favourite)
    db.commit()

    return {
        "message": "Фильм удалён из избранного",
        "id_movie": movie_id
    }


@router.get("/check/{movie_id}")
def check_favourite(
    movie_id: int,
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Проверить, в избранном ли фильм"""
    favourite = (
        db.query(FavouriteMovie)
        .filter(
            FavouriteMovie.id_movie == movie_id,
            FavouriteMovie.id_user == current_user_id
        )
        .first()
    )
    return {"is_favourite": favourite is not None}