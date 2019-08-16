'''
http://www.sinopipenet.com/price/管材管件网
'''
import requests
from fake_useragent import UserAgent
import random
from lxml import etree
import csv
from queue import Queue
from threading import Thread
import time

class GuancaiSpider(object):
    def __init__(self):
        self.url='http://www.sinopipenet.com/price/{}.html'
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Cookie': 'Hm_lvt_eaadb7e0447a51e01f6f7696f2887ea1=1565916994; Hm_lvt_8f1c820bda50bc9c1ac41b7760cc1160=1565916995; Hm_lpvt_eaadb7e0447a51e01f6f7696f2887ea1=1565917013; Hm_lpvt_8f1c820bda50bc9c1ac41b7760cc1160=1565919093',
            'Host': 'www.sinopipenet.com',
            'Referer': 'http://www.sinopipenet.com/price/2.html',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': UserAgent().random,
        }
        self.url_queue=Queue()

    #url入队列
    def url_in(self):
        for page in range(1,5895):
            url =self.url.format(str(page))
            self.url_queue.put(url)

    #线程事件函数（请求，解析，保存)
    def get_page(self):
        while True:
            #从队列中获取url
            if not self.url_queue.empty():
                url=self.url_queue.get()
                res = requests.get(url,headers=self.headers)
                res.encoding='utf-8'
                html=res.text
                # print(html)
                self.parse_page(html)
            else:
                break

    def parse_page(self,html):
        parse_html=etree.HTML(html)
        #基准xpath
        all_info = parse_html.xpath('//table[@class="lp-table "]/tr')
        # print(all_info)
        for item in all_info[1:]:
            #品名
            pingming=item.xpath('./td[1]/div/text()')[0]
            #单位
            if item.xpath('./td[2]/text()'):
                danwei=item.xpath('./td[2]/text()')[0]
            else:
                danwei ='/'
            #类型
            Offer_type=item.xpath('./td[3]/text()')[0]
            #报价
            price=item.xpath('./td[4]/text()')[0]
            #规格

            if item.xpath('./td[5]/text()'):
                size=item.xpath('./td[5]/text()')[0]
            else:
                size ='/'
            #产地
            if item.xpath('./td[6]/text()'):
                field=item.xpath('./td[6]/text()')[0]
            else:
                field ='/'

            #发布时间
            time=item.xpath('./td[7]/text()')[0]

            info=(pingming,danwei,Offer_type,price,size,field,time)
            self.write_info(info)
    #导入csv文件
    def write_info(self,info):
        list=[]
        list.append(info)
        # print(list)
        with open('guangcai.csv','a',newline='')as f:
            writer=csv.writer(f)
            writer.writerows(list)



    def main(self):
        #所有url地址入队列
        self.url_in()
        #创建线程
        t_list=[]
        #创建并启动线程
        for i in range(10):
            t=Thread(target=self.get_page)
            t_list.append(t)
            t.start()
        #回收线程
        for j in t_list:
            j.join()






if __name__=='__main__':
    start =time.time()
    spider=GuancaiSpider()
    spider.main()
    end=time.time()
    print('执行时间为:%.2f'%(end-start))

