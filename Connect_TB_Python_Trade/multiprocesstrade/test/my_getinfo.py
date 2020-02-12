# task_worker.py
import time, sys, queue
from multiprocessing.managers import BaseManager

# 创建类似的QueueManager:
class QueueManager(BaseManager):
    pass

# 由于这个QueueManager只从网络上获取Queue，所以注册时只提供名字:
QueueManager.register('get_task_queue')
QueueManager.register('get_result_queue')

# 连接到服务器，也就是运行task_master.py的机器:
#server_addr = '127.0.0.1'
server_addr = '192.168.5.2'
print('Connect to server %s...' % server_addr)
# 端口和验证码注意保持与task_master.py设置的完全一致:
m = QueueManager(address=(server_addr, 6000), authkey=b'abc')
# 从网络连接:
m.connect()
print('Success Connected')
# 获取Queue的对象:
task = m.get_task_queue()
result = m.get_result_queue()
# 从task队列取任务,并把结果写入result队列:


filepath = r"D:\rb_5min.txt"
datalist1 = fileRead(filepath)

def fun(barcount_list,S):
	global barcount
	#t=barcount_list[-1][0]
	print
	try:
		while True:
			try:
			#n = task.get(timeout=10)
				pretime=(barcount_list[-1][0],barcount_list[-1][1])  #pretime=(date,time),判断数据是更新还是添加 
				time,value = task.get()
				print("get time,t",(time,pretime))
				if time==pretime:
					print('flesh time',(time,value))
					barcount_list[-1]=(*time,*value)
					Fleshdata(data,barcount_list[-1])
					print(barcount_list)  
				else: 
					print('new time',(time,value))
					barcount=barcount+1
					barcount_list.append((*time,*value))
					Adddata(data,barcount_list[-1])
					self.data.goToNextBar()
					print(barcount_list)
				time.sleep(2)
				
				
			#print('run task %d * %d...' % (n, n))
			#r = '%d * %d = %d' % (n, n, n*n)
			#result.put(r)
			except queue.Empty:
				print('task queue is empty.')
				
	except ConnectionResetError:
		pass
		#print("ConnectionResetError")
# 处理结束:



while True:
	if barcount!=len(barcount_list):
		print(barcount_list[barcount])
		barcount=barcount+1
	else:
		fun(barcount_list)
		
print('worker exit.')

datalist = fileRead(filepath)
data = Data(datalist)
strategy = Strategy_Sample(data)
currentbar=0

while True:
	newdata = getnew(path)
	print(newdata)
	pretime = (strategy.data.date[0], strategy.data.Time[0])
	nowtime =(newdata[0],newdata[1])
	if time == pretime:
		print('flesh data')

		barcount_list[-1] = (*time, *value)
	Fleshdata(data, barcount_list[-1])
	print(barcount_list)
else:
	print('new time', (time, value))
	barcount = barcount + 1
	barcount_list.append((*time, *value))
	Adddata(data, barcount_list[-1])
	self.data.goToNextBar()


#回测历史部分
datalist = fileRead(filepath)
data = Data(datalist)
strategy = Strategy_Sample(data)
currentbar=0
LoopBack_Size=Strategy.data.barcount
if currentbar<=LoopBack_Size-1:
	strategy(dict_pram)
	strategy.data.goToNextBar()


while True:
	Receive  #接受数据
	#改变 datalist
	LoopBack_Size = Len(datalist)
	if currentbar<LoopBack_Size-1:
		strategy(dict_pram)
		strategy.data.goToNextBar()
	elif currentbar==LoopBack_Size-1 and (判断time<data.time[0]+数据周期)
		strategy(dict_pram)



		RealTrade(strategy,dict_pram)
    TBdir=r"F:\rb1"
    loopback_obj = LoopBack(data, [(Strategy_Sample, {'param1': 3, 'param2': 4})])

	