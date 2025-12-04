import sys
t=eval(sys.argv[1])
decideYesCnt=0
decideNoCnt=0
blockCnt=0
allCnt=0
rp=open("trans-script/fg.log",'r')
lineCnt = 0
formerState = "A"
formerLineNum = 0
for line in rp:
    lineCnt += 1
    if line.find("server : Server | phase : ") >= 0:
        if line.find("Stray")>=0:
            if formerState == 'S':
                print("S:",formerLineNum,lineCnt)
            formerState='S'
            formerLineNum = lineCnt
            continue
        if line.find("DecideYes")>=0:
            decideYesCnt+=1
            formerState='Y'
            formerLineNum = lineCnt
        elif line.find("DecideNo")>=0:
            decideNoCnt+=1
            formerState='N'
            formerLineNum = lineCnt
        elif line.find("Ask")>=0:
            blockCnt+=1
            formerState='A'
            formerLineNum = lineCnt
        allCnt+=1
if allCnt != t:
    print("Analyze error! Actually find", allCnt, "samples.")
else:
    print("Vote DecideYes rate: ",end="")
    print(decideYesCnt/allCnt)
    print("Vote DecideNo rate: ",end="")
    print(decideNoCnt/allCnt)
    print("Vote server block: ",end="")
    print(blockCnt/allCnt)
