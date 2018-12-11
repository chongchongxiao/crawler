import redis
import random
import datetime
import time

def create_str(len):
    str = ''
    for i in range(len):
        code = random.randint(32, 126) # 32到126为可见字符的ascii码
        str += chr(code) # chr根据ascii码生成字符，ord()显示一个字符的ascii码
    return str

def create_user():
    username_length = 20 #
    password_length = 20 #
    data_size = int(1e5)
    print(data_size)
    r = redis.Redis(host='localhost', port='6379', db=1)
    exp_time = datetime.datetime(2018, 11, 23, 19, 30, 0)
    for i in range(data_size):
        username = create_str(username_length)
        password = create_str(password_length)
        r.set(username, password)
        r.expireat(username, exp_time)
        print('%s\t%s' % (username, password))


if __name__ == '__main__':
    # create_user()
    r = redis.Redis(host='localhost', port='6379', db=1)
    while True:
        keys = r.keys()
        print(len(keys))
        time.sleep(5)
