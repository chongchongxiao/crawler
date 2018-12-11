import socket
import json
import redis
import random
import threading
import time

def login(username, password):
    conn = socket.socket()
    conn.connect(("127.0.0.1", 8080))
    dict = {}
    dict['username'] = username
    dict['password'] = password
    print(dict)
    send_content = json.dumps(dict)
    send_bytes = bytes(send_content, encoding='utf-8')
    conn.sendall(send_bytes)
    recv_bytes = conn.recv(1024)
    recv_str = str(recv_bytes, encoding='utf-8')
    print(recv_str)


def test():
    r = redis.Redis(host='localhost', port='6379', db=1)
    keys = r.keys()
    k = 1
    for username in keys:
        password = r.get(username)
        username = username.decode('utf-8')
        password = password.decode('utf-8')
        login(username, password)


def thread_login(keys, pool, id):
    print(id)
    conn = socket.socket()
    r = redis.Redis(connection_pool=pool)
    conn.connect(("127.0.0.1", 8080))
    while True:
        username = random.sample(keys, 1)[0] # 每次随机取一个用户
        password = r.get(username)
        dict = {}
        dict['username'] = username.decode('utf-8')
        dict['password'] = password.decode('utf-8')
        send_content = json.dumps(dict)
        send_bytes = bytes(send_content, encoding='utf-8')
        conn.sendall(send_bytes)
        recv_bytes = conn.recv(1024)
        recv_str = str(recv_bytes, encoding='utf-8')
        print('%d\t%s\t%s' %(id, username, recv_str))
        # conn.close()

def thread_test(num):
    pool = redis.ConnectionPool(host='localhost', port='6379', db=1)
    r = redis.Redis(connection_pool=pool)
    keys = r.keys()
    for id in range(num):
        t = threading.Thread(target=thread_login, args=(keys, pool, id,))
        t.start()
        # t.join()

    while True:
        print(111)
        time.sleep(1)

if __name__ =='__main__':
    thread_test(5)



