from contextlib import asynccontextmanager
from fastapi import FastAPI
from database import inicializar_db
from routers import games

@asynccontextmanager
async def lifespan(app: FastAPI):
    inicializar_db()
    yield

app = FastAPI(
    title="PixelVault API",
    description="Backend para gestión de biblioteca de videojuegos estilo Steam",
    version="0.1.0",
    lifespan=lifespan
)

app.include_router(games.router)

@app.get("/")
def read_root():
    return {"message": "Bienvenido a la API de PixelVault."}