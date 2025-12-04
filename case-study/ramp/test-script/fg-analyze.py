import sys
import re

t=eval(sys.argv[1])
allCnt=0
ctpCnt=0
txnCnt=0
txnTotalLat=0.0
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
    if line.find("< monitor : Monitor") >= 0:
        allCnt+=1
        # print("=====",allCnt)
        moni_stmt,i = get_moni_stmt_from(lines,i)
        # print(moni_stmt)
        events = moni_stmt[(moni_stmt.find("events")+9):-2].strip("()").split(" ; ")
        for i in range(len(events)):
            events[i]=events[i].strip("( )")
        # print(events)
        for j in range(len(events)):
            ctpFlag = False
            if events[j].startswith("start"):
                txnId = re.findall("\d+ . \d+ . \d+",events[j].split(" @ ")[0])[0]
                ts = float(events[j].split(" @ ")[1])
                # if txnId == "1 . 1 . 100":
                #     print(">> start", txnId)
                for k in range(j+1,len(events)):
                    if events[k].startswith("ctp"):
                        ctpFlag=True
                    if events[k].startswith("commit"):
                        txnId2 = re.findall("\d+ . \d+ . \d+",events[k].split(" @ ")[0])[0]
                        ts2 = float(events[k].split(" @ ")[1])
                        if txnId == txnId2:
                            lat = ts2 - ts
                            txnCnt+=1
                            txnTotalLat+=lat
                            # print(">>",lat,ctpFlag)
            if events[j].startswith("ctp"):
                ctpCnt+=1

if allCnt != t:
    print("Analyze error! Actually find", allCnt, "samples.")
else:
    print("ctp number:",ctpCnt)
    print("txn number:",txnCnt)
    print("total latency:",txnTotalLat)
    print("avg latency:",txnTotalLat/txnCnt)