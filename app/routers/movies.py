from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional

from app.database import get_db
from app.models import (
    Movie, Genre, GenreMovie,
    Actor, Acting, Director, Directing
)
from app.schemas import MovieShort, MovieDetail, GenreResponse


router = APIRouter(prefix="/movies", tags=["movies"])
#Список жанров из БД
@router.get("/genres", response_model=list[GenreResponse])
def get_genres(db: Session = Depends(get_db)):
    return db.query(Genre).order_by(Genre.name_ru).all()
#Список настроений из БД
@router.get("/moods", response_model=list[str])
def get_moods(db: Session = Depends(get_db)):
    moods = db.query(Movie.mood).distinct().order_by(Movie.mood).all()
    return [m[0] for m in moods if m[0]]
#Список рейтингов из БД
@router.get("/age-ratings", response_model=list[str])
def get_age_ratings(db: Session = Depends(get_db)):
    ratings = db.query(Movie.age_rating).distinct().order_by(Movie.age_rating).all()
    return [r[0] for r in ratings if r[0]]
#Подбор фильма
@router.get("/recommend", response_model=MovieDetail)
def recommend_movie(
    genre: str = Query(...),
    mood: str = Query(...),
    age_rating: str = Query(...),
    duration: Optional[str] = Query(None),
    year_period: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    if duration:
        if duration == "0-90": min_len, max_len = 0, 90
        elif duration == "90-120": min_len, max_len = 90, 120
        elif duration == "120-150": min_len, max_len = 120, 150
        elif duration == "150-500": min_len, max_len = 150, 500
        else: min_len, max_len = 0, 500
    else:
        min_len, max_len = 0, 500
    if year_period:
        if year_period == "2020-2026": min_year, max_year = 2020, 2026
        elif year_period == "2010-2019": min_year, max_year = 2010, 2019
        elif year_period == "2000-2009": min_year, max_year = 2000, 2009
        elif year_period == "1800-1999": min_year, max_year = 1800, 1999
        else: min_year, max_year = 1800, 2026
    else:
        min_year, max_year = 1800, 2026
    movie = (
        db.query(Movie)
        .join(GenreMovie, GenreMovie.id_movie == Movie.id_movie)
        .join(Genre, Genre.id_genre == GenreMovie.id_genre)
        .filter(
            Genre.name_ru == genre,
            Movie.mood == mood,
            Movie.age_rating == age_rating,
            Movie.length.between(min_len, max_len),
            func.extract('year', Movie.release_date).between(min_year, max_year)
        )
        .order_by(func.random())
        .first()
    )
    if not movie:
        raise HTTPException(404, "Фильм по заданным параметрам не найден")
    return movie
#Поиск фильма
@router.get("/search", response_model=list[MovieShort])
def search_movies(
    query: str = Query(..., min_length=1),
    limit: int = Query(30, ge=1, le=100),
    db: Session = Depends(get_db)
):
    pattern = f"%{query}%"
    return (
        db.query(Movie)
        .filter(
            Movie.rus_title.ilike(pattern) |
            Movie.orig_title.ilike(pattern) |
            Movie.title.ilike(pattern)
        )
        .order_by(Movie.rus_title)
        .limit(limit)
        .all()
    )
#Поиск всех актёров фильма
@router.get("/actors")
def get_all_actors(db: Session = Depends(get_db)):
    actors = db.query(Actor).order_by(Actor.first_name, Actor.second_name).all()
    return [
        {
            "id_actor": a.id_actor,
            "first_name": a.first_name,
            "second_name": a.second_name,
            "date_birth": a.date_birth,
            "date_death": a.date_death,
            "actor_photo": a.actor_photo,
            "actor_country": a.actor_country,
        }
        for a in actors
    ]
#Поиск всех режиссёров фильма
@router.get("/directors")
def get_all_directors(db: Session = Depends(get_db)):
    directors = db.query(Director).order_by(Director.first_name, Director.second_name).all()
    return [
        {
            "id_director": d.id_director,
            "first_name": d.first_name,
            "second_name": d.second_name,
            "date_birth": d.date_birth,
            "date_death": d.date_death,
            "director_photo": d.director_photo,
            "director_country": d.director_country,
        }
        for d in directors
    ]
#выодит список фильмов для актёра
@router.get("/actors/{actor_id}")
def get_actor(actor_id: int, db: Session = Depends(get_db)):
    actor = db.query(Actor).filter(Actor.id_actor == actor_id).first()
    if not actor:
        raise HTTPException(404, "Актёр не найден")

    films = (
        db.query(Movie)
        .join(Acting, Acting.id_movie == Movie.id_movie)
        .filter(Acting.id_actor == actor_id)
        .order_by(Movie.rus_title)
        .all()
    )

    return {
        "id_actor": actor.id_actor,
        "first_name": actor.first_name,
        "second_name": actor.second_name,
        "date_birth": actor.date_birth,
        "date_death": actor.date_death,
        "actor_photo": actor.actor_photo,
        "actor_country": actor.actor_country,
        "movies": [{"id_movie": m.id_movie, "rus_title": m.rus_title} for m in films],
    }
#выодит список фильмов для актёра
@router.get("/directors/{director_id}")
def get_director(director_id: int, db: Session = Depends(get_db)):
    director = db.query(Director).filter(Director.id_director == director_id).first()
    if not director:
        raise HTTPException(404, "Режиссёр не найден")

    films = (
        db.query(Movie)
        .join(Directing, Directing.id_movie == Movie.id_movie)
        .filter(Directing.id_director == director_id)
        .order_by(Movie.rus_title)
        .all()
    )

    return {
        "id_director": director.id_director,
        "first_name": director.first_name,
        "second_name": director.second_name,
        "date_birth": director.date_birth,
        "date_death": director.date_death,
        "director_photo": director.director_photo,
        "director_country": director.director_country,
        "movies": [{"id_movie": m.id_movie, "rus_title": m.rus_title} for m in films],
    }
#Все данные фильма
@router.get("/{movie_id}", response_model=MovieDetail)
def get_movie(movie_id: int, db: Session = Depends(get_db)):
    movie = db.query(Movie).filter(Movie.id_movie == movie_id).first()
    if not movie:
        raise HTTPException(404, "Фильм не найден")
    return movie