from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from database import engine
from models import Videojuego

router = APIRouter(
    prefix="/videojuegos",
    tags=["Videojuegos"]
)

def get_session():
    with Session(engine) as session:
        yield session

# ENDPOINTS

@router.get("/", response_model=List[Videojuego])
def listar_videojuegos(session: Session = Depends(get_session)):
    """Trae todos los videojuegos en la plataforma."""
    juegos = session.exec(select(Videojuego)).all()
    return juegos

@router.post("/bulk", status_code=status.HTTP_201_CREATED)
def carga_masiva_videojuegos(juegos_nuevos: List[Videojuego], session: Session = Depends(get_session)):
    """
    Recibe una lista de videojuegos y los inserta de forma optimizada
    en un único bloque de transacción.
    """
    if not juegos_nuevos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La lista de videojuegos no puede estar vacía."
        )
    try:
        session.add_all(juegos_nuevos)
        session.commit()
        
        return{
            "status": "success",
            "message": f"Se han insertado {len(juegos_nuevos)} videojuegos correctamente al catálogo."
        }
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno al realizar la carga masiva: {str(e)}."
        )