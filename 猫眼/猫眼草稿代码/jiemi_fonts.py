'''
映射字体和真正的字体
'''
from fontTools.ttLib import TTFont

#读取字体文件

ttfont= TTFont('font.ttf')
#存储到本地
ttfont.saveXML('123.xml')

base_uni_list = ttfont.getGlyphOrder()[2:]
for uni2 in base_uni_list:
    obj2 = ttfont['glyf'][uni2]
    dd = uni2[3:].lower()
    # print(dd)
    print(uni2)



#写出第一次字体的编码和对应的字体
origin_dict ={'uniF039':'0','uniF681':'4','uniEDAA':'8',
              'uniE04D':'3','uniE586':'5','uniE96A':'6',
              'uniE9E6':'2','uniE776':'7','uniE944':'1',
              'uniE047':'9'}



