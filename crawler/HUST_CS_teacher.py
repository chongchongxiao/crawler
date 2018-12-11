import requests
from lxml import etree
from fake_useragent import UserAgent
import time
import redis
# 这里要进行编码格式的转换，否则会中文乱码,返回html代码
def get_html_code(url):
    ua = UserAgent()
    headers = {"User-Agent": ua.random}
    # url = 'http://faculty.hust.edu.cn/chenkai/zh_CN/index.htm'
    req = requests.get(url, headers=headers)
    # print(req.headers['content-type'])
    # print(req.encoding)
    # print(req.apparent_encoding)
    # print(requests.utils.get_encodings_from_content(req.text))
    # 解决中文乱码问题
    # 因为返回的内容采用的是ISO-8859-1编码，但实际编码是utf-8，所以会出现中文乱码问题
    if req.encoding == 'ISO-8859-1':
        encodings = requests.utils.get_encodings_from_content(req.text)  # 寻找html代码头部的设置的编码
        if encodings:
            encoding = encodings[0]
        else:
            encoding = req.apparent_encoding
    # 以html头部设置的编码进行解码，并重新以utf-8进行编码
    encode_content = req.content.decode(encoding, 'replace').encode('utf-8', 'replace')
    # 新生成的代码时二进制格式，重新转成字节流
    html = bytes.decode(encode_content)
    return html


def get_url_list():
    url = 'http://cs.hust.edu.cn/szdw/szll.htm'
    url_list = []
    # 循环获取所有的老师个人主页的链接
    while True:
        html = get_html_code(url)
        selector = etree.HTML(html)
        urls = selector.xpath('//table[@class="table table-hover"]/tbody/tr/td/a/@href')
        next = selector.xpath('//a[contains(text(),"下页")]/@href')

        # 前几页的链接是完整链接，后面链接有变化，需要拼接
        for i in range(len(urls)):
            if urls[i] == '#':
                continue
            if urls[i].find('http') != -1:
                continue
            urls[i] = url[0:22] + urls[i][-18:]
        url_list.extend(urls)

        if not next:
            break
        next = next[0]
        url = url[0:31] +'/' + next[-5:]

    return url_list

def get_message(url):
    html = get_html_code(url)
    selector = etree.HTML(html)
    name = selector.xpath('//div[@class="blockwhite JS-display"]/div/div[@class="info"]/h2/text()')
    title = selector.xpath('//div[@class="dft-side"]/div[@class="blockwhite Psl-info"]/div[@class="cont"]/p/text()')
    if not name:
        return
    message = {}
    message['姓名'] = name[0]


    # 清除转义字符
    tmp = title
    title = []
    for s in tmp:
        str = "".join(s.split())
        if(str.find('性别')!=-1):
            title.append(str[0:str.find('性别')])
            title.append(str[str.find('性别'):])
            continue
        if str:
            title.append(str)

    message['职称'] = title[0]+','+title[1]
    for i in range(2, len(title)):
        str = title[i].split('：')
        if str[1]=='':
            message[str[0]] = title[i+1:]
            break
        message[str[0]] = str[1]

    resume = selector.xpath('//div[@class="dft-midcont"]/div[@class="blockwhite Psl-info"]/div[@class="cont"]/p/text()')
    if resume:
        message['个人简介'] = resume[0]
    else:
        message['个人简介'] = ''

    #之前想的是获取更多内容，发现网页过于复杂，还是算了
    # resume = selector.xpath('//div[@class="dft-midcont"]/div[@class="blockwhite Psl-info"]/div[@class="cont"]/p/a/@href')
    # if resume:
    #     new_url = url[0:26]+resume[0]
    #     new_html = get_html_code(new_url)
    #     new_selector = etree.HTML(new_html)
    #     new_resume = new_selector.xpath('//div[@class="atccont"]/p[2]/span/text()')
    #     message['个人简介'] = new_resume
    # else:
    #     new_resume = selector.xpath('//div[@class="dft-midcont"]/div[@class="blockwhite Psl-info"]/div[@class="cont"]/p/text()')
    #     message['个人简介'] = new_resume[0]

    direction = selector.xpath('//div[@class="dft-rightcont"]/div[@class="blockwhite Rsh-focus"]/div[@class="cont"]/ul/li/text()')
    if direction:
        value = ''
        for dir in direction:
            value += dir
        message['研究方向'] = value
    else:
        message['研究方向'] = '暂无内容'

    # 这里想爬访问量做个排序啥的，但是爬不下来，因为span标签下的内容是动态添加进去的，所以用xpath爬不出来
    # visit = selector.xpath('//div[@class="fwupd"]/p/text()')
    # visit = selector.xpath('//div[@class="fwupd"]/p/span/')
    # print(visit)

    # 正则也提取不出来访问量，难受
    # reg = r'<span id="u19_click">(.*)</span>'
    # reg_img = re.compile(reg)
    # visit = reg_img.findall(html)  # 进行匹配
    # print(visit)
    return message

# 把信息保存在redis数据库中
def save_message():
    # url_list = get_url_list()
    # f = open('urls', 'w')
    # for url in url_list:
    #     if url == '#':
    #         continue
    #     f.write(url)
    #     f.write('\n')
    # f.close()

    f = open('urls', 'r')
    urls = f.read().splitlines()
    f.close()
    keys = ['毕业院校', '在职信息', '性别', '个人简介', '学位', '学历',
            '学科', '所在单位', '研究方向', '姓名', '职称']
    r = redis.Redis(host='localhost', port='6379')

    k = 1
    for url in urls:
        # 获取信息
        mes = get_message(url)
        #空信息直接跳过
        if not mes:
            continue
        print(mes)

        #如果信息没有姓名，那么属于无效信息
        if not '姓名' in mes.keys():
            continue
        name = mes['姓名']
        for key in keys:
            # 插入每个key之前都要验证这个key是否存在，如果不存在，插入一条空信息
            if key in mes.keys():
                value = ''
                if type(key) is list:
                    for val in mes[key]:
                        value += val
                        value += ','
                else:
                    value = mes[key]
                r.lpush(name, value)
            else:
                r.lpush(name, '无')

        # 防止ip被封，读完一个网页之后，停顿一段时间
        time.sleep(3)






if __name__ == '__main__':
    save_message()