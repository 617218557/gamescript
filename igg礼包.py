# coding:utf-8
import urllib
from urllib import request
from urllib import parse
import json
import ssl
from bs4 import BeautifulSoup
import time
import threading
import random
from urllib.parse import urlparse
import re

ssl._create_default_https_context = ssl._create_unverified_context

codeList = set()

USER_AGENTS = [
               'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 OPR/26.0.1656.60',
               'Opera/8.0 (Windows NT 5.1; U; en)',
               'Mozilla/5.0 (Windows NT 5.1; U; en; rv:1.8.1) Gecko/20061208 Firefox/2.0.0 Opera 9.50',
               'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; en) Opera 9.50',
               'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0',
               'Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10',
               'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.57.2 (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2',
               'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36',
               'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
               'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/10.0.648.133 Safari/534.16',
               'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/2.0 Safari/536.11',
               'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER',
               'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; LBBROWSER)',
               'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 SE 2.X MetaSr 1.0',
               'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SV1; QQDownload 732; .NET4.0C; .NET4.0E; SE 2.X MetaSr 1.0)',
               'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122 UBrowser/4.0.3214.0 Safari/537.36'
               ]

def getCode():
    headers = {'Accept':'*/*',
    'Accept-Encoding':'br, gzip, deflate',
    'Accept-Language':'zh-cn',
    'Content-Type':'application/json',
    'User-Agent': random.choice(USER_AGENTS)}
    url='https://lm.176.com/project/wechat_miniprog/welfare_new.php?ac_id=63&from=0&limit=10&typ=1&page=1'
    request = urllib.request.Request(url, headers=headers)
    response = urllib.request.urlopen(request)
    content = response.read()
    jsonData = json.loads(content)
    ac_id = jsonData['data'][0]['ac_id']
    id = jsonData['data'][0]['id']
    print(ac_id)
    print(id)

    url = 'https://lm.176.com/project/wechat_miniprog/content.php?ac_id=' + str(ac_id) + '&a_id=' + str(id)
    request = urllib.request.Request(url ,headers=headers)
    response = urllib.request.urlopen(request)
    html = response.read()
    
    soup = BeautifulSoup(html,'lxml')
    #result = soup.find_all(style="font-size:14px;")
    result = soup.find_all('p')
   
    index = 0
    code = ''
    for soupStr in result:
        print(soupStr.get_text())
        if index == 0 :
            code = re.findall(r'([A-Z0-9]{8})',soupStr.get_text())[0]
        index = index + 1
    return code

def getReward(code):
    if not code :
        return
    if code in codeList:
        print(code+'该礼包码已自动领取过')
        return
    #codeList.add(code)
    url = 'http://lordsmobile.igg.com/event/cdkey/ajax.php?game_id=1051089902'
    iggId = {'339205745','368281116','359567511','362595149','362981673','376424371','375721672','427484233','421399109'}

    for id in iggId :
        f = {'ac': 'receive','iggid': id,'cdkey': code}
        data = urllib.parse.urlencode(f).encode('utf-8')
        request = urllib.request.Request(url, data)
        response = urllib.request.urlopen(request).read()
        jsonData = json.loads(response)
        print(id + '   '+ code + '   '+jsonData['msg'])

#通过搜狗微信搜索接口
def getSmallProgramCodeBySougou():
    headers = {  'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language':'zh-CN,zh;q=0.9',
    'Content-Type':'application/json',
    'Connection': 'keep-alive',
    'User-Agent': random.choice(USER_AGENTS)}

    url='http://weixin.sogou.com/weixin?type=1&s_from=input&query=%E7%8E%8B%E5%9B%BD%E7%BA%AA%E5%85%83&ie=utf8&_sug_=n&_sug_type_='

    #通过代理爬数据
    try_again_count = 0
    while try_again_count<5:
        httpproxy_handler = urllib.request.ProxyHandler({'http:':get_proxy()})
        opener = urllib.request.build_opener(httpproxy_handler)
        request = urllib.request.Request(url,headers=headers)
        response = opener.open(request)
        html = response.read()
        soup = BeautifulSoup(html,'lxml')
        result = soup.find_all(uigs="account_article_0")
        print('第'+str(try_again_count)+'次请求搜狗'+str(len(result)))
        try_again_count+=1
        if len(result)>0:
            try_again_count=5


    request = urllib.request.Request(url ,headers=headers)
    response = urllib.request.urlopen(request)
    html = response.read()
    soup = BeautifulSoup(html,'lxml')
    result = soup.find_all(uigs="account_image_0")
    link = result[0].attrs['href']
    
    request = urllib.request.Request(url=link, headers=headers)
    response = urllib.request.urlopen(request)
    html = response.read()
    soup = BeautifulSoup(html,'lxml')
    result = soup.find_all('span')
    final_result = matchCode(result)
    if(final_result != None):
        tips = final_result.find_all_next('p',text=re.compile('\*'))
    #    tips = final_result.find_all_next('p',limit = 3)
        print(soup.title.string)
        print(final_result.get_text())
        for string1 in tips:
            print(string1.get_text())
        return final_result.get_text()
    print('没有获取到礼包码')
    return ''

#正则匹配公众号礼包码
def matchCode(result):
    for tmp_soup in result:
        if re.match(r'[A-Z0-9]{8}',tmp_soup.get_text()):
            return tmp_soup
    return None

#爬代理
def get_proxy():
    page = random.randint(1,500)
    headers = {'User-Agent' : random.choice(USER_AGENTS)}
    request = urllib.request.Request("https://www.kuaidaili.com/free/inha/"+str(page), headers=headers)
    html = urllib.request.urlopen(request).read()
    # print html
    soup = BeautifulSoup(html,'lxml')
    ip = soup.find_all('td',attrs = {'data-title':'IP'})
    port = soup.find_all('td',attrs = {'data-title':'PORT'})
    index = random.randint(0,len(ip)-1)
    return ip[index].get_text()+':'+port[index].get_text()

def start():
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    print('----------------------------------------------------------------------------')
    #手动领取激活码
    getReward('9CYWSATY')

    
    
    print('小程序礼包')
        #try:
    code = getCode()
        #except BaseException:
        #print('exception')
        #else:
    getReward(code)

#    print('----------------------------------------------------------------------------')
#    print('公众号礼包')
#    try:
#        code = getSmallProgramCodeBySougou()
#    except BaseException:
#        print('exception')
#    else:
#        getReward(code)

    global timer
    timer = threading.Timer(3*60,start).start()
    print('\n\n\n')

if __name__ == "__main__":
    start()
