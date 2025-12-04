import sys
wp=open("test-script/fg-input.txt",'w')
wp.write("load f-output/init-dns\n")
wp.write("rew avgQueryDuration(initConfig) .\n")
# wp.write("rew maxQueryDuration(initConfig) .\n")
wp.close()