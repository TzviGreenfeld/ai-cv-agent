import pdfkit

def export_pdf(html: str, output_path="outputs/cv.pdf") -> str:
    pdfkit.from_string(html, output_path)
    return output_path


def html_file_to_pdf(input_path: str, output_path="outputs/cv.pdf") -> str:
    pdfkit.from_file(input_path, output_path)
    return output_path