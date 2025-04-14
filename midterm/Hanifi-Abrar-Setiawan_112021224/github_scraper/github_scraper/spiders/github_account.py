import scrapy
import json
from urllib.parse import urlparse
from scrapy.utils.project import get_project_settings

class GithubAccountSpider(scrapy.Spider):
    name = 'github_account'
    
    API_BASE = "https://api.github.com"
    
    def __init__(self, username=None, *args, **kwargs):
        super(GithubAccountSpider, self).__init__(*args, **kwargs)
        if not username:
            raise ValueError("Provide GitHub username with -a username=NAME")
        self.username = username
        self.settings = get_project_settings()
        
    def start_requests(self):
        headers = {'Accept': 'application/vnd.github.v3+json'}
        if self.settings.get('GITHUB_TOKEN'):
            headers['Authorization'] = f'token {self.settings["GITHUB_TOKEN"]}'
            
        # Get all repositories
        yield scrapy.Request(
            f"{self.API_BASE}/users/{self.username}/repos?per_page=100",
            callback=self.parse_repo_list,
            headers=headers
        )
    
    def parse_repo_list(self, response):
        repos = json.loads(response.text)
        headers = response.request.headers
        
        for repo in repos:
            item = {
                'url': repo['html_url'],
                'title': repo['name'],
                'about': repo['description'],
                'last_updated': repo['updated_at'],
                'total_commits': 0,  # Initialize to 0
                'last_commit': None,
                'last_commit_date': None
            }
            
            # Get accurate commit count using contributors API
            contributors_url = f"{self.API_BASE}/repos/{self.username}/{repo['name']}/contributors?anon=1"
            yield scrapy.Request(
                contributors_url,
                callback=self.parse_contributors,
                headers=headers,
                meta={'item': item}
            )
        
        # Handle pagination for repositories
        if 'link' in response.headers:
            links = response.headers['link'].decode('utf-8')
            if 'rel="next"' in links:
                next_url = [link.split(';')[0][1:-1] 
                          for link in links.split(', ') 
                          if 'rel="next"' in link][0]
                yield scrapy.Request(next_url, callback=self.parse_repo_list, headers=headers)
    
    def parse_contributors(self, response):
        item = response.meta['item']
        contributors_data = json.loads(response.text)
        
        # Calculate total commits from contributors data
        total_commits = sum(contributor['contributions'] 
                           for contributor in contributors_data)
        item['total_commits'] = total_commits
        
        # Now get the last commit details
        commits_url = f"{self.API_BASE}/repos/{self.username}/{item['title']}/commits?per_page=1"
        yield scrapy.Request(
            commits_url,
            callback=self.parse_last_commit,
            headers=response.request.headers,
            meta={'item': item}
        )
    
    def parse_last_commit(self, response):
        item = response.meta['item']
        commits_data = json.loads(response.text)
        
        if commits_data:
            item['last_commit'] = commits_data[0]['sha']
            item['last_commit_date'] = commits_data[0]['commit']['author']['date']
        
        yield item