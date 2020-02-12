
# 对多商品序列值测试
class Function_1(BaseFunction):
    def defineparam(self):
        self.addnum_1 = 0
        self.addnum_2 = 0

    def defineSeries(self):
        self.create_series("accumulate_1", 0)

    def defineSeriesfunction(self):
        self.fun = Function_2
        self.fun1 = Function_2

    def script(self):
        print("Function_1_**********")
        print(self.data0.Close[0], self.data1.Close[0])
        self.accumulate_1[0] = self.accumulate_1[1] + self.addnum_1
        print("accumulate_1:", self.accumulate_1[0])
        self.fun(addnum_2 = self.addnum_2+1)
        self.fun1(addnum_2=self.addnum_2+2)

class Function_2(BaseFunction):
    def defineparam(self):
        self.addnum_2 = 3

    def defineSeries(self):
        self.create_series("accumulate_2", 0)

    def defineSeriesfunction(self):
        pass

    def script(self):
        print("Function_2_**********:")
        print(self.data0.Close[0],self.data1.Close[0])
        self.accumulate_2[0] = self.accumulate_2[1] + self.addnum_2
        print("accumulate_2:", self.accumulate_2[0])


class Strategy1(BaseStrategy):
    def defineparam(self):
        self.addnum_0 = 1

    def defineSeries(self):
        self.create_series("accumulate_0", 0)

    def defineSeriesfunction(self):
        self.fun = Function_1
        self.fun1 = Function_1

    def script(self):
        print("series:",self.series_list)
        print("Seriesfunction_list:",self.Seriesfunction_list)
        for i in self.series_list:
            print(i.interlist)
        self.accumulate_0[0] = self.accumulate_0[1] + self.addnum_0
        print("accumulate_0:", self.accumulate_0[0])
        self.fun(addnum_1=self.addnum_0*2,addnum_2=self.addnum_0*2)
        self.fun1(addnum_1=self.addnum_0*4, addnum_2=self.addnum_0*4)

#  对多商品进行测试
class Strategy_pmutil(BaseStrategy):
    def defineparam(self):
        pass

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
            self.data1.Buy(mylots,self.data1.Open[0])

# 对单商品测试, 针对非singleproduct
class Strategy_psimgle(BaseStrategy):
    def defineparam(self):
        pass

    def defineSeries(self):
        pass

    def defineSeriesfunction(self):
        pass

    def script(self):
        print("script************")
        ConBuy = False
        ConSell = False
        ConSellShort = False
        mylots = 1

        print(self.data.Close[0])
        print("Close.interlist:", self.data.Close.interlist)
        if self.data.currentbar%10==1: ConBuy=True
        if self.data.currentbar%10 == 6: ConSellShort = True

        if self.data.MarketPosition != 1 and ConBuy:
            self.data.Buy(mylots, self.data.Open[0])

        if self.data.MarketPosition != -1 and ConSellShort:
            self.data.SellShort(mylots, self.data.Open[0])