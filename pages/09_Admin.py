"""
pages/09_Admin.py
Panel de administración — 5 tabs completos.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from pages.utils import api_call, require_auth, safe_detail, safe_json_key

user = require_auth(["admin"])
if not user:
    st.stop()

st.title("🛠️ Panel de Administración")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "👥 Usuarios",
    "📊 Analíticas Globales",
    "🔮 Predicciones Globales",
    "⚠️ Alertas",
    "📤 Exportar",
])

# ── Tab 1: Gestión de Usuarios ────────────────────────────────────────────────
with tab1:
    st.subheader("Gestión de Usuarios")
    col_l, col_r = st.columns([2, 1])

    with col_l:
        rol_filtro = st.selectbox("Filtrar por rol", ["Todos", "admin", "docente", "estudiante"])
        params_u = f"?rol={rol_filtro}" if rol_filtro != "Todos" else ""
        resp_usuarios = api_call("GET", f"/api/admin/usuarios{params_u}")
        if resp_usuarios.status_code == 200:
            usuarios = resp_usuarios.json()
            if usuarios:
                df_u = pd.DataFrame(usuarios)[["id", "nombre_completo", "email", "rol", "activo"]]
                df_u.columns = ["ID", "Nombre", "Email", "Rol", "Activo"]
                st.dataframe(df_u, use_container_width=True, hide_index=True)
                st.caption(f"Total: {len(usuarios)} usuarios")
            else:
                st.info("No hay usuarios.")
        else:
            st.warning("No se pudieron cargar los usuarios.")

    with col_r:
        # Crear usuario
        with st.expander("➕ Crear usuario"):
            with st.form("form_crear_user"):
                nombre_u = st.text_input("Nombre completo")
                email_u = st.text_input("Email")
                pass_u = st.text_input("Contraseña", type="password")
                rol_u = st.selectbox("Rol", ["estudiante", "docente", "admin"])
                if st.form_submit_button("Crear"):
                    resp = api_call("POST", "/api/admin/usuarios", json={
                        "nombre_completo": nombre_u,
                        "email": email_u,
                        "password": pass_u,
                        "rol": rol_u,
                    })
                    if resp.status_code == 201:
                        st.success("✅ Usuario creado.")
                        st.rerun()
                    else:
                        st.error(safe_detail(resp))

        # Actualizar usuario
        with st.expander("✏️ Actualizar usuario"):
            uid = st.number_input("ID del usuario", min_value=1, step=1, key="uid_update")
            nuevo_rol = st.selectbox("Nuevo rol", ["estudiante", "docente", "admin"], key="new_rol")
            activo_u = st.checkbox("Activo", value=True, key="activo_u")
            if st.button("Actualizar", key="btn_update_user"):
                resp = api_call("PATCH", f"/api/admin/usuarios/{int(uid)}", json={
                    "rol": nuevo_rol,
                    "activo": activo_u,
                })
                if resp.status_code == 200:
                    st.success("✅ Usuario actualizado.")
                    st.rerun()
                else:
                    st.error(safe_detail(resp))

    # Gestión de cursos
    st.divider()
    st.subheader("Cursos")
    col_c1, col_c2 = st.columns([2, 1])

    with col_c1:
        resp_cursos = api_call("GET", "/api/admin/cursos")
        if resp_cursos.status_code == 200:
            cursos = resp_cursos.json()
            if cursos:
                st.dataframe(pd.DataFrame(cursos), use_container_width=True, hide_index=True)

    with col_c2:
        with st.expander("➕ Crear curso"):
            with st.form("form_crear_curso"):
                nombre_c = st.text_input("Nombre del curso")
                periodo_c = st.text_input("Período", placeholder="2026-1")
                docente_id_c = st.number_input("ID del docente", min_value=1, step=1)
                if st.form_submit_button("Crear"):
                    resp = api_call("POST", "/api/admin/cursos", json={
                        "nombre": nombre_c,
                        "periodo": periodo_c,
                        "docente_id": int(docente_id_c),
                    })
                    if resp.status_code == 201:
                        st.success("✅ Curso creado.")
                        st.rerun()
                    else:
                        st.error(safe_detail(resp))

# ── Tab 2: Analíticas Globales ─────────────────────────────────────────────────
with tab2:
    st.subheader("Analíticas Globales")

    if st.button("🔄 Cargar analíticas globales"):
        col_h, col_d = st.columns(2)

        resp_hm = api_call("GET", "/api/analiticas/heatmap")
        if resp_hm.status_code == 200 and resp_hm.json():
            hm_data = resp_hm.json()
            temas = list(hm_data.keys())
            niveles_hm = ["junior", "semi_senior", "senior"]
            matrix = [
                [hm_data.get(t, {}).get(n, {}).get("score_promedio", 0) for n in niveles_hm]
                for t in temas
            ]
            fig_hm = go.Figure(data=go.Heatmap(
                z=matrix, x=niveles_hm, y=temas, colorscale="RdYlGn", zmin=0, zmax=1,
                text=[[f"{v:.0%}" for v in row] for row in matrix], texttemplate="%{text}",
            ))
            fig_hm.update_layout(title="Heatmap Global: Score por Tema × Nivel", height=400)
            with col_h:
                st.plotly_chart(fig_hm, use_container_width=True)

        resp_dist = api_call("GET", "/api/analiticas/distribucion-scores")
        if resp_dist.status_code == 200:
            dist_data = resp_dist.json()
            cortes_data = [
                {"Corte": f"Corte {corte}", "Score": score}
                for corte, info in dist_data.items()
                for score in info.get("scores", [])
            ]
            if cortes_data:
                fig_dist = px.violin(
                    pd.DataFrame(cortes_data), x="Corte", y="Score",
                    title="Distribución Global de Scores", color="Corte", box=True,
                )
                with col_d:
                    st.plotly_chart(fig_dist, use_container_width=True)

        resp_temas = api_call("GET", "/api/analiticas/temas-debiles?top_n=8")
        if resp_temas.status_code == 200 and resp_temas.json():
            temas_data = resp_temas.json()
            fig_temas = px.bar(
                pd.DataFrame(temas_data), x="score_promedio", y="tema", orientation="h",
                title="Top Temas más Débiles (global)", color="score_promedio",
                color_continuous_scale="RdYlGn", range_color=[0, 1],
            )
            st.plotly_chart(fig_temas, use_container_width=True)

            st.subheader("💡 Insight Global")
            resumen = {
                "scope": "global",
                "temas_debiles": [t["tema"] for t in temas_data[:3]],
                "total_sesiones": sum(t["total_sesiones"] for t in temas_data),
            }
            resp_ins = api_call("POST", "/api/analiticas/insights", json=resumen)
            if resp_ins.status_code == 200:
                st.info(safe_json_key(resp_ins, "insight", ""))

# ── Tab 3: Predicciones Globales ──────────────────────────────────────────────
with tab3:
    st.subheader("Predicciones Globales de Riesgo")

    col_ent, col_pred = st.columns([1, 2])

    with col_ent:
        st.markdown("#### Re-entrenar Modelo ML")
        st.caption("Requiere mínimo 10 evaluaciones en la BD.")
        if st.button("🤖 Entrenar modelo", type="primary"):
            with st.spinner("Entrenando RandomForest..."):
                resp_train = api_call("POST", "/api/analiticas/predicciones/entrenar")
            if resp_train.status_code == 200:
                res = resp_train.json()
                st.success(f"✅ Modelo entrenado: {res.get('muestras', 0)} muestras, ROC-AUC: {res.get('roc_auc_cv', 0):.3f}")
            else:
                st.warning(safe_detail(resp_train, "No se pudo entrenar."))

    with col_pred:
        corte_g = st.selectbox("Corte", [1, 2, 3], key="corte_g")
        resp_riesgo = api_call("GET", f"/api/analiticas/predicciones/riesgo?corte={corte_g}")
        if resp_riesgo.status_code == 200:
            pred_global = resp_riesgo.json()
            if pred_global:
                df_riesgo = pd.DataFrame(pred_global)
                df_riesgo["Riesgo %"] = df_riesgo["score_riesgo"].map(lambda x: f"{x:.0%}")
                st.dataframe(
                    df_riesgo[["estudiante_id", "Riesgo %", "notificado_docente"]].rename(
                        columns={"estudiante_id": "Estudiante", "notificado_docente": "Notificado"}
                    ),
                    use_container_width=True, hide_index=True,
                )

                fig_risk = px.histogram(df_riesgo, x="score_riesgo", nbins=10,
                                       title="Distribución de Score de Riesgo", range_x=[0, 1])
                st.plotly_chart(fig_risk, use_container_width=True)
            else:
                st.success("✅ No hay estudiantes en riesgo para este corte.")

# ── Tab 4: Alertas y Notificaciones ──────────────────────────────────────────
with tab4:
    st.subheader("Alertas Tempranas")

    corte_alert = st.selectbox("Corte", [1, 2, 3], key="corte_alert")
    resp_alertas = api_call("GET", f"/api/analiticas/predicciones/riesgo?corte={corte_alert}")

    if resp_alertas.status_code == 200:
        alertas = [a for a in resp_alertas.json() if not a.get("notificado_docente")]

        if alertas:
            st.warning(f"⚠️ {len(alertas)} estudiantes en riesgo sin notificar")
            for alerta in alertas:
                with st.container(border=True):
                    col_i, col_b = st.columns([4, 1])
                    with col_i:
                        st.markdown(f"**Estudiante #{alerta['estudiante_id']}** — Riesgo: `{alerta['score_riesgo']:.0%}`")
                        temas = [t.get("tema", "") for t in (alerta.get("temas_debiles") or [])]
                        if temas:
                            st.caption(f"Temas débiles: {', '.join(temas)}")
                    with col_b:
                        if st.button("📧 Notificar", key=f"a_{alerta['prediccion_id']}"):
                            resp_n = api_call("POST", f"/api/admin/alertas/notificar/{alerta['prediccion_id']}")
                            if resp_n.status_code == 200:
                                st.success("Notificado.")
                                st.rerun()
        else:
            st.success("✅ Todas las alertas activas ya han sido notificadas.")

# ── Tab 5: Exportar ───────────────────────────────────────────────────────────
with tab5:
    st.subheader("Exportar Datos Institucionales")

    if st.button("📥 Exportar usuarios (CSV)"):
        resp_u = api_call("GET", "/api/admin/usuarios")
        if resp_u.status_code == 200:
            df_export = pd.DataFrame(resp_u.json())
            csv = df_export.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️ Descargar usuarios.csv",
                data=csv,
                file_name="usuarios_andamiaje.csv",
                mime="text/csv",
            )

    if st.button("📥 Exportar predicciones (CSV)"):
        all_preds = []
        for c in [1, 2, 3]:
            resp_p = api_call("GET", f"/api/analiticas/predicciones/riesgo?corte={c}")
            if resp_p.status_code == 200:
                for item in resp_p.json():
                    item["corte"] = c
                    all_preds.append(item)
        if all_preds:
            df_preds = pd.DataFrame(all_preds)
            csv_p = df_preds.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️ Descargar predicciones.csv",
                data=csv_p,
                file_name="predicciones_riesgo.csv",
                mime="text/csv",
            )
