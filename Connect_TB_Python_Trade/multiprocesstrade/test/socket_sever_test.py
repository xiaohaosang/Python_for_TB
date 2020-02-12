import socket
import pickle,struct
import time
def sever():
	s = socket.socket()  # 创建 socket 对象
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	host = socket.gethostname()  # 获取本地主机名
	port = 11111  # 设置端口
	s.bind((host, port))
	s.listen(1)
	print("server is start", host, port)
	i=0
	while True:
		c, addr = s.accept()
		#c.setblocking(False)
		print('连接地址:', addr)
		c.send("sever is connect \n\r".encode("utf-8"))
		try:
			while True:
				i=i+1
				deque = [(1, 2)]*10000
				pickledata = pickle.dumps(deque)
				len_bytes = struct.pack('i', len(pickledata))
				if len(deque) != 0:
					print(i)
					c.sendall(len_bytes)
					c.sendall(pickledata)
				#time.sleep(0.25)
		except Exception as e:
			print(e)
			c.close()

sever()