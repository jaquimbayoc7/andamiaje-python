"""
pages/08_MiProgreso.py
Progreso del estudiante — evaluaciones, ruta de aprendizaje y radar chart.
"""

import plotly.graph_objects as go
import streamlit as st

from pages.utils import api_call, require_auth, safe_detail

user = require_auth(["estudiante"])
if not user:
    st.stop()

st.title("📈 Mi Progreso")
st.caption(f"Hola, **{user.get('nombre_completo', '')}**")

# ── Cargar evaluaciones ───────────────────────────────────────────────────────
resp = api_call("GET", "/api/evaluaciones/mis-evaluaciones")
evaluaciones = resp.json() if resp.status_code == 200 else []

# ── Sidebar: calcular evaluación ──────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Acciones")
    corte_calc = st.selectbox("Corte a calcular", [1, 2, 3])
    if st.button("🧮 Calcular mi evaluación", type="primary", use_container_width=True):
        with st.spinner("Calculando score y ruta de aprendizaje..."):
            resp_calc = api_call("POST", f"/api/evaluaciones/calcular/{corte_calc}")
        if resp_calc.status_code == 200:
            data_calc = resp_calc.json()
            if data_calc.get("enviada_email"):
                st.success("✅ Evaluación calculada. Se envió tu ruta de aprendizaje por email.")
            else:
                st.success("✅ Evaluación calculada.")
            st.rerun()
        else:
            st.error(f"Error: {safe_detail(resp_calc, 'Error')}")

    if evaluaciones:
        st.divider()
        ev_opts = {f"Corte {ev['corte']} — {ev['score_global']:.0%}": ev["id"] for ev in evaluaciones}
        sel_ev_label = st.selectbox("Enviar email de:", list(ev_opts.keys()))
        sel_ev_id = ev_opts.get(sel_ev_label)
        if st.button("📧 Enviar por email", use_container_width=True):
            with st.spinner("Enviando..."):
                resp_email = api_call("POST", f"/api/evaluaciones/enviar-email/{sel_ev_id}")
            data = resp_email.json()
            if data.get("enviado"):
                st.success(data.get("mensaje", "Email enviado."))
            else:
                st.warning(data.get("mensaje", "No se pudo enviar."))

# ── Métricas por corte ────────────────────────────────────────────────────────
if not evaluaciones:
    st.info("Aún no tienes evaluaciones calculadas. Completa sesiones de chat y luego calcula tu evaluación desde el panel lateral.")
    st.stop()

col1, col2, col3 = st.columns(3)
cols = [col1, col2, col3]

for ev in evaluaciones[:3]:
    with cols[ev["corte"] - 1]:
        score = ev["score_global"]
        color = "green" if score >= 0.7 else "orange" if score >= 0.5 else "red"
        st.metric(
            label=f"Corte {ev['corte']}",
            value=f"{score:.0%}",
            delta="✅ Aprobado" if score >= 0.6 else "⚠️ En riesgo",
        )
        if ev.get("enviada_email"):
            st.caption("📧 Email enviado")

# ── Radar chart ───────────────────────────────────────────────────────────────
ev_mas_reciente = max(evaluaciones, key=lambda e: e["corte"])
ruta = ev_mas_reciente.get("ruta_aprendizaje") or {}

temas_fuertes = ruta.get("temas_fuertes", [])
temas_reforzar = ruta.get("temas_a_reforzar", [])
todos_temas = list(set(temas_fuertes + temas_reforzar)) or ["variables", "listas", "funciones", "decoradores", "dataframes"]

scores_radar = [
    0.85 if t in temas_fuertes else 0.4 if t in temas_reforzar else 0.6
    for t in todos_temas
]

fig_radar = go.Figure(data=go.Scatterpolar(
    r=scores_radar + [scores_radar[0]],
    theta=todos_temas + [todos_temas[0]],
    fill="toself",
    name="Mi desempeño",
    line_color="#3498db",
))
fig_radar.update_layout(
    polar={"radialaxis": {"visible": True, "range": [0, 1]}},
    title=f"Radar de Competencias — Corte {ev_mas_reciente['corte']}",
    height=400,
)
st.plotly_chart(fig_radar, use_container_width=True)

# ── Ruta de aprendizaje ───────────────────────────────────────────────────────
st.subheader("🗺️ Tu Ruta de Aprendizaje")

if ruta.get("mensaje_motivacional"):
    st.success(ruta["mensaje_motivacional"])

col_f, col_r = st.columns(2)

with col_f:
    if temas_fuertes:
        st.markdown("### ✅ Temas Fuertes")
        for t in temas_fuertes:
            st.markdown(f"- **{t}**")

with col_r:
    if temas_reforzar:
        st.markdown("### 📚 Temas a Reforzar")
        for t in temas_reforzar:
            st.markdown(f"- **{t}**")

# Ejercicios recomendados
if ruta.get("ejercicios_recomendados"):
    st.markdown("### 🎯 Ejercicios Recomendados")
    for ej in ruta["ejercicios_recomendados"]:
        if not isinstance(ej, dict):
            st.markdown(f"- {ej}")
            continue
        with st.container(border=True):
            st.markdown(f"**{ej.get('titulo', 'Ejercicio')}**")
            st.caption(ej.get("razon", ""))

# Recursos externos
if ruta.get("recursos_externos"):
    st.markdown("### 🔗 Recursos Externos")
    for rec in ruta["recursos_externos"]:
        if not isinstance(rec, dict):
            st.markdown(f"- {rec}")
            continue
        tipo = rec.get("tipo", "recurso")
        icono = "🎥" if tipo == "video" else "📖" if tipo == "docs" else "💻"
        st.markdown(f"{icono} [{rec.get('titulo', 'Recurso')}]({rec.get('url', '#')}) — *{tipo}*")
