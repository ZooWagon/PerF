import sys
import re

avgDur=0.0
rp=open("test-script/fg.log",'r')
lines=rp.readlines()

def get_moni_stmt_from(lines, i):
    j = i
    while not lines[j].strip()[-1] == '>' :
        j += 1
    stmt = ""
    for k in range(i, j + 1):
        stmt += lines[k][0:-1].strip()
        if k != j:
            stmt += ' '
    return stmt, j


resultDurFlag = False
for i in range(len(lines)):
    line=lines[i]
    if line.find("QueryDuration(initConfig)") >= 0:
        resultDurFlag = True
    if resultDurFlag and line.startswith("result"):
        # print("=====")
        f1 = re.findall("\d+.\d+",line)
        f2 = re.findall("e\+\d+",line)
        avgDur=eval(f1[0]+f2[0])
        resultDurFlag = False


print("avg duration:",avgDur)
