import os,re
import time
#from decimal import quantize,Decimal
from decimal import *


def Readlastline(path):
	flag = -3
	with open(path, 'rb') as f:  #读取方式要以字节读取
		try:
			while 1:
				f.seek(flag, 2)         #参数flag表示逆序读取的位数，参数2表示逆序读取
				result = f.readlines()
				#print(result)
				if len(result) > 1:     #只少逆序读了2行，获取最后一行
					dataline=result[-1].decode('utf-8')
					#print(dataline)
					break
				flag *=2
		except OSError:
			f.seek(0, 0)
			dataline=f.readline().decode('utf-8')
	return dataline		


def Findlastfile(dir,aftertime):
	lists=os.listdir(dir)
	timelist=[os.path.splitext(i)[0] for i in lists]
	timelist=[t+'.txt' for t in timelist if float(t)>=aftertime]
	timelist.sort(key=lambda fn: os.path.getmtime(dir+'\\'+fn))
	filepaths=[os.path.join(dir,t) for t in timelist]
	#print(filepaths)
	return filepaths 
	
	#filepath=os.path.join(dir,lists[-1])
	#print(filepath)
	#return filepath



#prelastline=None
def getnew(dir,aftertime,predata,allowpredatasame):
	#global prelastline
	lastfile_list=Findlastfile(dir,aftertime)
	if lastfile_list==[]:return
	lastline_list=[]
	for f in lastfile_list:
		while True:
			try:
				#print("f:",f)
				l=Readlastline(f)
				#print(l)
				lastline_list.append(l.strip())
				break
			except IOError:
				continue
				
	#print("lastline_list:",lastline_list)
	#print("prelastline:",prelastline)
	#if allowpredatasame:
		#lastline_list = [l for l in lastline_list]
	#else:
		#lastline_list=[l for l in lastline_list if l!=prelastline]
	lastline_list = [l for l in lastline_list]

	#prelastline=lastline_list[-1]
	lastline_todata_list=[strtodata(l) for l in lastline_list]
	if not allowpredatasame: lastline_todata_list = [l for l in lastline_todata_list if tuple(l)!=tuple(predata)]
	if lastline_todata_list == []: return None
	return lastline_todata_list


def strtodata(line):
	_list = re.split(' |,', line.strip())
	# print(_list)
	_time = str(Decimal(_list[1]).quantize(Decimal('0.0000')) * 10000)
	data = (int(_list[0]), int(format(float(_time), '0.0f')), float(_list[2]), float(_list[3]), float(_list[4]),
			float(_list[5]), float(_list[6]),
			float(_list[7]), int(_list[8]))
	return data




if __name__ == '__main__':
	path=r"D:\RealTrade\20191205"
	aftertime=201912042255
	#datalist = fileRead(filepath)
	#data = Data(datalist)
	while 1:
		newdata_list=getnew(path,aftertime)
		if newdata_list is None:continue
		print(newdata_list)
		lastdata=newdata_list[-1]
		aftertime=lastdata[0]*10000+lastdata[1]
	
#path=r'D:\RealTrade\20191205\201912050900.txt'
#print(Readlastline(path))

	