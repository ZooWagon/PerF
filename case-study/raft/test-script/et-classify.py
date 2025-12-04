import csv


dict_et = {}

def get_class(t):
    n=int(eval(t)*100)
    n=n-(n%5)
    s=str(int(n/100))+'.'+str(n%100)
    # print(">>",t,n,s)
    return eval(s)


with open('ele_time_20-40_231031_2.csv', newline='') as f:
    reader = csv.reader(f)
    for row in reader:
        t=row[0]
        s=get_class(t)
        if s in dict_et:
            dict_et[s]=dict_et[s]+1
        else:
            dict_et[s]=1
    # print(dict_et)
    sum = 0
    ls_et_class = []
    et_key=sorted(dict_et.keys())
    for k in et_key:
        sum+=dict_et[k]
        ls_et_class.append([k,sum])
    print(ls_et_class)
    with open('ele_time_20-40_231031_class_sum_2.csv','w',newline='') as f:
        writer = csv.writer(f)
        for row in ls_et_class:
            writer.writerow(row)