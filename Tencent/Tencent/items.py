# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class TencentItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    zh_name = scrapy.Field()
    #类别
    zh_type = scrapy.Field()
    #职责
    zh_duty = scrapy.Field()
    #要求
    zh_require = scrapy.Field()
