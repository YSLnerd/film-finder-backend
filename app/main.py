from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, movies, search, favourites, stats, admin


app = FastAPI(
    title="Film Finder API",
    description="API для сервиса подбора фильмов",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(movies.router)
app.include_router(search.router)
app.include_router(favourites.router)
app.include_router(stats.router)
app.include_router(admin.router)


@app.get("/")
def root():
    return {"message": "Film Finder API работает", "docs": "/docs"}