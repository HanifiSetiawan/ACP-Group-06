# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders. 
from .github_repo_spider import GithubRepoSpider
__all__ = ['GithubRepoSpider']  