from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date
# АВТОРИЗАЦИЯ
class UserRegister(BaseModel):
    # Регистрация нового пользователя
    nickname: str = Field(..., min_length=2, max_length=30)
    password: str = Field(..., min_length=3)
class UserLogin(BaseModel):
    # Вход
    nickname: str
    password: str
class Token(BaseModel):
    # Ответ после успешного входа
    access_token: str
    token_type: str = "bearer"
class UserResponse(BaseModel):
    # Информация о пользователе
    id_user: int
    nickname: str
    role: str
    prof_pic_link: Optional[str] = None
    class Config:
        from_attributes = True
# ЖАНРЫ
class GenreResponse(BaseModel):
    # Информация о жанре
    id_genre: int
    name: str
    name_ru: str

    class Config:
        from_attributes = True
# РЕЖИССЁРЫ
class DirectorResponse(BaseModel):
    # Информация о режиссёре
    id_director: int
    first_name: str
    second_name: Optional[str] = None
    date_birth: Optional[date] = None
    date_death: Optional[date] = None
    director_photo: Optional[str] = None
    director_country: Optional[str] = None
    class Config:
        from_attributes = True
# АКТЁРЫ
class ActorResponse(BaseModel):
    # Информация об актёре
    id_actor: int
    first_name: str
    second_name: str
    date_birth: Optional[date] = None
    date_death: Optional[date] = None
    actor_photo: Optional[str] = None
    actor_country: Optional[str] = None
    class Config:
        from_attributes = True
# ФИЛЬМЫ
class MovieBase(BaseModel):
    # Базовые поля фильма
    id_movie: int
    title: str
    orig_title: str
    rus_title: Optional[str] = None
    release_date: date
    poster_url: Optional[str] = None
    length: int
    age_rating: str
    mood: str
    class Config:
        from_attributes = True
class MovieShort(MovieBase):
    # Краткая информация о фильме
    pass

class MovieDetail(MovieBase):
    # Полная информация о фильме (с актерами, режиссерами и жанрами)
    genres: List[GenreResponse] = []
    directors: List[DirectorResponse] = []
    actors: List[ActorResponse] = []
# СТАТИСТИКА
class GenreStatsResponse(BaseModel):
    # Топ жанров по избранному
    genre: str
    count: int
# АДМИН: ФИЛЬМЫ
class MovieCreate(BaseModel):
    # Создание фильма
    title: str = Field(..., min_length=1, max_length=300)
    orig_title: str = Field(..., min_length=1, max_length=300)
    rus_title: Optional[str] = Field(None, max_length=300)
    release_date: date
    poster_url: Optional[str] = None
    length: int = Field(..., gt=0, le=1000)
    age_rating: str = Field(..., min_length=1, max_length=10)
    mood: str = Field(..., min_length=1, max_length=50)
class MovieUpdate(BaseModel):
    # Обновление фильма
    title: Optional[str] = Field(None, min_length=1, max_length=300)
    orig_title: Optional[str] = Field(None, min_length=1, max_length=300)
    rus_title: Optional[str] = Field(None, max_length=300)
    release_date: Optional[date] = None
    poster_url: Optional[str] = None
    length: Optional[int] = Field(None, gt=0, le=1000)
    age_rating: Optional[str] = Field(None, min_length=1, max_length=10)
    mood: Optional[str] = Field(None, min_length=1, max_length=50)
# АДМИН: РЕЖИССЁРЫ
class DirectorCreate(BaseModel):
    # Создание режиссёра
    first_name: str = Field(..., min_length=1, max_length=100)
    second_name: Optional[str] = Field(None, max_length=100)
    date_birth: Optional[date] = None
    date_death: Optional[date] = None
    director_photo: Optional[str] = None
    director_country: Optional[str] = Field(None, max_length=100)
class DirectorUpdate(BaseModel):
    # Обновление режиссёра
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    second_name: Optional[str] = Field(None, max_length=100)
    date_birth: Optional[date] = None
    date_death: Optional[date] = None
    director_photo: Optional[str] = None
    director_country: Optional[str] = Field(None, max_length=100)
# АДМИН: АКТЁРЫ
class ActorCreate(BaseModel):
    # Создание актёра
    first_name: str = Field(..., min_length=1, max_length=100)
    second_name: str = Field(..., min_length=1, max_length=100)
    date_birth: Optional[date] = None
    date_death: Optional[date] = None
    actor_photo: Optional[str] = None
    actor_country: Optional[str] = Field(None, max_length=100)
class ActorUpdate(BaseModel):
    # Обновление актёра
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    second_name: Optional[str] = Field(None, min_length=1, max_length=100)
    date_birth: Optional[date] = None
    date_death: Optional[date] = None
    actor_photo: Optional[str] = None
    actor_country: Optional[str] = Field(None, max_length=100)
# АДМИН: УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ
class UserRoleUpdate(BaseModel):
    # Смена роли пользователя
    role: str = Field(..., pattern="^(user|admin)$")