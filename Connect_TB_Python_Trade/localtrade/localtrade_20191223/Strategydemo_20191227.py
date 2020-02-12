from BackTest_mutilproduct import *
#from  backTest20191204 import *

class Strategy_pmutil(BaseStrategy):
    class



    def defineparam(self):
        self.operation_dict={}

    def defineSeries(self):
        pass

    def defineSeriesfunction(self):
        pass

    def script(self):

        print("script************")
        ConBuy=False
        ConSell=False
        ConSellShort=False
        mylots=1
        print("currentbar:",self.currentbar)
        print("barcount:", self.barcount)
        print("Date[0]:", self.Date[0])
        print("Time[0]:",self.Time[0])
        #print("Close.interlist:",self.data.Close.interlist)
        print("Close.data[0]:",self.data.Close[0])
        print("Close.data1[0]:",self.data1.Close[0])
        if self.data1.Close[0]!=0:
            print("ratio:",self.data.Close[0]/self.data1.Close[0])

        if self.currentbar%10==1: ConBuy=True
        if self.currentbar%10 == 6: ConSellShort = True

        if self.data.MarketPosition != 1 and ConBuy:
            self.data.Buy(mylots, self.data.Open[0])
            self.data1.SellShort(mylots,self.data1.Open[0])

        if self.data.MarketPosition !=-1 and ConSellShort:
            self.data.SellShort(mylots, self.data.Open[0])
            self.data1.Buy(mylots, self.data1.Open[0])

        # 需要开仓的bar，写入字典，根据策略记录各种状态
        if self.currentbar not in self.operation_dict.keys():
            self.operation_dict[self.currentbar] = {}
            operbar = self.operation_dict[self.currentbar]
            if ConBuy:
                operbar['MarketPos'] = 1
            elif ConSellShort:
                operbar['MarketPos'] = -1
            operbar['EnterPrice'] = EnterPrice
            operbar['EnterHighest']=self.data.High[0]
            operbar['EnterLowest']= self.data.Low[0]




if __name__ == '__main__':
    #filepath = r"F:\rb_5min.txt"
    filepath=None
    datalist1 = fileRead(filepath)
    datalist2 = fileRead(filepath)
    print(datalist1)
	#datalist2 = fileRead(filepath)
    # print(data.series_list)
    # print(data.__dict__.keys())
    #a = Strategy(data)
    #a.operateData()
    TBdir1=r"F:\SimpleLocalTrade\opera\rb000"
    TBdir2 = r"F:\SimpleLocalTrade\opera\i9000"
    SSdir_1=r"F:\SimpleLocalTrade\tradedata\rb000"
    SSdir_2 = r"F:\SimpleLocalTrade\tradedata\i9000"
    Process_obj = Process([datalist1,datalist2], (Strategy_pmutil,{"addnum_0":1,"addnum_1":2,"addnum_2":3}))
    Process_obj.process([TBdir1,TBdir2],[SSdir_1,SSdir_2])
    #Process_obj = Process(Data(datalist1), (Strategy_pmutil,{"addnum_0":1,"addnum_1":2,"addnum_2":3}))
    #Process_obj.process(TBdir1,SSdir_1)