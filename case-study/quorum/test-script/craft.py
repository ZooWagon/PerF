import re
line = "    1 >>]]) @ 4.0526808496428259) ; ("
print(line.split("@"))

print(line.split("@")[1].strip("()"))

print(line.split("@")[1].strip("(); "))

print(line.split("@")[1].strip("(;) "))


