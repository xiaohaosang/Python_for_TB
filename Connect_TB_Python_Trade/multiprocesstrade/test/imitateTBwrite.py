import os
import time,random
prelastline_dict = {}
prelastline_dict_filepath={}

rootdir = r'F:\TradeData\constant\20191213\rb000_1'

def datetime():
	_localtime=time.localtime(time.time())
	_localdate=(_localtime[0]*10000+_localtime[1]*100+_localtime[2]+round(_localtime[3]/100+_localtime[4]/10000,5))*10000
	return _localdate
	
def writefile(filepath):
	with open(filepath, "a") as f:
		close_str=str(3586+random.random())
		_localtime=time.localtime(time.time())
		date_str=str(_localtime[0]*10000+_localtime[1]*100+_localtime[2])
		time_str=str(round(_localtime[3]/100+_localtime[4]/10000,6))
		close_str=str(3586+round(random.random(),1))
		_str=date_str+' '+time_str+' '+(close_str+' ')*4+'1 1 '+date_str+'\n'
		print(_str)
		f.write(_str)

nowtime=datetime()
txtname=str(nowtime)+'.txt'
path=rootdir+'//'+txtname
while True:
	if nowtime==datetime():
		writefile(path)
		time.sleep(0.5)
	else:
		nowtime=datetime()
		txtname=str(nowtime)+'.txt'
		path=rootdir+'//'+txtname

