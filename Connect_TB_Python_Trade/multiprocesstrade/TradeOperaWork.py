import socket
import pickle,struct

def sever():
    global deque
    global IsClientExit
    s = socket.socket()  # 创建 socket 对象
    host = socket.gethostname()  # 获取本地主机名
    port = 33333  # 设置端口
    s.bind((host, port))
    s.listen(1)
    print("Opera server is start", host, port)
    while True:
        try:
            c, addr = s.accept()
            print('连接地址:', addr)
            c.send("Opera sever is connect \n".encode("utf-8"))
            while True:
                data = c.recv(4)
                if data:
                    len_bytes = struct.unpack('i', data)[0]
                    series = c.recv(len_bytes)
                    deque = pickle.loads(series)
                    print(deque)
        except Exception as e:
            print(e)
            c.close()


def myrecv(socket):
    data = socket.recv(4)
    len_bytes = struct.unpack('i', data)[0]
    series = c.recv(len_bytes)
    data = pickle.loads(series)
    return data

def mysend(socket,data):
    pickledata = pickle.dumps(data)
    len_bytes = struct.pack('i', len(pickledata))  # 防止粘包,设置len_bytes
    s.sendall(len_bytes)
    s.sendall(pickledata)


def sever_epoll():
    global deque
    global IsClientExit
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 创建 socket 对象
    # 设置IP地址复用
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.setblocking(False)
    host = socket.gethostname()  # 获取本地主机名
    port = 33333  # 设置端口
    server.bind((host, port))
    fd_to_socket = {server.fileno(): server,}
    message_queues = {}

    pollout_rule={'h':'hello','l':'Are you live','d':'dir is created'}
    server.listen(5)
    p = select.poll()
    p.register(server, select.EPOLLIN)
    print("Opera server is start", host, port)
    while True:
        events = p.poll()  # 获取准备好的文件对象
        for fd, event in events:
            st = fd_to_socket[fd]
            if st is server:
                client, addr = server.accept()  # 处理连接
                print('Got connection from', addr)
                fd_to_socket[client.fileno()] = client
                message_queues[client] = Queue.Queue()
                p.register(client,select.POLLOUT)
                message_queues[client].put('You Are Connect')
                # fd_dict[c.fileno()].setblocking(False)


            elif event & select.EPOLLHUP:
                print('client close')
                # 在epoll中注销客户端的文件句柄
                epoll.unregister(fd)
                # 关闭客户端的文件句柄
                fd_to_socket[fd].close()
                del message_queues[st]
                # 在字典中删除与已关闭客户端相关的信息
                del fd_to_socket[fd]


            elif event & select.POLLIN:
                data = fd_dict[fd].recv(4)  # 接收时间

                if not data:
                    print(fd_dict[fd].getpeername(), 'disconnected')
                    p.unregister(fd)  # 取消注册
                    del fd_dict[fd]
                else:
                    print(data)

            elif event & select.POLLOUT:
                try:
                    msg = message_queues[st].get_nowait()
                except Queue.Empty:
                    print(socket.getpeername(), " queue empty")
                    epoll.modify(fd, select.EPOLLIN)
                else:
                    print("发送数据：", data, "客户端：", socket.getpeername())
                    # 发送数据
                    try:
                        socket.send(msg)
                    except Exception as e:
                        epoll.modify(fd, select.EPOLLHUP)
                    else:
                        epoll.modify(fd, select.EPOLLIN)


#判断是否创建文件夹,删除旧文件夹下的文件
def creatdirs(rootdir,symbol_stradegy_list):
    for symbol_stradegy in symbol_stradegy_list:
        p=rootdir + '//' + symbol_stradegy
        if not os.path.exists(p):
            os.makedirs(p)
        else:
            for f in os.listdir(p):
                f=os.path.join(p,f)
                if os.path.isfile(f):
                    os.remove(f)


def recodetoTB(rootdir,deque):
    symbol_stradegy=deque[0]
    date_time=str(deque[1][0])+str(deque[1][1])
    info=deque[2]
    if os.path.isdir(symbol_stradegy):
        filename=symbol_stradegy+'//'+date_time+'.txt'
        with open(filename,'w') as f:
            for info in self.strategy.data.oneBarInfo:
                if info[0] in ('Buy','Sell','SellShort','BuyToCover'):
                    f.write('['+info[0]+']'+'\n')
                    f.write('Price='+str(info[2])+'\n')
                    f.write('Lots='+str(info[1])+'\n')


if __name__ == '__main__':
    sever()