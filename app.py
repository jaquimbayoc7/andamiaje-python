"""
app.py — Entry point con navegación adaptativa por rol.
Ejecutar: streamlit run app.py
"""

import streamlit as st

st.set_page_config(
    page_title="Andamiaje Python",
    page_icon="🐍",
    layout="wide",
    initial_sidebar_state="expanded",
)

user = st.session_state.get("user")

# Invalidar sesión si el user guardado está incompleto (datos de sesión antigua)
if user and "rol" not in user:
    st.session_state.clear()
    user = None

rol = user.get("rol") if user else None

# ── Páginas disponibles ───────────────────────────────────────────────────────
login    = st.Page("pages/00_Login.py", title="Iniciar sesión",  icon="🔐")
chat     = st.Page("pages/07_Chat.py",  title="Chat Adaptativo", icon="💬")
progreso = st.Page("pages/08_MiProgreso.py", title="Mi Progreso", icon="📈")
docente  = st.Page("pages/06_Docente.py",    title="Panel Docente", icon="📚")
admin    = st.Page("pages/09_Admin.py",      title="Administración", icon="🛠️")

if rol == "estudiante":
    pages = {"Aprendizaje": [chat, progreso]}
elif rol == "docente":
    pages = {"Docente": [docente]}
elif rol == "admin":
    pages = {"Admin": [admin]}
else:
    pages = {"": [login]}

# ── Sidebar: info de usuario y logout ────────────────────────────────────────
if user:
    with st.sidebar:
        st.markdown(f"**{user.get('nombre_completo', user.get('email', 'Usuario'))}**")
        st.caption(f"Rol: {rol.capitalize()}")
        st.divider()
        if st.button("Cerrar sesión", use_container_width=True, type="secondary"):
            st.session_state.clear()
            st.rerun()
        st.divider()

pg = st.navigation(pages)
pg.run()
