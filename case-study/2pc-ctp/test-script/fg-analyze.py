import sys
import re

t=eval(sys.argv[1])
allCnt=0
txnCnt=0
txnTotalLat=0
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


for i in range(len(lines)):
    line=lines[i]
    if line.find("< log : Monitor") >= 0:
        # print("=====")
        allCnt+=1
        moni_stmt,i = get_moni_stmt_from(lines,i)
        # print(moni_stmt)
        events = moni_stmt[(moni_stmt.find("events")+9):-2].strip("()").split(" ; ")
        for i in range(len(events)):
            events[i]=events[i].strip("( )")
        # print(events)
        for j in range(len(events)):
            if events[j].startswith("start"):
                txnId=int((re.findall("\d+",events[j].split(" @ ")[0]))[0])
                for k in range(j+1,len(events)):
                    tmp=int((re.findall("\d+",events[k].split(" @ ")[0]))[0])
                    if tmp == txnId and \
                        (events[k].startswith("commit") or events[k].startswith("abort")):
                        # print(events[j],events[k])
                        lat = float(events[k].split(" @ ")[1]) - float(events[j].split(" @ ")[1])
                        txnCnt+=1
                        txnTotalLat+=lat
                        break

if allCnt != t:
    print("Analyze error! Actually find", allCnt, "samples.")
else:
    print("txn number:",txnCnt)
    print("total latency:",txnTotalLat)
    print("avg latency:",txnTotalLat/txnCnt)
