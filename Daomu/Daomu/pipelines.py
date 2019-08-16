# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


class DaomuPipeline(object):
    def process_item(self, item, spider):
        filename = '../盗墓小说/{}_{}-{}'.format(
            item['volume_name'],
            item['zh_num'],
            item['zh_name']
        )
        with open(filename,'w') as f:
            f.write(item['zh_content'])
        return item
