import sys
t=eval(sys.argv[1])
folder=sys.argv[2]
wp=open("test-script/fg-input.txt",'w')
wp.write("load "+folder+"/init-raft.maude\n")
for i in range(t):
    wp.write("rew run(init(5),200.0) .\n")
wp.write("q")
wp.close()