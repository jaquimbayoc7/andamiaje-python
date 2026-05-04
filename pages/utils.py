"""
pages/utils.py
Helper centralizado para llamadas a la API desde Streamlit.
"""

import os
from typing import Any

import httpx
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000")


def _auth_headers() -> dict:
    token = st.session_state.get("token", "")
    return {"Authorization": f"Bearer {token}"} if token else {}


def api_call(
    method: str,
    path: str,
    *,
    json: Any = None,
    data: Any = None,
    files: Any = None,
    timeout: float = 30.0,
) -> httpx.Response:
    """
    Realiza una llamada HTTP a la API con el token JWT del session_state.
    Lanza httpx.HTTPStatusError si la respuesta es 4xx/5xx.
    """
    url = f"{API_URL}{path}"
    headers = _auth_headers()
    with httpx.Client(timeout=timeout) as client:
        response = client.request(
            method.upper(),
            url,
            json=json,
            data=data,
            files=files,
            headers=headers,
        )
    return response


def require_auth(allowed_roles: list[str] | None = None) -> dict | None:
    """
    Verifica que el usuario esté autenticado y tenga el rol correcto.
    Si no, muestra un aviso y retorna None.
    Uso: user = require_auth(["admin", "docente"]); if not user: st.stop()
    """
    token = st.session_state.get("token")
    if not token:
        st.warning("Debes iniciar sesión para acceder a esta página.")
        st.page_link("pages/00_Login.py", label="Ir al login")
        return None

    user = st.session_state.get("user")
    if not user:
        try:
            resp = api_call("GET", "/api/auth/me")
            resp.raise_for_status()
            user = resp.json()
            st.session_state["user"] = user
        except Exception:
            st.session_state.pop("token", None)
            st.warning("Sesión expirada. Inicia sesión de nuevo.")
            st.page_link("pages/00_Login.py", label="Ir al login")
            return None

    if allowed_roles and user.get("rol") not in allowed_roles:
        st.error(f"Acceso denegado. Roles permitidos: {', '.join(allowed_roles)}")
        return None

    return user


def safe_detail(resp, fallback: str = "Error desconocido") -> str:
    """Extrae 'detail' del body JSON sin explotar si el body está vacío o no es JSON."""
    try:
        return resp.json().get("detail", fallback)
    except Exception:
        return fallback


def safe_json_key(resp, key: str, fallback: str = "") -> str:
    """Extrae una clave arbitraria del body JSON de forma segura."""
    try:
        return resp.json().get(key, fallback)
    except Exception:
        return fallback
