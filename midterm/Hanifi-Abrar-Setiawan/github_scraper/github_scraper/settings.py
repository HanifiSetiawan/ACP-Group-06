ITEM_PIPELINES = {
    'github_scraper.pipelines.XmlExportPipeline': 300,
}
SPIDER_MODULES = ['github_scraper.spiders']
ROBOTSTXT_OBEY = False # Respect GitHub's robots.txt
DOWNLOAD_DELAY = 2      # Be polite to GitHub's servers
RETRY_TIMES = 3
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
AUTOTHROTTLE_ENABLED = True
CONCURRENT_REQUESTS_PER_DOMAIN = 1
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en',
}