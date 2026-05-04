"""
backend/main.py
FastAPI app con CORS, middleware de seguridad y routers.
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.openapi.utils import get_openapi
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from backend.core.config import settings
from backend.routers import admin, analiticas, auth, chat, evaluaciones, preguntas


# ── Middleware de headers de seguridad ────────────────────────────────────────

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response


# ── Lifespan ─────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Andamiaje Python API",
    version="2.0.0",
    description=(
        "## Sistema Adaptativo de Aprendizaje de Python\n\n"
        "API REST para el sistema de docencia adaptativa con andamiaje dinámico basado en IA (Claude Haiku).\n\n"
        "### Autenticación\n"
        "1. Usa `POST /api/auth/login` con tu email y contraseña.\n"
        "2. Copia el `access_token` de la respuesta.\n"
        "3. Click en **Authorize** (🔒) arriba a la derecha y pega: `Bearer <token>`.\n\n"
        "### Roles\n"
        "| Rol | Acceso |\n"
        "|-----|--------|\n"
        "| `admin` | Gestión completa de usuarios, cursos y alertas globales |\n"
        "| `docente` | CRUD de preguntas, analíticas, asignación de estudiantes a sus cursos |\n"
        "| `estudiante` | Chat adaptativo, evaluaciones propias, ruta de aprendizaje |\n\n"
        "### Flujo principal\n"
        "1. **Auth** → `POST /api/auth/login` → obtener JWT\n"
        "2. **Chat** → `POST /api/chat/iniciar` → `POST /api/chat/responder` → ejercicios adaptativos\n"
        "3. **Evaluación** → `POST /api/evaluaciones/calcular/{corte}` → score + ruta de aprendizaje + **email automático**\n"
        "4. **Admin/Docente** → `GET /api/admin/estudiantes` → `POST /api/admin/usuarios/{id}/asignar-curso`\n\n"
        "### Credenciales de prueba\n"
        "| Rol | Email | Contraseña |\n"
        "|-----|-------|-----------|\n"
        "| admin | `admin@andamiaje.com` | `Admin1234!` |\n"
        "| docente | `cmendez@andamiaje.com` | `Docente1234!` |\n"
        "| estudiante | `sherrera@andamiaje.com` | `Estudiante1234!` |"
    ),
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# CORS — solo permite el frontend configurado
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SecurityHeadersMiddleware)

# ── Routers ───────────────────────────────────────────────────────────────────

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(preguntas.router, prefix="/api/preguntas", tags=["preguntas"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(evaluaciones.router, prefix="/api/evaluaciones", tags=["evaluaciones"])
app.include_router(analiticas.router, prefix="/api/analiticas", tags=["analiticas"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/api/health", tags=["health"])
async def health():
    return {"status": "ok", "version": app.version}


# ── OpenAPI con JWT en Swagger ────────────────────────────────────────────────

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=[
            {"name": "auth", "description": "Registro, login y perfil del usuario autenticado"},
            {"name": "chat", "description": "Sesiones de chat adaptativo con ejercicios generados por IA"},
            {"name": "evaluaciones", "description": "Cálculo de score por corte, ruta de aprendizaje y envío de email automático"},
            {"name": "preguntas", "description": "Banco de preguntas (CRUD para docentes y admin)"},
            {"name": "analiticas", "description": "Heatmaps, temas débiles y rendimiento por curso (docente/admin)"},
            {"name": "admin", "description": "Gestión de usuarios, cursos, asignación de estudiantes y alertas"},
            {"name": "health", "description": "Estado del servidor"},
        ],
    )
    schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Pega el token obtenido de POST /api/auth/login",
        }
    }
    for path in schema.get("paths", {}).values():
        for operation in path.values():
            operation.setdefault("security", [{"BearerAuth": []}])
    app.openapi_schema = schema
    return schema


app.openapi = custom_openapi
