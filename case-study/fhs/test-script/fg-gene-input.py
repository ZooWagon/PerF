import sys

wp=open("test-script/fg-input.txt",'w')
wp.write("load test-m.maude\n")
wp.write("rew getTES(initrun16) .\n")
wp.write("q")
wp.close()