import scrapy
import json
from urllib.parse import urlparse
from scrapy.utils.project import get_project_settings

class GithubRepoSpider(scrapy.Spider):
    name = 'github_repo'
    
    API_BASE = "https://api.github.com/repos"
    
    def __init__(self, repo_url=None, *args, **kwargs):
        super(GithubRepoSpider, self).__init__(*args, **kwargs)
        if not repo_url:
            raise ValueError("Provide the repository URL with -a repo_url=URL")
        self.repo_url = repo_url
        
        parsed = urlparse(repo_url)
        path_parts = parsed.path.strip('/').split('/')
        self.owner = path_parts[0]
        self.repo = path_parts[1]
        
        self.api_url = f"{self.API_BASE}/{self.owner}/{self.repo}"
        self.languages_url = f"{self.api_url}/languages"
        self.commits_url = f"{self.api_url}/commits"
        self.settings = get_project_settings()
        
    def start_requests(self):
        headers = {'Accept': 'application/vnd.github.v3+json'}
        if self.settings.get('GITHUB_TOKEN'):
            headers['Authorization'] = f'token {self.settings["GITHUB_TOKEN"]}'
            
        # First request for repo metadata
        yield scrapy.Request(
            self.api_url,
            callback=self.parse_repo,
            headers=headers
        )
    
    def parse_repo(self, response):
        repo_data = json.loads(response.text)
        headers = response.request.headers
        
        # Initialize the item with basic data
        item = {
            'url': self.repo_url,
            'name': repo_data.get('name'),
            'full_name': repo_data.get('full_name'),
            'about': repo_data.get('description'),
            'last_updated': repo_data.get('updated_at'),
            'stars': repo_data.get('stargazers_count'),
            'forks': repo_data.get('forks_count'),
            'watchers': repo_data.get('watchers_count'),
            'open_issues': repo_data.get('open_issues_count'),
            'license': repo_data.get('license', {}).get('name') if repo_data.get('license') else None,
            'is_private': repo_data.get('private'),
            'size_kb': repo_data.get('size'),
            'default_branch': repo_data.get('default_branch'),
            # Initialize these to None
            'languages': None,
            'language_bytes': None,
            'total_commits': None,
            'last_commit': None,
            'last_commit_message': None,
            'last_commit_date': None
        }
        
        # Create a list to track pending requests
        pending_requests = [
            scrapy.Request(
                self.languages_url,
                callback=self.parse_languages,
                headers=headers,
                meta={'item': item.copy()}  # Important: use copy() to avoid reference issues
            ),
            scrapy.Request(
                f"{self.commits_url}?per_page=100",
                callback=self.parse_commits,
                headers=headers,
                meta={'item': item.copy()}
            )
        ]
        
        # Use an item buffer to collect all data
        buffer = {'item': item, 'completed': 0}
        
        for request in pending_requests:
            request.meta['buffer'] = buffer
            yield request
    
    def parse_languages(self, response):
        buffer = response.meta['buffer']
        languages = json.loads(response.text)
        
        # Update the buffer with languages data
        buffer['item'].update({
            'languages': list(languages.keys()) if languages else None,
            'language_bytes': languages,
        })
        
        return self.check_completion(buffer)
    
    def parse_commits(self, response):
        buffer = response.meta['buffer']
        commits_data = json.loads(response.text)
        
        # Get total commits count
        commit_count = len(commits_data)
        
        # Check if there are more commits beyond what we fetched
        link_header = response.headers.get('Link')
        if link_header:
            link_header = link_header.decode('utf-8')
            if 'rel="last"' in link_header:
                last_link = [link for link in link_header.split(', ') if 'rel="last"' in link][0]
                last_page = int(last_link.split('page=')[1].split('&')[0])
                commit_count = (last_page - 1) * 100 + len(commits_data)
        
        # Update the buffer with commits data
        buffer['item'].update({
            'total_commits': commit_count,
            'last_commit': commits_data[0]['sha'] if commits_data else None,
            'last_commit_message': commits_data[0]['commit']['message'] if commits_data else None,
            'last_commit_date': commits_data[0]['commit']['author']['date'] if commits_data else None
        })
        
        return self.check_completion(buffer)
    
    def check_completion(self, buffer):
        buffer['completed'] += 1
        # Only yield when both requests are complete
        if buffer['completed'] == 2:
            return buffer['item']