'''
PerF Tool
1. do fault composition(including preprocessing)
2. do monitor transformation if required
3. do SMC by PVeStA if required
'''
from __future__ import print_function
import sys
import os
import time
import do_f_comp
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
Call do_f_comp, model composition with fault
'''
def generate_f_trans_file(args):
    print("Start model composition with fault")
    filename, module_name = get_file_module_name(args)
    # print(filename,module_name)
    do_f_comp.process_file_f(filename, module_name)
    print("Generating files: success.")


'''
Call do_m_trans, model transformation with monitor
'''
def generate_l_trans_file(args):
    print("Start model transformation with monitor")
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
        and "-f" in options and "-a" in options and "-d" in options

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
    options, args = getopt.getopt(sys.argv[1:], 'l:m:f:a:d:', ["pvesta","sim="])
    # print(options)
    # print(args)
    if len(args) < 3:
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
    if len(args) >= 4:
        generate_l_trans_file(args)
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
        if "--pvesta" in options:
            print("Analysis done (see also result.txt):")
        wrp = open(do_pvesta.OUTFILE, "a")
        wrp.write("Model composition and transformation time used: %f seconds\n" % (ts2 - ts1))
        if is_smc_on(options):
            wrp.write("SMC time used: %f seconds\n" % (ts3 - ts2))
            wrp.write("Total time used: %f seconds\n" % (ts3 - ts1))
        wrp.close()
        wrp = open(do_pvesta.OUTFILE, "r")
        for line in wrp:
            print(line, end = "")
        wrp.close()