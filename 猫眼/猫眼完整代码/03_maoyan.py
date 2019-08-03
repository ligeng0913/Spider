'''
url='https://piaofang.maoyan.com/?ver=normal'
得到电影名称和实时票房，难点是票房的数字用了字体加密
参考网址https://juejin.im/post/5cc02c0bf265da03ab232b01
'''
from fontTools.ttLib import TTFont
import re
import requests
import base64
from lxml import etree
import csv

class MaoyanSpider(object):
    def __init__(self):
        self.url ='https://piaofang.maoyan.com/?ver=normal'
        self.headers = {
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        }
        self.proxy = {
            'http': 'http://127.0.0.1:8888',
            'https': 'https://127.0.0.1:8888'
        }
        self.list = []

        # 本地已经下载好的字体处理
        # 打开本地的ttf文件
        self.base_font = TTFont('font.ttf')
        self.base_uni_list = self.base_font.getGlyphOrder()[2:]

        # 写出第一次字体的编码和对应的字体
        self.origin_dict = {'uniF039': '0', 'uniF681': '4', 'uniEDAA': '8',
                       'uniE04D': '3', 'uniE586': '5', 'uniE96A': '6',
                       'uniE9E6': '2', 'uniE776': '7', 'uniE944': '1',
                       'uniE047': '9'}

    #得到解析以后正确的response
    def get_response(self):
        response = requests.get(url=self.url, headers=self.headers, proxies=self.proxy).content.decode('utf-8')  # 得到字节
        # 获取刷新之后在线的字体
        # 获取字体文件中的base64编码
        oneline_ttf_base64 = re.findall(r"base64,(.*)\) format", response)[0]
        oneline_base64_info = base64.b64decode(oneline_ttf_base64)
        with open('online_font.ttf', 'wb')as f:
            f.write(oneline_base64_info)
        # 网上动态下载的字体文件
        oneline_font = TTFont('online_font.ttf')
        oneline_uni_list = oneline_font.getGlyphOrder()[2:]
        for uni2 in oneline_uni_list:
            obj2 = oneline_font['glyf'][uni2]
            for uni1 in self.base_uni_list:
                # 获取编码uni1在base_font.ttf中对应的对象
                obj1 = self.base_font['glyf'][uni1]
                # 判断两个对象是否相等
                if obj1 == obj2:
                    # 修改为unicode编码格式
                    dd = "&#x" + uni2[3:].lower() + ';'
                    # 如果编码ubi2的Unicode编码格式 在response中,替换成origin_dict中的数字
                    if dd in response:
                        response = response.replace(dd, self.origin_dict[uni1])
                        self.parse_response(response)


    def parse_response(self,response):

        parse_html = etree.HTML(response)
        #基准xpath
        base_info = parse_html.xpath('//*[@id="ticket_tbody"]/ul')
        for base in base_info:
            # 电影名称
            name = base.xpath('./li[1]/b/text()')[0]
            # 票房
            box_office = base.xpath("./li[@class='c1']//i[@class='cs']/text()")[0]
            # 实时票房
            real_time = base.xpath('./li[2]/b/i/text()')[0]
            # 票房占比
            box_office_of = base.xpath('./li[3]/i/text()')[0]
            result = (name,box_office,real_time,box_office_of)

            self.write_response(result)

    def write_response(self,result):
        with open('maoyan.csv','a',newline='',encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(result)



    def main(self):
        self.get_response()
        print('下载完成')


if __name__=='__main__':
    spider = MaoyanSpider()
    spider.main()
