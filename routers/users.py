from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import List
from sqlmodel import Session, select, desc
from sqlalchemy.orm import selectinload
from database import get_session
from models import Usuario, Videojuego, Biblioteca, Transaccion, UsuarioPublico, UsuarioCreate, VideojuegoConHoras, TipoTransaccion
from security import hashing_password, verify_password, create_access_token, obtener_usuario_actual, ExigirRol

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"]
)

# ENDPOINTS GET (LECTURA)

@router.get("/me", response_model=UsuarioPublico)
def obtener_usuario_actual_perfil(session: Session = Depends(get_session), usuario_logueado: dict = Depends(obtener_usuario_actual)):
    """
    Autenticado (Cualquier Rol): Trae la información del usuario logueado.
    Ya no se pasa ID por URL; el ID se extrae matemáticamente de su Token JWT.
    """
    statement = (
        select(Usuario)
        .where(Usuario.id == usuario_logueado["id"], Usuario.activo == True)
        .options(selectinload(Usuario.videojuegos))
    )
    usuario = session.exec(statement).first()

    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado.")
    return usuario


@router.get("/me/top-jugados", response_model=List[VideojuegoConHoras])
def obtener_top_jugados(session: Session = Depends(get_session), usuario_logueado: dict = Depends(obtener_usuario_actual)):
    """Autenticado (Cualquier Rol): Devuelve tus 3 videojuegos con más horas jugadas."""
    statement = (
        select(Videojuego, Biblioteca.horas_jugadas)
        .join(Biblioteca)
        .where(Biblioteca.usuario_id == usuario_logueado["id"], Videojuego.activo == True)
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

# ENDPOINTS POST (ESCRITURA / PROCESOS)

@router.post("/", response_model=UsuarioPublico, status_code=status.HTTP_201_CREATED)
def crear_user(usuario_in: UsuarioCreate, session: Session = Depends(get_session)):
    """Público: Permite registrarse a cualquier visitante. No requiere login."""
    existe = session.exec(select(Usuario).where(
        (Usuario.username == usuario_in.username) | (Usuario.email == usuario_in.email)
    )).first()

    if existe:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El nombre de usuario o email ya existen.")
    
    nuevo_usuario = Usuario(
        username=usuario_in.username,
        email=usuario_in.email,
        hashed_password=hashing_password(usuario_in.password), # Función corregida
        saldo_cartera=0.0
    )

    session.add(nuevo_usuario)
    session.commit()
    session.refresh(nuevo_usuario)
    return nuevo_usuario


@router.post("/login")
def login(credenciales: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    """Público: Intercambia credenciales válidas por un pasaporte Token JWT."""
    user = session.exec(select(Usuario).where(Usuario.username == credenciales.username)).first()
    
    if not user or not user.activo:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Nombre de usuario o contraseña incorrectos.")
    
    if not verify_password(credenciales.password, user.hashed_password): # Función corregida
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Nombre de usuario o contraseña incorrectos.")
    
    datos_user = {
        "sub": str(user.id),
        "username": user.username,
        "rol": user.rol.value
    }
    token_generado = create_access_token(data=datos_user)
    
    return {
        "access_token": token_generado,
        "token_type": "bearer"
    }


@router.post("/comprar/{videojuego_id}", status_code=status.HTTP_201_CREATED)
def comprar_videojuego(videojuego_id: int, session: Session = Depends(get_session), usuario_logueado: dict = Depends(obtener_usuario_actual)):
    """Autenticado (Cualquier Rol): Compra un juego para el usuario del token."""
    usuario = session.get(Usuario, usuario_logueado["id"])
    
    videojuego = session.get(Videojuego, videojuego_id)
    if not videojuego or not videojuego.activo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Videojuego no encontrado o fuera de catálogo.")
    
    enlace_existente = session.exec(
        select(Biblioteca)
        .where(Biblioteca.usuario_id == usuario.id, Biblioteca.videojuego_id == videojuego_id)
    ).first()
    
    if enlace_existente:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Ya posees el juego '{videojuego.titulo}'.")
    
    if usuario.saldo_cartera < videojuego.precio:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Saldo insuficiente ({usuario.saldo_cartera}€). Requiere {videojuego.precio}€.")
    
    try:
        usuario.saldo_cartera -= videojuego.precio

        nueva_adquisicion = Biblioteca(
            usuario_id=usuario.id,
            videojuego_id=videojuego.id,
            horas_jugadas=0.0
        )
        
        nueva_transaccion = Transaccion(
            usuario_id=usuario.id,
            tipo=TipoTransaccion.COMPRA,
            cantidad=videojuego.precio,
            detalles=f"Compra del juego: {videojuego.titulo}"
        )

        session.add(usuario)
        session.add(nueva_adquisicion)
        session.add(nueva_transaccion)
        session.commit()

        return {
            "status": "success",
            "message": f"Compra realizada con éxito. '{videojuego.titulo}' añadido.",
            "saldo_restante": usuario.saldo_cartera
        }
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error transaccional: {str(e)}.")


@router.post("/crear-videojuego", status_code=status.HTTP_201_CREATED)
def crear_videojuego_plataforma(juego_in: Videojuego, session: Session = Depends(get_session), creador_actual: dict = Depends(ExigirRol(["admin", "dev"]))):
    """Autenticado (Solo ADMIN y DEV): Permite dar de alta un nuevo juego individual."""
    try:
        session.add(juego_in)
        session.commit()
        session.refresh(juego_in)
        return {"status": "success", "juego_creado": juego_in}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=f"Error al crear el videojuego: {str(e)}")

# ENDPOINTS PATCH (ACTUALIZACIONES)

@router.patch("/add-saldo")
def add_saldo(cantidad: float, password_conf: str, session: Session = Depends(get_session), usuario_logueado: dict = Depends(obtener_usuario_actual)):
    """Autenticado (Cualquier Rol): Añade dinero a tu propia cuenta usando el Token JWT."""
    if cantidad <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La cantidad debe ser mayor a 0€.")
    
    usuario = session.get(Usuario, usuario_logueado["id"])
    
    if not verify_password(password_conf, usuario.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Contraseña incorrecta. Operación denegada.")
    
    usuario.saldo_cartera += cantidad
    
    nueva_transaccion = Transaccion(
        usuario_id=usuario.id,
        tipo=TipoTransaccion.INGRESO,
        cantidad=cantidad,
        detalles="Ingreso de fondos en billetera digital"
    )
    
    session.add(usuario)
    session.add(nueva_transaccion)
    session.commit()

    return {
        "status": "success",
        "message": f"Fondos añadidos con éxito. Nuevo saldo: {usuario.saldo_cartera}€."
    }

@router.patch("/jugar/{videojuego_id}")
def registrar_horas_juego(videojuego_id: int, horas: float, session: Session = Depends(get_session), usuario_logueado: dict = Depends(obtener_usuario_actual)):
    """Autenticado (Cualquier Rol): Registra horas jugadas en tu biblioteca."""
    if horas <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Las horas deben ser positivas.")
    
    registro_biblioteca = session.exec(
        select(Biblioteca).where(
            Biblioteca.usuario_id == usuario_logueado["id"], 
            Biblioteca.videojuego_id == videojuego_id
        )
    ).first()
    
    if not registro_biblioteca:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No posees este videojuego en tu biblioteca.")
    
    registro_biblioteca.horas_jugadas += horas
    session.add(registro_biblioteca)
    session.commit()
    return {
        "status": "success",
        "message": f"Horas acumuladas. Total: {registro_biblioteca.horas_jugadas} horas."
    }

# ENDPOINTS DELETE (BAJAS DE CUENTA)

@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_usuario(password_conf: str, session: Session = Depends(get_session), usuario_logueado: dict = Depends(obtener_usuario_actual)):
    """Autenticado (Cualquier Rol): El usuario logueado se da de baja a sí mismo (Soft Delete)."""
    usuario = session.get(Usuario, usuario_logueado["id"])
        
    if not verify_password(password_conf, usuario.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Contraseña de confirmación incorrecta.")
    
    usuario.activo = False
    session.add(usuario)
    session.commit()
    return None