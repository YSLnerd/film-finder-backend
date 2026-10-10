from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import FavouriteMovie, Movie, Genre, GenreMovie
from app.dependencies import get_current_user
router = APIRouter(prefix="/stats", tags=["stats"])
#Топ жанров для статистики
@router.get("/popular-genres")
def get_popular_genres(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
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
