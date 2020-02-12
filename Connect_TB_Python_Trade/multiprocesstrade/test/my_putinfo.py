# task_master.py
import random, time,queue
#from multiprocessing import Queue
from multiprocessing.managers import BaseManager


# 发送任务的队列:
task_queue =queue.Queue()
# 接收结果的队列:
result_queue = queue.Queue()

# 从BaseManager继承的QueueManager:
class QueueManager(BaseManager):
    pass

def get_task(): return task_queue
def get_result(): return result_queue	
	
# 把两个Queue都注册到网络上, callable参数关联了Queue对象:
#QueueManager.register('get_task_queue', callable=lambda:task_queue)
#QueueManager.register('get_result_queue', callable=lambda:result_queue)
def test():
	QueueManager.register('get_task_queue', callable=get_task)
	QueueManager.register('get_result_queue', callable=get_result)

	# 绑定端口5000, 设置验证码'abc':
	manager = QueueManager(address=('192.168.5.2', 6000), authkey=b'abc')
	# 启动Queue:
	manager.start()
	print("wait 10s")
	time.sleep(10)
	# 获得通过网络访问的Queue对象:

	task = manager.get_task_queue()
	result = manager.get_result_queue()
	
	n_list =[[1130,1004],[1130,1005],[1130,1006],[1130,1005],[1135,1001],[1135,1001],[1135,1001],[1135,1002],[1140,100],[1140,1001],[1140,1001],[1140,1002]]
	# 放几个任务进去:
	for n in n_list:
	#for i in range(12):
		#n = random.randint(0, 10000)
		try:
			old_n=task.get(block=False)
			print('get old_n {}'.format(old_n))
		except queue.Empty:
			pass
		#if not task.empty():
			
		print('Put task {}'.format(n))
		task.put(n)
		time.sleep(1)

			
	'''		
	# 从result队列读取结果:
	print('Try get results...')
	for i in range(10):
		r = result.get(timeout=10)
		print('Result: %s' % r)
	# 关闭:
	manager.shutdown()
	print('master exit.')
	'''
from multiprocessing import freeze_support
if __name__ == '__main__':
	freeze_support()
	test()
