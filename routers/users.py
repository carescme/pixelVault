from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from database import get_session
from models import Usuario, Videojuego, Biblioteca, UsuarioPublico

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"]
)

# ENDPOINTS
@router.get("/{usuario_id}", response_model=UsuarioPublico)
def obtener_usuario(usuario_id: int, session: Session = Depends(get_session)):
    """Trae la información de un usuario, incluyendo su saldo y los videojuegos que posee."""
    #usuario = session.get(Usuario, usuario_id)
    statement = select(Usuario).where(Usuario.id == usuario_id).options(selectinload(Usuario.videojuegos))
    usuario = session.exec(statement).first()

    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado.")
    return usuario

@router.post("/{usuario_id}/comprar/{videojuego_id}", status_code=status.HTTP_201_CREATED)
def comprar_videojuego(usuario_id: int, videojuego_id: int, session: Session = Depends(get_session)):
    """
    Simula la compra de un videojuego. Verifica existencias, saldo, evita
    duplicados, resta el dinero y lo añade a la biblioteca.
    """
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado.")
    
    videojuego = session.get(Videojuego, videojuego_id)
    if not videojuego:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Videojuego no encontrado.")
    
    enlace_existente = session.exec(
        select(Biblioteca)
        .where(Biblioteca.usuario_id == usuario_id,
               Biblioteca.videojuego_id == videojuego_id)
        ).first()
    
    if enlace_existente:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"El usuario ya posee el juego '{videojuego.titulo}' en su biblioteca.")
    
    if usuario.saldo_cartera < videojuego.precio:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Saldo insuficiente. El juego cuesta {videojuego.precio}€ y solo tienes {usuario.saldo_cartera}€.")
    
    try:
        usuario.saldo_cartera -= videojuego.precio

        nueva_adquisicion = Biblioteca(
            usuario_id=usuario.id,
            videojuego_id=videojuego.id,
            horas_jugadas=0.0
        )

        session.add(usuario)
        session.add(nueva_adquisicion)
        session.commit()

        return {
            "status": "success",
            "message": f"Compra realizada con éxito. {videojuego.titulo} añadido a la biblioteca.",
            "saldo_restante": usuario.saldo_cartera
        }
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al procesas la transacción: {str(e)}.")