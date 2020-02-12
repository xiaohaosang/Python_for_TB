from BaseCls import *
from tools import fileRead
import  time,os
import socket
import pickle,struct
import multiprocessing
from multiprocessing import freeze_support,RLock
import threading
from MySqlOperation import OperaMysql
dict_lock=RLock()
def recvConstantData():
    s = socket.socket()
    host = 'DESKTOP-O73ROK7'
    port = 22222
    s.connect((host, port))
    hello_info=b''
    while True:
        info=s.recv(1)
        if info!=b'\n':
            hello_info=hello_info+info
        else:
            print(hello_info.decode('utf-8'))
            break
    #start_time=time.time()
    #Multiflag=False
    while True:
        data =s.recv(4)
        if data:
            len_bytes = struct.unpack('i', data)[0]
            series = s.recv(len_bytes)
            deque = pickle.loads(series)
            with dict_lock:
                handleConstantData_multishare(deque,maxlen=10)
            #print(deque)
            #print(ConstantData)
        #if Multiflag is True: continue
        #elif time.time()-start_time>=0.5 and Multiflag is False:
            #Multiflag=True
            #print("开启多进程")


def init_Tradeinfos(opera_mysql,Tradeinfo_list,ConstantData):
    for tradeinfo in Tradeinfo_list:
        symboltype,barinterval=tradeinfo['symbol'].split('_')
        barinterval=int(barinterval)
        historydata=gethistory(tradeinfo['symbol'],tradeinfo['dates'],opera_mysql,history_localdir=r'D:\\ConstantData')
        data=mergeConstantdata(tradeinfo['symbol'],historydata,ConstantData)
        print(tradeinfo['symbol'],data)
        data_obj=Data(symboltype,barinterval,data)
        tradeinfo['process']=MultiProcess(tradeinfo['symbol'],data_obj, tradeinfo['stradegy_tuple'])


def gethistory(symbol,dates,opera_mysql,history_localdir):
    _localtime=time.localtime(time.time())
    _localdate=_localtime[0]*10000+_localtime[1]*100+_localtime[2]
    if len(dates)==1 or dates[1]==_localdate:
        askfor_start_date=dates[0]
        askfor_end_date=_localdate
        realtrade=True
    else:
        askfor_start_date=dates[0]
        askfor_end_date=dates[1]
        realtrade =False
    file_path=history_localdir+'\\'+symbol+'.txt'
    if os.path.exists(file_path):    # 如果本地有数据，先到本地取，代码后期完善
        file_data=readfile_from_mysql(path)
        file_start_date=data[1][0]
        file_end_date=data[-1][0]
        if (file_end_date>askfor_end_date):
            pass
    symboltype,barinterval = symbol.split('_')
    barinterval=int(barinterval)
    if barinterval==1: table='one_min_data'
    elif barinterval==5: table='five_min_data'
    mysql_data=opera_mysql.getData_byDate(askfor_start_date,askfor_end_date,symboltype,table)

    askfor_data=[tuple(list(i)[1:]) for i in mysql_data]
    return askfor_data

def readfile_from_mysql(file_path):
    pass


def mergeConstantdata(symbol,historydata,ConstantData):
    print("historydata:",historydata)
    newdata=multigetnew(symbol,ConstantData,historydata[-1])
    print("newdata:",newdata)
    if newdata is None or len(newdata)==0: return historydata
    firt_newdata=newdata[0]
    last_historydata=historydata[-1]
    if firt_newdata[0]==last_historydata[0] and firt_newdata[1]==last_historydata[1]:
        return historydata+newdata[1:]
    if firt_newdata[0] > last_historydata[0] or firt_newdata[1] > last_historydata[1]:
        return historydata+newdata


'''
def handleConstantData(deque):
    for symbol,data in deque:
        if symbol in ConstantData.keys():
            lastdata = ConstantData[symbol][-1]
            if data[0]==lastdata[0] and data[1]==lastdata[1]:
                ConstantData[symbol][-1]=data
            else:
                ConstantData[symbol].append(data)
        else:
            ConstantData[symbol]=[data]
'''


def handleConstantData_multishare(deque,maxlen=None):
    for symbol,data in deque:
        if symbol in ConstantData.keys():
            # 数据超过maxlen,清空
            if maxlen is not None and len(ConstantData[symbol]) >maxlen:
                print(symbol,len(data))
                ConstantData[symbol]=[data]
            else:
                lastdata = ConstantData[symbol][-1]
                if data[0]==lastdata[0] and data[1]==lastdata[1]:
                    temp=ConstantData[symbol][:-1]
                    temp.append(data)
                    ConstantData[symbol]=temp
                else:
                    temp=ConstantData[symbol]
                    temp.append(data)
                    ConstantData[symbol]=temp
        else:
            ConstantData[symbol]=[data]


def multigetnew(symbol,ConstantData,predata):
    if symbol in ConstantData.keys():
        with dict_lock:
            data_list=ConstantData[symbol]
        #print("predata:",predata)
        #print("data_list:",data_list)
        newdata_list=[]
        i=1
        while i<=len(data_list):
            #print("multigetnew,newdata_list:",newdata_list)
            #os.system("pause")
            newdata = data_list[-1*i]
            if (newdata[1] > predata[1]) or (newdata[0] > predata[0]):
                newdata_list.append(newdata)
            elif(newdata[1] == predata[1]) and (newdata[0] == predata[0]):
                if newdata!=predata:
                    newdata_list.append(newdata)
                else:
                    break
            i=i+1
        if newdata_list==[]:return None
        else: return list(reversed(newdata_list))
    else:
        return None



class MultiProcess(Process):
    def __init__(self,symbol, data,stradegy_tuple):
        self.symbol=symbol
        self.strategy = stradegy_tuple[0](data)
        self.strategy_param = stradegy_tuple[1]
        print("self.strategy_param:",self.strategy_param  )


    def process(self,TBdir,ConstantData):
        self.clearnrecord(TBdir)
        while self.strategy.data.currentbar< self.strategy.data.barcount:
            if  self.strategy.data.currentbar == self.strategy.data.barcount-1:
                self.strategy(**self.strategy_param)
                break
            self.strategy(**self.strategy_param)
            self.recodetoTB(TBdir)
            self.strategy.data.goToNextBar()
            #print("currentbar:", self.strategy.data.currentbar)

        #print(self.strategy.data.datalist[-1])
        #os.system("pause")
        while True:
            #print("datalist:",self.strategy.data.datalist)
            #predata = self.strategy.data.datalist[-1]
            predata = tuple([self.strategy.data.__dict__[k][0] for k in keyList])  # 用于判断是否是最新数据
            #print("pretime:",pretime)
            newdata_list = multigetnew(self.symbol,ConstantData,predata)
            if newdata_list is None: continue
            #print("newdata_list:",newdata_list)
            #os.system("pause")
            for newdata in newdata_list:
                if newdata[0] == predata[0] and newdata[1] == predata[1]:
                    #print('flesh data')
                    self.fleshdata(newdata)
                    self.strategy(**self.strategy_param)
                    self.recodetoTB(TBdir)
                if (newdata[0] > predata[0]) or (newdata[1] > predata[1]):
                    #print('add data')
                    #os.system("pause")
                    self.adddata(newdata)
                    self.strategy.data.goToNextBar()
                    self.strategy(**self.strategy_param)
                    self.recodetoTB(TBdir)


class Strategy1(BaseStrategy):
    def defineparam(self):
        pass

    def defineSeries(self):
        pass

    def defineSeriesfunction(self):
        pass

    def script(self):
        ConBuy=False
        ConSell=False
        ConSellShort=False
        mylots=1

        #print("\r {}, {}, {}, {}, {}, {}, {}, {}, {}, {}".format(
            #self.data.Symbol,self.data.BarInterval,self.data.currentbar,self.data.Time[0],self.data.Open[0],self.data.High[0],self.data.Low[0],self.data.Close[0],self.data.Vol[0],self.data.OpenInt[0]),end="")
        print(" {}, {}, {}, {}, {}, {}, {}, {}, {}, {}".format(
            self.data.Symbol,self.data.BarInterval,self.data.currentbar,self.data.Time[0],self.data.Open[0],self.data.High[0],self.data.Low[0],self.data.Close[0],self.data.Vol[0],self.data.OpenInt[0]))
        #print(self.data.currentbar, self.data.barcount)
        if self.data.currentbar%2==1: ConBuy=True
        else: ConSellShort=True

        if self.data.MarketPosition != 1 and ConBuy:
            self.data.Buy(mylots, self.data.Open[0])

        if self.data.MarketPosition !=-1 and ConSellShort:
            self.data.SellShort(mylots, self.data.Open[0])

        if self.data.High[0]>self.data.High[1]: ConBuy = True
        if self.data.BarsSinceEntry == 1: ConSell = True

        if self.data.MarketPosition ==1 and ConSell:
            self.data.Sell(mylots, self.data.Open[0])
        if self.data.MarketPosition == 0 and ConBuy:
            self.data.Buy(mylots, self.data.High[1]+1)


if __name__ == '__main__':
    '''
    Tradeinfo_list = [{'symbol': 'rb000_1', 'dates': (20191201,), 'stradegy_tuple': (Strategy1, {}),
                       'tbdir': r'F:\TradeOpera\20191213\rb000_1'},
                      {'symbol': 'i9000_1', 'dates': (20191201,), 'stradegy_tuple': (Strategy1, {}),
                       'tbdir': r'F:\TradeOpera\20191213\i9000_1'},
                      {'symbol': 'rb000_5', 'dates': (20191201,), 'stradegy_tuple': (Strategy1, {}),
                       'tbdir': r'F:\TradeOpera\20191213\rb000_5'}]
    '''
    Tradeinfo_list = [{'symbol': 'rb000_1', 'dates': (20191201,), 'stradegy_tuple': (Strategy1, {}),
    'tbdir': r'F:\TradeOpera\20191213\rb000_1'}]

    freeze_support()
    ConstantData = multiprocessing.Manager().dict()   #实时接收行情数据的容器
    threading.Thread(target=recvConstantData, args=()).start()  #开启线程，接收行情数据
    time.sleep(3)
    opera_mysql = OperaMysql('root', '123456', table='five_min_data')
    init_Tradeinfos(opera_mysql,Tradeinfo_list,ConstantData)  #处理初始化信息，包括申请数据库历史数据，合并内存中的零时数据(因为接收行情数据的线程先开)，生成MultiProcess的对象
    process_list = [multiprocessing.Process(target=tradeinfo['process'].process, args=(tradeinfo['tbdir'],ConstantData)) for tradeinfo in Tradeinfo_list]
    for p in process_list:
        p.start()
    for p in process_list:
        if p.is_alive():
            p.join()


    '''
    filepath = r"F:\rb_5min.txt"
    datalist1 = fileRead(filepath)
    data = Data(datalist1)
    # print(data.series_list)
    # print(data.__dict__.keys())
    #a = Strategy(data)
    #a.operateData()
    TBdir=r"F:\rb1"
    SSdir=r"D:\RealTrade\20191206"
    Process_obj = Process(data, (Strategy1,{"addnum_0":1,"addnum_1":2,"addnum_2":3}))
    Process_obj.process(TBdir,SSdir)
    '''