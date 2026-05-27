from datetime import datetime, timezone
from sqlmodel import Session, select
from database import engine
from models import Videojuego, Usuario, RolUser
from security import hashing_password

def poblar_db():
    print("Iniciando semillado de datos...")
    with Session(engine) as session:
        control_juegos = session.exec(select(Videojuego)).first()
        if control_juegos:
            print("La base de datos ya contiene datos de muestra. Proceso cancelado.")
            return
        
        print("Insertando videojuegos de prueba...")

        juego1 = Videojuego(titulo="The Witcher 3: Wild Hunt", descripcion="Un RPG de mundo abierto...", precio=29.99, desarrollador="CD Projekt Red")
        juego2 = Videojuego(titulo="Hades", descripcion="Un juego de mazmorras...", precio=24.50, desarrollador="Supergiant Games")
        juego3 = Videojuego(titulo="Cyberpunk 2077", descripcion="Un RPG de acción...", precio=59.99, desarrollador="CD Projekt Red")

        print("Insertando usuarios con Roles y Hashes reales...")
        admin = Usuario(
            username="carlos_admin",
            email="admin@pixelvault.com",
            hashed_password=hashing_password("admin123"),
            saldo_cartera=0.0,
            rol=RolUser.ADMIN 
        )
        
        usuario_normal = Usuario(
            username="gamer_pro",
            email="pro@pixelvault.com",
            hashed_password=hashing_password("12345"),
            saldo_cartera=100.0,
            rol=RolUser.USER_BASE 
        )

        usuario_dev = Usuario(
            username="dessarrollador1",
            email="dev@pixelvault.com",
            hashed_password=hashing_password("12345"),
            saldo_cartera=100.0,
            rol=RolUser.DEV 
        )

        session.add_all([juego1, juego2, juego3, admin, usuario_normal])

        session.add(juego1)
        session.add(juego2)
        session.add(juego3)
        session.add(admin)
        session.add(usuario_normal)
        session.add(usuario_dev)

        session.commit()
        print("¡Semillado v2.0 completado con éxito!")

if __name__ == "__main__":
    poblar_db()