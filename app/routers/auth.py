from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, field_validator
from app.database import get_db
from app.models import User
from app.schemas import UserRegister, UserLogin, Token, UserResponse
from app.auth import hash_password, verify_password, create_access_token
from app.dependencies import get_current_user


router = APIRouter(prefix="/auth", tags=["auth"])


# ============================================
# СХЕМА ДЛЯ ФОТО
# ============================================

class PhotoUpdate(BaseModel):
    prof_pic_link: str

    @field_validator('prof_pic_link')
    @classmethod
    def check_url(cls, v):
        v = v.strip()

        # Пустая ссылка — ок (удалить фото)
        if not v:
            return v

        # Схема
        if not (v.startswith('http://') or v.startswith('https://')):
            raise ValueError('Ссылка должна начинаться с http:// или https://')

        # Минимальная длина
        if len(v) < 12:
            raise ValueError('Ссылка слишком короткая')

        return v


# ============================================
# РЕГИСТРАЦИЯ
# ============================================

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.nickname == user.nickname).first()
    if existing:
        raise HTTPException(400, "Пользователь с таким никнеймом уже существует")

    new_user = User(
        nickname=user.nickname,
        password=hash_password(user.password),
        role="user",
        prof_pic_link=None
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "Пользователь успешно зарегистрирован",
        "id_user": new_user.id_user,
        "nickname": new_user.nickname
    }


# ============================================
# ЛОГИН
# ============================================

@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.nickname == user.nickname).first()
    if not db_user:
        raise HTTPException(401, "Неверный логин или пароль")

    if db_user.password.startswith("$2b$"):
        if not verify_password(user.password, db_user.password):
            raise HTTPException(401, "Неверный логин или пароль")
    else:
        if db_user.password != user.password:
            raise HTTPException(401, "Неверный логин или пароль")
        db_user.password = hash_password(user.password)
        db.commit()
        db.refresh(db_user)

    token = create_access_token({"sub": str(db_user.id_user)})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id_user": db_user.id_user,
            "nickname": db_user.nickname,
            "role": db_user.role,
        },
    }


# ============================================
# ТЕКУЩИЙ ПОЛЬЗОВАТЕЛЬ
# ============================================

@router.get("/me", response_model=UserResponse)
def get_me(
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id_user == current_user_id).first()
    if not user:
        raise HTTPException(404, "Пользователь не найден")
    return user


# ============================================
# ОБНОВЛЕНИЕ ФОТО
# ============================================

@router.put("/me/photo")
def update_photo(
    data: PhotoUpdate,
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id_user == current_user_id).first()
    if not user:
        raise HTTPException(404, "Пользователь не найден")

    user.prof_pic_link = data.prof_pic_link if data.prof_pic_link else None
    db.commit()
    db.refresh(user)

    return {
        "message": "Фото обновлено",
        "prof_pic_link": user.prof_pic_link,
    }