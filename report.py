import uuid
import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm

REPORT_DIR = "reports"
os.makedirs(REPORT_DIR, exist_ok=True)

def create_report(data: dict) -> tuple[str, str]:
    report_id = str(uuid.uuid4())[:8].upper()
    file_path = f"{REPORT_DIR}/{report_id}.pdf"

    doc = SimpleDocTemplate(
        file_path,
        rightMargin=20 * mm, leftMargin=20 * mm,
        topMargin=20 * mm,   bottomMargin=20 * mm,
    )
    styles = getSampleStyleSheet()
    heading = ParagraphStyle("heading", parent=styles["Heading2"], textColor=colors.HexColor("#1a73e8"))
    normal  = styles["Normal"]
    bold    = ParagraphStyle("bold", parent=normal, fontName="Helvetica-Bold")
    small   = ParagraphStyle("small", parent=normal, fontSize=8, textColor=colors.grey)

    severity_colors = {"high": "#ef4444", "medium": "#f97316", "mild": "#22c55e"}
    sev = data.get("severity", "medium")
    sev_color = colors.HexColor(severity_colors.get(sev, "#f97316"))
    sev_style = ParagraphStyle("sev", parent=bold, textColor=sev_color)

    content = []

    content.append(Paragraph("MediSense AI — Symptom Report", styles["Title"]))
    content.append(Spacer(1, 4 * mm))
    content.append(HRFlowable(width="100%", thickness=1, color=colors.lightgrey))
    content.append(Spacer(1, 4 * mm))

    content.append(Paragraph(f"Report ID: {report_id}", bold))
    content.append(Paragraph(f"Patient: {data.get('name', 'N/A')}", normal))
    content.append(Paragraph(f"Age: {data.get('age', 'N/A')}   Gender: {data.get('gender', 'N/A')}", normal))
    content.append(Paragraph(f"Symptoms: {data.get('symptoms', 'N/A')}", normal))
    content.append(Paragraph(f"Severity: {sev.upper()}", sev_style))
    content.append(Spacer(1, 4 * mm))

    content.append(Paragraph("Possible Conditions", heading))
    for c in data.get("possible_conditions", []):
        content.append(Paragraph(f"• {c}", normal))
    content.append(Spacer(1, 3 * mm))

    content.append(Paragraph("Explanation", heading))
    content.append(Paragraph(data.get("explanation", ""), normal))
    content.append(Spacer(1, 3 * mm))

    content.append(Paragraph("Advice", heading))
    for a in data.get("advice", []):
        content.append(Paragraph(f"• {a}", normal))
    content.append(Spacer(1, 3 * mm))

    if data.get("otc"):
        content.append(Paragraph("OTC Medicines", heading))
        for m in data["otc"]:
            content.append(Paragraph(f"• {m}", normal))
        content.append(Spacer(1, 3 * mm))

    if data.get("warning"):
        warn_style = ParagraphStyle("warn", parent=heading, textColor=colors.red)
        content.append(Paragraph("Warnings", warn_style))
        for w in data["warning"]:
            content.append(Paragraph(f"• {w}", normal))

    content.append(Spacer(1, 6 * mm))
    content.append(HRFlowable(width="100%", thickness=1, color=colors.lightgrey))
    content.append(Paragraph(
        "This report is AI-generated and does NOT replace professional medical advice. "
        "Always consult a qualified healthcare provider.",
        small
    ))

    doc.build(content)
    return report_id, file_path