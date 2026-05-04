"""
pages/00_Login.py
Landing page con explicación de la app + formulario de login/registro.
"""

import streamlit as st
import httpx

from pages.utils import api_call, safe_detail, API_URL

# Si ya hay sesión válida, app.py redirige automáticamente
if st.session_state.get("token") and st.session_state.get("user"):
    st.rerun()

# ── Layout: dos columnas ──────────────────────────────────────────────────────
col_info, col_form = st.columns([1.1, 0.9], gap="large")

# ── Columna izquierda: landing / descripción ──────────────────────────────────
with col_info:
    st.markdown("## 🐍 Andamiaje Python")
    st.markdown(
        "**Plataforma adaptativa de aprendizaje de Python** guiada por inteligencia artificial. "
        "Cada estudiante recibe ejercicios y pistas personalizadas según su nivel y ritmo de avance."
    )

    st.divider()

    st.markdown("### ¿Cómo funciona?")
    st.markdown(
        """
1. **Selección inteligente de ejercicios** — El sistema elige preguntas basadas en tus temas más débiles.
2. **Chat socrático con IA** — En lugar de darte la respuesta, el tutor te hace preguntas para que llegues solo.
3. **Andamiaje progresivo** — Si te atascas recibes pistas graduales: conceptual → procedimental → concreto.
4. **Evaluación automática** — Tu código se ejecuta en un sandbox seguro y se puntúa con tests + IA.
5. **Ruta de aprendizaje personalizada** — Cada corte genera un plan con tus temas fuertes y débiles.
        """
    )

    st.divider()

    st.markdown("### Para quién es")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("#### 🎓 Estudiante")
        st.caption("Practica ejercicios Junior, Semi-senior y Senior con retroalimentación inmediata.")
    with c2:
        st.markdown("#### 📚 Docente")
        st.caption("Crea preguntas, revisa analíticas de grupo y detecta estudiantes en riesgo.")
    with c3:
        st.markdown("#### 🛠️ Admin")
        st.caption("Gestiona usuarios, cursos y supervisa toda la plataforma.")

    st.divider()
    st.caption("Desarrollado con FastAPI · Streamlit · Claude Haiku · PostgreSQL")

# ── Columna derecha: formulario ───────────────────────────────────────────────
with col_form:
    st.markdown("### Acceder a la plataforma")

    tab_login, tab_registro = st.tabs(["Iniciar sesión", "Crear cuenta"])

    # ── Login ─────────────────────────────────────────────────────────────────
    with tab_login:
        with st.form("form_login"):
            email    = st.text_input("Email", placeholder="usuario@correo.com")
            password = st.text_input("Contraseña", type="password")
            submitted = st.form_submit_button("Ingresar", use_container_width=True, type="primary")

        if submitted:
            if not email or not password:
                st.error("Completa todos los campos.")
            else:
                with st.spinner("Verificando..."):
                    try:
                        resp = api_call(
                            "POST", "/api/auth/login",
                            json={"email": email, "password": password},
                        )
                        if resp.status_code == 200:
                            token = resp.json()["access_token"]
                            # Obtener perfil usando el token recién emitido
                            me = httpx.get(
                                f"{API_URL}/api/auth/me",
                                headers={"Authorization": f"Bearer {token}"},
                                timeout=10,
                            )
                            user = me.json()
                            # Limpiar estado de sesión anterior
                            st.session_state.clear()
                            st.session_state["token"] = token
                            st.session_state["user"]  = user
                            st.rerun()
                        elif resp.status_code == 429:
                            st.error("Demasiados intentos. Espera un minuto.")
                        elif resp.status_code == 401:
                            st.error("Email o contraseña incorrectos.")
                        else:
                            st.error(f"Error: {safe_detail(resp)}")
                    except Exception as e:
                        st.error(f"No se pudo conectar con el servidor: {e}")

        st.divider()
        st.markdown(
            "**Credenciales de prueba:**\n\n"
            "- Estudiante: `sherrera@andamiaje.com` / `Estudiante1234!`\n"
            "- Docente: `cmendez@andamiaje.com` / `Docente1234!`\n"
            "- Admin: `admin@andamiaje.com` / `Admin1234!`"
        )

    # ── Registro ──────────────────────────────────────────────────────────────
    with tab_registro:
        with st.form("form_registro"):
            nombre     = st.text_input("Nombre completo")
            email_r    = st.text_input("Email", key="email_reg", placeholder="usuario@correo.com")
            rol_r      = st.selectbox(
                "Rol",
                options=["estudiante", "docente"],
                format_func=lambda x: "Estudiante" if x == "estudiante" else "Docente",
            )
            password_r  = st.text_input("Contraseña (mín. 8 caracteres)", type="password", key="pass_reg")
            password_r2 = st.text_input("Confirmar contraseña", type="password", key="pass_reg2")
            submitted_r = st.form_submit_button("Crear cuenta", use_container_width=True)

        if submitted_r:
            if not all([nombre, email_r, password_r, password_r2]):
                st.error("Completa todos los campos.")
            elif password_r != password_r2:
                st.error("Las contraseñas no coinciden.")
            elif len(password_r) < 8:
                st.error("La contraseña debe tener al menos 8 caracteres.")
            else:
                with st.spinner("Creando cuenta..."):
                    try:
                        resp = api_call(
                            "POST", "/api/auth/register",
                            json={
                                "nombre_completo": nombre,
                                "email": email_r,
                                "password": password_r,
                                "rol": rol_r,
                            },
                        )
                        if resp.status_code == 201:
                            st.success("✅ Cuenta creada. Ya puedes iniciar sesión.")
                        elif resp.status_code == 409:
                            st.error("Ese email ya está registrado.")
                        elif resp.status_code == 429:
                            st.error("Demasiados intentos. Espera un minuto.")
                        else:
                            st.error(f"Error: {safe_detail(resp)}")
                    except Exception as e:
                        st.error(f"No se pudo conectar con el servidor: {e}")
