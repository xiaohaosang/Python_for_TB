from decimal import *
import re
def fileRead(filename):
    file = open(filename, "r", encoding='UTF-8-sig')
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
                float(datalist[i][3]), float(datalist[i][4]), float(datalist[i][5]), int(datalist[i][6]),
                int(datalist[i][7]), int(datalist[i][8])]
        result.append(hang)  # 每个bar时间表示形式例如201812020905 表示2018年12月2日9:05
    # result = pd.DataFrame(result, columns=["商品代码", "时间", "最高价", "最低价", "开盘价", "收盘价", "成交量", "持仓量"])  # 若将此行注释，则返回数值列表
    return result

def fileRead_tomysql(filename):
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
        time = str(Decimal([i][2]).quantize(Decimal('0.0000')) * 10000)
        hang = [ i[0] + "&" + str(int(i[1])) + "&" + str(time),i[0], int(i[1]), time,
                float(i[3]), float(i[4]), float(i[5]), float(i[6]), int(i[7]),
                int(i[8]), int(i[9])]
        result.append(hang)  # 每个bar时间表示形式例如201812020905 表示2018年12月2日9:05
    # result = pd.DataFrame(result, columns=["商品代码", "时间", "最高价", "最低价", "开盘价", "收盘价", "成交量", "持仓量"])  # 若将此行注释，则返回数值列表
    return result


