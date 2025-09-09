from playwright.sync_api import sync_playwright
from pathlib import Path


def html_to_pdf(html_content: str, output_path: str):
    """
    Convert HTML string to PDF using Playwright

    Args:
        html_content (str): HTML content as string
        output_path (str): Path where PDF should be saved
        options (dict): Optional PDF generation options
    """

    default_options = {
            "format": "A4",
            "margin": {"top": "0", "bottom": "0", "left": "0", "right": "0"},
            "print_background": True,  # Important for CSS backgrounds/colors
            "prefer_css_page_size": True,
        }

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.set_content(html_content)

            # Wait for any images or fonts to load
            page.wait_for_load_state("networkidle")

            page.pdf(path=output_path, **default_options)
            browser.close()
    except Exception as e:
        print(f"Error generating PDF: {e}")


if __name__ == "__main__":
    # Example usage
    html_file = Path("outputs/resume.html")
    html_content = html_file.read_text(encoding="utf-8")
    pdf_output = Path("outputs/resume.pdf")
    html_to_pdf(html_content, pdf_output)

    print(f"Converted {html_file} to {pdf_output}")
