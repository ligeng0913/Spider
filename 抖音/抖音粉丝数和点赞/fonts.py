'''
用来将字体文件转换为可以读的模式
'''
from fontTools.ttLib import TTFont

#读入字体文件
ttfont=TTFont('iconfont_9eb9a50 .woff')

#保存成xml文件　变成可读的xml文件用来保存数据的，传输数据
ttfont.saveXML('iconfont_9eb9a50 .xml')