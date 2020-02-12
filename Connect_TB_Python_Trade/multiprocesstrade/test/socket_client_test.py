import socket
import pickle,struct
import time
s = socket.socket()
host = 'DESKTOP-O73ROK7'
port = 11111
s.connect((host, port))
hello_info=b''
while True:
    info=s.recv(1)
    if info!=b'\n':
        hello_info=hello_info+info
    else:
        print(hello_info.decode('utf-8'))
        #break
info=s.recv(1)
time.sleep(1000)
'''
while True:
    data =s.recv(4)
    if data:
        len_bytes = struct.unpack('i', data)[0]
        series = s.recv(len_bytes)
        deque = pickle.loads(series)
        print(deque)
'''