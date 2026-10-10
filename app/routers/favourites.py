from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import FavouriteMovie, Movie
from app.schemas import MovieShort
from app.dependencies import get_current_user
router = APIRouter(prefix="/favourites", tags=["favourites"])

#Избранные фильмы пользователя
@router.get("/", response_model=list[MovieShort])
def get_favourites(
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
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

#Добавление в Избранное
@router.post("/{movie_id}", status_code=status.HTTP_201_CREATED)
def add_to_favourites(
    movie_id: int,
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
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