from enum import Enum
from datetime import datetime, timezone
from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel, Column, DateTime

class RolUser(str, Enum):
    ADMIN = "admin"
    DEV = "desarrollador"
    USER_BASE = "usuario"

class TipoTransaccion(str, Enum):
    INGRESO = "ingreso"
    COMPRA = "compra"

class Biblioteca(SQLModel, table=True):
    usuario_id: Optional[int] = Field(default=None, foreign_key="usuario.id", primary_key=True)
    videojuego_id: Optional[int] = Field(default=None, foreign_key="videojuego.id", primary_key=True)

    horas_jugadas: float = Field(default=0.0)
    fecha_adquisicion: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    )

class Usuario(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    saldo_cartera: float = Field(default=0.0)

    rol: RolUser = Field(default=RolUser.USER_BASE)

    activo: bool = Field(default=True)

    videojuegos: List["Videojuego"] = Relationship(back_populates="usuarios", link_model=Biblioteca)
    transacciones: List["Transaccion"] = Relationship(back_populates="usuario")

class Videojuego(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    titulo: str = Field(index=True, unique=True)
    descripcion: str
    precio: float
    desarrollador: str

    activo: bool = Field(default=True)

    usuarios: List[Usuario] = Relationship(back_populates="videojuegos", link_model=Biblioteca)

class Transaccion(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuario.id")

    tipo: TipoTransaccion
    cantidad: float
    detalles: str

    fecha: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    )

    usuario: Optional[Usuario] = Relationship(back_populates="transacciones")

# ESQUEMAS LECTURA

class UsuarioPublico(SQLModel):
    id: int
    username: str
    email: str
    saldo_cartera: float
    rol: RolUser
    activo: bool
    videojuegos: List[Videojuego] = []

class UsuarioCreate(SQLModel):
    username: str
    email: str
    password: str

class VideojuegoConHoras(SQLModel):
    titulo: str
    descripcion: str
    precio: float
    desarrollador: str
    horas_jugadas: float

class UserLogin(SQLModel):
    username: str
    password: str