from datetime import datetime, timezone
from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel

class Biblioteca(SQLModel, table=True):
    usuario_id: Optional[int] = Field(default=None, foreign_key="usuario.id", primary_key=True)
    videojuego_id: Optional[int] = Field(default=None, foreign_key="videojuego.id", primary_key=True)

    horas_jugadas: float = Field(default=0.0)
    fecha_adquisicion: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Usuario(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True)
    hashed_password: str
    saldo_cartera: float = Field(default=0.0)

    videojuegos: List["Videojuego"] = Relationship(back_populates="usuarios", link_model=Biblioteca)

class Videojuego(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    titulo: str = Field(index=True)
    descripcion: str
    precio: float
    desarrollador: str

    usuarios: List[Usuario] = Relationship(back_populates="videojuegos", link_model=Biblioteca)