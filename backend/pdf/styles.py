from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor

def get_report_styles():
    styles = getSampleStyleSheet()
    
    # Custom Styles
    styles.add(ParagraphStyle(
        name='CoverTitle',
        parent=styles['Heading1'],
        fontSize=28,
        leading=34,
        textColor=HexColor("#1A365D"),
        alignment=1, # Center
        spaceAfter=30
    ))
    
    styles.add(ParagraphStyle(
        name='CoverSubtitle',
        parent=styles['Normal'],
        fontSize=14,
        textColor=HexColor("#4A5568"),
        alignment=1,
        spaceAfter=10
    ))
    
    styles.add(ParagraphStyle(
        name='HealthScore',
        parent=styles['Heading1'],
        fontSize=36,
        alignment=1,
        spaceBefore=40,
        spaceAfter=40
    ))
    
    styles.add(ParagraphStyle(
        name='SectionHeader',
        parent=styles['Heading2'],
        fontSize=18,
        textColor=HexColor("#2B6CB0"),
        spaceBefore=20,
        spaceAfter=10,
        borderPadding=(0, 0, 4, 0),
        borderColor=HexColor("#E2E8F0"),
        borderWidth=1
    ))
    
    styles.add(ParagraphStyle(
        name='CardTitle',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=HexColor("#2D3748"),
        spaceBefore=10,
        spaceAfter=5
    ))
    
    styles.add(ParagraphStyle(
        name='CustomBodyText',
        parent=styles['Normal'],
        fontSize=11,
        leading=16,
        textColor=HexColor("#4A5568"),
        spaceAfter=10
    ))
    
    styles.add(ParagraphStyle(
        name='EvidenceText',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=HexColor("#718096"),
        leftIndent=20,
        spaceAfter=5,
        bulletIndent=5,
        bulletFontName='Helvetica',
        bulletFontSize=10
    ))
    
    return styles
