import sys
t=eval(sys.argv[1])
folder=sys.argv[2]
wp=open("trans-script/fg-input.txt",'w')
wp.write("load "+folder+"/init-vote.maude\n")
for i in range(t):
    wp.write("rew run(initconf,500.0) .\n")
wp.write("q")
wp.close()