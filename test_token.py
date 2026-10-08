from app.auth import create_access_token, decode_access_token, SECRET_KEY, ALGORITHM
from jose import jwt, JWTError

print("=" * 50)
print("SECRET_KEY:", SECRET_KEY)
print("ALGORITHM:", ALGORITHM)
print("=" * 50)
print()

# 1. Создаём свежий токен
token = create_access_token({"sub": "2"})
print("Свежий токен (первые 50):", token[:50], "...")
print()

# 2. Расшифровываем его же через нашу функцию
payload = decode_access_token(token)
print("decode_access_token() ->", payload)
print()

# 3. Пробуем напрямую через jose
try:
    payload2 = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    print("jwt.decode() напрямую ->", payload2)
except JWTError as e:
    print("jwt.decode() ОШИБКА:", e)
print()

# 4. Ваш токен из Swagger
old_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwiZXhwIjoxNzg5ODQyNDkzfQ.nFi67MRvOgog2OGGP7XiHNG9aO9UBGmSxOnMOanWYTc"
print("Ваш токен из Swagger (первые 50):", old_token[:50], "...")
print()

# 5. Расшифровка старого токена
try:
    payload3 = jwt.decode(old_token, SECRET_KEY, algorithms=[ALGORITHM])
    print("Ваш токен ВАЛИДНЫЙ ->", payload3)
except JWTError as e:
    print("Ваш токен НЕВАЛИДНЫЙ:", e)