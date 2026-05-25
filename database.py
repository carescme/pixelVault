from sqlmodel import SQLModel, create_engine
from config import settings
import models

DATABASE_URL = settings.DATABASE_URL
engine = create_engine(DATABASE_URL, echo=True)

def inicializar_db():
    SQLModel.metadata.create_all(engine)
    print("Base de datos PixelVault y sus tablas inicializados exitosamente.")