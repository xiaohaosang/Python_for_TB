import time
import multiprocessing
import os
import threading
from multiprocessing.managers import BaseManager
g_queue = multiprocessing.Queue()
 
def init_queue():
    print("init g_queue start")
    while not g_queue.empty():
        g_queue.get()
    for _index in range(8):
        g_queue.put(_index)
    print("init g_queue end")
    return
	
	

g_search_list = list(range(20000))
# 定义一个计算密集型任务：利用一些复杂加减乘除、列表查找等
def task_cpu(task_id,g_queue):
	#print(id(g_search_list))
	print("CPUTask[%s] start" % task_id)
	#print(id(g_queue))
	print(g_queue)
	while not g_queue.empty():
		count = 0
		for i in range(20000):
			count += pow(3*2, 3*2) if i in g_search_list else 0
		print("CPUTask[%s] count %s" %(task_id,count))			
		try:
			data = g_queue.get(block=True, timeout=1)
			print("CPUTask[%s] get data: %s" % (task_id, data))
		except Exception as excep:
			print("CPUTask[%s] error: %s" % (task_id, str(excep)))
	#os.system("pause");
	print("CPUTask[%s] end" % task_id)
	return task_id



if __name__ == '__main__':
	init_queue()
	time_0 = time.time()
	process_list = [multiprocessing.Process(target=task_cpu, args=(i,g_queue,)) for i in range(multiprocessing.cpu_count())]
	for p in process_list:
		p.start()
	for p in process_list:
		if p.is_alive():
			p.join()
	print("结束：", time.time() - time_0, "\n")
	
	init_queue()
	time_0 = time.time()
	task_cpu(0,g_queue)
	print("结束：", time.time() - time_0, "\n")
	
	
	init_queue()
	time_0 = time.time()
	thread_list = [threading.Thread(target=task_cpu, args=(i,g_queue)) for i in range(8)]
	for t in thread_list:
		t.start()
	for t in thread_list:
		if t.is_alive():
			t.join()
	print("结束：", time.time() - time_0, "\n")
