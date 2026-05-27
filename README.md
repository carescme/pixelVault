# 🎮 PixelVault API

PixelVault es un backend robusto y modular que simula las funciones principales de una plataforma de distribución digital de videojuegos (estilo Steam). Permite la gestión de usuarios, carteras digitales, un catálogo global de videojuegos y bibliotecas personalizadas mediante relaciones complejas en la base de datos.

Desarrollado con **Python**, **FastAPI**, **SQLModel** (SQLAlchemy) y **PostgreSQL**.

---

## 🚀 Características Clave

- **Arquitectura Modular:** Rutas organizadas limpiamente mediante `APIRouter` separando las responsabilidades de usuarios y videojuegos.
- **Autenticación Descentralizada (JWT):** Implementación de tokens de acceso eficientes y seguros mediante el algoritmo **HS256**. El servidor valida identidades matemáticamente sin almacenar sesiones en memoria.
- **Control de Accesos Basado en Roles (RBAC):** Sistema factoría centralizado para restringir endpoints críticos. Por ejemplo, la creación e inyección masiva de catálogo está reservada exclusivamente para roles autorizados (`admin`, `dev`).
- **Seguridad a Nivel de Fila (Implicit Ownership):** Eliminación completa de manipulación de IDs de usuario por la URL. Las operaciones financieras o de juego extraen el ID de forma oculta y segura desde el Token criptográfico.
- **Libro de Contabilidad e Historial Financiero:** Tabla de auditoría integrada (`Transacciones`) que registra cronológicamente cada ingreso de saldo o compra con marcas de tiempo UTC perfectas.
- **Relación Muchos a Muchos (Many-to-Many):** Implementación de la tabla intermedia `Biblioteca` para conectar usuarios y videojuegos, permitiendo acumular metadatos dinámicos (horas jugadas).
- **Ciclo de Vida de Datos (Soft Delete):** Preservación estricta de la integridad referencial y el histórico de compras. Los videojuegos o usuarios dados de baja pasan a estado inactivo (`activo = False`), desapareciendo del flujo público sin destruir registros en la base de datos.
- **Rendimiento Optimizado (Bulk Insert):** Endpoint administrativo diseñado para inyectar un catálogo masivo de videojuegos en una única transacción de base de datos.

---

## 🛠️ Tecnologías Utilizadas

- **Python 3.12+**
- **FastAPI:** Framework web asíncrono y de alto rendimiento.
- **SQLModel:** ORM moderno que fusiona la potencia de SQLAlchemy con la validación de Pydantic.
- **PostgreSQL:** Sistema de gestión de bases de datos relacionales.
- **Bcrypt:** Librería para el hashing seguro de contraseñas.
- **PyJWT:** Generación y decodificación de JSON Web Tokens para la seguridad.
- **Python-Multipart:** Procesamiento de datos de formulario web para sincronización nativa con la UI de Swagger.
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
JWT_SECRET=tu_clave_secreta_segura_de_64_caracteres_hexadecimales
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
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
