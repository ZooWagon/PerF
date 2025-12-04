import sys
import csv

t=eval(sys.argv[1])
allCnt=0
election_rec=[]
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
        # print("=====")
        allCnt+=1
        moni_stmt,i = get_moni_stmt_from(lines,i)
        # print(moni_stmt)
        events = moni_stmt[(moni_stmt.find("events")+9):-2].strip("()").split(" ; ")
        for i in range(len(events)):
            events[i]=events[i].strip("( )")
        # print(events)

        for j in range(len(events)):
            if events[j].startswith("die-leader"):
                death_time=float(events[j].split(" @ ")[1])
                for k in range(j+1,len(events)):
                    if events[k].startswith("new-leader"):
                        # print(events[j],events[k])
                        leader_time = float(events[k].split(" @ ")[1])
                        election_time=leader_time-death_time
                        # print("election time:",election_time)
                        election_rec.append(election_time)
                        break
                break


if allCnt != t:
    print("Analyze error! Actually find", allCnt, "samples.")
else:
    print("Analysis Success! Num:",len(election_rec))
    print("All election time:")
    # print(election_rec)
    sort_ele_rec = sorted(election_rec)
    print(sort_ele_rec)
    with open('ele_time.csv', 'w') as file:
        csv_writer = csv.writer(file)
        for t in sort_ele_rec:
            csv_writer.writerow([t])

