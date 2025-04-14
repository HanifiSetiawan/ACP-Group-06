import json
from itemadapter import ItemAdapter
from scrapy.exporters import JsonItemExporter, XmlItemExporter

class GithubScraperPipeline:
    def __init__(self):
        self.file = None
        self.exporter = None

    def open_spider(self, spider):
        # Open file in binary mode
        self.file = open('github_repositories.json', 'wb')
        # Initialize JSON exporter
        self.exporter = JsonItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item

class XmlExportPipeline:
    def __init__(self):
        self.file = None
        self.exporter = None

    def open_spider(self, spider):
        self.file = open('github_repositories.xml', 'wb')
        self.exporter = XmlItemExporter(self.file, item_element='repository', root_element='repositories')
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item
    
ITEM_PIPELINES = {
    'github_scraper.pipelines.XmlExportPipeline': 300,
}