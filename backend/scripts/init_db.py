"""
backend/scripts/init_db.py
Crea todas las tablas usando un engine síncrono (psycopg2) + registra alembic_version.

Uso: python -m backend.scripts.init_db
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from sqlalchemy import create_engine, text

from backend.core.config import settings

# Convertir URL asyncpg → psycopg2
SYNC_URL = settings.DATABASE_URL.replace(
    "postgresql+asyncpg://", "postgresql+psycopg2://"
)

# Importar todos los modelos para registrar la metadata
import backend.models  # noqa: F401
from backend.core.database import Base


def main() -> None:
    engine = create_engine(SYNC_URL, echo=True)

    with engine.begin() as conn:
        # Crear todas las tablas (y los ENUMs como parte de los tipos de columna)
        Base.metadata.create_all(conn)

        # Registrar la versión de Alembic para que alembic sepa que ya está aplicada
        conn.execute(text("CREATE TABLE IF NOT EXISTS alembic_version (version_num VARCHAR(32) NOT NULL PRIMARY KEY)"))
        exists = conn.execute(text("SELECT 1 FROM alembic_version WHERE version_num = '001_init'")).fetchone()
        if not exists:
            conn.execute(text("INSERT INTO alembic_version (version_num) VALUES ('001_init')"))
            print("[OK] alembic_version marcada como 001_init")
        else:
            print("[OK] alembic_version ya estaba en 001_init")

    print("[OK] Schema creado exitosamente.")
    engine.dispose()


if __name__ == "__main__":
    main()
