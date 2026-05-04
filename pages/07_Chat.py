"""
pages/07_Chat.py
Chat adaptativo con andamiaje para estudiantes.
"""

import streamlit as st

from pages.utils import api_call, require_auth, safe_detail

user = require_auth(["estudiante"])
if not user:
    st.stop()

st.title("💬 Chat Adaptativo de Python")

# ── Inicializar estado ────────────────────────────────────────────────────────
if "sesion_id" not in st.session_state:
    st.session_state.sesion_id = None
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
if "pregunta_actual" not in st.session_state:
    st.session_state.pregunta_actual = None
if "andamiaje_actual" not in st.session_state:
    st.session_state.andamiaje_actual = ""
if "nivel_andamiaje" not in st.session_state:
    st.session_state.nivel_andamiaje = "minimo"
if "sesion_completada" not in st.session_state:
    st.session_state.sesion_completada = False

# ── Sidebar: iniciar sesión ───────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Configuración")
    corte = st.selectbox("Corte académico", [1, 2, 3])

    if st.button("🚀 Iniciar nueva sesión", type="primary", use_container_width=True):
        with st.spinner("Seleccionando ejercicio..."):
            resp = api_call("POST", "/api/chat/iniciar", json={"corte": corte})
        if resp.status_code == 200:
            data = resp.json()
            st.session_state.sesion_id = data["sesion_id"]
            st.session_state.pregunta_actual = {
                "id": data["pregunta_id"],
                "titulo": data["titulo"],
                "enunciado": data["enunciado"],
            }
            st.session_state.andamiaje_actual = data["andamiaje"]
            st.session_state.nivel_andamiaje = data["nivel_andamiaje_actual"]
            st.session_state.sesion_completada = False
            st.session_state.chat_messages = [
                {"rol": "assistant", "contenido": data["mensaje_bienvenida"]}
            ]
            st.rerun()
        elif resp.status_code == 404:
            st.success("🎉 ¡Completaste todos los ejercicios disponibles para este corte!")
        else:
            st.error(f"Error: {safe_detail(resp)}")

    if st.session_state.sesion_id:
        st.divider()
        st.caption(f"Sesión #{st.session_state.sesion_id}")
        if st.button("🔄 Nueva sesión", use_container_width=True):
            for key in ["sesion_id", "chat_messages", "pregunta_actual", "andamiaje_actual", "nivel_andamiaje", "sesion_completada"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

# ── Área principal ────────────────────────────────────────────────────────────
if not st.session_state.sesion_id:
    st.info("👈 Inicia una nueva sesión en el panel lateral para comenzar a practicar.")
    st.stop()

col_chat, col_panel = st.columns([2, 1])

with col_chat:
    # Mostrar ejercicio
    pregunta = st.session_state.pregunta_actual
    with st.container(border=True):
        st.markdown(f"**📝 {pregunta['titulo']}**")
        st.write(pregunta["enunciado"])

    # Historial de chat
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["rol"]):
            st.write(msg["contenido"])

    # Input de chat
    if not st.session_state.sesion_completada:
        if prompt := st.chat_input("Escribe tu pregunta o reflexión sobre el ejercicio..."):
            # Mostrar mensaje usuario
            st.session_state.chat_messages.append({"rol": "user", "contenido": prompt})
            with st.chat_message("user"):
                st.write(prompt)

            # Obtener respuesta del tutor
            with st.spinner("El tutor está pensando..."):
                resp = api_call("POST", "/api/chat/mensaje", json={
                    "sesion_id": st.session_state.sesion_id,
                    "contenido": prompt,
                })

            if resp.status_code == 200:
                data = resp.json()
                st.session_state.chat_messages.append({"rol": "assistant", "contenido": data["contenido"]})
                st.session_state.nivel_andamiaje = data.get("nivel_andamiaje_actual", "minimo")
                with st.chat_message("assistant"):
                    st.write(data["contenido"])
            else:
                st.error("Error al obtener respuesta del tutor.")
    else:
        st.success("🎉 ¡Sesión completada! Iniciá una nueva sesión para continuar practicando.")

    # ── Editor de código ──────────────────────────────────────────────────────
    if not st.session_state.sesion_completada:
        st.divider()
        st.subheader("💻 Tu solución")
        codigo = st.text_area(
            "Escribe tu código aquí:",
            height=200,
            placeholder="def mi_funcion(...):\n    # Tu solución aquí\n    pass",
            key="codigo_editor",
        )
        if st.button("▶️ Evaluar código", type="primary"):
            if not codigo.strip():
                st.warning("Escribe algo de código antes de evaluar.")
            else:
                with st.spinner("Evaluando..."):
                    resp_eval = api_call("POST", "/api/chat/evaluar-codigo", json={
                        "sesion_id": st.session_state.sesion_id,
                        "codigo": codigo,
                    })

                if resp_eval.status_code == 200:
                    ev = resp_eval.json()
                    col_r1, col_r2, col_r3 = st.columns(3)
                    col_r1.metric("Tests", "✅ OK" if ev["passed_tests"] else "❌ Falla")
                    col_r2.metric("Score parcial", f"{ev['score_parcial']:.0%}")
                    col_r3.metric("Intentos", ev["intentos"])

                    with st.container(border=True):
                        st.write(ev["feedback"])

                    st.session_state.nivel_andamiaje = ev.get("nivel_andamiaje_actual", "minimo")
                    if ev.get("andamiaje_actualizado"):
                        st.session_state.andamiaje_actual = ev["andamiaje_actualizado"]

                    if ev.get("sesion_completada"):
                        st.session_state.sesion_completada = True
                        st.balloons()
                        st.rerun()
                elif resp_eval.status_code == 429:
                    st.warning("Demasiadas evaluaciones. Espera un minuto.")
                else:
                    st.error(f"Error: {safe_detail(resp_eval, 'Error en evaluación')}")

with col_panel:
    st.subheader("🏗️ Andamiaje")
    nivel_labels = {"minimo": "🟢 Mínimo", "parcial": "🟡 Parcial", "completo": "🔴 Completo"}
    st.caption(f"Nivel actual: **{nivel_labels.get(st.session_state.nivel_andamiaje, '')}**")
    with st.container(border=True):
        st.write(st.session_state.andamiaje_actual or "El andamiaje aparecerá aquí según tu progreso.")

    st.divider()
    st.caption("El andamiaje aumenta automáticamente si necesitas más ayuda.")
