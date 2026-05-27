import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from config import settings
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Optional

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="usuarios/login")

def hashing_password(password: str) -> str:
    """Transforma una contraseña en texto plano en un hash seguro e indescifrable."""
    password_bytes = password.encode('utf-8')
    sal = bcrypt.gensalt()
    hash_bytes = bcrypt.hashpw(password_bytes, sal)
    return hash_bytes.decode('utf-8')

def verify_password(password_plana: str, password_hasheada: str) -> bool:
    """Comprueba una contraseña introducida por el usuario con el hash guardado."""
    try:
        return bcrypt.checkpw(
            password_plana.encode('utf-8'),
            password_hasheada.encode('utf-8')
        )
    except Exception:
        return False
    
def create_access_token(data: str) -> str:
    """Genera un token JWT firmado que almacena información del usuario (id, username, rol)."""
    to_encode = data.copy()

    expiracion = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expiracion})

    encode_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm="HS256")
    return encode_jwt

def decode_access_token(token: str) -> Optional[dict]:
    """Lee un token JWT, verifica que la firma sea válida y que no haya caducado."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.PyJWTError:
        return None
    
def obtener_usuario_actual(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Dependencia que intercepta la petición, valida el JWT y devuelve
    los datos del usuario que está operando en la API.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se puedo validar el token de acceso o ha expirado.",
        headers={"WWW-Authenticate": "Bearer"}
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    username: Optional[str] = payload.get("username")
    rol: Optional[str] = payload.get("rol")
    usuario_id: Optional[str] = payload.get("sub")

    if username is None or rol is None or usuario_id is None:
        raise credentials_exception
    
    return {
        "id": int(usuario_id),
        "username": username,
        "rol": rol
    }

class ExigirRol:
    """
    Clase factoría para validar permisos por roles (RBAC).
    Permite proteger endpoints escribiendo Depends(ExigirRol(["admin"]))
    """
    def __init__(self, roles_permitidos: list[str]):
        self.roles_permitidos = roles_permitidos
    def __call__(self, usuario_actual: dict = Depends(obtener_usuario_actual)):
        if usuario_actual["rol"] not in self.roles_permitidos:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado. No tienes los permisos necesarios.")
        return usuario_actual