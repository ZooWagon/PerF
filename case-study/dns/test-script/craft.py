import re
line = "result FiniteFloat: 2.2247886658007187e+3"
f = re.findall("\d+.\d+e\+\d+",line)
f1 = re.findall("\d+.\d+",line)
f2 = re.findall("e\+\d+",line)
print(f)
print(f1)
print(f2)
print(f1[0]+f2[0])
print(eval(f1[0]+f2[0]))