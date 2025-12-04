import sys
t=eval(sys.argv[1])
folder=sys.argv[2]
wp=open("test-script/fg-input.txt",'w')
wp.write("load "+folder+"/init-2pc-ctp.maude\n")
for i in range(t):
    wp.write("rew run(initconf,1.0e+20) .\n")
wp.write("q")
wp.close()