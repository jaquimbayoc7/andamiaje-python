"""init

Revision ID: 001_init
Revises: 
Create Date: 2026-05-04

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001_init"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── ENUMS (DO block = idempotent, compatible con asyncpg) ────────────────
    op.execute(
        "DO $$ BEGIN "
        "CREATE TYPE rolusuario AS ENUM ('admin', 'docente', 'estudiante'); "
        "EXCEPTION WHEN duplicate_object THEN null; END $$"
    )
    op.execute(
        "DO $$ BEGIN "
        "CREATE TYPE nivelpregunta AS ENUM ('junior', 'semi_senior', 'senior'); "
        "EXCEPTION WHEN duplicate_object THEN null; END $$"
    )
    op.execute(
        "DO $$ BEGIN "
        "CREATE TYPE nivelandamiaje AS ENUM ('minimo', 'parcial', 'completo'); "
        "EXCEPTION WHEN duplicate_object THEN null; END $$"
    )
    op.execute(
        "DO $$ BEGIN "
        "CREATE TYPE rolmensaje AS ENUM ('user', 'assistant'); "
        "EXCEPTION WHEN duplicate_object THEN null; END $$"
    )

    # ── TABLAS ───────────────────────────────────────────────────────────────
    op.create_table(
        "usuarios",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nombre_completo", sa.String(150), nullable=False),
        sa.Column("email", sa.String(254), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("rol", sa.Enum("admin", "docente", "estudiante", name="rolusuario"), nullable=False),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_usuarios_email", "usuarios", ["email"], unique=True)
    op.create_index("ix_usuarios_id", "usuarios", ["id"])

    op.create_table(
        "cursos",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nombre", sa.String(200), nullable=False),
        sa.Column("docente_id", sa.Integer(), sa.ForeignKey("usuarios.id"), nullable=False),
        sa.Column("periodo", sa.String(20), nullable=False),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default="true"),
    )
    op.create_index("ix_cursos_id", "cursos", ["id"])

    op.create_table(
        "preguntas",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("titulo", sa.String(300), nullable=False),
        sa.Column("enunciado", sa.Text(), nullable=False),
        sa.Column("solucion_referencia", sa.Text(), nullable=False),
        sa.Column("nivel", sa.Enum("junior", "semi_senior", "senior", name="nivelpregunta"), nullable=False),
        sa.Column("tema", sa.String(100), nullable=False),
        sa.Column("docente_id", sa.Integer(), sa.ForeignKey("usuarios.id"), nullable=True),
        sa.Column("activa", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_preguntas_id", "preguntas", ["id"])

    op.create_table(
        "andamiajes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("pregunta_id", sa.Integer(), sa.ForeignKey("preguntas.id"), nullable=False),
        sa.Column("nivel_andamiaje", sa.Enum("minimo", "parcial", "completo", name="nivelandamiaje"), nullable=False),
        sa.Column("contenido", sa.Text(), nullable=False),
    )
    op.create_index("ix_andamiajes_id", "andamiajes", ["id"])

    op.create_table(
        "estudiantes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("usuario_id", sa.Integer(), sa.ForeignKey("usuarios.id"), nullable=False, unique=True),
        sa.Column("semestre", sa.Integer(), nullable=False),
        sa.Column("programa_academico", sa.String(200), nullable=False),
        sa.Column("curso_id", sa.Integer(), sa.ForeignKey("cursos.id"), nullable=True),
    )
    op.create_index("ix_estudiantes_id", "estudiantes", ["id"])

    op.create_table(
        "sesiones_chat",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("estudiante_id", sa.Integer(), sa.ForeignKey("estudiantes.id"), nullable=False),
        sa.Column("pregunta_id", sa.Integer(), sa.ForeignKey("preguntas.id"), nullable=False),
        sa.Column("corte", sa.Integer(), nullable=False),
        sa.Column("score_final", sa.Float(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_sesiones_chat_id", "sesiones_chat", ["id"])

    op.create_table(
        "mensajes_chat",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("sesion_id", sa.Integer(), sa.ForeignKey("sesiones_chat.id"), nullable=False),
        sa.Column("rol", sa.Enum("user", "assistant", name="rolmensaje"), nullable=False),
        sa.Column("contenido", sa.Text(), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_mensajes_chat_id", "mensajes_chat", ["id"])

    op.create_table(
        "respuestas_estudiante",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("sesion_id", sa.Integer(), sa.ForeignKey("sesiones_chat.id"), nullable=False),
        sa.Column("pregunta_id", sa.Integer(), sa.ForeignKey("preguntas.id"), nullable=False),
        sa.Column("codigo_enviado", sa.Text(), nullable=False),
        sa.Column("passed_tests", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("bleu_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("haiku_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("intentos", sa.Integer(), nullable=False, server_default="1"),
    )
    op.create_index("ix_respuestas_estudiante_id", "respuestas_estudiante", ["id"])

    op.create_table(
        "evaluaciones",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("estudiante_id", sa.Integer(), sa.ForeignKey("estudiantes.id"), nullable=False),
        sa.Column("corte", sa.Integer(), nullable=False),
        sa.Column("curso_id", sa.Integer(), sa.ForeignKey("cursos.id"), nullable=False),
        sa.Column("score_global", sa.Float(), nullable=False, server_default="0"),
        sa.Column("ruta_aprendizaje", postgresql.JSONB(), nullable=True),
        sa.Column("enviada_email", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_evaluaciones_id", "evaluaciones", ["id"])

    op.create_table(
        "predicciones_riesgo",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("estudiante_id", sa.Integer(), sa.ForeignKey("estudiantes.id"), nullable=False),
        sa.Column("corte", sa.Integer(), nullable=False),
        sa.Column("curso_id", sa.Integer(), sa.ForeignKey("cursos.id"), nullable=False),
        sa.Column("score_riesgo", sa.Float(), nullable=False, server_default="0"),
        sa.Column("en_riesgo", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("temas_debiles", postgresql.JSONB(), nullable=True),
        sa.Column("notificado_docente", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_predicciones_riesgo_id", "predicciones_riesgo", ["id"])


def downgrade() -> None:
    op.drop_table("predicciones_riesgo")
    op.drop_table("evaluaciones")
    op.drop_table("respuestas_estudiante")
    op.drop_table("mensajes_chat")
    op.drop_table("sesiones_chat")
    op.drop_table("estudiantes")
    op.drop_table("andamiajes")
    op.drop_table("preguntas")
    op.drop_table("cursos")
    op.drop_table("usuarios")

    op.execute("DROP TYPE IF EXISTS rolmensaje")
    op.execute("DROP TYPE IF EXISTS nivelandamiaje")
    op.execute("DROP TYPE IF EXISTS nivelpregunta")
    op.execute("DROP TYPE IF EXISTS rolusuario")
