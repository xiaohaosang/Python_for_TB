import pymysql
import objgraph
from collections.abc import Iterator
from dateDeal.dateCompare import operaMysql as operaMysqlOndate
from dateDeal.fiveDataExchange2_3ForMy import exchange_mainthread
import time
import os
import pandas as pd
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# 创建对象的基类:
Base = declarative_base()
SymbolType = ['a', 'ag', 'al', 'AP', 'au', 'b', 'bb', 'bu', 'c', 'CF', 'CJ', 'cs', 'cu', 'CY', 'eg', 'fb', 'FG', 'fu', 'hc', 'i', 'IC', 'IF', 'IH', 'j', 'jd', 'jm', 'JR'
        , 'l', 'LR', 'm', 'MA', 'ni', 'OI', 'p', 'pb', 'PM', 'pp', 'rb', 'RI', 'RM', 'RS', 'ru', 'sc', 'SF', 'SM', 'sn', 'sp', 'SR', 'TA', 'v', 'WH', 'wr', 'y', 'ZC', 'zn']

class one_min_data(Base):
    # 表的名字:
    __tablename__ = 'one_min_data'
    # 表的结构:
    id = Column(String(20), primary_key=True, nullable=False)
    symboltype = Column(String(5), nullable=False)
    date = Column(Integer(), nullable=False)
    time = Column(Integer(), nullable=False)
    high = Column(Float(3), nullable=False)
    low = Column(Float(3), nullable=False)
    open = Column(Float(3), nullable=False)
    close = Column(Float(3), nullable=False)
    vol = Column(Integer(), nullable=False)
    openint = Column(Integer(), nullable=False)
    truedate = Column(Integer(), nullable=False)
    bar = Column(Integer(), nullable=False)

    def getlist(self):
        return [self.symboltype, self.date, self.time, self.high, self.low, self.open, self.close, self.vol, self.openint, self.truedate]

    def __repr__(self):
        return self.__tablename__

class five_min_data(Base):
    # 表的名字:
    __tablename__ = 'five_min_data'
    # 表的结构:
    id = Column(String(20), primary_key=True, nullable=False)
    symboltype = Column(String(5), nullable=False)
    date = Column(Integer(), nullable=False)
    time = Column(Integer(), nullable=False)
    high = Column(Float(3), nullable=False)
    low = Column(Float(3), nullable=False)
    open = Column(Float(3), nullable=False)
    close = Column(Float(3), nullable=False)
    vol = Column(Integer(), nullable=False)
    openint = Column(Integer(), nullable=False)
    truedate = Column(Integer(), nullable=False)
    bar = Column(Integer(), nullable=False)

    def getlist(self):
        return [self.symboltype, self.date, self.time, self.high, self.low, self.open, self.close, self.vol, self.openint, self.truedate]

    def __repr__(self):
        return self.__tablename__

class fifteen_min_data(Base):
    # 表的名字:
    __tablename__ = 'fifteen_min_data'
    # 表的结构:
    id = Column(String(20), primary_key=True, nullable=False)
    symboltype = Column(String(5), nullable=False)
    date = Column(Integer(), nullable=False)
    time = Column(Integer(), nullable=False)
    high = Column(Float(3), nullable=False)
    low = Column(Float(3), nullable=False)
    open = Column(Float(3), nullable=False)
    close = Column(Float(3), nullable=False)
    vol = Column(Integer(), nullable=False)
    openint = Column(Integer(), nullable=False)
    truedate = Column(Integer(), nullable=False)
    bar = Column(Integer(), nullable=False)

    def getlist(self):
        return [self.symboltype, self.date, self.time, self.high, self.low, self.open, self.close, self.vol, self.openint, self.truedate]

    def __repr__(self):
        return self.__tablename__

class day_data(Base):
    # 表的名字:
    __tablename__ = 'day_data'
    # 表的结构:
    id = Column(String(20), primary_key=True, nullable=False)
    symboltype = Column(String(5), nullable=False)
    date = Column(Integer(), nullable=False)
    time = Column(Integer(), nullable=False)
    high = Column(Float(3), nullable=False)
    low = Column(Float(3), nullable=False)
    open = Column(Float(3), nullable=False)
    close = Column(Float(3), nullable=False)
    vol = Column(Integer(), nullable=False)
    openint = Column(Integer(), nullable=False)
    truedate = Column(Integer(), nullable=False)
    bar = Column(Integer(), nullable=False)

    def getlist(self):
        return [self.symboltype, self.date, self.time, self.high, self.low, self.open, self.close, self.vol, self.openint, self.truedate]

    def __repr__(self):
        return self.__tablename__


class operaMysql():
    def __init__(self,name,password,host='localhost',database="mydata"):
        self.name = name
        self.password = password
        # 初始化数据库连接:
        self.engine = create_engine('mysql+mysqlconnector://'+self.name+':'+self.password+'@'+host+':3306/'+database)
        # self.engine = create_engine('mysql+mysqlconnector://root:123456@localhost:3306/testdata')
        # 创建DBSession类型:
        self.DBSession = sessionmaker(bind=self.engine)
        self.DataSource = day_data

    def selectDataSource(self, table):
            if table != str(self.DataSource()):
                print("select "+table)
                self.DataSource = eval(table)

    # 20000条批量插入
    def batechInsert(self, totalList, table):
        len1 = int(len(totalList) / 10000)
        for i in range(len1+1):
            # print("start",i)
            # objgraph.show_growth()
            self.insert(totalList[i * 10000:(i + 1) * 10000], table)
            # print("end",i)
            # objgraph.show_growth()
        # self.insert([totalList[0]], barinterval, bartype)

    def insertOneByOne(self, i, table):
        self.selectDataSource(table)
        session = self.DBSession()
        try:
            new_bar = self.DataSource(id=i[0], symboltype=i[1], date=i[2], time=i[3], high=i[4], low=i[5], open=i[6], close=i[7], vol=i[8], openint=i[9], truedate=i[10], bar=i[11])
            session.add(new_bar)
            session.commit()
        except Exception as e:
            print("插入失败",i[0])        #, e)
        finally:
            # 关闭session:
            session.close()

    def sqlinsert(self, list, table="表名"):
        # # 创建session对象:
        # print(len(list))
        # conn = self.engine.connect()
        # try:
        #     for i in list:
        #         strsql = "insert into "+table+" (id,symboltype,date,time,high,low,open,close,vol,openInt,trueDate,bar) values ('"+str(i[0])+"','"+str(i[1])+"',"+str(i[2])+","+str(i[3])+","+str(i[4])+","+str(i[5])+","+str(i[6])+","+str(i[7])+","+str(i[8])+","+str(i[9])+","+str(i[10])+","+str(i[11])+")"
        #         conn.execute(strsql)
        # except Exception as e:
        #     print("插入失败", e)
        session = self.DBSession()
        try:
            for i in list:
                # strsql = "insert into " + table + " (id,symboltype,date,time,high,low,open,close,vol,openInt,trueDate,bar) values (?,?,?,?,?,?,?,?,?,?,?,?)"
                # row = ("'" + str(i[0]) + "'", "'" + str(i[1]) + "'")
                # row = row + tuple(i[2:])
                # session.execute(strsql, row)
                strsql = "insert into "+table+" (id,symboltype,date,time,high,low,open,close,vol,openInt,trueDate,bar) values ('"+str(i[0])+"','"+str(i[1])+"',"+str(i[2])+","+str(i[3])+","+str(i[4])+","+str(i[5])+","+str(i[6])+","+str(i[7])+","+str(i[8])+","+str(i[9])+","+str(i[10])+","+str(i[11])+")"
                session.execute(strsql)
            session.commit()
        except Exception as e:
            print("插入失败", e)
        finally:
            # 关闭session:
            session.close()

    def pymsql_init(self):
        self.conn = pymysql.connect(host=host,user =self.name, password =self.password,    database="mydata", charset="utf8")
        self.conn.autocommit(0)

    def pymysqlInsert(self, list, table="表名"):
        cursor = self.conn.cursor()
        try:
            for i in list:
                strsql = "insert into " + table + " (id,symboltype,date,time,high,low,open,close,vol,openInt,trueDate,bar) values ('" + str(i[0]) + "','" + str(i[1]) + "'," + str(i[2]) + "," + str(i[3]) + "," + str(i[4]) + "," + str(i[5]) + "," + str(i[6]) + "," + str(i[7]) + "," + str(i[8]) + "," + str(i[9]) + "," + str(i[10]) + "," + str(i[11]) + ")"
                cursor.execute(strsql)
            self.conn.commit()
        except Exception as e:
            print("插入失败", e)
            self.conn.rollback()
        finally:
            cursor.close()

    def pymysqlClose(self):
        try:
            self.conn.close()
        except Exception as e:
            print("关闭失败", e)

    # 直接插入
    def insert(self, list, table):
        self.selectDataSource(table)
        # 创建session对象:
        session = self.DBSession()
        # print("start")
        # objgraph.show_growth()
        try:
            for i in list:
                # 创建新User对象:
                new_bar = self.DataSource(id=i[0], symboltype=i[1], date=i[2], time=i[3],high = i[4],low = i[5],open = i[6],close = i[7],vol = i[8],openint = i[9],truedate = i[10],bar = i[11])
                # 添加到session:
                session.add(new_bar)
                new_bar = None
            # 提交即保存到数据库:
            session.commit()
        except Exception as e:
            print("插入失败")#, e)
        finally:
            # 关闭session:
            session.close()
            # print("end")
            # objgraph.show_growth()

    # 获取数据
    def getTrueDate(self, startTime, endTime, SymbolType, table):
        self.selectDataSource(table)
        # 创建session对象:
        session = self.DBSession()
        try:
            totalList = []                                                                                                                                           #asc,升序,desc,降序
            for i in session.query(self.DataSource).filter(self.DataSource.id.like(SymbolType+'&%')).filter((self.DataSource.truedate >= startTime) & (self.DataSource.truedate <= endTime) & self.DataSource.bar == 1).order_by(self.DataSource.date.asc(),self.DataSource.time.asc()).all():
                totalList.append(i.getlist()[-1])
            return totalList
        except Exception as e:
            print("数据获取失败")        #,e)
        finally:
            # 关闭session:
            session.close()

    # 获取数据
    def getData(self, startTime, endTime, SymbolType, table):
        self.selectDataSource(table)
        # 创建session对象:
        session = self.DBSession()
        try:
            totalList = []  # asc,升序,desc,降序
            for i in session.query(self.DataSource).filter(self.DataSource.id.like(SymbolType + '&%')).filter((self.DataSource.truedate >= startTime) & (self.DataSource.truedate <= endTime) & self.DataSource.bar == 1).order_by(self.DataSource.date.asc(), self.DataSource.time.asc()).all():
                totalList.append(i.getlist())
            return totalList
        except Exception as e:
            print("数据获取失败")  # ,e)
        finally:
            # 关闭session:
            session.close()

    # 获取数据
    def getDataBySql(self, startTime, endTime, SymbolType, table):
        self.selectDataSource(table)
        # 创建session对象:
        session = self.DBSession()
        try:        # symboltype
            totalList = session.execute("select date,time,high,low,open,close,vol,openint,truedate,bar from "+table+" where id like '"+SymbolType+"&%' and truedate between "+str(startTime)+" and "+str(endTime)+" order by date,time;")
            return [list(x) for x in totalList]
        except Exception as e:
            print("数据获取失败" ,e)
        finally:
            # 关闭session:
            session.close()

    def getDayData(self,startTime,endTime,SymbolType,table):
        self.selectDataSource(table)
        # 创建session对象:
        session = self.DBSession()
        try:  # symboltype
            totalList = session.execute("select date,time,high,low,open,close,vol,openint,truedate,bar from " + table + " where id like '" + SymbolType + "&%' and truedate between " + str(startTime) + " and " + str(endTime) + " order by date,time;")
            df = pd.DataFrame([list(x) for x in totalList], columns=["date", "time", "high", "low", "open", "close", "vol", "openint", "truedate", "bar"])
            highprice = df[["high", "truedate"]].groupby(by="truedate", axis=0, as_index=False).max()
            lowprice = df[["low", "truedate"]].groupby(by="truedate", axis=0, as_index=False).min()
            openprice = pd.merge(df[["bar", "truedate"]].groupby(by="truedate", axis=0, as_index=False).min(), df, on=["bar", "truedate"], how="left")[["open", "truedate"]]
            closeprice = pd.merge(df[["bar", "truedate"]].groupby(by="truedate", axis=0, as_index=False).max(), df, on=["bar", "truedate"], how="left")[["close", "truedate", "vol", "openint"]]

            result =  pd.concat([highprice,lowprice,openprice,closeprice],axis=1).T.drop_duplicates().T
            result.columns =["truedate", "high", "low", "open", "close", "vol", "openint"]
            return result
        except Exception as e:
            print("数据获取失败", e)
        finally:
            # 关闭session:
            session.close()

    def exchange_data_to_daydata(self,list):
        df = pd.DataFrame(list, columns=["date", "time", "high", "low", "open", "close", "vol", "openint", "truedate", "bar"])
        highprice = df[["high", "truedate"]].groupby(by="truedate", axis=0, as_index=False).max()
        lowprice = df[["low", "truedate"]].groupby(by="truedate", axis=0, as_index=False).min()
        openprice = pd.merge(df[["bar", "truedate"]].groupby(by="truedate", axis=0, as_index=False).min(), df, on=["bar", "truedate"], how="left")[["open", "truedate"]]
        closeprice = pd.merge(df[["bar", "truedate"]].groupby(by="truedate", axis=0, as_index=False).max(), df, on=["bar", "truedate"], how="left")[["close", "truedate", "vol", "openint"]]

        result = pd.concat([highprice, lowprice, openprice, closeprice], axis=1).T.drop_duplicates().T
        result.columns = ["truedate", "high", "low", "open", "close", "vol", "openint"]
        return result

    def update(self,list):
        for i in list:
            session = self.DBSession()
            try:
                session.query(self.DataSource).filter(self.DataSource.id==i[0]).update({"symboltype":i[1],"date":i[2],"time":i[3],"high":i[4],"low":i[5],"open":i[6],"close":i[7],"vol":i[8],"openint":i[9],"truedate":i[10],"bar":i[11]})
                session.commit()
            except Exception as e:
                print("数据更新失败", e)
            finally:
                # 关闭session:
                session.close()

    def deletedata(self, startTime, endTime, symboltype, table):
        self.selectDataSource(table)
        # 创建session对象:
        session = self.DBSession()
        try:
            result = session.query(self.DataSource).filter(self.DataSource.id.like(symboltype + '&%')).filter((self.DataSource.truedate >= startTime) & (self.DataSource.truedate <= endTime)).all()
            for i in result:
                session.delete(i)
            session.commit()
        except Exception as e:
            print(symboltype + "数据删除失败", e)
        finally:
            session.close()

    def deletedata_bysql(self, startTime, endTime, symboltype, table):
        # 创建session对象:
        session = self.DBSession()
        try:
            # print("delete from "+table+" where id like '"+symboltype+"&%' and truedate between "+str(startTime)+" and "+str(endTime)+";")
            session.execute("delete from "+table+" where id like '"+symboltype+"&%' and truedate between "+str(startTime)+" and "+str(endTime)+";")
            session.commit()
        except Exception as e:
            print(symboltype + "数据删除失败", e)
        finally:
            session.close()

    def deletedata_bysql_list(self, trueDate1, trueDate2, symlist, table):
        t = time.time()
        j = 0
        for i in symlist:
            self.deletedata_bysql(trueDate1, trueDate2, i, table)
            #     dataManager.deletedata(trueDate1, trueDate2, i, barinterval, bartype)
            j = j + 1
            print("删除了" + i + "," + str(trueDate1) + "-" + str(trueDate2) + "的数据...进度:{:.2f}%,耗时：{:d}s".format((j) * 100 / len(symlist), int(time.time() - t)), end="\n")

    # 文件读取
    def fileRead(self,filename):
        file = open(filename,"r",encoding='UTF-8-sig')
        datalist = []
        text_lines = file.read().strip()
        list1 = text_lines.split("\n")
        for i in range(0,len(list1)):
            list2 = list1[i].split(",")
            datalist.append(list2)
        file.close()
        result = []
        for i in datalist:
            time = int(float(i[2]) * 10000)
            hang = [ i[0] + "&" + str(int(i[1])) + "&" + str(time),i[0], int(i[1]), time,
                    float(i[3]), float(i[4]), float(i[5]), float(i[6]), int(i[7]),
                    int(i[8]), int(i[9])]
            result.append(hang)  # 每个bar时间表示形式例如201812020905 表示2018年12月2日9:05
        # result = pd.DataFrame(result, columns=["商品代码", "时间", "最高价", "最低价", "开盘价", "收盘价", "成交量", "持仓量"])  # 若将此行注释，则返回数值列表
        return result

    # 文件夹下所有文件读取并批量插入数据库
    def dirInster(self, filePath, table):
        txtList = os.listdir(filePath)
        print("当前操作文件夹："+filePath)
        j = 0
        print("\r开始插入文件...进度:{:.2f}%".format((j) * 100 / len(txtList)), end="\t")
        for i in txtList:
            fPath = os.path.join(filePath, i)
            alllist = self.fileRead(fPath)
            self.batechInsert(alllist,table)
            j = j + 1
            print("\r插入文件" + str(i) + "的内容中...进度:{:.2f}%".format((j) * 100 / len(txtList)), end="\n")

    # 文件夹下所有文件读取并批量插入数据库
    def dirCSVInster(self, filePath, table):
        txtList = os.listdir(filePath)
        print("当前操作文件夹："+filePath)
        j = 0
        t = time.time()
        print("\r开始插入文件...进度:{:.2f}%".format((j) * 100 / len(txtList)), end="\t")
        for i in txtList:
            if i.endswith(".csv"):
                fPath = os.path.join(filePath, i)
                alllist = pd.read_csv(fPath,header=None, chunksize=50000)
                m = 0
                for k in alllist:
                    m = m + k.shape[0]
                    self.batechInsert(k.values, table)
                    print("\r文件" + str(i) + "的内容插入进度:{:d}条,耗时：{:d}s".format(m,int(time.time()-t)), end="\t")
            j = j + 1
            print("\r文件" + str(i) + "的内容插入完成...进度:{:.2f}%,耗时：{:d}s".format((j) * 100 / len(txtList),int(time.time()-t)), end="\n")

    def dirCSVInsterSQL(self, filePath, table):
        txtList = os.listdir(filePath)
        print("当前操作文件夹：" + filePath)
        j = 0
        t = time.time()
        print("\r开始插入文件...进度:{:.2f}%".format((j) * 100 / len(txtList)), end="\t")
        for i in txtList:
            if i.endswith(".csv"):
                fPath = os.path.join(filePath, i)
                alllist = pd.read_csv(fPath, header=None, chunksize=50000)
                m = 0
                for k in alllist:
                    m = m + k.shape[0]
                    self.sqlinsert(k.values, table)
                    print("\r文件" + str(i) + "的内容插入进度:{:d}条,耗时：{:d}s".format(m,int(time.time()-t)), end="")
            j = j + 1
            print("\r文件" + str(i) + "的内容插入完成...进度:{:.2f}%,耗时：{:d}s".format((j) * 100 / len(txtList),int(time.time()-t)), end="\n")

    def dirCSVInsterPYMYSQL(self, filePath, table):
        txtList = os.listdir(filePath)
        print("当前操作文件夹：" + filePath)
        j = 0
        t = time.time()
        print("\r开始插入文件...进度:{:.2f}%".format((j) * 100 / len(txtList)), end="\t")
        for i in txtList:
            if i.endswith(".csv"):
                fPath = os.path.join(filePath, i)
                alllist = pd.read_csv(fPath, header=None, chunksize=5000)
                m = 0
                for k in alllist:
                    m = m + k.shape[0]
                    self.pymysqlInsert(k.values, table)
                    print("\r文件" + str(i) + "的内容插入进度:{:d}条,耗时：{:d}s".format(m,int(time.time()-t)), end="")
            j = j + 1
            print("\r文件" + str(i) + "的内容插入完成...进度:{:.2f}%,耗时：{:d}s".format((j) * 100 / len(txtList),int(time.time()-t)), end="\n")
        self.pymysqlClose()

    def dirCSVInsterOneByOne(self, filePath, table):
        txtList = os.listdir(filePath)
        print("当前操作文件夹：" + filePath)
        j = 0
        t = time.time()
        for i in txtList:
            if i.endswith(".csv"):
                fPath = os.path.join(filePath, i)
                alllist = pd.read_csv(fPath, header=None)
                for k in alllist.values:
                    self.insertOneByOne(k,table)
            j = j + 1
            print("\r文件" + str(i) + "的内容插入完成...进度:{:.2f}%,耗时：{:d}s".format((j) * 100 / len(txtList),int(time.time()-t)), end="\n")


# 校验数据
def dateCheck(name, password, host, dataManager, trueDate1, trueDate2, table):
    t = int(time.time())
    dateManager = operaMysqlOndate(name,password,host)
    f = open(r".\date"+str(t)+".txt", "w")
    for i in SymbolType:
        aset = set(dataManager.getTrueDate(trueDate1, trueDate2, i, table))
        dset = set(dateManager.getData(trueDate1, trueDate2))
        datelist = list(dset - aset)
        datelist.sort()
        print("aset:"+str(len(aset))+",dset:"+str(len(dset))+","+i+":"+str(datelist))
        f.write("aset:"+str(len(aset))+",dset:"+str(len(dset))+","+i+":"+str(datelist)+"\n")
    print("数据比对耗时："+str(int(time.time())-t)+"s")
    f.close()


def exchangeDataAndInsterAndCheck(rootdir, name, password, host, trueDate1, trueDate2, table):
    dataManager = operaMysql(name, password, host)
    t = time.time()
    # dataManager.dirCSVInster(rootdir, barinterval, bartype)        # 批量插入,吃内存

    dataManager.dirCSVInsterSQL(rootdir,table)                    # sql语句插入，性能较低，但能接受

    # dataManager.pymsql_init()
    # dataManager.dirCSVInsterPYMYSQL(rootdir,table)    #通过pymysql的sql语句插入
    # dataManager.pymysqlClose()

    print("总耗时："+str(int(time.time()-t))+"s")
    dateCheck(name, password, host, dataManager, trueDate1, trueDate2, table)


def replace_dircsv(rootdir, name, password, host, trueDate1, trueDate2, deletelist, table):
    dataManager = operaMysql(name, password, host)
    t = time.time()
    dataManager.deletedata_bysql_list(trueDate1, trueDate2, deletelist, table)  # 删除
    dataManager.dirCSVInster(rootdir, table)  # 批量插入,吃内存
    print("总耗时：" + str(int(time.time() - t)) + "s")


if __name__ == '__main__':
    '''
    步骤一、从tb获取数据(手动)
    步骤二、转换数据为csv(数据所在文件夹，起始时间（trueDate-1），终止时间（trueDate）)
    步骤三、读取数据并插入数据库(账号，密码，地址)
    步骤四、获取数据日期并与数据库日期对比(在当前目录下生成文件)
    
    *****下面四步唯一与上面的区别就是下面为逐条插入，上面是批量插入*****
    步骤五、重新获取数据(手动)
    步骤六、转换数据
    步骤七、逐条插入数据
    步骤八、重复步骤四，检验数据
    '''
    name = "python"
    password = ""
    host = "localhost"

    # 均为真实日期
    rootdir=r"D:\dataOutPut\OneMin\20190807-20191105"
    starttime = 20190807
    endtime = 20191105

    deletelist = SymbolType
    table = "one_min_data"
    dataManager = operaMysql(name, password, host)



    # print(pd.DataFrame(dataManager.getDataBySql(starttime, endtime, "rb", table)))
    # t = time.time()
    # d = dataManager.getDataBySql(starttime, endtime, "rb", table)
    # # print(d)
    # print("总耗时1：" + str(int(time.time() - t)) + "s")
    # print(dataManager.exchange_data_to_daydata(d))
    # print("总耗时1：" + str(int(time.time() - t)) + "s")

    # t = time.time()
    # result = dataManager.getDataBySql(starttime, endtime, "rb", table)
    # result = pd.DataFrame(result)
    # print(result)
    # print("总耗时1：" + str(int(time.time() - t)) + "s")

    # exchange_mainthread(rootdir, starttime, endtime)  #转换数据为csv
    #
    # exchangeDataAndInsterAndCheck(rootdir, name, password, host, starttime, endtime, table)  # 插入+检查

    # replace_dircsv(rootdir, name, password, host, starttime, endtime, deletelist, table)  # 删除+插入

    # dateCheck(name, password, host, dataManager, starttime, endtime, table)  # 单独检查
