# run_spider.py (in project root)
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from github_scraper.spiders.github_repo_spider import GithubRepoSpider

# Load project settings (including pipelines)
settings = get_project_settings()

# Configure the spider
process = CrawlerProcess(settings)
process.crawl(
    GithubRepoSpider,
    repo_url="https://github.com/vijawildan/Advance-Computer-Programming"  # ← REPLACE WITH YOUR TARGET REPO
)
process.start()