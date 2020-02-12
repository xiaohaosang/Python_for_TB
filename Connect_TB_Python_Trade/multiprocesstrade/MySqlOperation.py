from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, String, Integer,Float,ForeignKey,Text,Table
from sqlalchemy.ext.declarative import declarative_base
from tools import fileRead_tomysql
from decimal import *
import re,os
Base = declarative_base()


class one_min_data(Base):
    # 表的名字:
    __tablename__ = 'one_min_data'
    # 表的结构:
    id = Column(String(20), primary_key=True, nullable=False)
    symboltype = Column(String(5), nullable=False)
    date = Column(Integer(), nullable=False)
    time = Column(Integer(), nullable=False)
    open = Column(Float(3), nullable=False)	
    high = Column(Float(3), nullable=False)
    low = Column(Float(3), nullable=False)
    close = Column(Float(3), nullable=False)
    vol = Column(Integer(), nullable=False)
    openint = Column(Integer(), nullable=False)
    truedate = Column(Integer(), nullable=False)

    def getlist(self):
        return [self.symboltype, self.date, self.time, self.open, self.high, self.low, self.close, self.vol, self.openint, self.truedate]

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
    open = Column(Float(3), nullable=False)	
    high = Column(Float(3), nullable=False)
    low = Column(Float(3), nullable=False)
    close = Column(Float(3), nullable=False)
    vol = Column(Integer(), nullable=False)
    openint = Column(Integer(), nullable=False)
    truedate = Column(Integer(), nullable=False)

    def getlist(self):
        return [self.symboltype, self.date, self.time, self.high, self.low, self.open, self.close, self.vol, self.openint, self.truedate]

    def __repr__(self):
        return self.__tablename__
		
		
class OperaMysql(object):
    def __init__(self,name,password,host='localhost',database='tradedata',table=None):
        self.name = name
        self.password = password
        # 初始化数据库连接:
        self.engine = create_engine('mysql+mysqlconnector://'+self.name+':'+self.password+'@'+host+':3306/'+database)
        # self.engine = create_engine('mysql+mysqlconnector://root:123456@localhost:3306/testdata')
        # 创建DBSession类型:
        self.DBSession = sessionmaker(bind=self.engine)
        if table is not None:
            self.table = eval(table)
	
    def selecttable(self, table):
        self.table = eval(table)	

    def insert(self, list, table=None):
        #print(table,type(table))
        if table is not None: table=eval(table)
        # 创建session对象:
        session = self.DBSession()
        # print("start")
        # objgraph.show_growth()
        try:
            for i in list:
                # 创建新User对象:
                #print(i)
                new_bar = table(id=i[0], symboltype=i[1], date=i[2], time=i[3],open = i[4],high = i[5],low = i[6],close = i[7],vol = i[8],openint = i[9],truedate = i[10])
                # 添加到session:
                session.add(new_bar)
                new_bar = None
            # 提交即保存到数据库:
            session.commit()
        except Exception as e:
            print(("插入失败"), e)
        finally:
            # 关闭session:
            session.close()
            # print("end")
            # objgraph.show_growth()		
		
    def batechInsert(self, totalList, table=None):
        len1 = int(len(totalList) / 10000)
        for i in range(len1+1):
            # print("start",i)
            # objgraph.show_growth()
            self.insert(totalList[i * 10000:(i + 1) * 10000], table)


    def insertOneByOne(self, i, table=None):
        if table is not None: table=eval(table)
        else:table=self.table
        session = self.DBSession()
        try:
            new_bar = table(id=i[0], symboltype=i[1], date=i[2], time=i[3],open = i[4],high = i[5],low = i[6],close = i[7],vol = i[8],openint = i[9],truedate = i[10])
            session.add(new_bar)
            session.commit()
        except Exception as e:
            print("插入失败",i[0],e)
        finally:
            # 关闭session:
            session.close()


    # 获取数据
    def getData_byTruedate(self, startTime, endTime, SymbolType, table=None):
        if table is not None: table=eval(table)
        else:table=self.table

        # 创建session对象:
        session = self.DBSession()
        try:
            totalList = []  # asc,升序,desc,降序
            for i in session.query(table).filter(table.id.like(SymbolType + '&%')).filter((table.truedate >= startTime) & (table.truedate <= endTime)).order_by(table.date.asc(), table.time.asc()).all():
                totalList.append(i.getlist())
            return totalList
        except Exception as e:
            print("数据获取失败")  # ,e)
        finally:
            # 关闭session:
            session.close()

    def getData_byDate(self, startTime, endTime, SymbolType, table=None):
        if table is not None: table=eval(table)
        else:table=self.table
        #print(table)
        # 创建session对象:
        session = self.DBSession()
        try:
            totalList = []  # asc,升序,desc,降序
            for i in session.query(table).filter(table.id.like(SymbolType + '&%')).filter((table.date >= startTime) & (table.date <= endTime)).order_by(table.date.asc(), table.time.asc()).all():
                totalList.append(i.getlist())
            return totalList
        except Exception as e:
            print("数据获取失败")  # ,e)
        finally:
            # 关闭session:
            session.close()

    def deletedata_byTruedate(self, startTime, endTime, symboltype, table=None):
        if table is not None: table=eval(table)
        else:table=self.table
        # 创建session对象:
        session = self.DBSession()
        try:
            result = session.query(self.table).filter(self.table.id.like(symboltype + '&%')).filter((self.table.truedate >= startTime) & (self.table.truedate <= endTime)).all()
            for i in result:
                session.delete(i)
            session.commit()
        except Exception as e:
            print(symboltype + "数据删除失败", e)
        finally:
            session.close()

    def deletedata_byDate(self, startTime, endTime, symboltype=None, table=None):
        if table is not None: table=eval(table)
        else:table=table
        # 创建session对象:
        session = self.DBSession()
        try:
            if symboltype is None: result = session.query(table).filter((table.date >= startTime) & (table.date <= endTime)).all()
            else: result = session.query(table).filter(table.id.like(symboltype + '&%')).filter((table.date >= startTime) & (table.date <= endTime)).all()
            for i in result:
                session.delete(i)
            session.commit()
        except Exception as e:
            print(symboltype + "数据删除失败", e)
        finally:
            session.close()

			
    def update(self,list):
        for i in list:
            session = self.DBSession()
            try:
                session.query(self.table).filter(self.table.id==i[0]).update({"symboltype":i[1],"date":i[2],"time":i[3],"open":i[4],"high":i[5],"low":i[6],"close":i[7],"vol":i[8],"openint":i[9],"truedate":i[10]})
                session.commit()
            except Exception as e:
                print("数据更新失败", e)
            finally:
                # 关闭session:
                session.close()

    def fileRead(self,filename):
        file = open(filename,"r",encoding='UTF-8-sig')
        datalist = []
        text_lines = file.read().strip()
        list1 = text_lines.split("\n")
        for i in range(0,len(list1)):
            #list2 = list1[i].split(",")
            list2 = re.split(' |,', list1[i])
            datalist.append(list2)
        file.close()
        result = []
        for i in datalist:
            #print(i)
            _time = str(Decimal(i[2]).quantize(Decimal('0.0000')) * 10000)
            _time=int(format(float(_time), '0.0f'))
            hang = [ i[0] + "&" + str(int(i[1])) + "&" + str(_time),i[0], int(i[1]), _time ,
                    float(i[3]), float(i[4]), float(i[5]), float(i[6]), int(i[7]),
                    int(i[8]), int(i[9])]
            result.append(hang)  # 每个bar时间表示形式例如201812020905 表示2018年12月2日9:05
        # result = pd.DataFrame(result, columns=["商品代码", "时间", "最高价", "最低价", "开盘价", "收盘价", "成交量", "持仓量"])  # 若将此行注释，则返回数值列表
        return result

    def dirInsert(self, filePath, table=None):
        txtList =[t for t in os.listdir(filePath) if os.path.isfile(os.path.join(filePath, t))]
        print("当前操作文件夹："+filePath)
        j = 0
        print("\r开始插入文件...进度:{:.2f}%".format((j) * 100 / len(txtList)), end="\n")
        for i in txtList:
            fPath = os.path.join(filePath, i)
            alllist = self.fileRead(fPath)
            #print(i,alllist)
            self.batechInsert(alllist,table)
            j = j + 1
            print("\r插入文件" + str(i) + "的内容中...进度:{:.2f}%".format((j) * 100 / len(txtList)), end="")
			
    def update_bydate(self,startTime,endTime,table):
        if table is not None:
            filepath = update_filepath_dict[table]
            #print(filepath)
        self.deletedata_byDate(startTime, endTime, table=table)
        self.dirInsert(filepath,table=table)
        for symbol in symbol_list:
            length=len(list(self.getData_byDate(startTime, endTime, symbol, table=table)))
            print(symbol,length)



def build_db():
    engine = create_engine('mysql+mysqlconnector://root:123456@localhost:3306/tradedata')
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    '''
    db_conn = engine.connect()
    db_conn.execute(r'''
    ''')
    '''

update_filepath_dict={'one_min_data':r'F:\TradeData\history_from_TB\one_min_data',
                      'five_min_data': r'F:\TradeData\history_from_TB\five_min_data'}
symbol_list=['rb000','i9000','j9000']


if __name__ == '__main__':
    opera_mysql=OperaMysql('root','123456',table="one_min_data")

    #可以查看之前的情况
    #for i in opera_mysql.getData_byDate(20160101,20191216,'i9000',"five_min_data"):
        #print(i)

    #每日更新
    opera_mysql.update_bydate(20191219,20191219,'one_min_data')
    opera_mysql.update_bydate(20191219,20191219,'five_min_data')

 		

