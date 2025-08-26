from playwright.sync_api import sync_playwright
import os

def html_to_pdf(html_content: str, output_path: str, options: dict = None):
    """
    Convert HTML string to PDF using Playwright
    
    Args:
        html_content (str): HTML content as string
        output_path (str): Path where PDF should be saved
        options (dict): Optional PDF generation options
    """
    default_options = {
        "format": "A4",
        "margin": {
            "top": "0",
            "bottom": "0", 
            "left": "0",
            "right": "0"
        },
        "print_background": True,  # Important for CSS backgrounds/colors
        "prefer_css_page_size": True
    }
    
    if options:
        default_options.update(options)
    
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html_content)
        
        # Wait for any images or fonts to load
        page.wait_for_load_state('networkidle')
        
        page.pdf(path=output_path, **default_options)
        browser.close()

def html_file_to_pdf(html_file_path: str, output_path: str = "outputs/cv.pdf", options: dict = None):
    """Convert HTML file to PDF"""
    with open(html_file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    html_to_pdf(html_content, output_path, options)


# For more control over the PDF generation
# pdf_options = {
#     "format": "A4",
#     "margin": {
#         "top": "0.75in",
#         "bottom": "0.75in", 
#         "left": "0.75in",
#         "right": "0.75in"
#     },
#     "print_background": True,
#     "prefer_css_page_size": True,
#     "display_header_footer": False,
#     # "header_template": "<div style='font-size:10px; text-align:center;'>Header</div>",
#     # "footer_template": "<div style='font-size:10px; text-align:center;'>Page <span class='pageNumber'></span></div>",
# }

# html_to_pdf(resume_html, "resume_custom.pdf", pdf_options)