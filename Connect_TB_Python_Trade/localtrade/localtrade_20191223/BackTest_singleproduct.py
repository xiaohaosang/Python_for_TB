from decimal import *
import io
from collections import namedtuple
import pandas as pd
import numpy as np
import os
import re
from getnewdata_fromlocal import getnew

StartMoney = 1000000
EveryHand = 10
MarginRatio = 0.1
MinMove = 1  # 0.1
MoveNum = 0
HandlingFee = 0  # 0.0001
keyList = ["Date", "Time", "Open","High", "Low", "Close", "Vol", "OpenInt", "TrueDate"]


class Data(object):
    def __init__(self, datalist, keyList=keyList, initcash=StartMoney, everyhand=EveryHand):
        self.datalist = datalist
        self.barcount = len(datalist)
        self.keyList = keyList
        self.initcash = initcash  # 初始资金
        self.everyhand = EveryHand
        self.MarketPosition = 0
        self.BarsSinceEntry = -1
        self.share = 0
        self.currentbar = 0
        self.oneBarInfo = []
        self.allBarInfo = []
        self.EnterPrice = 0
        self.avgEnterPrice = 0
        self.pingchang_profit = 0  # 平仓盈亏  pc
        self.accumulate_pingchang_profit = 0  # 累计平仓盈亏
        self.series_list = []
        self.init_index()

    def init_index(self):
        for i in keyList:
            self.__dict__[i] = []
        for data in self.datalist:
            for i in range(len(keyList)):
                self.__dict__[keyList[i]].append(data[i])
        for i in keyList:
            self.__dict__[i] = BaseSeries(self.__dict__[i], self)

    @property
    def float_profit(self):
        if (self.MarketPosition == 0):
            return 0
        if (self.MarketPosition == 1):
            # return self.share * self.everyhand * (self.Close(0) - self.avgEnterPrice)
            return self.share * self.everyhand * (self.Close[0] - self.avgEnterPrice)
        if (self.MarketPosition == -1):
            # return self.share * self.everyhand * (self.avgEnterPrice - self.Close(0))
            return self.share * self.everyhand * (self.avgEnterPrice - self.Close[0])

    @property
    def posvalue(self):
        if (self.MarketPosition == 0):
            return 0
        if (self.MarketPosition == 1):
            # return self.share * self.everyhand * self.Close(0)
            return self.share * self.everyhand * self.Close[0]
        if (self.MarketPosition == -1):
            # return self.share * self.everyhand * self.Close(0)
            return self.share * self.everyhand * self.Close[0]

    @property
    def accumulate_profit(self):
        return self.float_profit + self.accumulate_pingchang_profit

    @property
    def all_fund(self):
        return self.accumulate_profit + self.initcash

    @property
    def deposit(self):
        return self.posvalue * MarginRatio

    @property
    def available_fund(self):
        return self.all_fund - self.deposit

    def goToNextBar(self):
        print('gotonextbar')
        print("currentbar",self.currentbar,"barcount",self.barcount)
        if(self.currentbar<self.barcount-1):
            self.currentbar = self.currentbar + 1
            if self.MarketPosition!=0:
                self.BarsSinceEntry=self.BarsSinceEntry+1
                print("goToNextBar",self.BarsSinceEntry)
        self.oneBarInfo = []
        for series in self.series_list:
            if self.currentbar < self.barcount:
                series[0] = series[1]

    # 真实价格调整
    def correctPrice(self, price):
        if price > self.High():
            truePrice = self.High()
        elif price < self.Low():
            truePrice = self.Low()
        else:
            truePrice = price
        truePrice = int(truePrice / MinMove) * MinMove
        return truePrice

    def correctPrice(self, price):
        if price > self.High[0]:
            truePrice = self.High[0]
        elif price < self.Low[0]:
            truePrice = self.Low[0]
        else:
            truePrice = price
        truePrice = int(truePrice / MinMove) * MinMove
        return truePrice

    # 真实手数调整
    def correctLots(self, lots):
        return min(abs(self.share), lots)

    '''动态权益= 现金 + 当前持仓保证金avg*手数*比率+ 当前浮动盈亏(close-avg)*手数'''

    # 以下常规四操作
    def Buy(self, lots, price):
        if self.MarketPosition != 1:
            self.BarsSinceEntry = 0
            # print("Buy,MarketPosition!=1", self.BarsSinceEntry)
        self.EnterPrice = self.correctPrice(price)
        if self.MarketPosition == -1:
            self.BuyToCover(self.share, self.EnterPrice)
        self.MarketPosition = 1
        self.avgEnterPrice = (self.avgEnterPrice * self.share + self.EnterPrice * lots) / (self.share + lots)
        self.share = self.share + lots
        self.oneBarInfo.append(["Buy", lots, self.EnterPrice])

    def Sell(self, lots, price):
        trueLots = self.correctLots(lots)
        ExitPrice = self.correctPrice(price)
        if self.MarketPosition == 1:
            self.pingchang_profit = trueLots * self.everyhand * (ExitPrice - self.avgEnterPrice)
            self.accumulate_pingchang_profit = self.pingchang_profit + self.accumulate_pingchang_profit
            self.share = self.share - trueLots
            if (self.share == 0):
                self.MarketPosition = 0
            self.oneBarInfo.append(["Sell", trueLots, ExitPrice, self.pingchang_profit])
        if self.MarketPosition ==0:
            self.BarsSinceEntry = -1
            # print("Sell,MarketPosition==0", self.BarsSinceEntry)

    def SellShort(self, lots, price):
        if self.MarketPosition != -1:
            self.BarsSinceEntry =0
            # print("SellShort,MarketPosition!=-1", self.BarsSinceEntry)
        self.EnterPrice = self.correctPrice(price)
        if self.MarketPosition == 1:
            self.Sell(self.share, self.EnterPrice)
        self.MarketPosition = -1
        self.avgEnterPrice = (self.avgEnterPrice * self.share + self.EnterPrice * lots) / (self.share + lots)
        self.share = self.share + lots
        self.oneBarInfo.append(["SellShort", lots, self.EnterPrice])

    def BuyToCover(self, lots, price):
        trueLots = self.correctLots(lots)
        ExitPrice = self.correctPrice(price)
        if self.MarketPosition == -1:
            self.pingchang_profit = -1 * trueLots * self.everyhand * (ExitPrice - self.avgEnterPrice)
            self.accumulate_pingchang_profit = self.pingchang_profit + self.accumulate_pingchang_profit
            self.share = self.share - trueLots
            if (self.share == 0):
                self.MarketPosition = 0
            self.oneBarInfo.append(["BuyToCover", trueLots, ExitPrice, self.pingchang_profit])
        if self.MarketPosition == 0:
            self.BarsSinceEntry = -1
            # print("Sell,MarketPosition==0", self.BarsSinceEntry)

    # 以下展示回测结果，直接写入到excel
    def showResult(self):
        print("currentbar: {}".format(self.currentbar))
        print("date and time:", self.Date, self.Time)
        print("self.oneBarInfo: {}".format(self.oneBarInfo))
        print("MarketPosition: {},share: {}".format(self.MarketPosition, self.share))
        print("float_profit: {}".format(self.float_profit))
        print("accumulate_pingchang_profit:{}".format(self.accumulate_pingchang_profit))
        print("accumulate_profit: {}".format(self.accumulate_profit))
        print("all_fund: {}".format(self.all_fund))
        print("deposit: {}".format(self.deposit))
        print("posvalue: {}".format(self.posvalue))
        print("available_fund: {}".format(self.available_fund))

    '''	
    def create_series(self,init_num = 0):

        #for i in globals().items():
            #print(i)	
        series = Series(init_num,self)
        self.series_list.append(series)
        return series		
    '''

    def create_series(self, name, init_num):

        # for i in globals().items():
        # print(i)
        series = Series(init_num, self)
        self.__dict__[name] = series
        self.series_list.append(series)


class BaseSeries(object):
    def __init__(self, init_obj, data_obj):
        self.data_obj = data_obj
        if isinstance(init_obj, list):
            self.interlist = init_obj
        elif (isinstance(init_obj, int) or isinstance(init_obj, float)):
            self.interlist = [init_obj] + [None] * (data_obj.barcount - 1)

    def __getitem__(self, index):
        currentbar = self.data_obj.currentbar
        if index <= currentbar:
            return self.interlist[currentbar - index]
        else:
            return self.interlist[0]

    def append(self,value):
        self.interlist.append(value)

    def flesh(self,value):
        self.interlist[-1]=value

class Series(BaseSeries):
    def __setitem__(self, index, value):
        currentbar = self.data_obj.currentbar
        if index != 0:
            print('index must is 0')
            raise NameError
        else:
            self.interlist[currentbar] = value


class LoopBack(object):
    def __init__(self,data,stradegys_list):
        self.data=data
        self.stradegys_list=stradegys_list

    def Loopback(self,TBdir):
        self.times = len(self.data.datalist)
        stradegys_list=[(stradegy_cls(self.data),param) for stradegy_cls,param in self.stradegys_list]
        for i in range(self.times):
            #print("i",i)
            for stradegy,param in stradegys_list:
                stradegy(**param)
            self.recodetoTB(TBdir)
            self.data.showResult()
            self.data.goToNextBar()
			
    def recodetoTB(self,TBdir):
        if self.data.oneBarInfo==[]: return
        if os.path.isdir(TBdir):
            filename=TBdir+'\\'+str(self.data.Date[0])+'&'+str(self.data.Time[0])+'.txt'
            with open(filename,'w') as f:
                for info in self.data.oneBarInfo:
                    f.write('['+info[0]+']'+'\n')
                    f.write('Price='+str(info[2])+'\n')
                    f.write('Lots='+str(info[1])+'\n')


class Process(object):
    def __init__(self, data, stradegy_tuple):
        self.strategy = stradegy_tuple[0](data)
        self.strategy_param = stradegy_tuple[1]
        print("self.strategy_param:",self.strategy_param  )

    def process(self,TBdir,SSdir):
        print("currentbar:",self.strategy.data.currentbar)
        print("barcount:",self.strategy.data.barcount)
        self.clearnrecord(TBdir)

        while self.strategy.data.currentbar< self.strategy.data.barcount:
            if  self.strategy.data.currentbar == self.strategy.data.barcount-1:
                self.strategy(**self.strategy_param)
                break
            self.strategy(**self.strategy_param)
            self.recodetoTB(TBdir)
            self.strategy.data.goToNextBar()
            #print("currentbar:", self.strategy.data.currentbar)


        os.system("pause")
        while True:
            predata = tuple([self.strategy.data.__dict__[k][0] for k in keyList])
            #print(predata)
            newdata_list = getnew(SSdir, predata[0]*10000+predata[1],predata,allowpredatasame=False)
            if newdata_list is None: continue
            print(newdata_list)
            for newdata in newdata_list:
                nowtime = (newdata[0], newdata[1])
                if newdata[0] == predata[0] and newdata[1] == predata[1]:
                    print('flesh data')
                    self.fleshdata(newdata)
                    self.strategy(**self.strategy_param)
                    self.recodetoTB(TBdir)
                    self.strategy.data.oneBarInfo = []
                if  (newdata[1] > predata[1]) or (newdata[0] > predata[0]):
                    print('add data')
                    self.adddata(newdata)
                    self.strategy.data.goToNextBar()
                    self.strategy(**self.strategy_param)
                    self.recodetoTB(TBdir)
                    self.strategy.data.oneBarInfo=[]

    def fleshdata(self, newdata):
        for i in range(len(keyList)):
            self.strategy.data.__dict__[keyList[i]].flesh(newdata[i])

    def adddata(self, newdata):
        for i in range(len(keyList)):
            self.strategy.data.__dict__[keyList[i]].append(newdata[i])
        self.strategy.data.barcount = self.strategy.data.barcount+1
        #print('Time:',self.strategy.data.Time.interlist)
        for s in self.strategy.data.series_list:
            s.append(None)

    def recodetoTB(self,TBdir):
        if self.strategy.data.oneBarInfo==[]: return
        if os.path.isdir(TBdir):
            filename=TBdir+'\\'+str(self.strategy.data.Date[0])+'&'+str(self.strategy.data.Time[0])+'.txt'
            with open(filename,'w') as f:
                for info in self.strategy.data.oneBarInfo:
                    f.write('['+info[0]+']'+'\n')
                    f.write('Price='+str(info[2])+'\n')
                    f.write('Lots='+str(info[1])+'\n')

    def clearnrecord(self,dir):
        os.chdir(dir)  # 切换到directory目录
        cwd = os.getcwd()
        files = os.listdir(cwd)  # 列出目录下的文件
        for file in files:
            os.remove(file)


class BaseStrategy(object):
    def __init__(self, data):
        self.data = data
        self.times = len(data.datalist)
        self.Seriesfunction_list=[]
        self.defineparam()
        self.defineSeries()
        self.defineSeriesfunction()
        HaveSeriesfunction=[self]
        while HaveSeriesfunction!=[]:
            fun=HaveSeriesfunction[0]
            for k in fun.__dict__.keys():
                f=fun.__dict__[k]
                if hasattr(f, '__bases__') and f.__bases__[-1]==BaseFunction:  # 判断是否是存在序列变量的函数
                    #print("BaseFunction:",f.__name__)
                    ojb_f=f(self.data)                #实例化BaseFunction
                    fun.__dict__[k]=ojb_f
                    HaveSeriesfunction.append(ojb_f)  #添加到HaveSeriesfunction,待下轮循环检验属性中是否含有BaseFunction
                    self.Seriesfunction_list.append(ojb_f)
                    #self.data.series_list.extend(ojb_f.data.series_list)
            HaveSeriesfunction.remove(fun)
		
    def defineparam(self):
        pass

    def defineSeries(self):
        pass

    def defineSeriesfunction(self):
        pass

    def script(self):
        pass

    def __call__(self, **param_dict):
        for k in param_dict.keys():
            if k in self.__dict__:
                self.__dict__[k] = param_dict[k]
        self.script()

		
class BaseFunction(object):
    def __init__(self, data):
        self.data = data
        self.times = len(data.datalist)
        self.defineparam()
        self.defineSeries()
        self.defineSeriesfunction()

    def defineparam(self):
        pass

    def defineSeries(self):
        pass

    def defineSeriesfunction(self):
        pass

    def script(self):
        pass

    def __call__(self, **kwargs):
    #将函数参数赋值给self.参数
        for k in kwargs.keys():
            if k in self.__dict__:
                self.__dict__[k] = kwargs[k]
        return self.script()

class Function1(BaseFunction):
	def defineparam(self):
		self.param1=1

	def defineSeries(self):
		self.data.create_series("accumulate", 0)

	def defineSeriesfunction(self):
		pass

	def script(self):
		#print("self.data.series_list:",self.data.series_list)
		#print("self.data.accumulate[0]",self.data.accumulate[0])
		#print("self.data.accumulate[1]",self.data.accumulate[1])
		self.data.accumulate[0]=self.data.accumulate[1]+1
		return self.data.accumulate[0]


class Strategy_Sample(BaseStrategy):
	def defineparam(self):
		self.param1=1
		self.param2=2

	def defineSeries(self):
		self.data.create_series("AvgValue1", 0)
		self.data.create_series("AvgValue2", 0)

	def defineSeriesfunction(self):
		self.fun1=Function1

	@staticmethod
	def Average(price, lenth):
		c = []
		for i in range(lenth):
			c.append(price[i])

		c = np.array(c)
		return c.mean()

	def script(self):
		print("currentbar:",self.data.currentbar)
		print("__dict__:",self.__dict__)
		print("data_attribute:",)
		for k in self.data.__dict__.keys():
			print(k)
		#print("Seriesfunction_list:")
		#print(self.Seriesfunction_list)
		#print(self.data.accumulate.interlist)
		fun1=self.fun1(param1=2)
		print("fun1:",fun1)
		#print("param2:", self.param2)
		self.data.AvgValue1[0] = self.Average(self.data.Close, 5)
		self.data.AvgValue2[0] = self.Average(self.data.Close, 10)

		#print("self.data.AvgValue1: {}".format(self.data.AvgValue1[1]))
		#print("self.data.AvgValue2: {}".format(self.data.AvgValue2[1]))
		if self.data.currentbar < 10: return
		if self.data.MarketPosition <= 0 and self.data.AvgValue1[1] > self.data.AvgValue2[1] and self.data.currentbar > 9:
			self.data.Buy(1, self.data.Open[0])

		if self.data.MarketPosition >= 0 and self.data.AvgValue1[1] < self.data.AvgValue2[1] and self.data.currentbar > 9:
			self.data.SellShort(1, self.data.Open[0])		
		

def fileRead(filename):
    if not filename: return [[0,0,0,0,0,0,0,0,0]]
    file = io.open(filename, "r", encoding='UTF-8-sig')
    datalist = []
    text_lines = file.read().strip()
    list1 = text_lines.split("\n")
    for i in range(0, len(list1)):
        #list2 = list1[i].split(",")
        list2 =re.split(' |,', list1[i])
        #print(list2)
        datalist.append(list2)
    file.close()
    result = []
    # print(datalist)
    for i in range(len(datalist)):
        time = str(Decimal(datalist[i][1]).quantize(Decimal('0.0000')) * 10000)
        hang = [int(datalist[i][0]), int(format(float(time), '0.0f')),
                float(datalist[i][2]),
                float(datalist[i][3]), float(datalist[i][4]), float(datalist[i][5]), float(datalist[i][6]),
                float(datalist[i][7]), int(datalist[i][8])]
        result.append(hang)  # 每个bar时间表示形式例如201812020905 表示2018年12月2日9:05
    # result = pd.DataFrame(result, columns=["商品代码", "时间", "最高价", "最低价", "开盘价", "收盘价", "成交量", "持仓量"])  # 若将此行注释，则返回数值列表
    return result


if __name__ == '__main__':
	pass
    # filepath = r"F:\dataoutput\1Htest20190101-20190501.txt"
    # filepath = r"F:\recode20190612.txt"
    # filepath = r"D:\rb_5min.txt"
    # datalist1 = fileRead(filepath)
    # data = Data(datalist1)
    # print(data.series_list)
    # print(data.__dict__.keys())
    # a = Strategy(data)
    # a.operateData()
    # TBdir=r"F:\rb1"
    # loopback_obj = LoopBack(data, [(Strategy_Sample, {'param1': 3, 'param2': 4})])
    # loopback_obj.Loopback(TBdir)
