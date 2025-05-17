from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routers import frontend, books
from contextlib import asynccontextmanager
from data.db import init_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Questo codice viene eseguito quando l'app si avvia
    init_database()
    yield
    # Questo codice verrebbe eseguito quando l'app si chiude (es. cleanup)

app = FastAPI(lifespan=lifespan)
app.include_router(frontend.router)
app.include_router(books.router, tags=["books"])

app.mount("/static", StaticFiles(directory="app/static"), name="static")


