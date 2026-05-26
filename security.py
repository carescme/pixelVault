import bcrypt

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