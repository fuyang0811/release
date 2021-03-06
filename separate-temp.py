import os
import numpy as np
import matplotlib.pyplot as plt

pi = 3.141592654
h = 6.62607004 * 10 ** -34
e = 1.60217733 * 10 ** -19
me = 9.10938356 * 10 ** -30
"""
使用origin删除掉废弃数据，最后留下四列（温度，磁场，电阻，霍尔）或者三列（温度，磁场，电阻）。保证每个温度，磁场都会从负值正值，或者正值到负值。
使用origin导出ASCII，使用“，”作为分隔符。不要抬头，即输出文件只有数据。(如图)
将程序和数据文件放入同一文件夹。注意需要只有一个dat文件。

运行程序，初始化大概需要几秒。
输入参数，若直接回车则是使用默认值。
最后会生成一张图，分别为原始的R，Ryx。以及处理后的rho，rhoyx。若输入为三列数据，则只有R。可以按需要保存。若输入的样品尺寸为1，1，1，则rho会自动改为R。
会生成R数据和hall数据。文件名并附有样品尺寸的信息，尺寸的逗号中英文皆可。
生成的数据文件可直接拖入origin中。

有时候会报警，因为内插时遇到了相同的x，和不同的y。python会只保留一个点。对最终结果没有影响。

文件夹中的Sheet1.dat为示例文件。
"""
workdir = os.getcwd()
def rename(newfile):
    i = 2
    last=newfile.strip().split('.')[-1]
    newfile = newfile[:-1*len(last)-1]
    while True:
        try:
            fpw = open(newfile+"."+last, "r")  # 如果不存在会报错
            fpw.close
            if i == 2:
                newfile = newfile + "(%i)" % i
            else:
                newfile = newfile[:-1*len(str(i))-2] + "(%i)" % i
            i = i + 1
        except IOError:
            break
    newfile=newfile+"."+last
    return newfile
def Rtorho(data, abc):
    """电阻到电阻率"""
    abc = abc.replace("，", ",")
    abc = abc.strip().split(',')
    abcdeal = []
    for i in abc:
        i = float(i)
        abcdeal.append(i)
    shape = data.shape
    i = 1
    while True:
        data[:, i] = data[:, i] * abcdeal[1] * abcdeal[2] / abcdeal[0]
        if i == shape[1] - 1:
            break
        i = i + 1
    return data
def Ryxtorhoyx(data, abc):
    """hall电阻到霍尔电阻率"""
    abc = abc.replace("，", ",")
    abc = abc.strip().split(',')
    abcdeal = []
    for i in abc:
        i = float(i)
        abcdeal.append(i)
    shape = data.shape
    i = 1
    while True:
        data[:, i] = data[:, i] * abcdeal[2]
        if i == shape[1] - 1:
            break
        i = i + 1
    return data
def addheadline(headline, oldfile, newfile):
    """在新文件中加入抬头，删除旧文件"""
    with open(oldfile, "r+")as fp:
        tmp_data = fp.read()  # 读取所有文件, 文件太大时不用使用此方法
        fp.seek(0)  # 移动游标
        fpw=open(rename(newfile),"w+")
        fpw.write(headline + "\n" + tmp_data)
        fpw.close()
    os.remove(oldfile)
def savesinglefile(headlines, data, type, abc):
    """将处理后的每个温度的数据储存在单个文件"""
    headlines = headlines.strip().split(',')
    k=0
    while True:
        if headlines[k] != "Field(T)":
            name = headlines[k].strip().split('(')
            np.savetxt("tmp.dat", data[:, [k-1, k]], fmt="%.8e", delimiter=",")
            if abc == "1,1,1":
                if type=="hall":
                    headline = "Field(T),Ryx(ohm)"
                else:
                    headline = "Field(T),Rxx(ohm)"
            else:
                if type=="hall":
                    headline = "Field(T),rhoyx(ohm)"
                else:
                    headline = "Field(T),rhoyx(ohm cm)"
            addheadline(headline, "tmp.dat", type + "-" + name[0] + ".dat")
        if k==len(headlines)-1:
            break
        k=k+1
def halltest(name):
    """通过判断初始数据列数，确认是否有hall数据，如果3行则无hall数据"""
    a = open(name, "r+")
    data = a.readlines()
    a.close()
    line = data[0].strip().split('\t')  # strip()默认移除字符串首尾空格或换行符
    if len(line) > 3:
        if len(line) > 4:
            print("报警：数据列数不标准")
            input("输入任意键继续或直接关闭窗口退出")
        return True
    else:
        return False
def dealdata(name, lie, plot):
    """处理数据的主体"""
    dataall = np.zeros([10000, 40])
    plt.subplot(plot)
    a = open(name, "r+")
    data = a.readlines()
    a.close()
    rows = len(data)  # 数据总行
    l = 0
    for line in data:
        line = line.strip().split('\t')  # strip()默认移除字符串首尾空格或换行符
        if line[lie] == "--":
            l = l + 1
    rows = rows - l  # 确认非空数据行数
    # print(rows)
    data2 = np.zeros((rows, 3))  # 创建数据储存矩阵
    row = 0  # 数据处理的行数
    Tchange = []  # 温度变化点
    for line in data:
        line = line.strip().split('\t')
        if line[lie] == "--" or line[lie] == "":
            continue
        data2[row, 0] = line[0]
        data2[row, 1] = line[1]
        data2[row, 2] = line[lie]  # 数据转移至data2并处理空格
        # print(data2[row,0])
        if row > 0:
            if abs(data2[row, 0] - data2[row - 1, 0]) > 0.1:  # 判读温度转变点
                Tchange.append(row)
        row += 1
    # print(Tchange)
    """a=0
    for i in Tchange:
        print(i-a)
        a=i
    print(rows-a)"""
    # print(Fchange)
    i = 0  # 数据以温度未根据进行的分组
    while True:
        if i > 0:  # 以温度为依据分段
            dataT = data2[Tchange[i - 1]:Tchange[i], :]  # dataT为每个温度的分离
            plt.plot(dataT[:, 1]/10000, dataT[:, 2], label="%.1f" % data2[Tchange[i - 1], 0] + "K")
            if lie == 3:
                plt.ylabel("Ryx(ohm)")
            else:
                plt.ylabel("R(ohm)")
            plt.xlabel("Field(T)")
            dataall[:dataT.shape[0], 2 * i] = dataT[:, 1]
            dataall[:dataT.shape[0], 2 * i + 1] = dataT[:, 2]
        else:  # 第一组则取0：。
            if Tchange == []:
                dataT = data2[:, :]
            else:
                dataT = data2[:Tchange[i], :]
            dataall[:dataT.shape[0], 0] = dataT[:, 1]
            dataall[:dataT.shape[0], 1] = dataT[:, 2]
            plt.plot(dataT[:, 1]/10000, dataT[:, 2], label="%.1f" % data2[0, 0] + "K")
            if lie == 3:
                plt.ylabel("Ryx(ohm)")
            else:
                plt.ylabel("R(ohm)")
            plt.xlabel("Field(T)")
            if Tchange == []:
                break
        if i == len(Tchange) - 1:  # 如果是最后一个点，则额外输出一个至最后的数组。并跳出循环
            dataT = data2[Tchange[i]:, :]
            dataall[:dataT.shape[0], 2 * i + 2] = dataT[:, 1]
            dataall[:dataT.shape[0], 2 * i + 3] = dataT[:, 2]
            plt.plot(dataT[:, 1]/10000, dataT[:, 2], label="%.1f" % data2[Tchange[i], 0] + "K")
            if lie == 3:
                plt.ylabel("Ryx(ohm)")
            else:
                plt.ylabel("R(ohm)")
            plt.xlabel("Field(T)")
            break
        # print(i)

        i = i + 1
    plt.legend()
    Tchange.insert(0, int(0))
    return dataall, data2[Tchange, 0]
def deal(file, abc):
    """处理数据的多个温度文件的储存"""
    if halltest(file):
        fig=plt.figure(figsize=(19.2, 10.8))
        [dataR, headline] = dealdata(file, 2, 121)
    else:
        fig=plt.figure(figsize=(9.6, 10.8))
        [dataR, headline] = dealdata(file, 2, 111)
    dataR = dataR[~(dataR == 0).all(1)]
    dataR = dataR.T[~(dataR == 0).all(0)].T  # 去除0列
    np.savetxt("data-R.dat", dataR, fmt="%.8e", delimiter=",")
    headlinestr = ""
    for i in headline:
        if abc == "1,1,1":
            headlinestr = headlinestr + "Field(T)," + "%.1f" % i + "K(ohm),"
        else:
            headlinestr = headlinestr + "Field(T)," + "%.1f" % i + "K(ohm cm),"
    headlinestr=headlinestr[:-1]
    addheadline(headlinestr, "data-R.dat", "data-R-" + abc + ".dat")
    savesinglefile(headlinestr, dataR, "R", abc)
    # hall处理
    if halltest(file):
        [datahall, headline] = dealdata(file, 3, 122)
        datahall = datahall[~(datahall == 0).all(1)]
        datahall = datahall.T[~(datahall == 0).all(0)].T  # 去除0列
        datahall = Ryxtorhoyx(datahall, abc)
        np.savetxt("data-hall.dat", datahall, fmt="%.8e", delimiter=",")
        addheadline(headlinestr, "data-hall.dat", "data-hall-" + abc + ".dat")
        savesinglefile(headlinestr, datahall, "hall", abc)
    plt.tight_layout()
    plt.show()
    fig.savefig(rename("alldata.png"))
try:
    file = [entry.path for entry in os.scandir(workdir) if entry.name.endswith(".dat")]
    if 0==0:
        if len(file) > 1:
            print("dat文件过多")
        else:
            print("文件名是" + file[0])
            abc = input("输入长宽高，逗号隔开，单位为cm，回车则皆为1，即输出为电阻\n")
            if abc == "":
                abc = "1,1,1"
            print("长宽高分别为" + abc)
            input("确认参数")
            abc = abc.replace("，", ",")
            deal(file[0], abc)
    file = [entry.path for entry in os.scandir(workdir) if entry.name.endswith(".dat")]
    for i in file:
        with open(i,"r+")as fp:
            b=open("tmp.dat","w+")
            for line in fp:
                line = line.replace("0.00000000e+00", "")
                b.write(line)
            b.close()
        with open("tmp.dat","r+") as fp:
            c=open(i,"w+")
            for line in fp:
                c.write(line)
            c.close()
    os.remove("tmp.dat")
except Exception as error:
    print(error)
input("by fuyang ヽ(°∀°)ﾉ  \n 按任意键结束")
