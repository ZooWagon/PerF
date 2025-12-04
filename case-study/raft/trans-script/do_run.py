'''
Fault Framework Maude Auto Tool
1. do F-trans automaticly
2. call smc script if required
2023.7.9 15:20
'''
from __future__ import print_function
import sys
import os
import time
import do_f_trans
import do_m_trans
import do_pvesta
import getopt

'''
Global flag for brief terminal display
0: All details, including F-trans, time, memory in terminal and result
10: Only info about calling pvesta in terminal and brief result 
2023.8.13 18:05
'''
BRIEF_PRINT = 0


'''
Get time now as seconds from epoch
Output: seconds from epoch
'''
def get_timestamp():
    return time.time()


'''
Get file and module name from sys.argv with smc mode
Input: smc: "off" or "on"
Output: 
    filename: the filename of the file
    module_name: the uppercase respective module name
'''
def get_file_module_name(args):
    filename = args  # get filename
    module_name = []
    for fn in filename:  #get module name with uppercase
        mn = fn[0:-6].upper()
        module_name.append(mn)
    return filename, module_name


'''
Call do_f_trans, generate f-trans file
'''
def generate_f_trans_file(args):
    print("Start F-trans")
    filename, module_name = get_file_module_name(args)
    # print(filename,module_name)
    do_f_trans.process_file_f(filename, module_name)
    print("Generating files: success.")


'''
Call do_m_trans, generate m-trans file
'''
def generate_m_trans_file(args):
    print("Start M-trans")
    filename, module_name = get_file_module_name(args)
    # print(filename,module_name)
    do_m_trans.process_file_m(filename, module_name)
    print("Generating files: success.")


'''
Judge whether argv require smc
'''
def is_smc_on(options):
    return "--pvesta" in options or "--sim" in options

'''
Check pvesta args
'''
def is_pvesta_args_enough(options):
    return "-l" in options and "-m" in options \
        and "-f" in options and "-a" in options

'''
Call pvesta
'''
def call_pvesta(options):
    print("Calling PVeStA")
    err_code = 1
    if "--moni" in options:
        err_code = do_pvesta.call_pvesta_with_monitor(options, 0)
    elif "--mlog" in options:
        err_code = do_pvesta.call_pvesta_with_monitor(options, 1)
    else:
        err_code = do_pvesta.call_pvesta(options)
    if err_code == 0:
        print("Calling PVeStA: success.")
    

if __name__ == "__main__":
    options, args = getopt.getopt(sys.argv[1:], 'l:m:f:a:', ["pvesta","sim="])
    if len(args) < 4:
        print("error: lack of input file.")
        exit()
    print("  >>> == PerF == <<<")
    options=dict(options)
    # print("opt:",options)
    # print("args:",args)
    # delete some previous log
    command = "rm -rf " + do_pvesta.OUTFILE
    os.system(command)
    # do
    ts1 = get_timestamp()
    generate_f_trans_file(args)
    generate_m_trans_file(args)
    ts2 = get_timestamp()
    if "--sim" in options:
        os.system("./trans-script/fg-test.sh " + options["--sim"] + " f-output")
    if "--pvesta" in options:
        if is_pvesta_args_enough(options):
            call_pvesta(options)
        else:
            print("error: lack of PVeStA parameters.")
    ts3 = get_timestamp()

    if BRIEF_PRINT <= 0:
        print("Analysis done (see also result.txt):")
        wrp = open(do_pvesta.OUTFILE, "a")
        wrp.write("F&M-trans time used: %f seconds\n" % (ts2 - ts1))
        if is_smc_on(options):
            wrp.write("SMC time used: %f seconds\n" % (ts3 - ts2))
            wrp.write("Total time used: %f seconds\n" % (ts3 - ts1))
        wrp.close()
        wrp = open(do_pvesta.OUTFILE, "r")
        for line in wrp:
            print(line, end = "")
        wrp.close()