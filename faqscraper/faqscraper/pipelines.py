# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import json
import os
from pathlib import Path


class FaqscraperPipeline:
    def process_item(self, item, spider):
        return item


class JsonWriterPipeline:
    def __init__(self):
        # Create data directory if it doesn't exist
        self.data_dir = Path(__file__).parent.parent.parent / 'data'
        self.data_dir.mkdir(exist_ok=True)
        
        self.items = []

    def process_item(self, item, spider):
        self.items.append(dict(item))
        return item

    def close_spider(self, spider):
        # Write all items at once with nice formatting
        output_file = self.data_dir / 'highrise_faq.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(
                self.items,
                f,
                indent=4,
                ensure_ascii=False
            )
