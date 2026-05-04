# 🐍 Andamiaje Python

> Sistema adaptativo de aprendizaje de Python con andamiaje dinámico generado por IA, diseñado para cursos universitarios de programación.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32-FF4B4B?logo=streamlit)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python)](https://python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql)](https://postgresql.org)
[![Claude Haiku](https://img.shields.io/badge/Claude-Haiku-orange?logo=anthropic)](https://anthropic.com)

---

## ¿Qué es?

**Andamiaje Python** aplica la teoría del andamiaje cognitivo (scaffolding) de Vygotsky al aprendizaje de programación. El sistema genera pistas progresivas (mínima → parcial → completa) para cada ejercicio usando Claude Haiku, evalúa el código del estudiante automáticamente y construye una ruta de aprendizaje personalizada al final de cada corte.

### Roles

| Rol | Capacidades |
|-----|-------------|
| **Estudiante** | Chat adaptativo con ejercicios, evaluación por corte, ruta de aprendizaje personalizada, email automático |
| **Docente** | Crear/editar preguntas, ver analíticas del curso, asignar estudiantes a cursos, recibir alertas de riesgo |
| **Admin** | Gestión completa de usuarios, cursos y configuración global |

---

## Arquitectura

| Diagrama | Descripción |
|----------|-------------|
| [Modelo de Negocio](docs/arquitectura_negocio.svg) | Flujo de valor entre actores del sistema |
| [Arquitectura Técnica](docs/arquitectura_tecnica.svg) | Stack tecnológico, capas y flujo de datos |

---

## Stack Tecnológico

| Capa | Tecnología |
|------|------------|
| Frontend | Streamlit 1.32 + Plotly |
| Backend API | FastAPI + Uvicorn (async) |
| Base de datos | PostgreSQL 16 + SQLAlchemy 2 async + Alembic |
| IA generativa | Claude Haiku (Anthropic) |
| Evaluación código | pytest + BLEU (nltk) + análisis radon |
| ML predicción riesgo | scikit-learn RandomForestClassifier |
| Email | SendGrid |
| Auth | JWT (python-jose) + bcrypt |
| Deploy | Render (web services + PostgreSQL addon) |

---

## Instalación local

### Requisitos

- Python 3.11+
- Docker (para PostgreSQL)
- Cuenta Anthropic (Claude Haiku)
- Cuenta SendGrid *(opcional, para emails)*

### 1. Clonar y crear entorno

```bash
git clone https://github.com/tu-usuario/andamiaje-python.git
cd andamiaje-python
python -m venv .venv

# Windows
.venv\Scripts\Activate.ps1

# Linux/Mac
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Variables de entorno

```bash
cp .env.example .env
# Edita .env con tus credenciales reales
```

Variables requeridas en `.env`:

```env
DATABASE_URL=postgresql+asyncpg://andamiaje:andamiaje123@localhost:5432/andamiaje_db
JWT_SECRET_KEY=una-clave-secreta-larga-y-aleatoria
ANTHROPIC_API_KEY=sk-ant-...

# Opcionales (email):
SENDGRID_API_KEY=SG....
SENDGRID_FROM_EMAIL=no-reply@tudominio.com
SENDGRID_FROM_NAME=Andamiaje Python
```

### 3. Base de datos (Docker)

```bash
docker run -d \
  --name andamiaje-db \
  -e POSTGRES_USER=andamiaje \
  -e POSTGRES_PASSWORD=andamiaje123 \
  -e POSTGRES_DB=andamiaje_db \
  -p 5432:5432 \
  postgres:16
```

### 4. Migraciones y seed

```bash
alembic upgrade head
python -m backend.scripts.seed
```

### 5. Levantar servicios

**Terminal 1 — Backend API:**
```bash
uvicorn backend.main:app --reload --port 8000
```

**Terminal 2 — Frontend Streamlit:**
```bash
streamlit run app.py
```

| Servicio | URL |
|----------|-----|
| App Streamlit | http://localhost:8501 |
| API Swagger UI | http://localhost:8000/api/docs |
| API ReDoc | http://localhost:8000/api/redoc |
| Health check | http://localhost:8000/api/health |

---

## Credenciales de prueba

| Rol | Email | Contraseña |
|-----|-------|------------|
| Admin | `admin@andamiaje.com` | `Admin1234!` |
| Docente 1 | `cmendez@andamiaje.com` | `Docente1234!` |
| Docente 2 | `lrios@andamiaje.com` | `Docente1234!` |
| Estudiante 1 | `sherrera@andamiaje.com` | `Estudiante1234!` |
| Estudiante 2 | `amora@andamiaje.com` | `Estudiante1234!` |
| Estudiante 3 | `vcastro@andamiaje.com` | `Estudiante1234!` |

---

## Flujo de uso

```
1. Docente → asigna estudiantes a su curso (Tab "Mis Estudiantes")
2. Estudiante → entra al Chat Adaptativo → resuelve ejercicios con pistas progresivas
3. Estudiante → "Calcular mi evaluación" → score + ruta de aprendizaje + email automático
4. Docente → Analíticas → heatmap de temas, predicción de riesgo, alertas
5. Admin → Gestión global de usuarios y cursos
```

---

## Estructura del proyecto

```
andamiaje-python/
├── app.py                  # Entrada Streamlit (navegación por rol)
├── pages/
│   ├── 00_Login.py         # Landing page + autenticación JWT
│   ├── 06_Docente.py       # Preguntas, analíticas, asignación estudiantes
│   ├── 07_Chat.py          # Chat adaptativo con andamiaje
│   ├── 08_MiProgreso.py    # Score, ruta de aprendizaje, recursos
│   ├── 09_Admin.py         # Gestión global
│   └── utils.py            # api_call(), safe_detail(), require_auth()
├── backend/
│   ├── main.py             # FastAPI app (CORS, middleware, OpenAPI)
│   ├── core/               # config, database (async), security (JWT)
│   ├── models/             # SQLAlchemy models (usuario, curso, evaluacion…)
│   ├── routers/            # auth, chat, evaluaciones, admin, analiticas
│   ├── schemas/            # Pydantic schemas
│   ├── services/           # scoring, email, analytics, andamiaje, chat
│   └── scripts/            # init_db.py, seed.py
├── src/
│   ├── claude_haiku.py     # Cliente Anthropic (llamar_haiku, llamar_haiku_json)
│   ├── evaluator.py        # Evaluación de código (pytest + BLEU + radon)
│   └── reward_schema.py    # Esquema de puntuación
├── exercises/              # Ejercicios por nivel (junior/semi-senior/senior)
├── alembic/                # Migraciones de base de datos
├── docs/
│   ├── arquitectura_negocio.svg
│   └── arquitectura_tecnica.svg
├── .env.example            # Plantilla de variables de entorno
├── requirements.txt
└── alembic.ini
```

---

## API Reference

La documentación interactiva está disponible en `/api/docs` (Swagger UI) y `/api/redoc`.

### Endpoints principales

| Método | Ruta | Descripción | Rol |
|--------|------|-------------|-----|
| `POST` | `/api/auth/login` | Obtener JWT | Público |
| `GET` | `/api/auth/me` | Perfil del usuario actual | Todos |
| `POST` | `/api/chat/iniciar` | Iniciar sesión de chat | Estudiante |
| `POST` | `/api/chat/responder` | Enviar código y obtener feedback | Estudiante |
| `POST` | `/api/evaluaciones/calcular/{corte}` | Calcular score + enviar email | Estudiante |
| `GET` | `/api/evaluaciones/mis-evaluaciones` | Historial de evaluaciones | Estudiante |
| `POST` | `/api/evaluaciones/enviar-email/{id}` | Reenviar email manualmente | Estudiante |
| `GET` | `/api/admin/estudiantes` | Listar estudiantes con su curso | Admin, Docente |
| `POST` | `/api/admin/usuarios/{id}/asignar-curso` | Asignar estudiante a curso | Admin, Docente |
| `GET` | `/api/analiticas/heatmap` | Heatmap temas × corte | Docente, Admin |
| `GET` | `/api/analiticas/predicciones-riesgo` | Predicciones ML por curso | Docente, Admin |

---

## Fórmula de scoring

$$\text{score} = \text{tests} \times 0.40 + \text{haiku} \times 0.30 + \text{BLEU} \times 0.20 + \text{eficiencia} \times 0.10$$

---

## Deploy en Render

1. Fork del repositorio en GitHub
2. Crear un **PostgreSQL** addon en Render
3. Crear dos **Web Services**: uno para la API, otro para Streamlit
4. Configurar las variables de entorno del `.env.example` en el dashboard de Render
5. El startup corre automáticamente: `alembic upgrade head && python -m backend.scripts.seed`

---

## Variables de entorno

Ver [`.env.example`](.env.example) para la lista completa con descripción de cada variable.

> ⚠️ **Seguridad:** El archivo `.env` está en `.gitignore`. Nunca subas credenciales reales al repositorio.

---

## Tests

```bash
pytest tests/ -v
```

Los tests cubren los tres niveles de ejercicios (junior, semi-senior, senior) con el evaluador de código.

---

## Licencia

MIT — libre para uso académico y educativo.

---

Desarrollado por **Ing. Julian Andres Quimbayo Castro**
