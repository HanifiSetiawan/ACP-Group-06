import scrapy

class GithubSpider(scrapy.Spider):
    name = "github_spider"
    allowed_domains = ["github.com"]
    start_urls = ["https://github.com/vijawildan?tab=repositories"]

    def parse(self, response):
        repo_links = response.css('div.d-inline-block h3 a::attr(href)').getall()
        for link in repo_links:
            yield response.follow(url=link, callback=self.parse_repo)

    def parse_repo(self, response):
        repo_url = response.url
        name = repo_url.split('/')[-1]

        about = response.css('p.f4.my-3::text').get()
        about = about.strip() if about else None

        is_empty = response.css('div.Box-body p::text').re_first(r"This repository is empty")

        if not about and not is_empty:
            about = name

        updated = response.css('relative-time::attr(datetime)').get()

        if not is_empty:
            languages = response.css('ul[data-testid="repo-language-list"] li span::text').getall()
            commits = response.css('li.commits a span::text').re_first(r'\d+')
        else:
            languages = None
            commits = None

        yield {
            'url': repo_url,
            'about': about,
            'last_updated': updated,
            'languages': languages,
            'commits': commits
        }
