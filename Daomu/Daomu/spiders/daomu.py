# -*- coding: utf-8 -*-
import scrapy
from ..items import DaomuItem

class DaomuSpider(scrapy.Spider):
    name = 'daomu'
    allowed_domains = ['daomubiji.com']
    start_urls = ['http://www.daomubiji.com/']

    #解析一级页面的parse函数
    def parse(self, response):
        #link_list :['http://xxx/dao-mu-bi-ji-1','','']
        link_list = response.xpath('//ul[@class="sub-menu"]/li/a/@href').extract()
        print(link_list)
        print('*'*50)
        for link in link_list:
            #交给调度器
            yield scrapy.Request(
                url = link,
                callback=self.parse_two_html
            )
    #解析二级页面函数（卷名 章节数 章节名 链接）
    def parse_two_html(self,response):
        #基准xpath
        article_list = response.xpath('//article')
        for article in article_list:
            #创建item对象
            item = DaomuItem()
            #info_list:['七星鲁王','第一章','血尸']
            info_list = article.xpath('./a/text()').extract_first().split()
            if len(info_list)==3:
                item['volume_name'] = info_list[0]
                item['zh_num'] = info_list[1]
                item['zh_name'] = info_list[2]

            else:
                item['volume_name'] = info_list[0]
                item['zh_num'] = ''
                item['zh_name'] = info_list[1]
            #提取链接并发给调度器入队列
            item['zh_link'] = article.xpath('./a/@href').extract_first()
            yield scrapy.Request(
                url = item['zh_link'],
                #meta参数：传递item对象到下一个解析函数
                meta={'item':item},
                callback=self.parse_three_html
            )
    #解析三级页面的小说内容
    def parse_three_html(self,response):
        #获取上一个函数传递过来的item对象
        item = response.meta['item']
        #content_list:['段落1','段落2','','']
        content_list=response.xpath('//article[@class="article-content"]//p/text()').extract()
        item['zh_content'] = '\n'.join(content_list)

        yield item








