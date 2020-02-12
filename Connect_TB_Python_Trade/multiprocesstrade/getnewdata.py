import os,re
import time
#from decimal import quantize,Decimal
from decimal import *


def Readlastline(path):
	flag = -3
	with open(path, 'rb') as f:  #读取方式要以字节读取
		while 1:
			f.seek(flag, 2)         #参数flag表示逆序读取的位数，参数2表示逆序读取
			result = f.readlines()    
			if len(result) > 1:     #只少逆序读了2行，获取最后一行
				dataline=result[-1].decode('utf-8')
				#print(dataline)
				break
			flag *=2
	return dataline		


def Findlastfile(dir):
	lists=os.listdir(dir)
	if lists==[]: return None
	#print(lists)
	lists.sort(key=lambda fn: os.path.getmtime(dir+'\\'+fn))

	filepath=os.path.join(dir,lists[-1])
	#print(filepath)
	return filepath


def getnew(rootdir,relpath,prelastline_dict,barstarttime_list,BarInterval):
	abspath = os.path.join(rootdir, relpath)
	barstarttime=barstarttime_list[0]
	while True:
		if barstarttime is not None and time.time()-barstarttime_list[0]>BarInterval*60:
			return None
		lastfile=Findlastfile(abspath)
		if lastfile is None: continue
		if lastfile is not None:
			try:
				#print("prelastline:",prelastline)
				lastline=Readlastline(lastfile)
				prelastline=prelastline_dict[relpath]
				if (lastline is not None) and (lastline!=prelastline):
					prelastline_dict[relpath]=lastline
					newdata = strtodata(lastline)
					return newdata
			#except Exception as e:
			except IOError:
				continue

def strtodata(line):
	_list =re.split(' |,', line)	
	_time = str(Decimal(_list[1]).quantize(Decimal('0.0000')) * 10000)
	data = (int(_list[0]), int(format(float(_time), '0.0f')),float(_list[2]),float(_list[3]), float(_list[4]), float(_list[5]), float(_list[6]),
                float(_list[7]), int(_list[8]))		
	return data	

if __name__ == '__main__':
	prelastline_dict = {'rb000': None}
	rootdir =r"F:\TradeData\constant\20191216\rb000_1"
	while True:
		newdata=getnew(rootdir,"rb000",prelastline_dict)
		print(newdata)

