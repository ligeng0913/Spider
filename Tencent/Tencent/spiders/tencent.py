# -*- coding: utf-8 -*-
import json
from ..items import TencentItem
import scrapy


class TencentSpider(scrapy.Spider):
    name = 'tencent'
    allowed_domains = ['careers.tencent.com']
    one_url ='https://careers.tencent.com/tencentcareer/api/post/Query?timestamp=1562741982891&countryId=&cityId=&bgIds=&productId=&categoryId=&parentCategoryId=&attrId=&keyword=&pageIndex={}&pageSize=10&language=zh-cn&area=cn'
    start_urls = [one_url.format(1)]
    two_url ='https://careers.tencent.com/tencentcareer/api/post/ByPostId?timestamp=1562742974336&postId={}&language=zh-cn'

    def parse(self,response):
        for page_index in range(1,51):
            url = self.one_url.format(page_index)
            yield scrapy.Request(
                url=url,
                callback=self.parse_one
            )

    def parse_one(self,response):
        html = json.loads(response.text)
        for job in html['Data']['Posts']:
            item = TencentItem()
            item['zh_name']=job['RecruitPostName']
            item['zh_type']=job['CategoryName']
            #postId:拼接二级页面的地址
            post_id = job['PostId']
            two_url = self.two_url.format(post_id)
            yield scrapy.Request(
                url=two_url,
                meta={'item':item},
                callback=self.parse_two
            )
    def parse_two(self,response):
        item = response.meta['item']
        html = json.loads(response.text)
        #职责
        item['zh_duty'] = html['Data']['Responsibility']
        #要求
        item['zh_require']=html['Data']['Requirement']
        yield item