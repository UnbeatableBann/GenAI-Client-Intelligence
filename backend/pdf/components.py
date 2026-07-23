from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib.colors import HexColor
from reportlab.lib import colors
from .styles import get_report_styles

styles = get_report_styles()

def create_card(title, content):
    """Creates a basic card with a title and content, kept together."""
    elements = []
    elements.append(Paragraph(title, styles['CardTitle']))
    
    if isinstance(content, str):
        elements.append(Paragraph(content, styles['CustomBodyText']))
    elif isinstance(content, list):
        for item in content:
            if isinstance(item, str):
                elements.append(Paragraph(item, styles['CustomBodyText']))
            else:
                elements.append(item)
    
    return KeepTogether(elements)

def create_evidence_block(evidence_list):
    """Formats an array of quotes."""
    elements = []
    for ev in evidence_list:
        elements.append(Paragraph(f"\"{ev}\"", styles['EvidenceText']))
    return elements

def create_metric_grid(metrics_dict):
    """Creates a clean grid for health metrics."""
    data = [["Metric", "Value", "Status", "Confidence"]]
    for title, field in metrics_dict.items():
        val = str(field.value) if field.value is not None else "N/A"
        status = field.status.replace("_", " ").title()
        conf = f"{field.confidence:.2f}"
        data.append([title, val, status, conf])
        
    table = Table(data, colWidths=[100, 200, 100, 60])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor("#EDF2F7")),
        ('TEXTCOLOR', (0, 0), (-1, 0), HexColor("#2D3748")),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), HexColor("#4A5568")),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor("#E2E8F0")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    return table

def get_trend_arrow(trend_text):
    t = trend_text.lower()
    if "improv" in t or "increas" in t or "up" in t:
        return "↑"
    if "declin" in t or "decreas" in t or "wors" in t or "down" in t:
        return "↓"
    return "→"
