import time
import multiprocessing
import os
#import threading
#from multiprocessing.managers import BaseManager
#g_queue = multiprocessing.Queue()
from multiprocessing import freeze_support	
		
def showdata(key,TradeData):
	while 1:
		data=TradeData[key]
		time.sleep(1)
		print("show",key,data)

def addddata(TradeData):
	while 1:
		print("add:")
		for key,value in TradeData.items():
			temp=value
			temp.append(value[-1]*2)
			TradeData[key]=temp
			print(key,value)
		time.sleep(1)	


if __name__ == '__main__':
	freeze_support()
	TradeData=multiprocessing.Manager().dict()
	TradeData['rb']=[1]
	TradeData['i']=[3]
	'''
	#mylist=multiprocessing.Manager().list(range(5))
	p = multiprocessing.Process(target=addddata, args=(TradeData,))
	p.start()
	process_list = [multiprocessing.Process(target=showdata, args=(key,TradeData)) for key in TradeData.keys()]
	for p in process_list:
		p.start()
	#for p in process_list:
		#if p.is_alive():
			#p.join()
	'''