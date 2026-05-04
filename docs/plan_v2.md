# Plan v2 — Andamiaje Python: Sistema Adaptativo Completo

## Resumen

Evolucionar el proyecto actual (pipeline de investigación Streamlit) a un sistema educativo productivo con autenticación por roles, base de datos PostgreSQL, chat adaptativo con Claude Haiku API, scoring por corte académico, rutas de aprendizaje personalizadas, analíticas descriptivas + predictivas para docentes y admin, y envío por email con SendGrid. Primero estable local, luego deploy en Render.

---

## Stack Tecnológico

| Capa | Tecnología |
|------|-----------|
| Backend API | FastAPI + SQLAlchemy (async) + Alembic |
| Base de datos | PostgreSQL |
| Autenticación | JWT (python-jose) + bcrypt |
| Frontend | Streamlit (conservar páginas actuales + nuevas) |
| LLM | Claude Haiku API directa (claude-haiku-4-5) |
| ML Predictivo | scikit-learn + joblib (sin GPU) |
| Email | SendGrid (free tier — 100 emails/día) |
| Deploy | Render (2 web services + 1 PostgreSQL addon) |

---

## Roles y Permisos

| Funcionalidad | Admin | Docente | Estudiante |
|--------------|-------|---------|-----------|
| Gestionar usuarios y roles | ✓ | — | — |
| Crear/editar preguntas | ✓ | ✓ solo suyas | — |
| Ver pipeline investigación (01–05) | ✓ | ✓ | — |
| Chat adaptativo | — | — | ✓ |
| Ver mi progreso + ruta aprendizaje | — | — | ✓ |
| Analíticas de su curso | — | ✓ | — |
| Predicciones de riesgo de su curso | — | ✓ | — |
| Analíticas globales (todos los cursos) | ✓ | — | — |
| Predicciones globales | ✓ | — | — |
| Alertas tempranas | ✓ global | ✓ su curso | — |

---

## Modelo de Datos (PostgreSQL)

```
usuarios
  id, nombre_completo, email, password_hash,
  rol (admin | docente | estudiante), activo, created_at

cursos
  id, nombre, docente_id (FK→usuarios), periodo (ej: 2026-1), activo

estudiantes
  id, usuario_id (FK→usuarios), semestre, programa_academico, curso_id (FK→cursos)

preguntas
  id, titulo, enunciado, solucion_referencia,
  nivel (junior | semi_senior | senior), tema,
  docente_id (FK→usuarios), activa, created_at

andamiajes
  id, pregunta_id (FK→preguntas),
  nivel_andamiaje (minimo | parcial | completo),
  contenido (TEXT — generado por Haiku)

sesiones_chat
  id, estudiante_id (FK→estudiantes), pregunta_id (FK→preguntas),
  corte (1 | 2 | 3), score_final, started_at, ended_at

mensajes_chat
  id, sesion_id (FK→sesiones_chat), rol (user | assistant),
  contenido, timestamp

respuestas_estudiante
  id, sesion_id (FK→sesiones_chat), pregunta_id (FK→preguntas),
  codigo_enviado, passed_tests (bool), bleu_score, haiku_score, intentos

evaluaciones
  id, estudiante_id (FK→estudiantes), corte (1 | 2 | 3),
  curso_id (FK→cursos), score_global,
  ruta_aprendizaje (JSONB), enviada_email (bool), created_at

predicciones_riesgo
  id, estudiante_id (FK→estudiantes), corte, curso_id,
  score_riesgo (float 0–1), en_riesgo (bool),
  temas_debiles (JSONB), notificado_docente (bool), created_at
```

---

## Estructura de Carpetas

```
andamiaje-python/
├── app.py                          # Streamlit entry (conservar)
├── backend/
│   ├── main.py                     # FastAPI app + CORS + routers
│   ├── core/
│   │   ├── config.py               # Settings con pydantic-settings
│   │   ├── database.py             # AsyncSession + engine
│   │   └── security.py            # JWT + bcrypt
│   ├── models/
│   │   ├── usuario.py
│   │   ├── curso.py
│   │   ├── pregunta.py
│   │   ├── sesion_chat.py
│   │   ├── evaluacion.py
│   │   └── prediccion_riesgo.py
│   ├── schemas/                    # Pydantic request/response
│   ├── routers/
│   │   ├── auth.py
│   │   ├── preguntas.py
│   │   ├── chat.py
│   │   ├── evaluaciones.py
│   │   ├── analiticas.py
│   │   └── admin.py
│   └── services/
│       ├── andamiaje_service.py
│       ├── chat_service.py
│       ├── scoring_service.py
│       ├── email_service.py
│       └── analytics_service.py
├── pages/
│   ├── 00_Login.py                 # NUEVO
│   ├── 01_Datos.py                 # conservar
│   ├── 02_Etiquetado.py            # conservar
│   ├── 03_SFT.py                   # conservar
│   ├── 04_RLHF.py                  # conservar
│   ├── 05_Evaluacion.py            # conservar
│   ├── 06_Docente.py               # NUEVO
│   ├── 07_Chat.py                  # NUEVO
│   ├── 08_MiProgreso.py            # NUEVO
│   └── 09_Admin.py                 # NUEVO
├── src/                            # Conservar módulos existentes
├── exercises/                      # Conservar (seed inicial)
├── data/
│   └── models/
│       └── riesgo_model.pkl        # Modelo ML persistido
├── alembic/
│   └── versions/
├── alembic.ini
├── render.yaml
├── Dockerfile
└── requirements.txt
```

---

## Nuevas Dependencias

```
fastapi>=0.111.0
uvicorn[standard]>=0.29.0
sqlalchemy[asyncio]>=2.0.0
asyncpg>=0.29.0
alembic>=1.13.0
pydantic-settings>=2.2.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
httpx>=0.27.0
sendgrid>=6.11.0
python-multipart>=0.0.9
scikit-learn>=1.4.0
joblib>=1.3.0
```

---

## Fases de Implementación

### FASE 1 — Backend FastAPI + Base de Datos

**Objetivo:** API corriendo local con PostgreSQL y tablas creadas.

1. PostgreSQL local (Docker: `docker run -e POSTGRES_PASSWORD=pass -p 5432:5432 postgres`)
2. `backend/core/config.py` con pydantic-settings leyendo `.env`
3. `backend/core/database.py` — engine async + `get_db` dependency
4. Todos los modelos SQLAlchemy en `backend/models/`
5. Alembic init + primera migración: `alembic revision --autogenerate -m "init"`
6. Aplicar: `alembic upgrade head`
7. `backend/main.py` con `GET /api/health`
8. `backend/scripts/seed.py` — importa 30 ejercicios de `exercises/` como preguntas iniciales

**Verificación:** `GET http://localhost:8000/api/health` → `{"status": "ok"}` + tablas en psql

---

### FASE 2 — Autenticación JWT (3 roles)

**Objetivo:** Login funcional con tokens y control de acceso por rol.

1. `backend/core/security.py` — hash/verify password, create/decode JWT, `get_current_user`
2. `POST /api/auth/register`, `POST /api/auth/login`, `GET /api/auth/me`
3. Decoradores `require_role("admin")`, `require_role("docente")`
4. `pages/00_Login.py` — guarda token en `st.session_state["token"]`
5. `pages/utils.py` — `api_call(method, path, **kwargs)` con header Authorization
6. Todas las páginas verifican token al inicio; sin token → redirigir a `00_Login.py`

**Verificación:** JWT válido en login; 401 sin token en rutas protegidas

---

### FASE 3 — Módulo Docente: Gestión de Preguntas

**Objetivo:** Docente crea/edita preguntas; Haiku genera andamiajes automáticamente.

1. CRUD `/api/preguntas/` + `POST /api/preguntas/importar-csv`
2. `andamiaje_service.py` — llama `llamar_haiku()` 3 veces al crear pregunta (mínimo/parcial/completo)
3. `pages/06_Docente.py` Tab 1 — formulario + tabla + upload CSV + preview andamiajes

**Verificación:** Crear pregunta → 3 registros en tabla `andamiajes` generados por Haiku

---

### FASE 4 — Chat Adaptativo del Estudiante

**Selección de ejercicios:**
- Peso mayor a temas con score < 0.6 en sesiones previas del mismo corte
- Siempre al menos 1 pregunta de bases (variables, listas, funciones)
- Sin repetir preguntas completadas con score ≥ 0.8 en el mismo corte

**Progresión del andamiaje:**
- Inicio: `mínimo`
- Tras 3 intentos sin avance → `parcial`
- Tras 2 intentos más → `completo`

1. `POST /api/chat/iniciar` · `POST /api/chat/mensaje` · `POST /api/chat/evaluar-codigo` · `GET /api/chat/sesion/{id}`
2. `chat_service.py` — progresión + construcción del system prompt contextual
3. `pages/07_Chat.py` — `st.chat_message` + editor código + panel andamiaje + tests en tiempo real

**Verificación:** Código correcto → tests pasan + score guardado en BD

---

### FASE 5 — Scoring, Rutas de Aprendizaje y Email

**Fórmula:**
```
score_global = (pass_tests × 0.40) + (haiku_score × 0.30) + (bleu_score × 0.20) + (eficiencia_intentos × 0.10)
eficiencia_intentos = max(0, 1 - (intentos - 1) × 0.1)
```

**Ruta de aprendizaje (JSONB):**
```json
{
  "temas_fuertes": ["listas", "funciones"],
  "temas_a_reforzar": ["decoradores", "dataframes"],
  "ejercicios_recomendados": [{"id": "sr_03", "titulo": "...", "razon": "..."}],
  "recursos_externos": [{"titulo": "...", "url": "...", "tipo": "video|docs|ejercicio"}],
  "mensaje_motivacional": "..."
}
```

1. `POST /api/evaluaciones/calcular/{estudiante_id}/{corte}` + `POST /api/evaluaciones/enviar-email/{id}`
2. `scoring_service.py` — cálculo + Haiku genera ruta JSON personalizada
3. `email_service.py` — SendGrid HTML: score + ruta de aprendizaje
4. `pages/08_MiProgreso.py` — radar chart Plotly + tarjetas de ruta + botones calcular/enviar

**Verificación:** Score correcto + email en bandeja de entrada (SendGrid Activity Feed)

---

### FASE 6 — Analíticas Descriptivas + Predictivas (Docente y Admin)

**Objetivo:** Docente ve analíticas de su curso; Admin ve analíticas globales. Ambos acceden a predicciones de riesgo y alertas tempranas.

#### Analítica Descriptiva

| Visualización | Docente | Admin |
|--------------|---------|-------|
| Heatmap tema × nivel (scores promedio) | Solo su curso | Todos los cursos |
| Curvas de cohorte por corte 1→2→3 | Solo su curso | Global |
| Tasa de abandono por ejercicio | Solo su curso | Global |
| Tiempo promedio por pregunta | Solo su curso | Global |
| Distribución de scores por nivel | Solo su curso | Global |
| Top 5 temas más débiles | Solo su curso | Por programa académico |

#### Analítica Predictiva — scikit-learn (sin GPU)

**Features del modelo:**
```
[score_tema_variables, score_tema_listas, score_tema_funciones,
 score_tema_decoradores, score_tema_dataframes,
 semestre, intentos_promedio, tasa_completion_sesiones, corte_actual]
```

**Target:** `en_riesgo` (0/1) — riesgo de no alcanzar score_global ≥ 0.6 al cierre del corte

**Algoritmo:** `RandomForestClassifier` — robusto con pocos datos, interpretable vía `feature_importances_`

**Flujo:**
- Re-entrena automáticamente cada 50+ evaluaciones nuevas
- Modelo persistido en `data/models/riesgo_model.pkl` con joblib
- Se carga en memoria al iniciar el API

#### Análisis narrativo con Haiku

Haiku recibe resumen estadístico del grupo y devuelve insight en lenguaje natural:
> *"El 68% de estudiantes de semestre 6 falla en decoradores en el primer corte. Recomendación: introducir closures como ejercicio previo."*

#### Alertas Tempranas

- Score < 0.4 en las primeras 3 sesiones del corte → `en_riesgo = true` en `predicciones_riesgo`
- Docente ve tabla de sus estudiantes en riesgo (nombre, semestre, temas débiles, score actual)
- Admin ve alertas de todos los cursos
- Botón "Notificar al docente" → email automático

#### Endpoints

```
GET  /api/analiticas/heatmap              (param: curso_id — docente filtra el suyo)
GET  /api/analiticas/cohortes
GET  /api/analiticas/abandono
GET  /api/analiticas/distribucion-scores
GET  /api/analiticas/temas-debiles
POST /api/analiticas/insights             (Haiku narrativo del grupo)
GET  /api/predicciones/riesgo
GET  /api/predicciones/temas-criticos
POST /api/predicciones/entrenar           (solo admin)
POST /api/admin/alertas/notificar/{id}
```

#### Páginas Streamlit

**`pages/06_Docente.py`** (3 tabs):
- Tab 1: Gestión de preguntas (CRUD + CSV)
- Tab 2: Analíticas del curso (heatmap, cohortes, abandono, distribución)
- Tab 3: Predicciones y alertas (tabla en riesgo + insights Haiku)

**`pages/09_Admin.py`** (5 tabs):
- Tab 1: Gestión de usuarios (CRUD + cambio roles + asignación cursos)
- Tab 2: Analíticas globales (todos los cursos/programas)
- Tab 3: Predicciones globales (ranking por riesgo, temas críticos)
- Tab 4: Alertas y notificaciones (globales + notificar docente)
- Tab 5: Exportar reporte institucional (CSV/Excel)

**Verificación:** Heatmap correcto + predicción ML 0–1 + insights Haiku coherentes + alerta email al docente

---


### FASE 6.5 — Verificación de Seguridad (Transversal)

**Objetivo:** Garantizar que el sistema cumple con las principales mitigaciones del OWASP Top 10 antes del deploy en producción.

#### Autenticación y Control de Acceso (A01, A07)

- Todos los endpoints protegidos usan `get_current_user` como dependencia FastAPI; ninguna ruta sensible es pública accidentalmente.
- Verificar que `require_role("admin")` y `require_role("docente")` devuelven **403** (no 404) ante rol incorrecto.
- Tokens JWT firmados con `HS256`; `JWT_SECRET_KEY` de mínimo 32 caracteres aleatorios, nunca hardcodeado en código.
- Expiración de token: `JWT_EXPIRE_HOURS=24`; implementar refresh token o re-login obligatorio al vencer.
- Contraseñas hasheadas con `bcrypt` (cost factor >= 12); nunca almacenar ni loguear en texto plano.

#### Inyección (A03) — SQL y Prompt Injection

- Toda interacción con la BD usa **parámetros ORM SQLAlchemy**; prohibido concatenar strings SQL.
- Inputs del usuario enviados a Claude Haiku sanitizados antes de incluirse en el system prompt (eliminar secuencias `\n---\n`, `<|im_end|>`, `[INST]` u otros separadores de rol).
- Código enviado por el estudiante al endpoint `evaluar-codigo` ejecutado en subproceso aislado con timeout y sin acceso a red ni filesystem fuera del sandbox.

#### Exposición de Datos Sensibles (A02)

- Respuestas de la API nunca incluyen `password_hash`; esquemas Pydantic usan `exclude={"password_hash"}`.
- Logs no registran tokens JWT, API keys ni contenido de mensajes de chat.
- Variables de entorno en Render marcadas como **Secret**; nunca en el repositorio (`.gitignore` incluye `.env`).

#### CORS y Configuración Segura (A05)

- `allow_origins` restringido a `FRONTEND_URL` exacto; prohibido `"*"` en producción.
- Headers de seguridad HTTP añadidos vía middleware: `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Strict-Transport-Security` (en Render con TLS automático).

#### Rate Limiting y Disponibilidad (A04)

- Endpoints de autenticación (`/api/auth/login`, `/api/auth/register`) limitados a **10 req/min por IP** con `slowapi`.
- Endpoint `evaluar-codigo` limitado a **5 req/min por estudiante** para evitar abuso del sandbox.

#### Dependencias Vulnerables (A06)

- Ejecutar `pip-audit -r requirements.txt` antes de cada deploy; bloquear build si hay CVEs de severidad alta.
- Fijar versiones exactas en `requirements.txt` en producción (evitar `>=`).

#### Checklist de Verificación de Seguridad

| Control | Herramienta / Comando | Estado esperado |
|---------|----------------------|-----------------|
| Rutas sin autenticación | `pytest tests/test_security.py` | 0 rutas sin proteger |
| SQL injection | Revisión manual ORM | Sin raw SQL concatenado |
| Prompt injection | Revisión de `chat_service.py` | Inputs saneados |
| Contraseñas en texto plano | `grep -r "password" backend/ --include="*.py"` | Solo `password_hash` |
| Secretos en código | `git secrets --scan` | Sin hallazgos |
| CVEs en dependencias | `pip-audit -r requirements.txt` | 0 CVEs altos/críticos |
| CORS wildcard | `grep allow_origins backend/main.py` | Sin `"*"` en producción |
| Rate limiting activo | `ab -n 20 -c 5 /api/auth/login` | 429 tras 10 req/min |

**Verificación:** `pytest tests/test_security.py` pasa sin fallos + `pip-audit` sin CVEs críticos + checklist OWASP completado.

---


### FASE 7 — Deploy en Render

**Objetivo:** Sistema productivo accesible en internet.

1. Cuenta Render + PostgreSQL addon (free tier: 1GB, 90 días)
2. `Dockerfile`:
   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```
3. `render.yaml` — 3 servicios: `api` (Docker), `frontend` (Streamlit), `db` (PostgreSQL)
4. Variables de entorno en Render: `DATABASE_URL`, `ANTHROPIC_API_KEY`, `SENDGRID_API_KEY`, `JWT_SECRET_KEY`, `FRONTEND_URL`, `API_URL`
5. Startup hook: `alembic upgrade head && python backend/scripts/seed.py`
6. CORS: `allow_origins=[os.getenv("FRONTEND_URL")]`
7. `pages/utils.py`: `API_URL = os.getenv("API_URL", "http://localhost:8000")`
8. Smoke tests E2E: registro → login → crear pregunta → chat → score → email → analíticas

**Verificación:** `https://andamiaje-api.onrender.com/api/health` → 200; flujo completo desde URL pública

---

## Módulos Existentes Reutilizados

| Archivo | Reutilizado en |
|---------|---------------|
| `src/claude_haiku.py` | `andamiaje_service`, `chat_service`, `scoring_service`, `analytics_service` |
| `src/evaluator.py` | `chat_service` (pytest + BLEU + Haiku score) |
| `src/reward_schema.py` | `scoring_service` (RubricaPedagogica) |
| `src/ab_generator.py` | `andamiaje_service` |
| `exercises/*/ejercicio_*.py` | `seed.py` (preguntas iniciales) |
| `pages/01–05` | Conservar como sección "Pipeline de Investigación" (admin/docente) |

---

## Variables de Entorno (.env)

```env
# Existente
ANTHROPIC_API_KEY=sk-ant-...

# Base de datos
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/andamiaje

# Auth
JWT_SECRET_KEY=cambia-esto-en-produccion
JWT_ALGORITHM=HS256
JWT_EXPIRE_HOURS=24

# SendGrid
SENDGRID_API_KEY=SG...
SENDGRID_FROM_EMAIL=noreply@tu-dominio.com
SENDGRID_FROM_NAME=Andamiaje Python

# URLs
API_URL=http://localhost:8000
FRONTEND_URL=http://localhost:8501
```

---

## Costo Estimado en Producción (Render)

| Servicio | Plan | Costo/mes |
|---------|------|----------|
| Render FastAPI (web service) | Free (spin-down 15min) | $0 |
| Render Streamlit (web service) | Free | $0 |
| PostgreSQL Render | Free 90d → Starter | $0 → $7 |
| SendGrid | Free (100 emails/día) | $0 |
| Claude Haiku (~2000 interacciones/mes) | $0.001/interacción | ~$2 |
| **Total** | | **~$2–9/mes** |

---

## Criterios de Éxito por Fase

| Fase | Criterio de Verificación |
|------|--------------------------|
| 1 | `GET /api/health` → 200 + tablas en BD |
| 2 | JWT válido en login; 401 sin token |
| 3 | Crear pregunta → 3 andamiajes en BD generados por Haiku |
| 4 | Código correcto → tests pasan + score guardado en BD |
| 5 | Score calculado correctamente + email en bandeja de entrada |
| 6 | Heatmap correcto + predicción ML 0–1 + insights Haiku coherentes + alerta email docente |
| 6.5 | `pytest tests/test_security.py` sin fallos + `pip-audit` sin CVEs críticos |
| 7 | URL pública Render responde + flujo E2E completo funciona |
