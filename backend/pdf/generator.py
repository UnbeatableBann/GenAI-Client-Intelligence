import io
import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import HexColor
from reportlab.lib.units import inch

from backend.models import FinalReport
from .styles import get_report_styles
from .components import create_card, create_evidence_block, create_metric_grid, get_trend_arrow

class FooterDocTemplate(SimpleDocTemplate):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.report_id = "REP-" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        
    def add_page_info(self, canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(HexColor("#A0AEC0"))
        
        # Footer text
        footer_text = f"GenAI Client Intelligence | Page {doc.page} | Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} | ID: {self.report_id}"
        
        canvas.drawCentredString(letter[0] / 2.0, 0.5 * inch, footer_text)
        canvas.restoreState()

def generate_pdf_report(report: FinalReport, health_data: dict) -> bytes:
    buffer = io.BytesIO()
    doc = FooterDocTemplate(buffer, pagesize=letter,
                            rightMargin=50, leftMargin=50,
                            topMargin=50, bottomMargin=50)
                            
    styles = get_report_styles()
    story = []
    
    info = report.extracted_info
    reasoning = report.reasoning
    
    # --- Cover Page ---
    story.append(Spacer(1, 1.5 * inch))
    story.append(Paragraph("Client Intelligence Report", styles['CoverTitle']))
    story.append(Paragraph(f"Date: {datetime.datetime.now().strftime('%B %d, %Y')}", styles['CoverSubtitle']))
    
    score = health_data['overall_score']
    score_color = "#28A745" if score >= 80 else "#FFC107" if score >= 60 else "#DC3545"
    score_style = get_report_styles()['HealthScore']
    score_style.textColor = HexColor(score_color)
    
    story.append(Paragraph(f"Health Score: {score}/100", score_style))
    
    if info.risk_flags:
        max_severity = info.risk_flags[0].severity
        story.append(Paragraph(f"Priority Risk Level: {max_severity}", styles['CoverSubtitle']))
    else:
        story.append(Paragraph(f"Priority Risk Level: None", styles['CoverSubtitle']))
        
    story.append(Spacer(1, 1 * inch))
    story.append(Paragraph("Executive Summary", styles['SectionHeader']))
    story.append(Paragraph(info.weekly_summary.value if info.weekly_summary.value else "No summary available.", styles['CustomBodyText']))
    
    story.append(PageBreak())
    
    # --- Health Overview ---
    story.append(Paragraph("Health Overview", styles['SectionHeader']))
    metrics_map = {
        "Nutrition": info.nutrition,
        "Exercise": info.exercise,
        "Steps": info.steps,
        "Sleep": info.sleep,
        "Water": info.water_intake,
        "Stress": info.stress,
        "Energy": info.energy,
        "Weight": info.weight,
        "Symptoms": info.symptoms
    }
    story.append(create_metric_grid(metrics_map))
    story.append(Spacer(1, 20))
    
    # --- Trend Analysis ---
    if reasoning.trends:
        story.append(Paragraph("Trend Analysis", styles['SectionHeader']))
        trend_data = [["Metric", "Trend", "Status"]]
        for t in reasoning.trends:
            arrow = get_trend_arrow(t.trend)
            trend_data.append([t.metric, t.trend, arrow])
            
        t_table = Table(trend_data, colWidths=[150, 200, 50])
        t_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor("#EDF2F7")),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor("#E2E8F0")),
            ('ALIGN', (2, 1), (2, -1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(t_table)
        story.append(Spacer(1, 20))
        
    # --- Priority Risks ---
    if info.risk_flags:
        story.append(Paragraph("Priority Risks", styles['SectionHeader']))
        for r in info.risk_flags:
            risk_content = [
                Paragraph(f"<b>Severity:</b> {r.severity} | <b>Confidence:</b> {r.confidence:.2f}", styles['CustomBodyText']),
                Paragraph(f"<b>Reason:</b> {r.reason}", styles['CustomBodyText']),
                Paragraph("<b>Evidence:</b>", styles['CustomBodyText'])
            ] + create_evidence_block(r.evidence)
            story.append(create_card(r.title, risk_content))
            story.append(Spacer(1, 10))
            
    # --- Key Barriers ---
    if info.key_barriers.value:
        story.append(Paragraph("Key Barriers", styles['SectionHeader']))
        barrier_content = [
            Paragraph(info.key_barriers.value, styles['CustomBodyText']),
            Paragraph("<b>Evidence:</b>", styles['CustomBodyText'])
        ] + create_evidence_block(info.key_barriers.evidence)
        story.append(create_card("Identified Barriers", barrier_content))
        story.append(Spacer(1, 20))
        
    # --- Coach Action Plan ---
    if reasoning.coach_recommendation:
        story.append(Paragraph("Coach Action Plan", styles['SectionHeader']))
        story.append(Paragraph(reasoning.coach_recommendation, styles['CustomBodyText']))
        story.append(Spacer(1, 20))
        
    # --- Follow-up Questions ---
    if reasoning.suggested_follow_up_questions:
        story.append(Paragraph("Suggested Follow-up Questions", styles['SectionHeader']))
        for i, q in enumerate(reasoning.suggested_follow_up_questions, 1):
            story.append(Paragraph(f"{i}. {q}", styles['CustomBodyText']))
        story.append(Spacer(1, 20))
        
    # --- Timeline ---
    if reasoning.timeline:
        story.append(Paragraph("Chronological Timeline", styles['SectionHeader']))
        for entry in reasoning.timeline:
            events_list = [f"• {e}" for e in entry.events]
            story.append(create_card(entry.day, events_list))
            story.append(Spacer(1, 10))
            
    # --- Missing Information ---
    if info.missing_information:
        story.append(Paragraph("Missing Information", styles['SectionHeader']))
        for m in info.missing_information:
            story.append(Paragraph(f"• {m}", styles['CustomBodyText']))
            
    # Build document
    doc.build(story, onFirstPage=doc.add_page_info, onLaterPages=doc.add_page_info)
    
    return buffer.getvalue()
