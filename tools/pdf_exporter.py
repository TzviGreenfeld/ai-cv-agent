import pdfkit

def export_pdf(html: str, output_path="outputs/cv.pdf") -> str:
    pdfkit.from_string(html, output_path)
    return output_path
