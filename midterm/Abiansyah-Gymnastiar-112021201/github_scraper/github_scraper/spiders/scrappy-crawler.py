import scrapy
import json
from urllib.parse import quote
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

class GitHubAPISpider(scrapy.Spider):
    name = "github_api_spider"
    
    # Configuration
    GITHUB_USER = "abi-gymnastiar"  # CHANGE THIS
    ACCESS_TOKEN = None  # Optional: "ghp_your_token_here"
    OUTPUT_FILE = "github_repos.xml"

    def start_requests(self):
        headers = {"Accept": "application/vnd.github.v3+json"}
        if self.ACCESS_TOKEN:
            headers["Authorization"] = f"token {self.ACCESS_TOKEN}"
        
        yield scrapy.Request(
            url=f"https://api.github.com/users/{self.GITHUB_USER}/repos",
            headers=headers,
            callback=self.parse_repos
        )

    def parse_repos(self, response):
        try:
            repos = json.loads(response.text)
        except json.JSONDecodeError:
            self.logger.error("API response is not valid JSON")
            return

        for repo in repos:
            item = {
                "url": repo["html_url"],
                "about": repo["description"] or repo["name"],
                "last_updated": repo["updated_at"],
                "languages": "None",
                "commits": "0"  # Default to 0 commits
            }

            # Skip empty repos early
            if repo["size"] == 0:
                yield item
                continue

            # Request languages
            yield scrapy.Request(
                url=repo["languages_url"],
                headers={"Accept": "application/vnd.github.v3+json"},
                callback=self.parse_languages,
                meta={"item": item, "repo_name": repo["name"]}
            )

    def parse_languages(self, response):
        item = response.meta["item"]
        repo_name = response.meta["repo_name"]
        
        try:
            langs = json.loads(response.text)
            item["languages"] = ", ".join(langs.keys()) if langs else "None"
        except json.JSONDecodeError:
            item["languages"] = "None"

        # Properly encode repository name for URL
        encoded_name = quote(repo_name)
        commits_url = f"https://api.github.com/repos/{self.GITHUB_USER}/{encoded_name}/commits?per_page=1"
        
        yield scrapy.Request(
            url=commits_url,
            headers={"Accept": "application/vnd.github.v3+json"},
            callback=self.parse_commit_count,
            meta={"item": item},
            method="HEAD"
        )

    def parse_commit_count(self, response):
        item = response.meta["item"]
        
        if response.status == 200:
            link_header = response.headers.get("Link", b"").decode()
            if 'rel="last"' in link_header:
                last_page = link_header.split('page=')[-1].split('>')[0]
                item["commits"] = last_page if last_page.isdigit() else "0"
        elif response.status == 409:  # Empty repository
            item["commits"] = "0"
        
        yield item

def run_spider(username=None, token=None):
    """Run the GitHub spider programmatically"""
    process = CrawlerProcess(get_project_settings())
    
    # Allow runtime configuration
    spider_kwargs = {}
    if username:
        spider_kwargs['GITHUB_USER'] = username
    if token:
        spider_kwargs['ACCESS_TOKEN'] = token
    
    process.crawl(GitHubAPISpider, **spider_kwargs)
    process.start()



def main():
    """Main entry point for command line execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Scrape GitHub repositories')
    parser.add_argument('-u', '--username', help='GitHub username to scrape')
    parser.add_argument('-t', '--token', help='GitHub access token')
    args = parser.parse_args()
    
    run_spider(username=args.username, token=args.token)

if __name__ == "__main__":
    main()