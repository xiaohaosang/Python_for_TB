# _*_ encoding:utf-8 _*_

from multiprocessing import Process,Queue,Pool,Pipe
import os,time,random

#写数据进程执行的代码：
def write(p):
	print("write p id is:",id(p))
	for value in ['A','B','C']:
		print ('Write---Before Put value---Put %s to queue...' % value)
		p.put(value)
		print ('Write---After Put value')
		time.sleep(random.random())
		print ('Write---After sleep')

#读数据进程执行的代码：
def read(p):
	print("read p id is:",id(p))
	while True:
		print ('Read---Before get value')
		value = p.get(True)
		print ('Read---After get value---Get %s from queue.' % value)

if __name__ == '__main__':
    #父进程创建Queue，并传给各个子进程：
    p = Queue()
    pw = Process(target=write,args=(p,))
    pr = Process(target=read,args=(p,))
    #启动子进程pw，写入：
    pw.start()
    #启动子进程pr，读取:
    pr.start()
    #等待pw结束：
    pw.join()
    #pr进程里是死循环，无法等待其结束，只能强行终止：
    pr.terminate()