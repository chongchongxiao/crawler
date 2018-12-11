import threading
import time
import random
import redis
import datetime

def run(arg):
    while True:
        print(arg)
        time.sleep(1)

def create_str(len):
    str = ''
    for i in range(len):
        code = random.randint(32, 126) # 32到126为可见字符的ascii码
        str += chr(code) # chr根据ascii码生成字符，ord()显示一个字符的ascii码
    return str

def test_memory():
    r = redis.Redis(host='localhost', port='6379', db=1)
    exp_time = datetime.datetime(2018, 11, 26, 19, 30, 0)
    print(r.keys())
    while True:
        key = create_str(1)
        value = create_str(1)
        r.set(key, value)
        r.expireat(key, exp_time)
        print(r.keys())
        time.sleep(5)

if __name__=='__main__':
    test_memory()