import base64

def get_pdf_preview_html(pdf_bytes: bytes) -> str:
    """Generates an HTML iframe to preview the PDF in Streamlit."""
    base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800px" style="border:1px solid #ccc;"></iframe>'
    return pdf_display
