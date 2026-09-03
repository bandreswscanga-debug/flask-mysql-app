#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genera el Informe Ejecutivo SRE (Post-Mortem) en PDF.

Uso:
    python3 generar_pdf.py                    # genera el PDF plantilla
    python3 generar_pdf.py --capturas dst/    # usa capturas existentes (opcional)

El script inserta automáticamente las imágenes que encuentre en ./capturas con
estos nombres (si existen):
    seccion1_bloqueo.png   - pipeline bloqueando (Bandit/Trivy)
    seccion1_verde.png     - pipeline exitoso tras parcheo
    seccion2_pytest.png    - log Pytest aprobado
    seccion3_down.png      - alerta Telegram caida
    seccion3_stacktrace.png- stacktrace en Dozzle
    seccion3_up.png        - alerta Telegram recuperacion
"""
import os
import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CAPTURAS = os.path.join(BASE_DIR, "capturas")

# ---------------------------------------------------------------------------
# Estilos
# ---------------------------------------------------------------------------
styles = getSampleStyleSheet()

TITULO = ParagraphStyle(
    "Titulo", parent=styles["Title"], fontSize=20, leading=24,
    textColor=colors.HexColor("#1a5276"), spaceAfter=6,
)
SUBTITULO = ParagraphStyle(
    "Sub", parent=styles["Normal"], fontSize=12, alignment=1,
    textColor=colors.HexColor("#566573"), spaceAfter=14,
)
H1 = ParagraphStyle(
    "H1", parent=styles["Heading1"], fontSize=15, textColor=colors.HexColor("#1a5276"),
    spaceBefore=12, spaceAfter=6,
)
H2 = ParagraphStyle(
    "H2", parent=styles["Heading2"], fontSize=12, textColor=colors.HexColor("#2e86c1"),
    spaceBefore=8, spaceAfter=4,
)
BODY = ParagraphStyle("Body", parent=styles["BodyText"], fontSize=10, leading=14)
BULLET = ParagraphStyle("Bullet", parent=BODY, leftIndent=14, bulletIndent=4, spaceAfter=3)
SMALL = ParagraphStyle("Small", parent=styles["BodyText"], fontSize=8, textColor=colors.grey)
CAPTION = ParagraphStyle(
    "Caption", parent=styles["BodyText"], fontSize=8, alignment=1,
    textColor=colors.HexColor("#7f8c8d"), spaceBefore=2, spaceAfter=8,
)


def tabla_datos(datos):
    """Tabla sencilla clave/valor."""
    filas = [[Paragraph("<b>%s</b>" % k, BODY), Paragraph(v, BODY)] for k, v in datos]
    t = Table(filas, colWidths=[5.5 * cm, 11 * cm])
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d5d8dc")),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#eaf2f8")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def img_captura(archivo, titulo_imagen=None):
    """Inserta una imagen si existe; si no, un marcador de posición."""
    ruta = os.path.join(CAPTURAS, archivo)
    if os.path.exists(ruta):
        img = Image(ruta)
        img._restrictSize(15.5 * cm, 9 * cm)
        elems = [img]
    else:
        placeholder = Table(
            [[Paragraph(
                "&#9888; <b>PENDIENTE DE CAPTURA</b><br/><font size=8>Coloca la imagen "
                "<b>%s</b> en la carpeta <b>capturas/</b> y vuelve a ejecutar este script.</font>"
                % archivo, BODY)]],
            colWidths=[15.5 * cm], rowHeights=[3 * cm],
        )
        placeholder.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#f5b041")),
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fdf2e9")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ]))
        elems = [placeholder]
    if titulo_imagen:
        elems.append(Paragraph(titulo_imagen, CAPTION))
    return elems


# ---------------------------------------------------------------------------
# Construccion del PDF
# ---------------------------------------------------------------------------
def construir(pdf_path):
    doc = SimpleDocTemplate(
        pdf_path, pagesize=A4,
        rightMargin=2 * cm, leftMargin=2 * cm, topMargin=2 * cm, bottomMargin=2 * cm,
        title="Informe Ejecutivo SRE - Post-Mortem",
        author="Proyecto SRE",
    )
    E = []

    # ---- Portada ----
    E.append(Paragraph("INFORME EJECUTIVO SRE", TITULO))
    E.append(Paragraph("Reporte Técnico Post-Incidente (Post-Mortem)", SUBTITULO))
    E.append(Spacer(1, 0.5 * cm))
    E.append(tabla_datos([
        ("Proyecto", "Sistema de Monitoreo y Alta Disponibilidad (Flask + MySQL)"),
        ("Autor", "Aprendiz SRE - oswal"),
        ("Fecha", "Septiembre 2026"),
        ("Estado", "RECUPERADO - Servicio disponible"),
    ]))
    E.append(Spacer(1, 0.8 * cm))

    E.append(Paragraph("Accesos a Producción", H2))
    E.append(tabla_datos([
        ("Repositorio (GitHub)", "https://github.com/bandreswscanga-debug/flask-mysql-app"),
        ("API (Producción)", "https://api.oswal-sre.duckdns.org"),
        ("Portal de Logs (Dozzle)", "https://logs.oswal-sre.duckdns.org"),
        ("Usuario Dozzle", "ProfeChristian"),
        ("Contraseña Dozzle", "Evidencia2"),
        ("Uptime Kuma", "http://18.118.206.166:3001"),
    ]))
    E.append(Spacer(1, 0.8 * cm))

    E.append(Paragraph("Resumen Ejecutivo", H1))
    E.append(Paragraph(
        "Este documento resume el desarrollo del proyecto SRE a través de sus cinco fases: "
        "despliegue de la arquitectura base (Flask + MySQL + Nginx Proxy Manager), barrera de "
        "seguridad DevSecOps con pipeline de Falla Rápida (Bandit + Trivy), visibilidad absoluta "
        "sobre los contenedores (Uptime Kuma + Telegram + Dozzle), simulación controlada de una "
        "interrupción severa del servicio de base de datos, y la posterior recuperación y "
        "redacción del presente informe. Se incluye la evidencia gráfica (capturas) de cada "
        "punto de control exigido.", BODY))
    E.append(PageBreak())

    # ---- Seccion 1: DevSecOps ----
    E.append(Paragraph("Sección 1 — DevSecOps (Pipeline de Seguridad)", H1))
    E.append(Paragraph(
        "El pipeline de GitHub Actions integra herramientas de seguridad en la etapa de "
        "integración continua: <b>Bandit</b> (SAST para Python) y <b>Trivy</b> (escaneo de "
        "contenedores). Estas herramientas implementan la barrera de <i>Falla Rápida</i> "
        "(Fail-Fast), que aborta el despliegue si se detectan vulnerabilidades críticas.", BODY))
    E.append(Spacer(1, 0.4 * cm))
    E.append(Paragraph("1.1 Pipeline bloqueando el despliegue inseguro", H2))
    E.append(Paragraph(
        "Se creó la rama <b>feature/bad-security</b> con contraseña hardcodeada en el código de "
        "Flask y una imagen obsoleta <b>python:3.8</b> en el Dockerfile. Al intentar el Pull "
        "Request a main, el pipeline se abortó detectando las vulnerabilidades críticas y "
        "evitando el despliegue inseguro.", BODY))
    E.extend(img_captura("seccion1_bloqueo.png", "Captura: Pipeline en rojo/abortado por Bandit y Trivy (rama feature/bad-security)."))
    E.append(Spacer(1, 0.4 * cm))
    E.append(Paragraph("1.2 Pipeline exitoso tras el parcheo", H2))
    E.append(Paragraph(
        "Tras corregir el código (eliminar la contraseña hardcodeada) y actualizar la imagen a "
        "<b>python:3.12-slim</b> (con librerías del sistema parcheadas), el pipeline volvió a "
        "pasar en verde y permitió el despliegue.", BODY))
    E.extend(img_captura("seccion1_verde.png", "Captura: Pipeline en verde tras el parcheo de seguridad."))
    E.append(PageBreak())

    # ---- Seccion 2: Evidencia de pruebas ----
    E.append(Paragraph("Sección 2 — Evidencia de Pruebas (Pytest)", H1))
    E.append(Paragraph(
        "La etapa de pruebas unitarias del pipeline ejecuta <b>Pytest</b> sobre "
        "<b>test_app.py</b>, validando los endpoints de la API. A continuación se muestra el "
        "log de GitHub Actions con las pruebas aprobadas.", BODY))
    E.append(Spacer(1, 0.4 * cm))
    E.extend(img_captura("seccion2_pytest.png", "Captura: Log de GitHub Actions con Pytest aprobado (3 passed)."))
    E.append(PageBreak())

    # ---- Seccion 3: Bitacora de incidente ----
    E.append(Paragraph("Sección 3 — Bitácora de Incidente", H1))
    E.append(Paragraph("Interrupción severa del servicio de base de datos MySQL.", BODY))
    E.append(Spacer(1, 0.4 * cm))

    E.append(Paragraph("Línea de tiempo del incidente", H2))
    E.append(tabla_datos([
        ("t0", "Simulación de caída: <b>docker stop servidor-bd-ejemplo</b> mediante SSH."),
        ("t0 + 60s", "Uptime Kuma detecta la caída del monitor y envía <b>alerta DOWN</b> al grupo de Telegram."),
        ("t0 + 60-120s", "La API web falla al intentar conectar con la base de datos (navegador)."),
        ("Diagnóstico", "Sin usar SSH: inicio de sesión en Dozzle y localización de la excepción PyMySQL en el contenedor <b>servidor-api-ejemplo</b>."),
        ("Recuperación", "Ejecución de <b>docker start servidor-bd-ejemplo</b>."),
        ("Post-recuperación", "Uptime Kuma detecta la recuperación y envía <b>alerta UP</b> al grupo de Telegram."),
    ]))
    E.append(Spacer(1, 0.5 * cm))

    E.append(Paragraph("3.1 Alerta de caída (Telegram — DOWN)", H2))
    E.extend(img_captura("seccion3_down.png", "Captura: Alerta roja 'DOWN' recibida en el grupo de Telegram."))

    E.append(Paragraph("3.2 Rastreo del error (Dozzle)", H2))
    E.extend(img_captura("seccion3_stacktrace.png", "Captura: Stacktrace de PyMySQL (OperationalError) en el log de Dozzle."))

    E.append(Paragraph("3.3 Alerta de recuperación (Telegram — UP)", H2))
    E.extend(img_captura("seccion3_up.png", "Captura: Alerta verde 'UP' de recuperación en el grupo de Telegram."))
    E.append(PageBreak())

    # ---- Causa raiz y lecciones ----
    E.append(Paragraph("Análisis de causa raíz y lecciones aprendidas", H1))
    E.append(Paragraph("Causa raíz", H2))
    E.append(Paragraph(
        "El servicio <b>MySQL</b> (contenedor servidor-bd-ejemplo) fue detenido deliberadamente "
        "para simular una interrupción catastrófica. La API Flask, que depende de la conexión a "
        "la base de datos, quedó inoperante para los endpoints que requieren BD "
        "(/health y /api/data), generando excepciones PyMySQL <i>OperationalError</i>.", BODY))
    E.append(Spacer(1, 0.4 * cm))
    E.append(Paragraph("Tiempos de detección y recuperación (MTTA / MTTR)", H2))
    E.append(tabla_datos([
        ("MTTA (detección)", "~60 segundos (detección automática por Uptime Kuma + alerta Telegram)"),
        ("MTTR (recuperación)", "Inmediato tras ejecutar docker start (recuperación manual controlada)"),
    ]))
    E.append(Spacer(1, 0.4 * cm))
    E.append(Paragraph("Lecciones aprendidas y acciones resilientes", H2))
    for item in [
        "<b>Señalización automática</b>: Uptime Kuma + Telegram permiten tener visibilidad inmediata sin depender de SSH.",
        "<b>Observabilidad centralizada</b>: Dozzle facilita el diagnóstico de logs en tiempo real de todos los contenedores.",
        "<b>Barrera DevSecOps</b>: el pipeline bloqueó el despliegue de código inseguro, previniendo vulnerabilidades en producción.",
        "<b>Recomendación</b>: considerar <i>restart: unless-stopped</i> (ya configurado) y evaluación de políticas de auto-recarga/HA para MySQL.",
    ]:
        E.append(Paragraph("&#8226; " + item, BULLET))
    E.append(Spacer(1, 0.6 * cm))

    E.append(Paragraph("Conclusión", H1))
    E.append(Paragraph(
        "El sistema demostró su capacidad para detectar, diagnosticar y recuperar una "
        "interrupción severa mediante las herramientas de monitoreo y observabilidad "
        "implementadas (Uptime Kuma + Telegram + Dozzle), respaldadas por un pipeline CI/CD "
        "con controles de seguridad automatizados. El servicio quedó restaurado y disponible, "
        "con todas las alertas de recuperación activadas correctamente.", BODY))

    doc.build(E)
    print("PDF generado: %s" % pdf_path)


if __name__ == "__main__":
    salida = os.path.join(BASE_DIR, "Informe_Ejecutivo_SRE_PostMortem.pdf")
    construir(salida)
