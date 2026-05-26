# 🎮 PixelVault API

PixelVault es un backend robusto y modular que simula las funciones principales de una plataforma de distribución digital de videojuegos (estilo Steam). Permite la gestión de usuarios, carteras digitales, un catálogo global de videojuegos y bibliotecas personalizadas mediante relaciones complejas en la base de datos.

Desarrollado con **Python**, **FastAPI**, **SQLModel** (SQLAlchemy) y **PostgreSQL**.

---

## 🚀 Características Clave

- **Arquitectura Modular:** Rutas organizadas limpiamente mediante `APIRouter` separando las responsabilidades de usuarios y videojuegos.
- **Relación Muchos a Muchos (Many-to-Many):** Implementación nativa de la tabla intermedia `Biblioteca` para conectar usuarios y videojuegos, registrando metadatos adicionales (horas jugadas y fechas de adquisición).
- **Rendimiento Optimizado (Bulk Insert):** Endpoint diseñado para realizar inyecciones masivas de videojuegos en una única transacción de red.
- **Seguridad y Hashing:** Registro de usuarios con encriptación de contraseñas en tiempo real mediante el algoritmo **Bcrypt**.
- **Validación Transaccional:** Control estricto de lógica de negocio (verificación de saldo suficiente, prevención de juegos duplicados en la biblioteca y confirmación de identidad mediante contraseña para operaciones críticas).
- **Esquemas de Lectura Protectores:** Uso avanzado de Pydantic/SQLModel para estructurar las respuestas de la API, ocultando datos sensibles (como contraseñas hasheadas) y resolviendo la carga de relaciones mediante `selectinload`.

---

## 🛠️ Tecnologías Utilizadas

- **Python 3.12+**
- **FastAPI:** Framework web asíncrono y de alto rendimiento.
- **SQLModel:** ORM moderno que fusiona la potencia de SQLAlchemy con la validación de Pydantic.
- **PostgreSQL:** Sistema de gestión de bases de datos relacionales.
- **Bcrypt:** Librería para el hashing seguro de contraseñas.
- **Pydantic v2:** Validación de datos y gestión de configuraciones mediante variables de entorno (`.env`).

---

## 📦 Estructura del Proyecto

```text
pixelVault/
│
├── routers/
│   ├── __init__.py
│   ├── games.py         # Rutas del catálogo de videojuegos y Bulk Insert
│   └── users.py         # Rutas de usuarios, compras, saldo y Top Jugados
│
├── config.py            # Configuración y validación del entorno (Pydantic Settings)
├── database.py          # Conexión del motor (Engine) e inicialización de tablas
├── main.py              # Punto de entrada de la aplicación (Lifespan y FastAPI)
├── models.py            # Modelos de tablas de la BD y Esquemas de Pydantic
├── security.py          # Lógica de hashing y verificación de contraseñas
├── seed.py              # Script independiente para poblar la BD con datos de prueba
├── .gitignore           # Archivo protector para evitar subir entornos virtuales o claves
└── README.md            # Documentación del proyecto
```

---

## 🔧 Instalación y Configuración

Sigue estos pasos para levantar el proyecto en tu entorno local:

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu_usuario/pixelVault.git
cd pixelVault
```

### 2. Configurar el Entorno Virtual

```bash
python -m venv .venv

# En Windows (PowerShell):
.\.venv\Scripts\Activate.ps1

# En Linux/Mac:
source .venv/bin/activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Variables de Entorno (`.env`)

Crea un archivo llamado `.env` en la raíz del proyecto y configura tus credenciales de PostgreSQL:

```env
DATABASE_URL=postgresql://tu_usuario:tu_contraseña@localhost:5432/pixelvault_db
```

### 5. Semillado de la Base de Datos (Opcional)

Para poblar las tablas automáticamente con datos iniciales seguros (hashes Bcrypt reales), ejecuta:

```bash
python seed.py
```

---

## 🏃‍♂️ Ejecución

Inicia el servidor de desarrollo local con Uvicorn:

```bash
uvicorn main:app --reload
```

El servidor comenzará a correr en:

```text
http://127.0.0.1:8000
```

---

## 📑 Documentación Interactiva de la API

Una vez encendido el servidor, puedes acceder a la documentación interactiva autogenerada para realizar pruebas de todos los endpoints:

- **Swagger UI:** `http://127.0.0.1:8000/docs`
