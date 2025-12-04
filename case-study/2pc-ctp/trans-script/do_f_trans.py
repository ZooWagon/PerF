'''
do F-trans
'''
from __future__ import print_function
from run_lib import *
import os
import re

INPUT_FOLDER = "input-modules"
OUTPUT_FOLDER = "f-output"
INIT_STATE_EQ = ["eq initconf", "eq initConf"]


'''
Input: 
    filename[0]: protocol's maude model
    filename[1]: protocol's init module
    filename[2]: injector's module
    module_name is the upper case of filename
Output:
    at ./{OUTPUT_FOLDER}, same name of filename[0] and filename[1]
'''
def process_file_f(filename, module_name):
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
    # 1. extract fault list from fault module, file[2]
    fault_ls = extract_fault_register(filename[2])
    # print(fault_ls)
    # 2. trans protocol
    trans_protocol(filename[0], module_name[0], fault_ls)
    # 3. add injector to init, file[1]
    trans_init(filename[1], filename[2], module_name[2])



'''
Input: filename of fault module
Output:
    fault_ls: fault to be injected by injector, list of their abbr
'''
def extract_fault_register(filename):
    frp = open("./" + INPUT_FOLDER + '/' + filename, 'r')
    ftxt = frp.readlines()
    fault_ls = []
    i = 0
    while i < len(ftxt):
        line = ftxt[i].strip()
        if line.startswith("eq faultRegister"):
            regi_stmt, i = get_stmt_from(ftxt, i)
            fault_ls = regi_stmt[regi_stmt.find(" = ")+3:].strip(" \t\n.()").split(" :: ")
            break
        i += 1
    frp.close()
    return fault_ls


'''
Input: filename of init module, fault descrption, and injector_obj
Output: at ./{OUTPUT_FOLDER}, new init module file with fault
'''
def trans_init(filename, filename_fault_des, module_fault):
    frp = open("./" + INPUT_FOLDER + '/' + filename, 'r')
    fwp = open("./" + OUTPUT_FOLDER + '/' + filename, 'w')
    ftxt = frp.readlines()
    fwp.write("load ../" + INPUT_FOLDER + "/" + filename_fault_des + "\n")
    i = 0
    while i < len(ftxt):
        line = ftxt[i]
        if is_start_within_list(line, INIT_STATE_EQ):
            fwp.write("  inc " + module_fault + " .\n")
            init_stmt, i = get_stmt_from(ftxt, i)
            ind = find_last(init_stmt,".")
            # ind = init_stmt.find('.')
            if ind >= 0:
                fwp.write("  %s\n" % init_stmt[0:ind])
                fwp.write("    %s .\n" % "injectorObj")
            else:
                print("ERROR: can't find init state .")
        else:
            fwp.write(line)
        i += 1
    frp.close()
    fwp.close()
    return


'''
Input: filename of protocol's module, protocal_name(upper case), injector_obj, fault list
Output:  at ./{OUTPUT_FOLDER}, new protocol module file with fault
'''
def trans_protocol(filename, protocol_name, fault_ls):
    frp = open("./" + INPUT_FOLDER + '/' + filename, 'r')
    frp2 = open("./fault-lib.maude", 'r')
    fwp = open("./" + OUTPUT_FOLDER + '/' + filename, 'w')
    ftxt = frp.readlines()
    ftxt2 = frp2.readlines()
    # preliminary
    fault_ls_comp = []  # complement set of used fault, namely not used fault
    for fault_abbr in fault_module_map.keys():
        if fault_abbr not in fault_ls:
            fault_ls_comp.append(fault_abbr)
    # print("fault_ls_comp: ",fault_ls_comp)

    # 3.1 add fault exec module to protocol
    fwp.write("load ../apfmaude\n")
    fwp.write("load ../fault-lib\n\n")
    j = 0
    copy_flag = False
    while j < len(ftxt2):
        line2 = ftxt2[j]
        if copy_flag:
            fwp.write(line2)
            if line2.find("endm") >= 0:
                fwp.write("\n")
                copy_flag = False
        else:
            for fault_abbr in fault_ls:
                if line2.find(fault_module_map[fault_abbr] + " is") >= 0:
                    copy_flag = True
                    fwp.write(line2)
        j += 1
        if ftxt2[j].find("FAULT-COMBINE is") >= 0:
            break
    # 3.2 add injector combine module to protocol
    fwp.write(ftxt2[j])
    j += 1
    while j < len(ftxt2):
        line2 = ftxt2[j]
        # for unused fault
        for fault_abbr_comp in fault_ls_comp:
            if line2.find(fault_abbr_comp.upper()+"-") >= 0 \
                or line2.find(fault_abbr_comp+"-") >= 0 \
                or line2.find(fault_module_map[fault_abbr_comp]) >= 0 :
                line2 = "  --- " + line2
                break
        fwp.write(line2)
        j += 1
        if ftxt2[j].find("FAULT-LIB is") >= 0:
            fwp.write(ftxt2[j] + '\n')
            j += 1
            break
    # 3.3 add fault-lib module
    while j < len(ftxt2):
        line2 = ftxt2[j]
        fwp.write(line2)
        j += 1
        if ftxt2[j].find("endm") >= 0:
            fwp.write(ftxt2[j] + '\n')
            j += 1
            break
    
    # 3.4 copy lines, inc FAULT-LIB to each module, delete apmaude
    i = 0
    while i < len(ftxt):
        line = ftxt[i]
        if line.find("apmaude") >= 0 or line.find("APMAUDE") >=0:
            i += 1
            continue
        if line.find("rl [") >= 0:
            rl_stmt, rl_stmt_end_line_n = get_stmt_from(ftxt,i)
            rl_name, r = get_text_between(rl_stmt,0,'[',']')
            rl_name = rl_name.strip("[ ]")
            # copy left state
            line = ftxt[i]
            while line.find(" =>") < 0:
                fwp.write(line)
                i += 1
                line = ftxt[i]
            line=line.replace(" =>"," => MarkRuleLabel('"+rl_name+", ")
            fwp.write(line)
            i += 1
            line = ftxt[i]
            rightEndFlag = False
            while i <= rl_stmt_end_line_n :
                if line.find(" if ") >= 0:
                    j = i 
                    fiFlag = False
                    while j <= rl_stmt_end_line_n:
                        if ftxt[j].find(" fi ") >= 0:
                            fiFlag = True
                            break
                        j += 1
                    if not fiFlag:
                        line = line.replace(" if ","\n  ) if ")
                        rightEndFlag = True
                elif i == rl_stmt_end_line_n:
                    if not rightEndFlag:
                        line = line.replace(" .","\n  ) .")
                fwp.write(line)
                i += 1
                line = ftxt[i]
        else:
            fwp.write(line)
            i += 1
        if line.startswith("mod "):
            # inc FAULT-LIB
            fwp.write("  inc FAULT-LIB .\n")
        
    frp.close()
    frp2.close()
    fwp.close()
    return



'''
Input: filename of init module
Output: at ./{OUTPUT_FOLDER}, copy the same init module file
'''
def cp_init(filename):
    frp = open("./" + INPUT_FOLDER + '/' + filename, 'r')
    fwp = open("./" + OUTPUT_FOLDER + '/' + filename, 'w')
    ftxt = frp.readlines()
    i = 0
    while i < len(ftxt):
        line = ftxt[i]
        fwp.write(line)
        i += 1
    frp.close()
    fwp.close()
    return