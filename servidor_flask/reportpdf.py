from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def generate_pdf(results):
    doc = SimpleDocTemplate("reporte.pdf")
    styles = getSampleStyleSheet()

    content = []

    content.append(Paragraph("Reporte de Escaneo", styles["Title"]))
    content.append(Spacer(1, 10))

    for r in results:
        text = f"Puerto: {r['port']} - Servicio: {r['banner']} - Vuln: {r['vuln']}"
        content.append(Paragraph(text, styles["Normal"]))
        content.append(Spacer(1, 5))

    doc.build(content)