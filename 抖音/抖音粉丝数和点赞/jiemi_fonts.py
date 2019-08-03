'''
用来映射字体和真正的字体
'''
from fontTools.ttLib import TTFont
import re
import requests
#读取字体文件
ttfont = TTFont('iconfont_9eb9a50 .woff')


#读取映射表,网页中的加密的字符串到num_x
best_cmap= ttfont['cmap'].getBestCmap()


def get_best_cmap():
    """
    这个函数用来返回映射表

    :return: 返回映射表
    """
    new_best_cmpa = {}
    for key,value in best_cmap.items():
        # print(hex(key),value)#hex转成十六进制
        # new_best_cmpa.update({key:value})
        new_best_cmpa[hex(key)] =value
        #yield new_best_cmap
    print(new_best_cmpa)
    return new_best_cmpa


def get_num_cmap():
    """

    :return:返回num和真正的数字的映射关系
    """
    num_map ={
        'x':'',
        'num_':'1',
        'num_1':'0',
        'num_2':'3',
        'num_3':'2',
        'num_4':'4',
        'num_5':'5',
        'num_6':'6',
        'num_7':'9',
        'num_8':'7',
        'num_9':'8',
    }
    return num_map

def map_cmap_num(get_best_cmap,get_num_cmap):
    """
    'num_2':'3' --> 0xe604:3
    :param get_best_cmap: 函数
    :param get_num_cmap: 函数
    :return: 返回值
    """
    result = {}
    for key,value in get_best_cmap().items():
        key = re.sub('0','&#',key,count=1)+';'
        result[key] = get_num_cmap()[value]

    return result
def get_html(url):
    """
    获取网页源码
    :param url:
    :return:
    """
    headers = {'User-Agent':'Mozilla/5.0'}
    response=requests.get(url,headers=headers).text

    return response

def resplace_num_and_cmap(result,response):
    for key ,value in result.items():
        if key in response:
            response =re.sub(key,value,response)
    return response

def save_to_file(response):
    """
    保存
    :param response:
    :return:
    """
    with open('douyin.html','w',encoding='utf-8') as f:
        f.write(response)


if __name__=='__main__':
    result =map_cmap_num(get_best_cmap,get_num_cmap)
    url = 'https://www.iesdouyin.com/share/user/58590836959?u_code=1496ajejh&sec_uid=MS4wLjABAAAA0gR10qCxbMYkuUcH7YJrGXEllrMzEjw6AmogeWie5Ls&utm_campaign=client_share&app=aweme&utm_medium=ios&tt_from=copy&utm_source=copy'
    response = get_html(url)

    response=resplace_num_and_cmap(result,response)
    save_to_file(response)








