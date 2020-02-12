import getnewdata
import threading
import os
#import collections
from multiprocessing import freeze_support
import time
# from multiprocessing import Queue
#from multiprocessing.managers import BaseManager
import socket
import pickle,struct
deque =[]
lock = threading.Lock()
IsClientExit=False
from MySqlOperation import OperaMysql

BarInterval_dict={}

def sever():
    global deque
    global IsClientExit
    s = socket.socket()         # 创建 socket 对象
    host = socket.gethostname() # 获取本地主机名
    port = 22222                # 设置端口
    s.bind((host, port))
    s.listen(1)
    print("server is start",host,port)
    while True:
        try:
            c, addr = s.accept()
            print('连接地址:', addr)
            c.send("sever is connect \n".encode("utf-8"))
            with lock:
                IsClientExit = True
            while True:
                #print(IsClientExit)
                with lock:
                    #deque=[(1,2)]
                    #print(deque)
                    if len(deque) != 0:
                        #print("sever queue:",deque)
                        pickledata = pickle.dumps(deque)
                        len_bytes = struct.pack('i', len(pickledata)) #防止粘包,设置len_bytes
                        c.sendall(len_bytes)
                        c.sendall(pickledata)
                    deque=[]
                time.sleep(0.25)
        except Exception as e:
            print(e)
            c.close()
            IsClientExit=False


def sever_1():
    global deque
    global IsClientExit
    s = socket.socket()         # 创建 socket 对象
    s.setblocking(False)
    host = socket.gethostname() # 获取本地主机名
    port = 22222                # 设置端口
    s.bind((host, port))
    s.listen(1)
    client_list=[]
    print("server is start",host,port)
    while True:
        try:
            c, addr = s.accept()
            print('连接地址:', addr)
            c.send("sever is connect \n".encode("utf-8"))
        except Exception:
            pass
        else:
            client_list.append(c)
        #print("client_list",client_list)
        if client_list:
            if IsClientExit==False:
                with lock:
                    IsClientExit = True

            with lock:
                if len(deque) != 0:
                    pickledata = pickle.dumps(deque)
                    len_bytes = struct.pack('i', len(pickledata))  # 防止粘包,设置len_bytes
                    for c in client_list:
                        try:
                            c.sendall(len_bytes)
                            c.sendall(pickledata)
                        except Exception as e:
                            print(e)
                            c.close()
                            client_list.remove(c)
                    deque=[]
            time.sleep(0.25)
        else:
            with lock:
                IsClientExit = False

def getnewforever(rootdir,relpath, prelastline_dict,prelastdata_dict,opera_mysql):
    barstarttime_list = [None]
    symboltype,barinterval=relpath.split("_")
    barinterval=int(barinterval)
    if barinterval==1:
        table='one_min_data'
        print(relpath,table)
    if barinterval==5:
        table ='five_min_data'
        print(relpath, table)
    #print("BarInterval:",BarInterval)
    while True:
        newdata = getnewdata.getnew(rootdir,relpath, prelastline_dict,barstarttime_list,barinterval) #获取最新的数据
        if newdata is None:
            data_DataBase = prelastdata_dict[relpath]
            print(relpath, "over time insert:", data_DataBase)
            insertMysql(symboltype, data_DataBase, opera_mysql, table)
            barstarttime_list=[None]
            continue
        prelastdata = prelastdata_dict[relpath]     #线程中,创建自己的变量，记录前一个数据，不需要prelastdata_dict[relpath]，后期优化
        #print(relpath, "prelastdata:",prelastdata)
        #print(relpath, "newdata:", newdata)
        if (prelastdata is None) or (prelastdata[0]!= newdata[0] or prelastdata[1] != newdata[1]): #初始，或和前一个数据的时间不一样(不是同一个bar)
            data_DataBase=prelastdata
            barstarttime_list=[time.time()] #获取这根bar开始的时间,用于判断周期过后，加到数据库(针对最后一个bar，即无交易时间段的前一个bar，加到数据库）
        else:
            data_DataBase = None
        #print(relpath,"data_DataBase",data_DataBase)
        prelastdata_dict[relpath] = newdata
        with lock:
            #print("IsClientExit：",IsClientExit)
            if IsClientExit is True:
                deque.append((relpath,newdata))
        if data_DataBase is not None:
            print(relpath,"has newbar insert:",data_DataBase)
            insertMysql(symboltype, data_DataBase, opera_mysql, table)



def insertMysql(symboltype,data_DataBase,opera_mysql,table):
    date = str(data_DataBase[0])
    _time = str(data_DataBase[1])
    id = symboltype + '&' + date + '&' + _time
    insertdata = [id, symboltype] + list(data_DataBase)
    print("insertdata", insertdata)
    opera_mysql.insertOneByOne(insertdata, table)


def startthreads(rootdir,opera_mysql):
    prelastline_dict={}
    prelastdata_dict={}
    thread_list = []
    for relpath in os.listdir(rootdir):
        #abspath=os.path.join(rootdir,relpath)
        relpath=relpath.split('.')[0]
        #print('relpath:',relpath)
        #os.system("pause")
        prelastline_dict[relpath]=None
        prelastdata_dict[relpath]=None
        t = threading.Thread(target=getnewforever, args=(rootdir,relpath, prelastline_dict,prelastdata_dict,opera_mysql))
        thread_list.append(t)
        t.start()
    #for t in thread_list:
        #t.join()

def creatdirs(rootdir):
    _localtime = time.localtime(time.time())
    _localdate = _localtime[0] * 10000 + _localtime[1] * 100 + _localtime[2]
    newday_rootdir = rootdir+"//"+str(_localdate)
    #print(newday_rootdir)
    for tradesymbol in tradesymbol_list:
        p=newday_rootdir + '//' + tradesymbol
        #print(p)
        if not os.path.exists(p):
            os.makedirs(p)
    return newday_rootdir


tradesymbol_list=['rb000_1','i9000_1','j9000_1',
                  'rb000_5','i9000_5','j9000_5']

if __name__ == '__main__':
    rootdir=r"F:/TradeData/constant"
    newday_rootdir = creatdirs(rootdir)
    freeze_support()
    #opera_mysql = OperaMysql('root', '123456', table='one_min_data')
    #print(opera_mysql.getData_byDate(20160101, 20160104, 'i9000'))
    opera_mysql = OperaMysql('root', '123456', table='one_min_data')
    startthreads(newday_rootdir,opera_mysql)
    time.sleep(1)
    sever_1()
    #test()













