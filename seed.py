from datetime import datetime, timezone
from sqlmodel import Session, select
from database import engine
from models import Videojuego, Usuario

def poblar_db():
    print("Iniciando semillado de datos...")
    with Session(engine) as session:
        control_juegos = session.exec(select(Videojuego)).first()
        if control_juegos:
            print("La base de datos ya contiene datos de muestra. Proceso cancelado.")
            return
        
        print("Insertando videojuegos de prueba...")

        juego1 = Videojuego(
            titulo="The Witcher 3: Wild Hunt",
            descripcion="Un RPG de mundo abierto basado en las novelas de fantasía de Andrzej Sapkowski.",
            precio=29.99,
            desarrollador="CD Projekt Red"
        )
        juego2 = Videojuego(
            titulo="Hades",
            descripcion="Un juego de mazmorras de acción rápida donde desafías al Dios del Inframundo.",
            precio=24.50,
            desarrollador="Supergiant Games"
        )
        juego3 = Videojuego(
            titulo="Cyberpunk 2077",
            descripcion="Un RPG de acción y aventura ambientado en la megalópolis futurista de Night City.",
            precio=59.99,
            desarrollador="CD Projekt Red"
        )

        print("Insertando usuarios de prueba...")
        print("Insertando usuarios de prueba...")
        usuario1 = Usuario(
            username="gamer_pro",
            email="pro@pixelvault.com",
            hashed_password="clave_falsa_segura_1", # En la Fase de seguridad usaremos bcrypt/passlib
            saldo_cartera=100.00
        )
        usuario2 = Usuario(
            username="casual_player",
            email="casual@pixelvault.com",
            hashed_password="clave_falsa_segura_2",
            saldo_cartera=20.00
        )

        session.add(juego1)
        session.add(juego2)
        session.add(juego3)
        session.add(usuario1)
        session.add(usuario2)

        session.commit()
        print("Semillado completado con éxito.")

if __name__ == "__main__":
    poblar_db()