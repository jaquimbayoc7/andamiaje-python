"""
backend/services/email_service.py
Envío de emails con SendGrid: score + ruta de aprendizaje.
"""

import logging
import os
from typing import Optional

from backend.core.config import settings
from backend.models.evaluacion import Evaluacion, Estudiante
from backend.models.usuario import Usuario

logger = logging.getLogger(__name__)


def _construir_html(usuario: Usuario, estudiante: Estudiante, evaluacion: Evaluacion) -> str:
    """Construye el HTML del email con el score y la ruta de aprendizaje."""
    ruta = evaluacion.ruta_aprendizaje or {}
    score_pct = f"{evaluacion.score_global:.0%}"

    # Color del score
    color = "#27ae60" if evaluacion.score_global >= 0.7 else "#e67e22" if evaluacion.score_global >= 0.5 else "#e74c3c"

    temas_fuertes = ruta.get("temas_fuertes", [])
    temas_reforzar = ruta.get("temas_a_reforzar", [])
    ejercicios_rec = ruta.get("ejercicios_recomendados", [])
    recursos = ruta.get("recursos_externos", [])
    mensaje_mot = ruta.get("mensaje_motivacional", "¡Sigue adelante!")

    # Generar filas de ejercicios recomendados
    filas_ejercicios = "".join(
        f"<li><b>{ej.get('titulo', '')}</b> — {ej.get('razon', '')}</li>"
        for ej in ejercicios_rec[:3]
    )

    filas_recursos = "".join(
        f"<li><a href='{r.get('url', '#')}' style='color:#3498db;'>{r.get('titulo', '')}</a> ({r.get('tipo', '')})</li>"
        for r in recursos[:3]
    )

    return f"""
<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"></head>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; color: #333;">
  <div style="background: #2c3e50; color: white; padding: 24px; border-radius: 8px 8px 0 0;">
    <h1 style="margin:0;">🐍 Andamiaje Python</h1>
    <p style="margin:4px 0 0;">Reporte de Evaluación — Corte {evaluacion.corte}</p>
  </div>

  <div style="padding: 24px; background: #f9f9f9;">
    <p>Hola <b>{usuario.nombre_completo}</b>,</p>
    <p>Tu evaluación del <b>Corte {evaluacion.corte}</b> ya está disponible:</p>

    <div style="text-align: center; margin: 24px 0;">
      <div style="font-size: 64px; font-weight: bold; color: {color};">{score_pct}</div>
      <div style="color: #666;">Score Global</div>
    </div>

    <p style="background: #ecf0f1; padding: 12px; border-radius: 6px; font-style: italic;">
      {mensaje_mot}
    </p>

    {"<h3>✅ Temas Fuertes</h3><ul>" + "".join(f"<li>{t}</li>" for t in temas_fuertes) + "</ul>" if temas_fuertes else ""}
    {"<h3>📚 Temas a Reforzar</h3><ul>" + "".join(f"<li>{t}</li>" for t in temas_reforzar) + "</ul>" if temas_reforzar else ""}
    {"<h3>🎯 Ejercicios Recomendados</h3><ul>" + filas_ejercicios + "</ul>" if filas_ejercicios else ""}
    {"<h3>🔗 Recursos</h3><ul>" + filas_recursos + "</ul>" if filas_recursos else ""}

    <hr style="margin: 24px 0; border: none; border-top: 1px solid #ddd;">
    <p style="color: #999; font-size: 12px;">
      Programa: {estudiante.programa_academico} | Semestre: {estudiante.semestre}<br>
      Este es un correo automático de Andamiaje Python. No responder.
    </p>
  </div>
</body>
</html>
"""


async def enviar_email_evaluacion(
    usuario: Usuario,
    estudiante: Estudiante,
    evaluacion: Evaluacion,
) -> bool:
    """
    Envía el email de evaluación con SendGrid.
    Retorna True si fue exitoso, False si no.
    """
    api_key = settings.SENDGRID_API_KEY
    if not api_key or not api_key.startswith("SG."):
        logger.warning("SENDGRID_API_KEY no configurada — email no enviado")
        return False

    try:
        import sendgrid
        from sendgrid.helpers.mail import Mail, Email, To, Content

        sg = sendgrid.SendGridAPIClient(api_key=api_key)
        html_content = _construir_html(usuario, estudiante, evaluacion)

        message = Mail(
            from_email=Email(settings.SENDGRID_FROM_EMAIL, settings.SENDGRID_FROM_NAME),
            to_emails=To(usuario.email),
            subject=f"Tu evaluación Corte {evaluacion.corte} — Andamiaje Python",
            html_content=Content("text/html", html_content),
        )

        response = sg.send(message)
        if response.status_code in (200, 202):
            logger.info("Email enviado a %s (evaluación %d)", usuario.email, evaluacion.id)
            return True
        else:
            logger.error("SendGrid respondió %d", response.status_code)
            return False

    except ImportError:
        logger.error("sendgrid no instalado — pip install sendgrid")
        return False
    except Exception as exc:
        logger.error("Error enviando email: %s", type(exc).__name__)
        return False


async def enviar_alerta_docente(
    docente: Usuario,
    estudiante_nombre: str,
    temas_debiles: list[str],
    score_actual: float,
    curso_nombre: str,
) -> bool:
    """Envía alerta de estudiante en riesgo al docente."""
    api_key = settings.SENDGRID_API_KEY
    if not api_key or not api_key.startswith("SG."):
        return False

    html = f"""
<!DOCTYPE html>
<html lang="es">
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
  <div style="background: #e74c3c; color: white; padding: 20px; border-radius: 8px 8px 0 0;">
    <h2 style="margin:0;">⚠️ Alerta Temprana — Estudiante en Riesgo</h2>
  </div>
  <div style="padding: 20px; background: #f9f9f9;">
    <p>Estimado/a <b>{docente.nombre_completo}</b>,</p>
    <p>El/la estudiante <b>{estudiante_nombre}</b> del curso <b>{curso_nombre}</b> 
    muestra indicadores de riesgo académico:</p>
    <ul>
      <li>Score actual: <b style="color:#e74c3c;">{score_actual:.0%}</b></li>
      <li>Temas débiles: <b>{', '.join(temas_debiles) if temas_debiles else 'varios'}</b></li>
    </ul>
    <p>Se recomienda realizar una intervención personalizada a la brevedad.</p>
    <hr>
    <p style="color:#999; font-size:12px;">Andamiaje Python — Alertas Tempranas</p>
  </div>
</body>
</html>
"""
    try:
        import sendgrid
        from sendgrid.helpers.mail import Mail, Email, To, Content

        sg = sendgrid.SendGridAPIClient(api_key=api_key)
        message = Mail(
            from_email=Email(settings.SENDGRID_FROM_EMAIL, settings.SENDGRID_FROM_NAME),
            to_emails=To(docente.email),
            subject=f"⚠️ Alerta: {estudiante_nombre} en riesgo — {curso_nombre}",
            html_content=Content("text/html", html),
        )
        response = sg.send(message)
        return response.status_code in (200, 202)
    except Exception as exc:
        logger.error("Error enviando alerta: %s", exc)
        return False
