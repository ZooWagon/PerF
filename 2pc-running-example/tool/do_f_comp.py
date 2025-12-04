'''
Do F-comp
'''
from __future__ import print_function
from run_lib import *
import os
import re

INPUT_FOLDER = "input-modules"
OUTPUT_FOLDER = "output-fault-comp"
INIT_STATE_EQ = ["eq initconf", "eq initConf", "eq initstate", "eq initState"]


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
    trans_protocol(filename[0], module_name[0], fault_ls,filename[2])
    # 3. add injector to init, file[1]
    trans_init(filename[1], filename[2], fault_ls)



'''
Input: filename of fault config module
Output:
    fault_ls: fault to be injected by injector, 
            list of their abbr in uppercase
'''
def extract_fault_register(filename):
    frp = open("./" + INPUT_FOLDER + '/' + filename, 'r')
    ftxt = frp.readlines()
    fault_ls = []
    i = 0
    while i < len(ftxt):
        line = ftxt[i].strip()
        for abbr in fault_module_map.keys():
            if line.startswith('eq '+abbr) and not abbr in fault_ls:
                fault_ls.append(abbr)
                break
        # if line.startswith("eq ML") and not "ML" in fault_ls:
        #     fault_ls.append("ML")
        # elif line.startswith("eq MD") and not "MD" in fault_ls:
        #     fault_ls.append("MD")
        # elif line.startswith("eq PT") and not "PT" in fault_ls:
        #     fault_ls.append("PT")
        i += 1
    frp.close()
    return fault_ls


'''
Input: filename of init module, fault descrption, and fault_ls
Output: at ./{OUTPUT_FOLDER}, new init module file with injector
'''
def trans_init(filename, filename_fault_des, fault_ls):
    frp = open("./" + INPUT_FOLDER + '/' + filename, 'r')
    frp2 = open("./" + INPUT_FOLDER + '/' + filename_fault_des, 'r')
    fwp = open("./" + OUTPUT_FOLDER + '/' + filename, 'w')
    ftxt = frp.readlines()
    ftxt2 = frp2.readlines()
    # fwp.write("load ../" + INPUT_FOLDER + "/" + filename_fault_des + "\n")
    i = 0
    while i < len(ftxt):
        line = ftxt[i]
        if is_start_within_list(line, INIT_STATE_EQ):
            # fwp.write("  eq md = lognormal(0.0, 1.0, rand) .\n")
            # fwp.write("  eq LIMIT = 1000000.0 .\n")
            fault_attr = []
            # copy from fault-module
            k = 0
            while k < len(ftxt2):
                line2 = ftxt2[k]
                if line2.find("eq ") >= 0:
                    fwp.write(line2)
                    # get fault attr
                    fault_attr.append(line2.strip().split('eq', 1)[1].split('=', 1)[0].strip())
                k += 1
            init_stmt, i = get_stmt_from(ftxt, i)
            ind = find_last(init_stmt,".")
            # ind = init_stmt.find('.')
            if ind >= 0:
                fwp.write("  %s\n" % init_stmt[0:ind])
                # put injector
                fwp.write("    { 0.0 | nilSL } < ctrl : Controller | fbhvs: fbhv >\n")
                # print(fault_attr,fault_ls)
                l = 0
                while l < len(fault_ls):
                    prefix = fault_ls[l]
                    formatted_items = []
                    for attr in fault_attr:
                        if attr.startswith(prefix):
                            suffix = attr[len(prefix):]
                            formatted_items.append("{}: {}".format(suffix, attr))
                    handler_attr = ', '.join(formatted_items)
                    handler = fault_handler_map[prefix] + handler_attr + " >"
                    # print(handler)
                    if l != len(fault_ls) - 1:
                        fwp.write('    ' + handler + '\n')
                    else:
                        fwp.write('    ' + handler + ' .\n')
                    l += 1                
            else:
                print("ERROR: can't find initial state .")
        else:
            fwp.write(line)
        i += 1
    frp.close()
    fwp.close()
    return


'''
Input: filename of protocol's module, protocal_name(upper case), fault list, filename of fault module
Output:  at ./{OUTPUT_FOLDER}, new protocol module file with fault
'''
def trans_protocol(filename, protocol_name, fault_ls,filename_fault):
    frp = open("./" + INPUT_FOLDER + '/' + filename, 'r')
    frp2 = open("./fault-injector.maude", 'r')
    fwp = open("./" + OUTPUT_FOLDER + '/' + filename, 'w')
    ftxt = frp.readlines()
    ftxt2 = frp2.readlines()
    # preliminary
    fault_ls_comp = []  # complement set of used fault, namely not used fault
    for fault_abbr in fault_module_map.keys():
        if fault_abbr not in fault_ls:
            fault_ls_comp.append(fault_abbr)
    # print("fault_ls_comp: ",fault_ls_comp)

    # 1 load fault-injector files
    fwp.write("load ../apfmaude\n") 
    fwp.write("load ../probability\n") 
    fwp.write("load ../fault-injector\n\n")
    fwp.write("load ../" + INPUT_FOLDER + "/" + filename_fault + "\n")
    j = 0
    # copy_flag = False
    while j < len(ftxt2):
        # line2 = ftxt2[j]
        # if copy_flag:
        #     fwp.write(line2)
        #     if line2.find("endm") >= 0:
        #         fwp.write("\n")
        #         copy_flag = False
        # else:
        #     for fault_abbr in fault_ls:
        #         if line2.find(fault_module_map[fault_abbr] + " is") >= 0:
        #             copy_flag = True
        #             fwp.write(line2)
        j += 1
        if ftxt2[j].find("FAULT-CONTROLLER is") >= 0:
            break
    # 2 copy controller module to protocol
    fwp.write(ftxt2[j])
    j += 1
    while j < len(ftxt2):
        line2 = ftxt2[j]
        # for unused fault
        for fault_abbr_comp in fault_ls_comp:
            if line2.find(fault_abbr_comp.upper()+"-") >= 0 \
                or line2.find(fault_abbr_comp.lower()+"-") >= 0 \
                or line2.find(fault_module_map[fault_abbr_comp]) >= 0 :
                line2 = "  --- " + line2
                break
        fwp.write(line2)
        j += 1
        if ftxt2[j].find("FAULT-INJECTOR is") >= 0:
            fwp.write(ftxt2[j] + '\n')
            j += 1
            break
    # 3 copy fault-injector module
    while j < len(ftxt2):
        line2 = ftxt2[j]
        fwp.write(line2)
        j += 1
        if ftxt2[j].find("endm") >= 0:
            fwp.write(ftxt2[j] + '\n')
            j += 1
            break
    # 4 copy lines, attach source rule label, 
    # add eager enable, inc FAULT-INJECTOR to each module
    i = 0
    while i < len(ftxt):
        line = ftxt[i]
        # if line.find("apmaude") >= 0 or line.find("APMAUDE") >=0:
        #     i += 1
        #     continue
        if line.find("rl [") >= 0:  # find rl
            rl_stmt, rl_stmt_end_line_n = get_stmt_from(ftxt,i)
            rl_name, r = get_text_between(rl_stmt,0,'[',']')
            rl_name = rl_name.strip("[ ]")
            # copy left state, check eager enable
            msgFlag = False
            leftAC = ""
            line = ftxt[i]
            start_content = line.split(':', 1)[1] if ':' in line else ''
            for j in range(i, len(ftxt)):
                if '=>' in ftxt[j]:
                    content_parts = [start_content] + ftxt[i+1:j] + [ftxt[j].split('=>')[0]]
                    leftAC = ''.join(content_parts).strip()
                    leftAC = re.sub(r'\s+', ' ', leftAC).strip()
                    msgFlag = has_msg(leftAC)
                    # print(leftAC,msgFlag)
                    break
            while line.find(" =>") < 0:
                fwp.write(line)
                i += 1
                line = ftxt[i]
            line=line.replace(" =>"," => AttachRuleLabel('"+rl_name+", ")
            # fwp.write(line)
            # i += 1
            # line = ftxt[i]
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
                        line = line.replace(" if "," ) if ")
                        rightEndFlag = True
                if i == rl_stmt_end_line_n:
                    if not rightEndFlag:
                        line = line.replace(" ."," ) .")
                fwp.write(line)
                i += 1
                line = ftxt[i]
            # write eagerEnable if obj-triggered rule
            if not msgFlag:
                fwp.write("  eq eagerEnabled(" + leftAC + " AC ) = true .\n")
        else:
            fwp.write(line)
            i += 1
        if line.startswith("mod "):
            # inc FAULT-INJECTOR
            fwp.write("  inc FAULT-INJECTOR .\n")
        
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


# is text has msg pattern in it?
def has_msg(text):
    stack = []
    parentheses_pairs = []
    for i, char in enumerate(text):
        if char == '(':
            stack.append(i)
        elif char == ')':
            if stack:
                start = stack.pop()
                if not stack:
                    parentheses_pairs.append((start, i))
    for start, end in parentheses_pairs:
        content = text[start+1:end]  
        # check "from...to" or "to"
        if re.search(r'\bfrom\b.*\bto\b', content) or re.search(r'\bto\b', content):
            return True
    return False
