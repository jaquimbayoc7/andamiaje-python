"""
pages/06_Docente.py
Panel del docente — 3 tabs: Preguntas, Analíticas, Predicciones y Alertas.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from pages.utils import api_call, require_auth, safe_detail, safe_json_key


user = require_auth(["docente", "admin"])
if not user:
    st.stop()

st.title("👨‍🏫 Panel del Docente")

tab1, tab2, tab3, tab4 = st.tabs(["📝 Gestión de Preguntas", "📊 Analíticas del Curso", "⚠️ Predicciones y Alertas", "👥 Mis Estudiantes"])

# ── Tab 1: Gestión de Preguntas ───────────────────────────────────────────────
with tab1:
    st.subheader("Mis Preguntas")

    col1, col2 = st.columns([3, 1])
    with col2:
        nivel_filtro = st.selectbox("Filtrar por nivel", ["Todos", "junior", "semi_senior", "senior"])
        solo_activas = st.checkbox("Solo activas", value=True)

    resp_preguntas = api_call("GET", "/api/preguntas/")
    if resp_preguntas.status_code == 200:
        preguntas = resp_preguntas.json()
        if nivel_filtro != "Todos":
            preguntas = [p for p in preguntas if p["nivel"] == nivel_filtro]
        if solo_activas:
            preguntas = [p for p in preguntas if p["activa"]]

        if preguntas:
            df_preguntas = pd.DataFrame(preguntas)[["id", "titulo", "nivel", "tema", "activa"]]
            df_preguntas.columns = ["ID", "Título", "Nivel", "Tema", "Activa"]
            st.dataframe(df_preguntas, use_container_width=True, hide_index=True)
        else:
            st.info("No hay preguntas registradas aún.")
    else:
        st.warning("No se pudieron cargar las preguntas.")

    st.divider()

    with st.expander("➕ Crear nueva pregunta"):
        with st.form("form_crear_pregunta"):
            titulo = st.text_input("Título *")
            enunciado = st.text_area("Enunciado *", height=120)
            col_a, col_b = st.columns(2)
            with col_a:
                nivel = st.selectbox("Nivel *", ["junior", "semi_senior", "senior"])
            with col_b:
                tema = st.text_input("Tema *", placeholder="ej: variables, listas, decoradores")
            solucion = st.text_area("Solución de referencia *", height=120)
            submitted = st.form_submit_button("Crear Pregunta", type="primary")

        if submitted:
            if not all([titulo, enunciado, nivel, tema, solucion]):
                st.error("Completa todos los campos obligatorios.")
            else:
                with st.spinner("Creando pregunta y generando andamiajes..."):
                    resp = api_call("POST", "/api/preguntas/", json={
                        "titulo": titulo,
                        "enunciado": enunciado,
                        "solucion_referencia": solucion,
                        "nivel": nivel,
                        "tema": tema,
                    })
                if resp.status_code == 201:
                    data = resp.json()
                    st.success(f"✅ Pregunta #{data['id']} creada con {len(data.get('andamiajes', []))} andamiajes.")
                    st.rerun()
                else:
                    st.error(f"Error: {safe_detail(resp)}")

    with st.expander("📤 Importar desde CSV"):
        st.caption("Columnas requeridas: `titulo,enunciado,solucion_referencia,nivel,tema`")
        archivo = st.file_uploader("Selecciona el CSV", type=["csv"])
        gen_csv = st.checkbox("Generar andamiajes para cada pregunta importada", value=True)
        if archivo and st.button("Importar"):
            with st.spinner("Importando..."):
                resp = api_call(
                    "POST",
                    f"/api/preguntas/importar-csv?generar_andamiaje={str(gen_csv).lower()}",
                    files={"archivo": (archivo.name, archivo.getvalue(), "text/csv")},
                )
            if resp.status_code == 200:
                res = resp.json()
                st.success(f"✅ {res['creadas']} preguntas importadas.")
                if res.get("errores"):
                    st.warning("Errores:\n" + "\n".join(res["errores"]))
            else:
                st.error("Error en importación.")

    with st.expander("🔍 Ver andamiajes de una pregunta"):
        pid = st.number_input("ID de la pregunta", min_value=1, step=1)
        if st.button("Cargar andamiajes"):
            resp = api_call("GET", f"/api/preguntas/{int(pid)}")
            if resp.status_code == 200:
                p = resp.json()
                st.markdown(f"**{p['titulo']}** — {p['nivel']} — {p['tema']}")
                for a in p.get("andamiajes", []):
                    with st.container(border=True):
                        st.markdown(f"**Nivel {a['nivel_andamiaje'].upper()}**")
                        st.write(a["contenido"])
            else:
                st.warning("Pregunta no encontrada.")

# ── Tab 2: Analíticas del Curso ───────────────────────────────────────────────
with tab2:
    st.subheader("Analíticas del Curso")

    resp_cursos = api_call("GET", "/api/admin/cursos")
    cursos_list = resp_cursos.json() if resp_cursos.status_code == 200 else []
    curso_opciones = {c["nombre"]: c["id"] for c in cursos_list}

    curso_sel_nombre = st.selectbox(
        "Seleccionar curso", list(curso_opciones.keys()) if curso_opciones else ["Sin cursos"],
    )
    curso_sel_id = curso_opciones.get(curso_sel_nombre)

    if st.button("🔄 Cargar analíticas"):
        col_h, col_d = st.columns(2)
        params = f"?curso_id={curso_sel_id}" if curso_sel_id else ""

        resp_hm = api_call("GET", f"/api/analiticas/heatmap{params}")
        if resp_hm.status_code == 200:
            hm_data = resp_hm.json()
            if hm_data:
                temas = list(hm_data.keys())
                niveles_hm = ["junior", "semi_senior", "senior"]
                matrix = [
                    [hm_data.get(tema, {}).get(nivel, {}).get("score_promedio", 0) for nivel in niveles_hm]
                    for tema in temas
                ]
                fig_hm = go.Figure(data=go.Heatmap(
                    z=matrix, x=niveles_hm, y=temas, colorscale="RdYlGn", zmin=0, zmax=1,
                    text=[[f"{v:.0%}" for v in row] for row in matrix], texttemplate="%{text}",
                ))
                fig_hm.update_layout(title="Heatmap: Score promedio por Tema × Nivel", height=400)
                with col_h:
                    st.plotly_chart(fig_hm, use_container_width=True)
            else:
                with col_h:
                    st.info("No hay datos de sesiones para este curso aún.")

        resp_dist = api_call("GET", f"/api/analiticas/distribucion-scores{params}")
        if resp_dist.status_code == 200:
            dist_data = resp_dist.json()
            cortes_data = [
                {"Corte": f"Corte {corte}", "Score": score}
                for corte, info in dist_data.items()
                for score in info.get("scores", [])
            ]
            if cortes_data:
                fig_dist = px.box(pd.DataFrame(cortes_data), x="Corte", y="Score",
                                  title="Distribución de Scores por Corte", color="Corte", range_y=[0, 1])
                with col_d:
                    st.plotly_chart(fig_dist, use_container_width=True)

        resp_temas = api_call("GET", f"/api/analiticas/temas-debiles{params}&top_n=5")
        temas_data = resp_temas.json() if resp_temas.status_code == 200 else []
        if temas_data:
            fig_temas = px.bar(
                pd.DataFrame(temas_data), x="score_promedio", y="tema", orientation="h",
                title="Top 5 Temas más Débiles", color="score_promedio",
                color_continuous_scale="RdYlGn", range_color=[0, 1],
            )
            st.plotly_chart(fig_temas, use_container_width=True)

            st.subheader("💡 Insight del Grupo")
            resumen = {
                "temas_debiles": [t["tema"] for t in temas_data[:3]],
                "score_promedio": round(sum(t["score_promedio"] for t in temas_data) / len(temas_data), 3),
            }
            resp_insight = api_call("POST", "/api/analiticas/insights", json=resumen)
            if resp_insight.status_code == 200:
                st.info(safe_json_key(resp_insight, "insight", "Sin insight disponible."))

# ── Tab 3: Predicciones y Alertas ─────────────────────────────────────────────
with tab3:
    st.subheader("Estudiantes en Riesgo")

    corte_pred = st.selectbox("Corte", [1, 2, 3], key="corte_pred")
    resp_cursos2 = api_call("GET", "/api/admin/cursos")
    cursos2 = resp_cursos2.json() if resp_cursos2.status_code == 200 else []
    curso_map2 = {c["nombre"]: c["id"] for c in cursos2}
    curso_pred = st.selectbox("Curso", list(curso_map2.keys()) if curso_map2 else ["Sin cursos"], key="curso_pred")
    curso_pred_id = curso_map2.get(curso_pred)

    params_pred = f"?corte={corte_pred}" + (f"&curso_id={curso_pred_id}" if curso_pred_id else "")

    if st.button("🔍 Cargar predicciones"):
        resp_pred = api_call("GET", f"/api/analiticas/predicciones/riesgo{params_pred}")
        if resp_pred.status_code == 200:
            pred_data = resp_pred.json()
            if pred_data:
                df_pred = pd.DataFrame(pred_data)
                df_pred["Riesgo"] = df_pred["score_riesgo"].map(lambda x: f"{x:.0%}")
                st.dataframe(
                    df_pred[["estudiante_id", "Riesgo", "notificado_docente"]].rename(
                        columns={"estudiante_id": "Estudiante ID", "notificado_docente": "Notificado"}
                    ),
                    use_container_width=True, hide_index=True,
                )
                for _, row in df_pred.iterrows():
                    if not row.get("notificado_docente"):
                        if st.button(f"📧 Notificar — Estudiante #{row['estudiante_id']}", key=f"notif_{row['prediccion_id']}"):
                            resp_n = api_call("POST", f"/api/admin/alertas/notificar/{row['prediccion_id']}")
                            if resp_n.status_code == 200:
                                st.success("Notificación enviada al docente.")
                            else:
                                st.error("Error al enviar notificación.")
            else:
                st.success("✅ No hay estudiantes en riesgo para este corte/curso.")

# ── Tab 4: Mis Estudiantes ─────────────────────────────────────────────────────
with tab4:
    st.subheader("Gestión de Estudiantes")

    # Cargar cursos del docente y todos los estudiantes visibles
    resp_cursos_d = api_call("GET", "/api/admin/cursos")
    mis_cursos = resp_cursos_d.json() if resp_cursos_d.status_code == 200 else []
    curso_map_d = {c["nombre"]: c["id"] for c in mis_cursos}

    resp_est = api_call("GET", "/api/admin/estudiantes")
    estudiantes = resp_est.json() if resp_est.status_code == 200 else []

    if not estudiantes:
        st.info("No hay estudiantes disponibles. Los estudiantes aparecen aquí una vez que inician su primera sesión de chat.")
    else:
        # Separar en asignados y sin curso
        sin_curso = [e for e in estudiantes if e["curso_id"] is None]
        con_curso = [e for e in estudiantes if e["curso_id"] is not None]

        # Tabla general
        df_est = pd.DataFrame(estudiantes)[[
            "nombre_completo", "email", "semestre", "programa_academico", "curso_nombre", "usuario_id"
        ]].rename(columns={
            "nombre_completo": "Nombre",
            "email": "Email",
            "semestre": "Semestre",
            "programa_academico": "Programa",
            "curso_nombre": "Curso",
            "usuario_id": "ID Usuario",
        })
        st.dataframe(df_est, use_container_width=True, hide_index=True)

        st.divider()

        # Panel de asignación
        col_izq, col_der = st.columns([1, 1])

        with col_izq:
            st.markdown("#### ➕ Asignar estudiante a curso")
            if not mis_cursos:
                st.warning("No tienes cursos asignados.")
            else:
                opciones_est = {
                    f"{e['nombre_completo']} ({e['email']})": e["usuario_id"]
                    for e in estudiantes
                }
                est_sel_label = st.selectbox("Estudiante", list(opciones_est.keys()), key="est_sel")
                est_sel_uid = opciones_est.get(est_sel_label)

                curso_asignar_label = st.selectbox("Curso destino", list(curso_map_d.keys()), key="curso_asignar")
                curso_asignar_id = curso_map_d.get(curso_asignar_label)

                if st.button("✅ Asignar", type="primary", use_container_width=True):
                    with st.spinner("Asignando..."):
                        resp_asignar = api_call(
                            "POST",
                            f"/api/admin/usuarios/{est_sel_uid}/asignar-curso",
                            json={"curso_id": curso_asignar_id},
                        )
                    if resp_asignar.status_code == 200:
                        st.success(f"✅ Estudiante asignado a **{curso_asignar_label}**.")
                        st.rerun()
                    else:
                        st.error(f"Error: {safe_detail(resp_asignar)}")

        with col_der:
            st.markdown("#### ⚠️ Sin curso asignado")
            if sin_curso:
                for e in sin_curso:
                    st.warning(f"**{e['nombre_completo']}** — {e['email']}")
            else:
                st.success("Todos los estudiantes tienen curso asignado.")
