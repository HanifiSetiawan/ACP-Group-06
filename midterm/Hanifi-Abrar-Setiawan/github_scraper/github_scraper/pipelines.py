from scrapy.exporters import XmlItemExporter

class XmlExportPipeline:
    def __init__(self):
        self.file = None
    
    def open_spider(self, spider):
        self.file = open('github_repo.xml', 'wb')
        self.exporter = XmlItemExporter(self.file, item_element='repository', root_element='repositories')
        self.exporter.start_exporting()
    
    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()
    
    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item