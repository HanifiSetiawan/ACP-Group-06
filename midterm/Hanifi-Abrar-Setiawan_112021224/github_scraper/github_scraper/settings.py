BOT_NAME = 'github_scraper'

SPIDER_MODULES = ['github_scraper.spiders']
NEWSPIDER_MODULE = 'github_scraper.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests
CONCURRENT_REQUESTS = 1  # Be gentle to GitHub's API
# settings.py
ROBOTSTXT_OBEY = False
DOWNLOAD_DELAY = 1  # Be polite to GitHub's API
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'application/vnd.github.v3+json'
}

# Disable cookies
COOKIES_ENABLED = False

# Configure item pipelines
ITEM_PIPELINES = {
    'github_scraper.pipelines.GithubScraperPipeline': 300,
}

# Set user agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

# GitHub API settings (optional)
#  GITHUB_TOKEN = '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'  # Set your token here if you have one