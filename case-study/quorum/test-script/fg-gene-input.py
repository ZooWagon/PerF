import sys

wp=open("test-script/fg-input.txt",'w')
wp.write("load test-m.maude\n")
wp.write("rew throughput(initrun) .\n")
wp.write("rew totalTxn(initrun) .\n")
wp.write("rew totalReadTxn(initrun) .\n")
wp.write("rew totalFailTxn(initrun) .\n")
wp.write("q")
wp.close()