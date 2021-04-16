import os
import math
from scipy import interpolate
import numpy as np


def spit(dataT, j):
    a1 = dataT[:j, :]
    a2 = dataT[j:, :]
    print(a1)
    print(a2)
    av = (inter(a1) + inter(a2)) / 2
    np.savetxt(str(dataT[0, 0]) + ".dat", av, fmt="%.8e", delimiter=",")


def inter(m):
    a = 1
    if m[0, 3] < 0:
        a = -1
    fx = interpolate.interp1d(m[:,1], m[:,3], kind="linear", fill_value="extrapolate")
    x = np.linspace(0, a * 140000, 7001)
    intery = np.zeros([x.size, 2])
    intery[:, 0] = a * x
    intery[:, 1] = a * fx(x)
    return intery

def hall(name):
    a=open(name, "r+")
    data=a.readlines()
    rows=len(data)
    l=0
    for line in data:
        line = line.strip().split(',')#strip()默认移除字符串首尾空格或换行符
        if line[3]=="--":
            l=l+1
    rows=rows-l
    print(rows)
    data2 = np.zeros((rows, 4))
    row=0
    Tchange=[]
    Fchange=[]
    for line in data:
        line = line.strip().split(',')#strip()默认移除字符串首尾空格或换行符
        if line[3]=="--":
            continue
        data2[row,:]=line[:]
        #print(data2[row,0])
        if row > 0:
            if abs(data2[row,0]-data2[row-1,0]) > 0.3:
                Tchange.append(row)
            dataF=data2[row,1] * data2[row-1,1]
            if dataF < 0:
                Fchange.append(row)
        row+=1
    i=0
    print(Tchange)
    print(Fchange)
    while True:
        if i>0:
            dataT=data2[Tchange[i-1]:Tchange[i],:]
            j=Fchange[i]-Tchange[i]
            spit(dataT,j)
        elif i==0:
            dataT=data2[:Tchange[i],:]
            spit(dataT,Fchange[0])
        if i == len(Tchange)-1:
            dataT = data2[Tchange[i]:, :]
            spit(dataT, Fchange[i + 1]-Tchange[i])
            break
        print(i)
        i=i+1


hall('Sheet11.dat')

