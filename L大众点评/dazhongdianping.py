import requests
import time
from lxml import etree
from threading import Thread
from queue import Queue
from fake_useragent import UserAgent
import re
from fontTools.ttLib import TTFont
import random


class DazhongSpider():
    def __init__(self):
        self.url = 'http://www.dianping.com/guangzhou/ch10/g110p{}'
        self.queue = Queue()
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Cookie': 'cy=4; cye=guangzhou; _lxsdk_cuid=16c51b7add9c8-0266f4c56ee1be-c343162-1fa400-16c51b7add953; _lxsdk=16c51b7add9c8-0266f4c56ee1be-c343162-1fa400-16c51b7add953; _hc.v=dd922dde-4227-97e9-1472-64a9bd2ad6c5.1564739088; s_ViewType=10; cityid=4; default_ab=shopList%3AC%3A4; _lx_utm=utm_source%3DBaidu%26utm_medium%3Dorganic; _lxsdk_s=16c56069623-b0-e1d-073%7C%7C41',
            'Host': 'www.dianping.com',
            'Upgrade-Insecure-Requests': '1',
            # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
            'User-Agent': UserAgent().random
        }
        self.headers_woff = {
            'Origin': 'http://www.dianping.com',
            'Referer': 'http://s3plus.meituan.net/v1/mss_0a06a471f9514fc79c981b5466f56b91/svgtextcss/c602026dfd7f5781a034d04b6287f622.css',
            # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
            'User-Agent': UserAgent().random
        }

    def parse_html(self,info_list):
        while not self.queue.empty():
            url = self.queue.get()
            time.sleep(random.uniform(3, 5))
            print(url)
            try:
                html = requests.get(url, headers=self.headers).content.decode('utf-8', 'ignore')
                woff_link = "http:" + re.findall(r'href="(.*?/svgtextcss/.*?)"', html)[0]
                woff_html = requests.get(woff_link, headers=self.headers_woff).content.decode('utf-8')
            except:
                self.queue.put(url)
                continue
            # 加密都是在标签svgmtsi中
            # 提取所有的class属性到集合中
            parse_html = etree.HTML(html)
            svgmtsi_list = parse_html.xpath('//svgmtsi')
            class_type = set()  # class_type 所有加密的class的集合
            for svgmtsi in svgmtsi_list:
                type = svgmtsi.xpath('./@class')[0].strip()
                class_type.add(type)

            # [(url, html的class类型),...,(url, html的class类型)] 所有的加密类型
            font_list = re.findall(r'src:url.*?src:url.*?url\("(.*?)"\);}\s\.(.*?){', woff_html, re.S)
            # 加密编码与解密字的对应
            corresponding_list = []
            for item in font_list:
                #　有个加密类型并未出现
                if item[1] not in class_type:
                    continue
                link = 'http:' + item[0]
                print(link)
                type = item[1]
                coding_list = self.ttfont(link)
                decryption_list = self.decryption(coding_list, info_list)
                corresponding_list.append({type: decryption_list})
            # 解密
            for type_dic in corresponding_list:
                for type, word_list in type_dic.items():
                    contents = re.findall(r'<svgmtsi class="'+ type + r'">(&#x.*?;)</svgmtsi>', html, re.S)
                    # <svgmtsi class="shopNum">&#xef55;</svgmtsi>
                    for content in contents:
                        for word_dic in word_list:
                            if content in word_dic:
                                html = re.sub(r'\s*?<svgmtsi class="'+ type +r'">' + content + '</svgmtsi>\s*?', word_dic[content], html)
            self.get_cotent(html)

    def decryption(self, coding_list, info_list):
        '''
        对字体反爬与自定义的字体进行对比解密
        :param coding_list: 反爬字体
        :param info_list: 自定义的反爬字体
        :return:[{'加密的编码':'字'}, ..., {'加密的编码':'字'}]
        '''
        for coding in coding_list:
            for key, value in coding.items():
                for info in info_list:
                    for word, word_info in info.items():
                        if value == word_info:
                            coding[key] = word
        return coding_list

    def ttfont(self, link):
        '''
        字体反爬
        :param link:
        :return:[{'字体的编码':[(x, y), ..., (x, y)]}, ..., {'字体编码':[(x, y), ..., (x, y)]}]
        '''
        html = requests.get(link, headers=self.headers_woff).content
        filename = link.split('/')[-1]
        with open(filename, 'wb') as f:
            f.write(html)
        font = TTFont(filename)
        # print(font)
        glyphOrder_list = font.getGlyphOrder()[2:]
        info_list = []
        for glyphOrder in glyphOrder_list:
            coding = glyphOrder.replace('uni', '&#x') + ';'
            glyf = font['glyf'][glyphOrder].coordinates
            info = {}
            info[coding] = []
            for item in glyf:
                info[coding].append(item)
            info_list.append(info)
        return info_list

    def index_ttfont(self):
        '''
        自定义字体反爬
        :return:[{'字':[(x, y), ...,(x, y)]},{'字':[(x, y), ...,(x, y)]}]
        '''
        font = TTFont('index.woff')
        font_str = '1234567890店中美家馆小车大市公酒行国品发电金心业商司超生装园场食有新限天面工服海华水房饰城乐汽香部利子老艺花专东肉菜学福饭' \
                   '人百餐茶务通味所山区门药银农龙停尚安广鑫一容动南具源兴鲜记时机烤文康信果阳理锅宝达地儿衣特产西批坊州牛佳化五米修爱北养卖建材三会鸡室红站' \
                   '德王光名丽油院堂烧江社合星货型村自科快便日民营和活童明器烟育宾精屋经居庄石顺林尔县手厅销用好客火雅盛体旅之鞋辣作粉包楼校鱼平彩上吧保永万' \
                   '物教吃设医正造丰健点汤网庆技斯洗料配汇木缘加麻联卫川泰色世方寓风幼羊烫来高厂兰阿贝皮全女拉成云维贸道术运都口博河瑞宏京际路祥青镇厨培力惠' \
                   '连马鸿钢训影甲助窗布富牌头四多妆吉苑沙恒隆春干饼氏里二管诚制售嘉长轩杂副清计黄讯太鸭号街交与叉附近层旁对巷栋环省桥湖段乡厦府铺内侧元购前' \
                   '幢滨处向座下県凤港开关景泉塘放昌线湾政步宁解白田町溪十八古双胜本单同九迎第台玉锦底后七斜期武岭松角纪朝峰六振珠局岗洲横边济井办汉代临弄团' \
                   '外塔杨铁浦字年岛陵原梅进荣友虹央桂沿事津凯莲丁秀柳集紫旗张谷的是不了很还个也这我就在以可到错没去过感次要比觉看得说常真们但最喜哈么别位能' \
                   '较境非为欢然他挺着价那意种想出员两推做排实分间甜度起满给热完格荐喝等其再几只现朋候样直而买于般豆量选奶打每评少算又因情找些份置适什蛋师气' \
                   '你姐棒试总定啊足级整带虾如态且尝主话强当更板知己无酸让入啦式笑赞片酱差像提队走嫩才刚午接重串回晚微周值费性桌拍跟块调糕'
        glyphOrder_list = font.getGlyphOrder()[2:]
        info_list = []
        for i in range(len(glyphOrder_list)):
            glyf = font['glyf'][glyphOrder_list[i]].coordinates
            info = {}
            info[font_str[i]] = []
            for item in glyf:
                info[font_str[i]].append(item)
            info_list.append(info)
        return info_list

    def get_cotent(self, decode_html):
        parse_html = etree.HTML(decode_html)
        li_list = parse_html.xpath('//div[@id="shop-all-list"]/ul/li')
        for li in li_list:
            name = li.xpath('.//h4/text()')[0].strip()
            comment_number = li.xpath('./div[2]/div[2]/a[1]/b/text()')[0].strip()
            average_price = li.xpath('./div[2]/div[2]/a[2]/b/text()')[0].strip()
            info_list = li.xpath('./div[2]/div[3]//text()')
            info = '{},{},{}'.format(info_list[1], info_list[5], info_list[-2])
            print(name, comment_number, average_price, info)

    def main(self):
        # 设置自定义的字体及编码
        info_list = self.index_ttfont()

        # for p in range(1, 20):
        #     self.queue.put(self.url.format(p))
        # t_list = []
        # for i in range(5):
        #     t = Thread(target=self.parse_html, args=(info_list,))
        #     t_list.append(t)
        #     t.start()
        #     time.sleep(random.uniform(1, 3))
        # for t in t_list:
        #     t.join()
        self.queue.put(self.url.format(3))
        self.parse_html(info_list)


if __name__ == '__main__':
    spider = DazhongSpider()
    spider.main()
