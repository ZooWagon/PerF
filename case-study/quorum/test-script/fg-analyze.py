import sys
import re

rp=open("test-script/fg.log",'r')
lines=rp.readlines()

throughput = 0
totalTxn = 0
totalReadTxn = 0
totalFailTxn = 0
for i in range(len(lines)):
    line=lines[i]
    if line.find("throughput") >= 0:
        for j in range(i+1,len(lines)):
            if lines[j].find("result FiniteFloat:") >= 0 :
                numstr=lines[j].split(": ")[1]
                throughput=eval(lines[j].split(": ")[1])
                break
    if line.find("totalTxn") >= 0:
        for j in range(i+1,len(lines)):
            if lines[j].find("result FiniteFloat:") >= 0:
                numstr=lines[j].split(": ")[1]
                totalTxn=eval(lines[j].split(": ")[1])
                break
    if line.find("totalReadTxn") >= 0:
        for j in range(i+1,len(lines)):
            if lines[j].find("result FiniteFloat:") >= 0:
                numstr=lines[j].split(": ")[1]
                totalReadTxn=eval(lines[j].split(": ")[1])
                break
    if line.find("totalFailTxn") >= 0:
        for j in range(i+1,len(lines)):
            if lines[j].find("result FiniteFloat:") >= 0:
                numstr=lines[j].split(": ")[1]
                totalFailTxn=eval(lines[j].split(": ")[1])
                break

print("throughput:", throughput)
print("totalTxn:", totalTxn)
print("totalReadTxn:", totalReadTxn)
print("totalFailTxn:", totalFailTxn)

