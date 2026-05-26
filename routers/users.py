from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlmodel import Session, select, desc
from sqlalchemy.orm import selectinload
from database import get_session
from models import Usuario, Videojuego, Biblioteca, UsuarioPublico, UsuarioCreate, VideojuegoConHoras
from security import hashing_password, verify_password

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"]
)

# ENDPOINTS
#GET
@router.get("/{usuario_id}", response_model=UsuarioPublico)
def obtener_usuario(usuario_id: int, session: Session = Depends(get_session)):
    """Trae la información de un usuario, incluyendo su saldo y los videojuegos que posee."""
    #usuario = session.get(Usuario, usuario_id)
    statement = select(Usuario).where(Usuario.id == usuario_id).options(selectinload(Usuario.videojuegos))
    usuario = session.exec(statement).first()

    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado.")
    return usuario

@router.get("/{usuario_id}/top-jugados", response_model=List[VideojuegoConHoras])
def obtener_top_jugados(usuario_id: int, session: Session = Depends(get_session)):
    """Devuelve los 3 videojuegos en los que el usuario ha acumulado más horas."""
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El usuario no existe.")
    
    statement = (select(Videojuego, Biblioteca.horas_jugadas)
                 .join(Biblioteca)
                 .where(Biblioteca.usuario_id == usuario_id)
                 .order_by(desc(Biblioteca.horas_jugadas))
                 .limit(3)
                 )
    resultados = session.exec(statement).all()

    top_juegos = []
    for juego, horas in resultados:
        top_juegos.append(
            VideojuegoConHoras(
                id=juego.id,
                titulo=juego.titulo,
                descripcion=juego.descripcion,
                precio=juego.precio,
                desarrollador=juego.desarrollador,
                horas_jugadas=horas
            )
        )
    return top_juegos

#POST
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
    
@router.post("/", response_model=UsuarioPublico, status_code=status.HTTP_201_CREATED)
def crear_user(usuario_in: UsuarioCreate, session: Session = Depends(get_session)):
    """Registra un nuevo usuario en la plataforma encriptando su contraseña."""
    existe = session.exec(select(Usuario).where(
        (Usuario.username == usuario_in.username) | (Usuario.email == usuario_in.email)
    )).first()

    if existe:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El nombre de usuario o email ya existen.")
    
    nuevo_usuario = Usuario(
        username=usuario_in.username,
        email=usuario_in.email,
        hashed_password=hashing_password(usuario_in.password),
        saldo_cartera=0.0
    )

    session.add(nuevo_usuario)
    session.commit()
    session.refresh(nuevo_usuario)
    return nuevo_usuario

#UPDATE
@router.patch("/{usuario_id}/add-saldo")
def add_saldo(usuario_id: int, cantidad: float, password_conf: str, session: Session = Depends(get_session)):
    """Añade fondos a la cartera del usuario, requiriendo su contraseña por seguridad."""
    if cantidad <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La cantidad a añadir debe ser mayor a 0€.")
    
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado.")
    
    if not verify_password(password_conf, usuario.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Contraseña incorrecta. Operación denegada.")
    
    usuario.saldo_cartera += cantidad
    session.add(usuario)
    session.commit()
    session.refresh(usuario)

    return {
        "message": f"Fondos añadidos con éxito. Nuevo saldo: {usuario.saldo_cartera}€."
    }

@router.patch("/{usuario_id}/jugar/{videojuego_id}")
def registrar_horas_juego(usuario_id: int, videojuego_id: int, horas: float, session: Session = Depends(get_session)):
    """Suma horas de juego a un videojuego específico que el usuario ya tenga en su biblioteca."""
    if horas <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se pueden añadir horas negativas.")
    
    registro_biblioteca = session.exec(
        select(Biblioteca).where(
            Biblioteca.usuario_id == usuario_id, Biblioteca.videojuego_id == videojuego_id
        )).first()
    
    if not registro_biblioteca:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Imposible registrar horas. El usuario no posee este videojuego.")
    
    registro_biblioteca.horas_jugadas += horas
    session.add(registro_biblioteca)
    session.commit()
    return {
        "status": "success",
        "message": f"Sesión de juego registrada. Has acumulado un total de {registro_biblioteca.horas_jugadas} horas jugadas."
    }

#DELETE
@router.delete("/usuario_id", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_usuario(usuario_id: int, password_conf: str, session: Session = Depends(get_session)):
    """Elimina un usuario y libera sus registros de la base de datos."""
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado.")
        
    if not verify_password(password_conf, usuario.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Contraseña incorrecta. Operación denegada.")
    
    session.delete(usuario)
    session.commit()
    return None