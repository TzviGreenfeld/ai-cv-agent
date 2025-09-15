from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright
from pathlib import Path

DEFAULT_OPTIONS = {
    "format": "A4",
    "margin": {"top": "0", "bottom": "0", "left": "0", "right": "0"},
    "print_background": True,  # Important for CSS backgrounds/colors
    "prefer_css_page_size": True,
}


def html_to_pdf(html_content: str, output_path: str):
    """
    Convert HTML string to PDF using Playwright

    Args:
        html_content (str): HTML content as string
        output_path (str): Path where PDF should be saved
        options (dict): Optional PDF generation options
    """

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.set_content(html_content)

            # Wait for any images or fonts to load
            page.wait_for_load_state("networkidle")

            page.pdf(path=output_path, **DEFAULT_OPTIONS)
            browser.close()
    except Exception as e:
        print(f"Error generating PDF: {e}")


async def html_to_pdf_async(html_content: str, output_path: str):
    """Async version of HTML to PDF conversion"""

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.set_content(html_content)
            await page.wait_for_load_state("networkidle")
            await page.pdf(path=output_path, **DEFAULT_OPTIONS)
            await browser.close()
    except Exception as e:
        print(f"Error generating PDF: {e}")


if __name__ == "__main__":
    # Example usage
    html_file = Path("outputs/resume.html")
    html_content = html_file.read_text(encoding="utf-8")
    pdf_output = Path("outputs/resume.pdf")
    html_to_pdf(html_content, pdf_output)

    print(f"Converted {html_file} to {pdf_output}")
