import json
from itemadapter import ItemAdapter
from scrapy.exporters import JsonItemExporter, XmlItemExporter

class GithubScraperPipeline:
    def __init__(self):
        self.file = None
        self.exporter = None

    def open_spider(self, spider):
        self.file = open('github_repositories.json', 'wb')
        self.exporter = JsonItemExporter(self.file, encoding='utf-8', ensure_ascii=False, indent=2)
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
        # Create custom exporter with indentation
        self.exporter = PrettyXmlItemExporter(
            self.file,
            item_element='repository',
            root_element='repositories',
            indent=4
        )
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item

# Custom XML exporter with proper indentation
class PrettyXmlItemExporter(XmlItemExporter):
    def __init__(self, file, **kwargs):
        # Set default values if not provided
        kwargs.setdefault('item_element', 'item')
        kwargs.setdefault('root_element', 'items')
        kwargs.setdefault('indent', 4)
        super().__init__(file, **kwargs)
        
    def start_exporting(self):
        self.xg.startDocument()
        self.xg.startElement(self.root_element, {})
        # Add newline and indentation after root element
        self.xg.characters("\n")
        
    def export_item(self, item):
        # Add indentation before each item
        self.xg.characters(" " * self.indent)
        self._export_xml_item(item)
        # Add newline after each item
        self.xg.characters("\n")
        
    def _beautify_value(self, value, depth=1):
        """Recursively format nested structures with proper indentation"""
        if isinstance(value, dict):
            self.xg.characters("\n")
            for k, v in value.items():
                self.xg.characters(" " * (self.indent * (depth + 1)))
                self.xg.startElement(k, {})
                self._beautify_value(v, depth + 1)
                self.xg.endElement(k)
                self.xg.characters("\n")
            self.xg.characters(" " * (self.indent * depth))
        else:
            if value is None:
                value = ''
            self.xg.characters(str(value))