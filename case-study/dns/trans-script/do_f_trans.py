'''
do F-trans
'''
from __future__ import print_function
from run_lib import *
import os
import re

INPUT_FOLDER = "input-modules"
OUTPUT_FOLDER = "f-output"


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
    # 1. extract injectorObj from injector, file[2]
    injector_obj, fault_ls = extract_injector(filename[2])
    # print(injector_obj)
    # print(fault_ls)
    # whether need injector
    if isnotNeedInjector(injector_obj,fault_ls):
        # 2. trans protocol without injector
        trans_protocol_without_injector(injector_obj,fault_ls,filename[0])
        # 3. copy init
        cp_init(filename[1])
    else:
        # 2. add injector to init, file[1]
        trans_init(filename[1], filename[2], module_name[2], injector_obj)
        # 3. trans protocol
        trans_protocol(filename[0], module_name[0], injector_obj, fault_ls)


'''
Input: filename of injector module
Output:
    injector_obj: string
    fault_ls: fault to be injected by injector, list of their abbr
'''
def extract_injector(filename):
    frp = open("./" + INPUT_FOLDER + '/' + filename, 'r')
    ftxt = frp.readlines()
    i = 0
    while i < len(ftxt):
        line = ftxt[i].strip()
        if line.startswith("eq injectorObj"):
            evil_stmt, i = get_stmt_from(ftxt, i)
            injector_obj = get_text_between(evil_stmt,0,'<','>')[0]
            fault_ls = get_text_between(injector_obj,injector_obj.find("faultRegi :"),'(',')')[0].strip("()").split(" :: ")
            break
        i += 1
    frp.close()
    return injector_obj, fault_ls


'''
Input: filename of fault module
Output:
    fault_aux_lines: aux lines for fault description
'''
def extract_fault_aux_lines(filename, module_fault):
    frp = open("./" + INPUT_FOLDER + '/' + filename, 'r')
    ftxt = frp.readlines()
    i = 0
    copyFlag=False
    fault_aux_lines = []
    while i < len(ftxt):
        line = ftxt[i]
        if line.find("eq injectorObj") >= 0:
            copyFlag=False
        if copyFlag and line.find("inc ")<0 and len(line) > 0:
            fault_aux_lines.append(line)
        if line.find("mod "+module_fault) >= 0:
            copyFlag=True
        
        i += 1
    frp.close()
    return fault_aux_lines

'''
Input: filename of init module, fault descrption, and injector_obj
Output: at ./{OUTPUT_FOLDER}, new init module file with fault
'''
def trans_init(filename, filename_fault_des, module_fault, injector_obj):
    frp = open("./" + INPUT_FOLDER + '/' + filename, 'r')
    fwp = open("./" + OUTPUT_FOLDER + '/' + filename, 'w')
    ftxt = frp.readlines()
    # fwp.write("load ../" + INPUT_FOLDER + "/" + filename_fault_des + "\n")
    i = 0
    while i < len(ftxt):
        line = ftxt[i]
        if is_start_within_list(line, ["eq initconf ", "eq init("]):
            # fwp.write("  inc " + module_fault + " .\n")
            fwp.writelines(extract_fault_aux_lines(filename_fault_des,module_fault))
            init_stmt, i = get_stmt_from(ftxt, i)
            ind = init_stmt.find('{')
            if ind >= 0:
                fwp.write("  %s\n" % init_stmt[0:ind])
                fwp.write("    %s\n" % injector_obj)
                fwp.write("    %s\n" % init_stmt[ind:])
            else:
                print("ERROR!")
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
def trans_protocol(filename, protocol_name, injector_obj, fault_ls):
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
    fault_otr_comp = []  # complement set for fault used in obj trigger rule
    for fault_abbr in fault_module_map.keys():
        if fault_abbr not in ["cr"]:
            fault_otr_comp.append(fault_abbr)

    # 3.1 add fault exec module to protocol
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
                    # warning: here hard code protocol's interface module
                    # fwp.write("  inc INTERFACE-" + protocol_name + " .\n")
        j += 1
        if ftxt2[j].find("FAULT-COMPOSITE is") >= 0:
            break
    # 3.2 add injector composite module to protocol
    fwp.write(ftxt2[j])
    j += (len(fault_module_map) + 1)
    for fault_abbr in fault_ls:
        fwp.write("  inc " + fault_module_map[fault_abbr] + " .\n")
    while j < len(ftxt2):
        line2 = ftxt2[j]
        # for unused fault
        for fault_abbr_comp in fault_ls_comp:
            if line2.find(" " + fault_abbr_comp.upper()) >= 0:
                line2 = "  --- " + line2
                break
        # revise debugFlagM
        if line2.find("debugFlagM") >= 0:
            tmp, r = get_text_between(line2,line2.find("debugFlag"),'(',')')
            tmp2 = []
            for fault_abbr in fault_module_map.keys():
                if fault_abbr in fault_ls:
                    tmp2.append("M" + fault_number_map[fault_abbr])
                else:
                    tmp2.append("0.0")
            tmp2 = '(' + ",".join(tmp2) + ')'
            line2 = line2.replace(tmp,tmp2)
        fwp.write(line2)
        j += 1
        if ftxt2[j].find("endm") >= 0:
            fwp.write(ftxt2[j] + '\n')
            j += 1
            break
    # 3.3 trans protocol's msg trigger rule
    # 3.4 trans protocol's obj trigger rule if fault cr is used
    # preliminary
    var_lines = []  # var declare lines
    injector_left_lines = []  # left part of injector, for msg trigger rule
    injector_right_lines = []  # right part of injector, for msg trigger rule
    evil_cond_lines = []  # cond for msg trigger rule
    # extract var decl and left injector
    copy_flag = False
    while j < len(ftxt2):
        line2 = ftxt2[j]
        if line2.find(" var ") >= 0 or  line2.find(" vars ") >= 0:
            var_lines.append(line2)
        if line2.find("< injector : Injector") >= 0:
            copy_flag = True
        if copy_flag:
            injector_left_lines.append(line2)
        j += 1
        if ftxt2[j].find("=>") >= 0:
            break
    # extract right injector
    copy_flag = False
    while j < len(ftxt2):
        line2 = ftxt2[j]
        if line2.find("< injector : Injector") >= 0:
            copy_flag = True
        if copy_flag:
            injector_right_lines.append(line2)
        j += 1
        if ftxt2[j].find("if") >= 0:
            break
    # extract cond (notFault)
    while j < len(ftxt2):
        line2 = ftxt2[j]
        if line2.find("notFault") >= 0:
            tmp = line2.strip().strip("\ ./")
            evil_cond_lines.append(tmp)
        j += 1
        if ftxt2[j].find("endm") >= 0:
            j += 1
            break
    # debug: show preliminary
    # print(var_lines)
    # print(injector_left_lines)
    # print(injector_right_lines)
    # print(evil_cond_lines)
    # 3.0 copy lines until the declare line of protocol module
    i = 0
    while i < len(ftxt):
        line = ftxt[i]
        if line.startswith("mod "):
            # 3.3.1 inc FAULT-FAULT and declare var
            while i < len(ftxt):
                line = ftxt[i]
                fwp.write(line)
                i += 1
                if i < len(ftxt) and ftxt[i].find("var") >= 0:
                    fwp.write("  inc FAULT-LIB .\n")
                    for line_evil in var_lines:
                        copy_flag = True
                        for fault_abbr_comp in fault_ls_comp:
                            if line_evil.find(fault_abbr_comp.upper()) >= 0:
                                copy_flag = False
                                break
                        if copy_flag:
                            fwp.write(line_evil)
                    break
        elif line.find("rl [") >= 0:
            # print("Find RL: ",line)
            # 3.3.2 rule
            # a rule
            rl_stmt, rl_stmt_end_line_n = get_stmt_from(ftxt,i)
            # print("--------")
            # print(rl_stmt)
            rl_name, r = get_text_between(rl_stmt,0,'[',']')
            msg_stmt, r = get_text_between(rl_stmt,0,'{','}')
            # print(msg_stmt)
            if rl_name.find("clean") < 0 \
                and r > 0 and msg_stmt.find("to") >= 0 \
                and msg_stmt.find("from") >= 0:
                # msg trigger rule
                # print("msg")
                msg_ele = msg_stmt.strip("() {}").split()
                dstO = ""
                srcO = ""
                conO = []
                for t in range(1,len(msg_ele)):
                    if msg_ele[t] == "to":
                        dstO = msg_ele[t+1]
                    if msg_ele[t] == "from":
                        srcO = msg_ele[t+1]
                    if len(dstO) == 0 and len(srcO) == 0:
                        conO.append(msg_ele[t].strip("( "))
                conO = " ".join(conO)
                rl_flag = 'n'  # n, l, le, r, re, c: null, left (evil), right (evil)
                rl_type = ''
                while i <= rl_stmt_end_line_n:
                    line = ftxt[i]
                    if line.find(" rl [") >= 0:
                        rl_type = "rl"
                        line = line.replace(" rl ["," crl [")
                        # print(">> find rl[]",line)
                    elif line.find(" crl [") >= 0:
                        rl_type = "crl"
                    if rl_flag == 'n' and (line.find("{") >= 0 or line.find("<") >= 0):
                        rl_flag = 'l'
                        # print(">> n to l",line)
                    elif rl_flag == 'l' and (ftxt[i-1].strip()[-1] == '>' or ftxt[i-1].strip()[-1] == '}'):
                        # write left injector obj
                        for line_evil in injector_left_lines:
                            copy_flag = True
                            for fault_abbr_comp in fault_ls_comp:
                                if line_evil.find(fault_abbr_comp.upper()) >= 0:
                                    copy_flag = False
                                    break
                            if copy_flag:
                                fwp.write(line_evil)
                        rl_flag = 'le'
                        # print(">> l to le")
                    elif rl_flag == 'le' and line.find("=>") >= 0:
                        rl_flag = 'r'
                        # print(">> le to r")
                    elif rl_flag == 'r' and (ftxt[i-1].strip()[-1] == '>' or ftxt[i-1].strip()[-1] == '}'):
                        # write right injector obj
                        for line_evil in injector_right_lines:
                            copy_flag = True
                            for fault_abbr_comp in fault_ls_comp:
                                if line_evil.find(fault_abbr_comp.upper()) >= 0:
                                    copy_flag = False
                                    break
                            if copy_flag:
                                fwp.write(line_evil)
                        rl_flag = 're'
                    if rl_flag == 're' and rl_type == "rl" and i == rl_stmt_end_line_n:
                        # for rl
                        line = del_comment(line).rstrip()[:-1] + "\n  if "
                        rl_flag = 'c'
                    elif rl_flag == 're' and rl_type == "crl" and i == rl_stmt_end_line_n:
                        # for crl
                        line = del_comment(line).rstrip()[:-1] + "\n    /\ "
                        rl_flag = 'c'
                    fwp.write(line)
                    if rl_flag == 'c':
                        # print(">> cond")
                        # write notFault cond
                        evil_cond = []
                        for line_evil in evil_cond_lines:
                            copy_flag = True
                            for fault_abbr_comp in fault_ls_comp:
                                if line_evil.find(fault_abbr_comp.upper()) >= 0:
                                    copy_flag = False
                                    break
                            if copy_flag:
                                evil_cond.append(line_evil)
                        evil_cond = " /\ ".join(evil_cond) + " .\n"
                        evil_cond = evil_cond.replace("SRCO",srcO).replace("DSTO",dstO).replace("CON",conO)
                        fwp.write(evil_cond)
                    i += 1
            elif rl_name.find("clean") < 0:
                # obj trigger rule
                # print("obj")
                if "cr" in fault_ls:
                    # crush fault, add crnotFault
                    dstO = ""
                    rl_type = ''
                    rl_flag = 'l'
                    res = re.findall(r"<.+?:.+?\|.+?>", rl_stmt)
                    obj_ele = res[0].split()
                    for t in range(len(obj_ele)):
                        if obj_ele[t] == "<":
                            dstO = obj_ele[t+1]
                            break
                    while i <= rl_stmt_end_line_n:
                        line = ftxt[i]
                        if line.find(" rl [") >= 0:
                            rl_type = "rl"
                            line = line.replace(" rl ["," crl [")
                        elif line.find(" crl [") >= 0:
                            rl_type = "crl"
                        
                        if rl_flag == 'n' and line.find("{") >= 0:
                            rl_flag = 'l'
                        elif rl_flag == 'l' and (ftxt[i-1].strip()[-1] == ')' or ftxt[i-1].strip()[-1] == '>'):
                            # write left injector obj
                            for line_evil in injector_left_lines:
                                copy_flag = True
                                for fault_abbr_comp in fault_otr_comp:
                                    if line_evil.find(fault_abbr_comp.upper()) >= 0:
                                        copy_flag = False
                                        break
                                if copy_flag:
                                    fwp.write(line_evil)
                            rl_flag = 'le'
                        elif rl_flag == 'le' and line.find("=>") >= 0:
                            rl_flag = 'r'
                        elif rl_flag == 'r' and (ftxt[i-1].strip()[-1] == ')' or ftxt[i-1].strip()[-1] == '>'):
                            # write right injector obj
                            for line_evil in injector_right_lines:
                                copy_flag = True
                                for fault_abbr_comp in fault_otr_comp:
                                    if line_evil.find(fault_abbr_comp.upper()) >= 0:
                                        copy_flag = False
                                        break
                                if copy_flag:
                                    fwp.write(line_evil)
                            rl_flag = 're'
                        if rl_flag == "re" and i == rl_stmt_end_line_n and rl_type == "rl":
                            # for rl
                            line = line.rstrip()[:-1] + "\n  if "
                            rl_flag = 'c'
                        elif rl_flag == "re" and i == rl_stmt_end_line_n and rl_type == "crl":
                            # for crl
                            line = line.rstrip()[:-1] + "\n    /\ "
                            rl_flag = 'c'
                        fwp.write(line)
                        if rl_flag == 'c':
                            # write crnotFault cond
                            evil_cond = []
                            for line_evil in evil_cond_lines:
                                if line_evil.find("CR") >= 0:
                                    evil_cond.append(line_evil)
                            evil_cond = " /\ ".join(evil_cond) + " .\n"
                            evil_cond = evil_cond.replace("DSTO",dstO).replace("CON","nullCON").replace("CRVCL","nilCL")
                            fwp.write(evil_cond)
                        i += 1
                    # eagerEnabled
                    while ftxt[i].find("eagerEnabled") < 0:
                        fwp.write(ftxt[i])
                        i += 1
                    # find line eagerEnabled
                    line = ftxt[i]
                    ind = line.find("eagerEnabled(")
                    fwp.write(line[0:(ind+13)])
                    # write left injector obj
                    for line_evil in injector_left_lines:
                        copy_flag = True
                        for fault_abbr_comp in fault_otr_comp:
                            if line_evil.find(fault_abbr_comp.upper()) >= 0:
                                copy_flag = False
                                break
                        if copy_flag:
                            fwp.write(line_evil)
                    fwp.write(line[(ind+13):])
                    i += 1
                    while not is_end_with_dot(ftxt[i]):
                        fwp.write(ftxt[i])
                        i += 1
                    line = ftxt[i]
                    line = line.rstrip()[:-1] + "\n    /\ "
                    fwp.write(line)
                    evil_cond = []
                    for line_evil in evil_cond_lines:
                        if line_evil.find("CR") >= 0:
                            evil_cond.append(line_evil)
                    evil_cond = " /\ ".join(evil_cond) + " .\n"
                    evil_cond = evil_cond.replace("DSTO",dstO).replace("CON","nullCON").replace("CRVCL","nilCL")
                    fwp.write(evil_cond)
                    i += 1
                else:
                    # obj trigger rule and no crush fault, no trans
                    fwp.write(line)
                    i += 1
            else:
                # clean rule, no trans
                fwp.write(line)
                i += 1
        else:
            fwp.write(line)
            i += 1
    
    
    frp.close()
    frp2.close()
    fwp.close()
    return


'''
whether fault not need an injector
output: True-not need injector; False-need injector.
'''
def isnotNeedInjector(injector_obj,fault_ls):
    if "de" in fault_ls and injector_obj.find("DEvulnerableRule : nilQLF") < 0:
        return True
    return False


'''
trans protocol for not need of injector
1. delay by rule with rate 1.0
'''
def trans_protocol_without_injector(injector_obj,fault_ls,filename):
    # delay by rule
    if "de" in fault_ls and injector_obj.find("DEvulnerableRule : nilQLF") < 0:
        p = injector_obj.find("DEvulnerableRule :") + len("DEvulnerableRule :")
        q = injector_obj.find(",",p) 
        de_rule = injector_obj[p:q].strip().split(" ^:^ ")
        p = injector_obj.find("DEtime :") + len("DEtime :")
        q = injector_obj.find(",",p) 
        de_time = eval(injector_obj[p:q].strip())
        # delayed rule, delay time
        # print(de_rule)
        # print(de_time)
        # write file
        frp = open("./" + INPUT_FOLDER + '/' + filename, 'r')
        fwp = open("./" + OUTPUT_FOLDER + '/' + filename, 'w')
        ftxt = frp.readlines()
        i = 0
        while i < len(ftxt):
            line = ftxt[i]
            # a rule
            if line.find("rl [") >= 0:
                rl_stmt, rl_stmt_end_line_n = get_stmt_from(ftxt,i)
                # print("--------")
                # print("Find RL: ",line)
                # print(rl_stmt)
                rl_name, r = get_text_between(rl_stmt,0,'[',']')
                rl_name = '\'' + rl_name.strip("[]")
                # print("rl name:",rl_name)
                if rl_name in de_rule:
                    # delayed rule
                    rl_flag = 'n'  # n, l, r, re
                    while i <= rl_stmt_end_line_n:
                        line = ftxt[i]
                        if rl_flag == 'n' and (line.find("{") >= 0 or line.find("<") >= 0):
                            rl_flag = 'l'
                            # print(">> n to l",line)
                        elif rl_flag == 'l' and line.find("=>") >= 0:
                            rl_flag = 'r'
                            # print(">> l to r")
                        elif rl_flag == 'r' and (line.find("from ") >= 0 and line.find("to ") >= 0):
                            # find generated msg, inject delay
                            # print("dline:",line)
                            p = line.find("[")
                            q = line.find(",",p)
                            old=line[p:q]
                            line=line.replace(old,old+" + "+str(de_time))
                            # print("dlinea:",line)
                            rl_flag = 're'
                        fwp.write(line)
                        i += 1
                else:
                    # normal rule
                    fwp.write(line)
                    i += 1
            else:
                # not a rule
                fwp.write(line)
                i += 1
        frp.close()
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