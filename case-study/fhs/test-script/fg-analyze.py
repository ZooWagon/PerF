import sys
import re

rp=open("test-script/fg.log",'r')
lines=rp.readlines()

commitNum = 0
totalTime = 0
for i in range(len(lines)):
    line=lines[i]
    if line.find("commit(") >= 0:
        commitNum += 1
        for j in range(i,len(lines)):
            if lines[j].find("@") >= 0:
                ttxt = lines[j].split("@")[1].strip("(); \n")
                if len(ttxt) == 0:
                    ttxt = lines[j+1].strip("(; \n\t)")
                t = eval(ttxt)
                totalTime = t
    elif line.find("commit-p(") >= 0:
        commitNum += 2
        for j in range(i,len(lines)):
            if lines[j].find("@") >= 0:
                ttxt = lines[j].split("@")[1].strip("(); \n")
                if len(ttxt) == 0:
                    ttxt = lines[j+1].strip("(; \n\t)")
                t = eval(ttxt)
                totalTime = t


print("total commit number of 16 nodes:", commitNum)
print("avg commit number of 16 nodes:", commitNum/16)
print("total run time:",totalTime)
if totalTime != 0:
    print("throughput:", commitNum / totalTime / 16 )
