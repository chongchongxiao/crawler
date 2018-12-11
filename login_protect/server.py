import socketserver
import json
import redis


class Myserver(socketserver.BaseRequestHandler):
    pool = redis.ConnectionPool(host='localhost', port='6379', db=1)
    max_login_times = 5;
    # login_times_pool = redis.ConnectionPool(host='localhost', port='6379', db=2)
    # r = redis.Redis(connection_pool=pool)
    def get_conn(self):
        return redis.Redis(connection_pool=self.pool)


    def handle(self):
        conn = self.request
        # conn.sendall(bytes("你好，我是机器人",encoding="utf-8"))
        while True:
            ret_bytes = conn.recv(1024)
            ret_str = ret_bytes.decode('utf-8') # 接收到的数据都是bytes数据，因此要进行解码
            try:
                mes = json.loads(ret_str)
            except:
                conn.sendall(bytes('data format is error', encoding='utf-8'))
                # return
                continue
            if not ('username' in mes and 'password' in mes):
                conn.sendall(bytes('not username or password', encoding='utf-8'))
                # return
                continue
            username = mes['username']
            password = mes['password']
            if self.login_redis(username, password):
                conn.sendall(bytes('success', encoding='utf-8'))
            else:
                conn.sendall(bytes('failed', encoding='utf-8'))

    def login_redis(self, username, password):
        r = self.get_conn()
        username_time_key = username + '_t' # 用户名后面加_t表示登录次数的key
        if not r.exists(username):
            print('用户名不存在')
            return False
        pass_word = r.get(username).decode('utf-8')
        if pass_word != password:
            print('用户密码错误')
            return False
        if r.exists(username_time_key):
            # 这里是有一点问题的，就是在r.exists的时候数据还有,但是到r.get的时候数据就没了，这就会导致获取times失败
            times = r.get(username_time_key)
            times = int(times.decode('utf-8'))
            p_time = r.pttl(username_time_key) # 获取当前存活时长，毫秒
            # print(times)
            if times >= self.max_login_times:
                print('%s登录次数超过次数限制%d' % (username,self.max_login_times))
                return False
            times += 1
            r.set(username_time_key, times, px=p_time)
        else:
            r.set(username_time_key, 1, ex=60)
        return True

if __name__ == "__main__":
    server = socketserver.ThreadingTCPServer(("127.0.0.1", 8080), Myserver)
    server.serve_forever()

