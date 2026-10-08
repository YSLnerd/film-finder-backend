from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    Movie, Director, Actor,
    GenreMovie, Directing, Acting,
    User, FavouriteMovie
)
from app.schemas import (
    MovieCreate, MovieUpdate, MovieShort,
    DirectorCreate, DirectorUpdate, DirectorResponse,
    ActorCreate, ActorUpdate, ActorResponse,
    UserResponse, UserRoleUpdate
)
from app.dependencies import require_admin


router = APIRouter(prefix="/admin", tags=["admin"])


# ============================================================
# ФИЛЬМЫ
# ============================================================

@router.post("/movies", response_model=MovieShort, status_code=status.HTTP_201_CREATED)
def create_movie(
    data: MovieCreate,
    admin_id: int = Depends(require_admin),
    db: Session = Depends(get_db)
):
    existing = db.query(Movie).filter(
        Movie.title == data.title,
        Movie.release_date == data.release_date
    ).first()
    if existing:
        raise HTTPException(400, "Фильм с таким названием и датой уже существует")

    movie = Movie(**data.model_dump())
    db.add(movie)
    db.commit()
    db.refresh(movie)
    return movie


@router.put("/movies/{movie_id}", response_model=MovieShort)
def update_movie(
    movie_id: int,
    data: MovieUpdate,
    admin_id: int = Depends(require_admin),
    db: Session = Depends(get_db)
):
    movie = db.query(Movie).filter(Movie.id_movie == movie_id).first()
    if not movie:
        raise HTTPException(404, "Фильм не найден")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(movie, key, value)

    db.commit()
    db.refresh(movie)
    return movie


@router.delete("/movies/{movie_id}")
def delete_movie(
    movie_id: int,
    admin_id: int = Depends(require_admin),
    db: Session = Depends(get_db)
):
    movie = db.query(Movie).filter(Movie.id_movie == movie_id).first()
    if not movie:
        raise HTTPException(404, "Фильм не найден")

    db.query(GenreMovie).filter(GenreMovie.id_movie == movie_id).delete()
    db.query(Directing).filter(Directing.id_movie == movie_id).delete()
    db.query(Acting).filter(Acting.id_movie == movie_id).delete()
    db.query(FavouriteMovie).filter(FavouriteMovie.id_movie == movie_id).delete()

    db.delete(movie)
    db.commit()
    return {"message": "Фильм удалён", "id_movie": movie_id}


# ============================================================
# РЕЖИССЁРЫ
# ============================================================

@router.post("/directors", response_model=DirectorResponse, status_code=status.HTTP_201_CREATED)
def create_director(
    data: DirectorCreate,
    admin_id: int = Depends(require_admin),
    db: Session = Depends(get_db)
):
    director = Director(**data.model_dump())
    db.add(director)
    db.commit()
    db.refresh(director)
    return director


@router.put("/directors/{director_id}", response_model=DirectorResponse)
def update_director(
    director_id: int,
    data: DirectorUpdate,
    admin_id: int = Depends(require_admin),
    db: Session = Depends(get_db)
):
    director = db.query(Director).filter(Director.id_director == director_id).first()
    if not director:
        raise HTTPException(404, "Режиссёр не найден")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(director, key, value)

    db.commit()
    db.refresh(director)
    return director


@router.delete("/directors/{director_id}")
def delete_director(
    director_id: int,
    admin_id: int = Depends(require_admin),
    db: Session = Depends(get_db)
):
    director = db.query(Director).filter(Director.id_director == director_id).first()
    if not director:
        raise HTTPException(404, "Режиссёр не найден")

    db.query(Directing).filter(Directing.id_director == director_id).delete()
    db.delete(director)
    db.commit()
    return {"message": "Режиссёр удалён", "id_director": director_id}


# ============================================================
# АКТЁРЫ
# ============================================================

@router.post("/actors", response_model=ActorResponse, status_code=status.HTTP_201_CREATED)
def create_actor(
    data: ActorCreate,
    admin_id: int = Depends(require_admin),
    db: Session = Depends(get_db)
):
    actor = Actor(**data.model_dump())
    db.add(actor)
    db.commit()
    db.refresh(actor)
    return actor


@router.put("/actors/{actor_id}", response_model=ActorResponse)
def update_actor(
    actor_id: int,
    data: ActorUpdate,
    admin_id: int = Depends(require_admin),
    db: Session = Depends(get_db)
):
    actor = db.query(Actor).filter(Actor.id_actor == actor_id).first()
    if not actor:
        raise HTTPException(404, "Актёр не найден")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(actor, key, value)

    db.commit()
    db.refresh(actor)
    return actor


@router.delete("/actors/{actor_id}")
def delete_actor(
    actor_id: int,
    admin_id: int = Depends(require_admin),
    db: Session = Depends(get_db)
):
    actor = db.query(Actor).filter(Actor.id_actor == actor_id).first()
    if not actor:
        raise HTTPException(404, "Актёр не найден")

    db.query(Acting).filter(Acting.id_actor == actor_id).delete()
    db.delete(actor)
    db.commit()
    return {"message": "Актёр удалён", "id_actor": actor_id}


# ============================================================
# УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ
# ============================================================

@router.get("/users", response_model=list[UserResponse])
def get_all_users(
    admin_id: int = Depends(require_admin),
    db: Session = Depends(get_db)
):
    return db.query(User).order_by(User.id_user).all()


@router.put("/users/{user_id}/role", response_model=UserResponse)
def change_user_role(
    user_id: int,
    data: UserRoleUpdate,
    admin_id: int = Depends(require_admin),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id_user == user_id).first()
    if not user:
        raise HTTPException(404, "Пользователь не найден")

    if user_id == admin_id:
        raise HTTPException(400, "Нельзя менять роль самому себе")

    if user.role == "admin":
        raise HTTPException(403, "Нельзя менять роль другому администратору")

    user.role = data.role
    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    admin_id: int = Depends(require_admin),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id_user == user_id).first()
    if not user:
        raise HTTPException(404, "Пользователь не найден")

    if user_id == admin_id:
        raise HTTPException(400, "Нельзя удалить самого себя")

    if user.role == "admin":
        raise HTTPException(403, "Нельзя удалить другого администратора")

    db.query(FavouriteMovie).filter(FavouriteMovie.id_user == user_id).delete()
    db.delete(user)
    db.commit()

    return {
        "message": "Пользователь удалён",
        "id_user": user_id,
        "nickname": user.nickname
    }
# ============================================================
# ЖАНРЫ
# ============================================================

from pydantic import BaseModel


class GenreCreate(BaseModel):
    name: str
    name_ru: str


class GenreUpdate(BaseModel):
    name: str | None = None
    name_ru: str | None = None


@router.post("/genres", status_code=status.HTTP_201_CREATED)
def create_genre(
    data: GenreCreate,
    admin_id: int = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Добавить жанр"""
    from app.models import Genre

    existing = db.query(Genre).filter(
        (Genre.name == data.name) | (Genre.name_ru == data.name_ru)
    ).first()
    if existing:
        raise HTTPException(400, "Жанр с таким названием уже существует")

    genre = Genre(name=data.name, name_ru=data.name_ru)
    db.add(genre)
    db.commit()
    db.refresh(genre)

    return {
        "id_genre": genre.id_genre,
        "name": genre.name,
        "name_ru": genre.name_ru,
    }


@router.put("/genres/{genre_id}")
def update_genre(
    genre_id: int,
    data: GenreUpdate,
    admin_id: int = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Изменить жанр"""
    from app.models import Genre

    genre = db.query(Genre).filter(Genre.id_genre == genre_id).first()
    if not genre:
        raise HTTPException(404, "Жанр не найден")

    if data.name is not None:
        genre.name = data.name
    if data.name_ru is not None:
        genre.name_ru = data.name_ru

    db.commit()
    db.refresh(genre)

    return {
        "id_genre": genre.id_genre,
        "name": genre.name,
        "name_ru": genre.name_ru,
    }


@router.delete("/genres/{genre_id}")
def delete_genre(
    genre_id: int,
    admin_id: int = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Удалить жанр"""
    from app.models import Genre, GenreMovie

    genre = db.query(Genre).filter(Genre.id_genre == genre_id).first()
    if not genre:
        raise HTTPException(404, "Жанр не найден")

    # Сначала удаляем связи с фильмами
    db.query(GenreMovie).filter(GenreMovie.id_genre == genre_id).delete()
    # Потом сам жанр
    db.delete(genre)
    db.commit()

    return {"message": "Жанр удалён", "id_genre": genre_id}
# ============================================================
# ПРИВЯЗКА РЕЖИССЁРОВ К ФИЛЬМУ
# ============================================================

@router.post("/movies/{movie_id}/directors/{director_id}")
def attach_director(
    movie_id: int,
    director_id: int,
    admin_id: int = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Привязать одного режиссёра к фильму"""
    from app.models import Movie, Director, Directing

    movie = db.query(Movie).filter(Movie.id_movie == movie_id).first()
    if not movie:
        raise HTTPException(404, "Фильм не найден")

    director = db.query(Director).filter(Director.id_director == director_id).first()
    if not director:
        raise HTTPException(404, "Режиссёр не найден")

    existing = db.query(Directing).filter(
        Directing.id_movie == movie_id,
        Directing.id_director == director_id
    ).first()
    if existing:
        raise HTTPException(400, "Этот режиссёр уже привязан к фильму")

    db.add(Directing(id_movie=movie_id, id_director=director_id))
    db.commit()

    return {
        "message": "Режиссёр привязан к фильму",
        "movie_id": movie_id,
        "director_id": director_id
    }


@router.delete("/movies/{movie_id}/directors/{director_id}")
def detach_director(
    movie_id: int,
    director_id: int,
    admin_id: int = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Отвязать режиссёра от фильма"""
    from app.models import Directing

    link = db.query(Directing).filter(
        Directing.id_movie == movie_id,
        Directing.id_director == director_id
    ).first()
    if not link:
        raise HTTPException(404, "Связь не найдена")

    db.delete(link)
    db.commit()
    return {"message": "Режиссёр отвязан от фильма"}


# ============================================================
# ПРИВЯЗКА АКТЁРОВ К ФИЛЬМУ
# ============================================================

@router.post("/movies/{movie_id}/actors/{actor_id}")
def attach_actor(
    movie_id: int,
    actor_id: int,
    admin_id: int = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Привязать одного актёра к фильму"""
    from app.models import Movie, Actor, Acting

    movie = db.query(Movie).filter(Movie.id_movie == movie_id).first()
    if not movie:
        raise HTTPException(404, "Фильм не найден")

    actor = db.query(Actor).filter(Actor.id_actor == actor_id).first()
    if not actor:
        raise HTTPException(404, "Актёр не найден")

    existing = db.query(Acting).filter(
        Acting.id_movie == movie_id,
        Acting.id_actor == actor_id
    ).first()
    if existing:
        raise HTTPException(400, "Этот актёр уже привязан к фильму")

    db.add(Acting(id_movie=movie_id, id_actor=actor_id))
    db.commit()

    return {
        "message": "Актёр привязан к фильму",
        "movie_id": movie_id,
        "actor_id": actor_id
    }


@router.delete("/movies/{movie_id}/actors/{actor_id}")
def detach_actor(
    movie_id: int,
    actor_id: int,
    admin_id: int = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Отвязать актёра от фильма"""
    from app.models import Acting

    link = db.query(Acting).filter(
        Acting.id_movie == movie_id,
        Acting.id_actor == actor_id
    ).first()
    if not link:
        raise HTTPException(404, "Связь не найдена")

    db.delete(link)
    db.commit()
    return {"message": "Актёр отвязан от фильма"}
# ============================================================
# ПРИВЯЗКА ЖАНРОВ К ФИЛЬМУ
# ============================================================

@router.post("/movies/{movie_id}/genres/{genre_id}")
def attach_genre(
    movie_id: int,
    genre_id: int,
    admin_id: int = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Привязать один жанр к фильму"""
    from app.models import Movie, Genre, GenreMovie

    movie = db.query(Movie).filter(Movie.id_movie == movie_id).first()
    if not movie:
        raise HTTPException(404, "Фильм не найден")

    genre = db.query(Genre).filter(Genre.id_genre == genre_id).first()
    if not genre:
        raise HTTPException(404, "Жанр не найден")

    existing = db.query(GenreMovie).filter(
        GenreMovie.id_movie == movie_id,
        GenreMovie.id_genre == genre_id
    ).first()
    if existing:
        raise HTTPException(400, "Этот жанр уже привязан к фильму")

    db.add(GenreMovie(id_movie=movie_id, id_genre=genre_id))
    db.commit()

    return {
        "message": "Жанр привязан к фильму",
        "movie_id": movie_id,
        "genre_id": genre_id
    }


@router.delete("/movies/{movie_id}/genres/{genre_id}")
def detach_genre(
    movie_id: int,
    genre_id: int,
    admin_id: int = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Отвязать жанр от фильма"""
    from app.models import GenreMovie

    link = db.query(GenreMovie).filter(
        GenreMovie.id_movie == movie_id,
        GenreMovie.id_genre == genre_id
    ).first()
    if not link:
        raise HTTPException(404, "Связь не найдена")

    db.delete(link)
    db.commit()
    return {"message": "Жанр отвязан от фильма"}