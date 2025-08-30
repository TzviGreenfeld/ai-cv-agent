import trafilatura
from playwright.sync_api import sync_playwright
import time

def read_job_description(url: str) -> str:
    # For MVP: just mock with static text instead of scraping
    return "We are looking for a Python developer with Azure and FastAPI experience."

def read_url(url: str) -> str:
    print(f"Fetching URL: {url}")
    
    # First try with trafilatura
    downloaded = trafilatura.fetch_url(url)
    
    if downloaded:
        # Try with different extraction parameters
        text = trafilatura.extract(
            downloaded, 
            include_links=True,
            include_formatting=True,
            favor_precision=False,
            favor_recall=True
        )
        
        if text:
            print("Successfully extracted with trafilatura")
            return text
    
    # If trafilatura fails, use playwright for JavaScript-heavy sites
    print("Trafilatura failed, trying Playwright...")
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Navigate to the URL
            page.goto(url, wait_until="networkidle")
            
            # Wait a bit for dynamic content to load
            time.sleep(3)
            
            # Try to extract text content
            # For job postings, look for common selectors
            job_content = None
            
            # Try different strategies to find job content
            selectors = [
                'main',  # Common main content area
                '[role="main"]',  # ARIA main role
                '.job-description',  # Common class for job descriptions
                '#job-details',  # Common ID
                'article',  # Article tag
                'div[class*="job"]',  # Divs with "job" in class name
                'body'  # Fallback to entire body
            ]
            
            for selector in selectors:
                try:
                    element = page.query_selector(selector)
                    if element:
                        content = element.inner_text()
                        if content and len(content) > 100:  # Ensure we have substantial content
                            job_content = content
                            print(f"Found content using selector: {selector}")
                            break
                except:
                    continue
            
            browser.close()
            
            if job_content:
                return job_content
            else:
                return "Failed to extract content from the page using Playwright."
                
    except Exception as e:
        print(f"Playwright error: {str(e)}")
        return f"Error using Playwright: {str(e)}"

if __name__ == "__main__":
    url = "https://jobs.careers.microsoft.com/global/en/job/1824895"
    # print(read_job_description(url))
    result = read_url(url)
    print("\n" + "="*50 + "\n")
    print("EXTRACTED CONTENT:")
    print(result[:1000] + "..." if len(result) > 1000 else result)
