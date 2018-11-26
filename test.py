import requests
import redis

r = redis.Redis(host='localhost', port='6379', db='0')
print(r.ping())



keys = ['毕业院校', '在职信息', '性别', '个人简介', '学位', '学历', '学科', '所在单位', '研究方向', '姓名', '职称']

names = r.keys()
print(len(names))
for name in names:
    print(name.decode('utf-8'))
    messages = r.lrange(name, 0, -1)
    # r.delete(name)
    for mes in messages:
        print(mes.decode('utf-8')),

    print("")