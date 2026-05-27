from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from database import get_session
from models import Videojuego
from security import ExigirRol

router = APIRouter(
    prefix="/videojuegos",
    tags=["Videojuegos"]
)

# ENDPOINTS
#GET
@router.get("/", response_model=List[Videojuego])
def listar_videojuegos(offset: int = 0, limit: int = 5, session: Session = Depends(get_session)):
    """Trae todos los videojuegos en la plataforma."""
    statement = (
        select(Videojuego)
        .where(Videojuego.activo == True)
        .offset(offset)
        .limit(limit)
    )
    
    juegos = session.exec(statement).all()
    return juegos

@router.get("/buscar", response_model=List[Videojuego])
def buscar_titulo(titulo: str, session: Session = Depends(get_session)):
    """Busca videojuegos cuyo título contenga el texto enviado."""
    statement = select(Videojuego).where(Videojuego.titulo.ilike(f"%{titulo}%"))
    juegos = session.exec(statement).all()
    return juegos

@router.get("/desarrollador/{desarrollador_nombre}", response_model=List[Videojuego])
def filtrar_desarrollador(desarrollador_nombre: str, session: Session = Depends(get_session)):
    """Trae todos los videojuegos creados por un desarrollador específico."""
    statement = select(Videojuego).where(Videojuego.desarrollador.ilike(f"%{desarrollador_nombre}%"))
    juegos = session.exec(statement).all()
    return juegos

@router.get("/precio-max", response_model=List[Videojuego])
def filtrar_precio_max(precio: float, session: Session = Depends(get_session)):
    """Trae los videojuegos del catálogo que cuesten igual o menos que el precio determinado."""
    if precio < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El precio no puedes ser inferior a 0.")
    
    statement = select(Videojuego).where(Videojuego.precio <= precio)
    juegos = session.exec(statement).all()
    return juegos

#POST
@router.post("/bulk", status_code=status.HTTP_201_CREATED)
def carga_masiva_videojuegos(juegos_nuevos: List[Videojuego], session: Session = Depends(get_session), admin_actual: dict = Depends(ExigirRol(["admin"]))):
    """
    Recibe una lista de videojuegos y los inserta de forma optimizada
    en un único bloque de transacción. Solo pueden hacerlo los administradores.
    """
    if not juegos_nuevos:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La lista de videojuegos no puede estar vacía.")
    try:
        session.add_all(juegos_nuevos)
        session.commit()
        
        return{
            "status": "success",
            "message": f"Se han insertado {len(juegos_nuevos)} videojuegos correctamente al catálogo."
        }
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error interno al realizar la carga masiva: {str(e)}.")
    
@router.post("/", response_model=Videojuego, status_code=status.HTTP_201_CREATED)
def crear_videojuego(juego_in: Videojuego, session: Session = Depends(get_session)):
    """Añade un nuevo videojuego de forma individual al catálogo general."""
    session.add(juego_in)
    session.commit()
    session.refresh(juego_in)
    return juego_in

# DELETE
@router.delete("/{videojuego_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_videojuego(videojuego_id: int, session: Session = Depends(get_session), admin_actual: dict = Depends(ExigirRol(["admin"]))):
    """
    Realiza el borrado lógico de un videojuego.
    El juego sigue en la base de datos para no romper el historial de compras, 
    pero desaparece del catálogo público de la tienda.
    """
    juego = session.get(Videojuego, videojuego_id)
    if not juego:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El juego que se intenta borrar no existe.")
    if not juego.activo:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El videojuego ya estaba eliminado.")
    
    juego.activo = False
    session.add(juego)
    session.commit()
    return {
        "status": "success",
        "message": f"El videojuego '{juego.titulo}' ha sido retidado del catálogo."
    }