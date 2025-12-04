import sys
t=eval(sys.argv[1])
folder=sys.argv[2]
wp=open("test-script/fg-input.txt",'w')
wp.write("load " + folder + "\n")
for i in range(t):
    wp.write("rew initconfrun .\n")
wp.write("q")
wp.close()