import asyncio
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import  CrawlerRunConfig

excluded_tags = [
        "script", "style", "nav", "header", "footer", 
        "aside", "button", "input", "form", "select", 
        "textarea", "svg", "iframe"
    ]

excluded_selector = """
        .cookie-banner, .privacy-notice, .social-share,
        [role="navigation"], [role="banner"], [role="contentinfo"],
        .navbar, .header, .footer, .sidebar, .menu,
        [class*="cookie"], [class*="consent"], [class*="share"]
    """

async def read_url(url: str) -> str:
    print(f"Fetching URL: {url}")

    crawler_run_config = CrawlerRunConfig(
        wait_until="networkidle", 
        verbose=False,
        excluded_tags=excluded_tags,
        excluded_selector=excluded_selector,
        remove_forms=True,
        keep_data_attributes=False,
        only_text=False,
        # delay_before_return_html=2
    )
    
    try:
        async with AsyncWebCrawler(
        ) as crawler:
            result = await crawler.arun(
                url=url,
                config=crawler_run_config
            )
            
            if result.success and result.markdown:
                return result.markdown
            else:
                raise ValueError(f"Failed to fetch content. Error: {result.error_message if hasattr(result, 'error_message') else 'Unknown error'}")

    except Exception as e:
        return f"Error fetching job description: {str(e)}"

async def read_job_description(url: str) -> str:
    result = await read_url(url)
    return result

if __name__ == "__main__":
    # Test with different job sites
    test_urls = [
        # "https://jobs.careers.microsoft.com/global/en/job/1824895",
        "https://www.google.com/about/careers/applications/jobs/results/115044372650566342-software-engineer-ii-ios-google-notifications?location=Tel%20Aviv%2C%20Israel&q=%22Software%20Engineer%22"
        # "https://www.activefence.com/careers/?comeet_pos=FD.B54&coref=1.10.r94_41D&t=1756629558672" # doesnt work
    ]
    for url in test_urls:
        result = asyncio.run(read_job_description(url))
        print(f"Job Description for {url}:\n{result}\n")
        print("="*80)