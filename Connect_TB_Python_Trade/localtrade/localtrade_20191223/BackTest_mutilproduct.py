from decimal import *
import io
from collections import namedtuple
import pandas as pd
import numpy as np
import os
import re
from getnewdata_fromlocal import getnew
from collections import Iterable

StartMoney = 1000000
EveryHand = 1
MarginRatio = 0.1
MinMove =  0.1
MoveNum = 0
HandlingFee = 0  # 0.0001
keyList = ["Date", "Time", "Open","High", "Low", "Close", "Vol", "OpenInt", "TrueDate"]


class Data(object):
    def __init__(self, datalist, obj_stradegy,keyList=keyList, initcash=StartMoney, everyhand=EveryHand):
        self.datalist = datalist
        self.currentbar = 0
        self.barcount = len(datalist)
        self.keyList = keyList
        self.initcash = initcash  # 初始资金
        self.everyhand = EveryHand
        self.MarketPosition = 0
        self.BarsSinceEntry = -1
        self.share = 0
        self.oneBarInfo = []
        self.allBarInfo = []
        self.EnterPrice = 0
        self.avgEnterPrice = 0
        self.pingchang_profit = 0  # 平仓盈亏  pc
        self.accumulate_pingchang_profit = 0  # 累计平仓盈亏
        self.series_list = []
        self.init_index(obj_stradegy)

    def init_index(self,obj_stradegy):
        for i in keyList:
            self.__dict__[i] = []
        for data in self.datalist:
            for i in range(len(keyList)):
                self.__dict__[keyList[i]].append(data[i])
        for i in keyList:
            self.__dict__[i] = BaseSeries(self.__dict__[i], obj_stradegy)

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


class BaseSeries(object):
    def __init__(self, init_obj, Strategy_obj):
        self.Strategy_obj = Strategy_obj
        if isinstance(init_obj, list):
            self.interlist = init_obj
        elif (isinstance(init_obj, int) or isinstance(init_obj, float)):
            self.interlist = [init_obj] + [None] * (Strategy_obj.barcount - 1)

    def __getitem__(self, index):
        currentbar = self.Strategy_obj.currentbar
        #print('__getitem__:',currentbar)
        if index <= currentbar:
            return self.interlist[currentbar - index]
        else:
            return self.interlist[0]

    def append(self,value):
        self.interlist.append(value)

    def fresh(self,value):
        self.interlist[-1]=value

class Series(BaseSeries):
    def __setitem__(self, index, value):
        currentbar = self.Strategy_obj.currentbar
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
    def __init__(self, data_raw_list, stradegy_tuple):
        self.strategy = stradegy_tuple[0](data_raw_list)
        self.strategy_param = stradegy_tuple[1]
        print("self.strategy_param:",self.strategy_param  )

    def process(self,TBdir_list,SSdir_list):
        if isinstance(SSdir_list,str): SSdir_list=[SSdir_list]
        print("currentbar:",self.strategy.currentbar)
        print("barcount:",self.strategy.barcount)
        self.clearnrecord(TBdir_list)

        while self.strategy.currentbar<self.strategy.barcount:
            if  self.strategy.currentbar == self.strategy.barcount-1:
                self.strategy(**self.strategy_param)
                break
            self.strategy(**self.strategy_param)
            self.recodetoTB(TBdir)
            self.goToNextBar()
            #print("currentbar:", self.strategy.data.currentbar)

        #os.system("pause")
        while True:
            pretime = (self.strategy.Date[0], self.strategy.Time[0])
            #print(pretime)
            newdatas_list=[]
            for SSdir,obj_Data in zip(SSdir_list,self.strategy.obj_Data_list):
                predata = tuple([obj_Data.__dict__[k][0] for k in keyList])
                newdatas = getnew(SSdir,pretime[0]*10000+pretime[1],predata,allowpredatasame=True)  #True
                #print(SSdir,"getnew",newdatas)
                newdatas_list.append(newdatas)
            time_list, newdatas_list = IntersectionData(newdatas_list)
            if newdatas_list is None: continue

            # 转化格式,序列中数据为时间相同的各商品数据
            newdata_multip_list_bysametime=transform_newdatas(newdatas_list)
            #print("newdata_multip_list_bysametime",newdata_multip_list_bysametime)

            #os.system("pause")
            for nowtime, newdata_multip in zip(time_list, newdata_multip_list_bysametime):
                #os.system("pause")
                #print("nowtime:",nowtime,"newdata_multip:",newdata_multip)
                if nowtime[0] == pretime[0] and nowtime[1] == pretime[1]:
                    # 获取之前的各商品的数据,predata_list
                    predata_multip = []
                    for obj_Data in self.strategy.obj_Data_list:
                        predata = tuple([obj_Data.__dict__[k][0] for k in keyList])
                        predata_multip.append(predata)
                    #print("predata_multip:",predata_multip)
                    # 如果判断和之前的数据完全一致，break
                    IsEque, unequal_list_sn = judge_equal(newdata_multip, predata_multip)
                    #print("IsEque:",IsEque,"unequal_list_sn:",unequal_list_sn)
                    if IsEque:continue
                    # 更新数据
                    else:
                        self.freshdata(newdata_multip,unequal_list_sn)

                if (nowtime[1] > pretime[1]) or (nowtime[0] > pretime[0]):
                    self.adddata(newdata_multip,nowtime)
                    self.goToNextBar()

                self.strategy(**self.strategy_param)
                self.recodetoTB(TBdir_list)
                for obj_Data in self.strategy.obj_Data_list:
                    obj_Data.oneBarInfo = []


    def freshdata(self,newdata_multip,unequal_list_sn):
        for sn in unequal_list_sn:
            obj_Data=self.strategy.obj_Data_list[sn]
            newdata=newdata_multip[sn]
            print('fresh data'+str(sn))
            for i in range(len(keyList)):
                obj_Data.__dict__[keyList[i]].fresh(newdata[i])

    def adddata(self, newdata_multip,nowtime):
        for sn in range(len(newdata_multip)):
            obj_Data = self.strategy.obj_Data_list[sn]
            newdata = newdata_multip[sn]
            print('add data' + str(sn))
            for i in range(len(keyList)):
                obj_Data.__dict__[keyList[i]].append(newdata[i])
        self.strategy.Date.append(nowtime[0])
        self.strategy.Time.append(nowtime[1])
        self.strategy.barcount = self.strategy.barcount+1
        #print('Time:',self.strategy.data.Time.interlist)
        for s in self.strategy.series_list:
            s.append(None)

    def goToNextBar(self):
        print('gotonextbar')
        print("currentbar",self.strategy.currentbar,"barcount",self.strategy.barcount)
        if(self.strategy.currentbar<self.strategy.barcount-1):
            self.strategy.currentbar = self.strategy.currentbar + 1
            for obj_Data in self.strategy.obj_Data_list:
                if obj_Data.MarketPosition!=0:
                    obj_Data.BarsSinceEntry=obj_Data.BarsSinceEntry+1
                print("goToNextBar,BarsSinceEntry:",obj_Data.BarsSinceEntry)
                obj_Data.oneBarInfo = []
        for series in self.strategy.series_list:
            if self.strategy.currentbar < self.strategy.barcount:
                series[0] = series[1]


    def recodetoTB(self,TBdir_list):
        for TBdir, obj_Data in zip(TBdir_list, self.strategy.obj_Data_list):
            if obj_Data.oneBarInfo==[]: return
            if os.path.isdir(TBdir):
                filename=TBdir+'\\'+str(self.strategy.Date[0])+'&'+str(self.strategy.Time[0])+'.txt'
                with open(filename,'w') as f:
                    for info in obj_Data.oneBarInfo:
                        f.write('['+info[0]+']'+'\n')
                        f.write('Price='+str(info[2])+'\n')
                        f.write('Lots='+str(info[1])+'\n')

    def clearnrecord(self,TBdir_list):
        for dir in TBdir_list:
            if not os.path.exists(dir):
                os.makedirs(dir)
            os.chdir(dir)  # 切换到directory目录
            cwd = os.getcwd()
            files = os.listdir(cwd)  # 列出目录下的文件
            for file in files:
                os.remove(file)


# 对多商品（date,time,open,high,low,close,...)数据序列,进行具有共同的(date,time)交集处理
def IntersectionData(data_raw_list):
    if (None in data_raw_list) or (not data_raw_list):
        return (None,None)
    time_inter = set([(i[0], i[1]) for i in data_raw_list[0]])
    for data_raw in data_raw_list[1:]:
        time_inter=set([(i[0],i[1]) for i in data_raw])&time_inter
    if not time_inter: return (None,None)
    time_inter = sorted(sorted(time_inter, key=lambda x: x[1], reverse=False), key=lambda x: x[0], reverse=False)
    inter_data_list=[]
    for data_raw in data_raw_list:
          inter_data=[i for i in data_raw if (i[0],i[1]) in time_inter]
          inter_data_list.append(inter_data)
    return (time_inter,inter_data_list)


# 对newdatas_list 进行格式转换[[(datetime1,dataA),(datetime2,dataA)],[(datetime1,dataB),(datetime2,dataB)]]
# 转化为[[(datetime1,dataA),(datetime1,dataB)],[(datetime2,dataA),(datetime2,dataB)]]
def transform_newdatas(newdatas_list):
    length=len(newdatas_list[0])
    data_bysametime_list=[]
    for i in range(length):
        data_bysametime=[newdata[i] for newdata in newdatas_list]
        data_bysametime_list.append(data_bysametime)
    return data_bysametime_list


def judge_equal(data_1_list,data_2_list):
    unequal_list_sn=[]
    for i in range(len(data_1_list)):
        if data_1_list[i]!=data_2_list[i]:
            unequal_list_sn.append(i)
    if unequal_list_sn:
        return False,unequal_list_sn
    else:
        return True, unequal_list_sn


class BaseStrategy(object):
    def __init__(self, data_raw_list):
        self.obj_Data_list=[]
        self.name_Data_list=[]
        if isinstance(data_raw_list,Iterable) and data_raw_list:
            #(date,time)交集处理
            time_inter,inter_data_list=IntersectionData(data_raw_list)
            #对data0,data1...赋值
            if inter_data_list is None:
                inter_data_list= [[(0, 0, 0, 0, 0, 0, 0, 0, 0)] for i in range(len(data_raw_list))]
                time_inter =[(0, 0) for i in range(len(data_raw_list))]

            print("time_inter",time_inter)
            print("inter_data_list",inter_data_list)
            for i,d in enumerate(inter_data_list):
                print(i,d)
                obj_Data=Data(d,self)
                name = 'data'+str(i)
                self.__dict__[name]=obj_Data
                self.name_Data_list.append(name)
                self.obj_Data_list.append(obj_Data)
            self.data=self.data0
            print("obj_Data_list:",self.obj_Data_list)
            #对其他基础数据赋值
            self.Date=Series([t[0] for t in time_inter],self)
            self.Time=Series([t[1] for t in time_inter],self)
            self.incurrentbar =[0]
            self.inbarcount=[len(time_inter)]

        self.Seriesfunction_list=[]
        self.series_list=[]
        self.defineparam()
        self.defineSeries()
        self.defineSeriesfunction()
        for i in self.series_list:
            print(i,i.interlist)
        HaveSeriesfunction=[self]
        print("序列值提升")
        #os.system("pause")
        circle = 0
        while HaveSeriesfunction!=[]:
            circle = circle + 1
            #print("circle",circle)
            fun=HaveSeriesfunction[0]
            for k in fun.__dict__.keys():
                #print(k,fun.__dict__[k])
                f=fun.__dict__[k]
                if hasattr(f, '__bases__') and f.__bases__[-1]==BaseFunction:  # 判断是否是存在序列变量的函数
                    #print("BaseFunction:",f.__name__)
                    ojb_f=f(self,k)                #实例化BaseFunction
                    fun.__dict__[k]=ojb_f
                    #print("fun.__dict__[k]",ojb_f)
                    #for i in self.series_list:
                        #print(i,i.interlist)
                    #os.system("pause")
                    HaveSeriesfunction.append(ojb_f)  #添加到HaveSeriesfunction,待下轮循环检验属性中是否含有BaseFunction
                    self.Seriesfunction_list.append(ojb_f)
                    #self.data.series_list.extend(ojb_f.data.series_list)
            HaveSeriesfunction.remove(fun)

    @property
    def currentbar(self):
        return self.incurrentbar[0]
    @currentbar.setter
    def currentbar(self,value):
        self.incurrentbar[0] = value

    @property
    def barcount(self):
        return self.inbarcount[0]
    @barcount.setter
    def barcount(self,value):
        self.inbarcount[0] = value

    def create_series(self,name,init_num = 0):
        series = Series(init_num,self)
        self.__dict__[name] = series
        print("creat series {}:{}".format(name, series))
        self.series_list.append(series)
        return series


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
    def __init__(self, strategy_obj,name):
        self.name=name
        self.strategy_obj = strategy_obj
        #for key,value in self.strategy_obj.__dict__.items():
            #self.__dict__[key] = value
        for name_data, obj_data in zip(self.strategy_obj.name_Data_list,self.strategy_obj.obj_Data_list):
            self.__dict__[name_data]=obj_data
        self.data=self.data0
        self.incurrentbar =self.strategy_obj.incurrentbar
        self.inbarcount = self.strategy_obj.inbarcount
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


    @property
    def currentbar(self):
        return self.incurrentbar[0]

    @property
    def barcount(self):
        return self.inbarcount[0]


    def __call__(self, **kwargs):
    #将函数参数赋值给self.参数
        for k in kwargs.keys():
            if k in self.__dict__:
                self.__dict__[k] = kwargs[k]
        return self.script()

    def create_series(self,name,init_num = 0):
        series = Series(init_num,self)
        self.__dict__[name] = series
        print("creat series {}:{}".format(name,series))
        self.strategy_obj.series_list.append(series)
        return series


class Function1(BaseFunction):
	def defineparam(self):
		self.param1=1

	def defineSeries(self):
		self.create_series("accumulate", 0)

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
		self.create_series("AvgValue1", 0)
		self.create_series("AvgValue2", 0)

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
    if not filename: return [(0,0,0,0,0,0,0,0,0)]
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
