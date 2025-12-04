'''
Do m-trans
Other python programs may invoke function process_file_m(filename, module_name), where 2 maude files are in path INPUT_FOLDER_M which abide by the maude grammar, 2 maude files in INPUT_FOLDER_O and according 4 module names are the same name of filename. 
The function will generate 2 m-trans file of file 1 and file 2 in the path OUTPUT_FOLDER_M with the same name.
2023.9.2
'''
from __future__ import print_function
import os
import sys
import re
from run_lib import *

INPUT_FOLDER_M = "f-output"  # f-trans file folder
INPUT_FOLDER_O = "input-modules"  # origin file folder
OUTPUT_FOLDER_M = "m-output"


'''
Process file and generate m-trans file in OUTPUT_FOLDER_M as required
Input: 
    filename: list of filename, first 2 maude files are in path INPUT_FOLDER_M which abide by the maude grammar, 2 maude files in INPUT_FOLDER_O
    module_name: a list, the same name module name of the filename
Output: no return value, but generate required m-trans file in OUTPUT_FOLDER_M
'''
def process_file_m(filename, module_name):
    # 1. create output folder, get file pointers
    if not os.path.exists(OUTPUT_FOLDER_M):
        os.makedirs(OUTPUT_FOLDER_M)
    frp = []  # file read pointers
    for i in range(len(filename)):
        if i < 2:
            input_folder = INPUT_FOLDER_M
        else:
            input_folder = INPUT_FOLDER_O
        fr = open(os.path.join(input_folder, filename[i]),"r")
        frp.append(fr)
    # file1 write pointer
    fwp = open(os.path.join(OUTPUT_FOLDER_M, filename[0]),"w")
    fwp2 = open(os.path.join(OUTPUT_FOLDER_M, filename[1]),"w")

    # 2. get eventMap info from file 4
    ftxt4 = frp[3].readlines()
    event = get_event_info(ftxt4)
    event_map = {}
    for item in event:
        event_map[item[0]] = item
    
    # 3. rewrite file 1, analyze lines one by one
    ftxt1 = frp[0].readlines()  # text for file 1
    module_flag = False
    addline = "load ../input-modules/" + filename[3]
    # addline = "load ../events"
    fwp.write("%s\n" % addline)
    i = 0
    while i < len(ftxt1):
        line = ftxt1[i]
        if line.startswith("mod "):
            # case 1: find target module, add lines around module declaration
            module_flag = True  # in target module now
            fwp.write(line)
            addline = "  inc " + module_name[3] + " ."
            fwp.write("%s\n" % addline)
        elif module_flag and is_start_within_list(line, ["rl", "crl"]):
            # case 2: find rule in target module
            rule_name = extract_rule_name(ftxt1,i)
            if rule_name in event_map:
                # add something
                i = rewrite_rule_m(fwp, ftxt1, i, rule_name, event_map)
            else:
                fwp.write(line)
        elif line.startswith("endm"):
            # case 3: a module ends, clear module flag
            module_flag = False
            fwp.write(line)
        else:
            # case default: line with no need for process
            fwp.write(line)
        i += 1
        
    # 4. rewrite file 2
    ftxt2 = frp[1].readlines()  # text for file 2
    generate_init_file_m(fwp2, ftxt2)
    
    # close file
    for fp in frp:
        fp.close()
    fwp.close()
    fwp2.close()


'''
Generate file 2 as required in m-trans
Input: 
    fwp: file write pointer for file 2;
    lines: string list of file 2;
Output: no return value, but write m-trans init file in fwp file
'''
def generate_init_file_m(fwp, lines):
    for line in lines:
        fwp.write(line)
        if is_start_within_list(line, ["eq initconf","eq init("]):
            fwp.write("    < monitor : Monitor | events : empty >\n")


'''
Rewrite rule as required in m-trans
Input:
    fwp: file write pointer;
    lines: string list of file 1;
    i: rule start line index
    rule_name: a rule name;
    event_map: map from rule name to eventMap in file 4
Output: no return value, but write p-trans rule in fwp file
'''
def rewrite_rule_m(fwp, lines, i, rule_name, event_map):
    cnt = 0
    while not is_end_with_dot(lines[i]):
        line = lines[i]
        fwp.write(line)
        if is_end_within_list(line, ['>']):
            # add something
            if cnt == 0: 
                # left
                cnt += 1
                fwp.write("    < monitor : Monitor | events : @TES:TimedEvents >\n")
            elif cnt == 2:
                # right
                cnt += 1
                fwp.write("    < monitor : Monitor | events : (@TES:TimedEvents ; (%s @ T)) >\n" % event_map[rule_name][1])
        if line.strip().startswith("=>"):
            cnt = 2
        i += 1
    fwp.write(lines[i])
    return i


'''
Get eventMap info from file 4
Input: lines: string list of file 4
Output:
    event: list of eventMap, as defined by "eq eventMap =" in file 4
'''
def get_event_info(lines):
    event = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if is_start_within_list(line, ["eq eventMap"]):
            # get eventMap
            event_text, i = get_stmt_from(lines, i)
            p = event_text.index('=')
            while event_text.find(";;", p) != -1:
                # for each tuple, like [xxx, yyy]
                tp_text, p = get_text_between(event_text, p, '[', ']')
                p += 2
                tp_text = tp_text.strip("[ ]") + '\n'
                cnt1 = 0  # round bracket cnt stack
                j = 0
                q = 1
                tp = []  # tuple
                while j < len(tp_text):
                    # get each element in tuple [xxx, yyy]
                    c = tp_text[j]
                    if c == '\n' or (c == ',' and cnt1 ==0):
                        # find a tuple element
                        tp.append(tp_text[q:j].strip(' '))
                        q = j + 1
                    elif c == '(':
                        cnt1 += 1
                    elif c == ')':
                        cnt1 -= 1
                    j += 1
                event.append(tuple(tp))
        i += 1
    
    # debuging info
    # for item in event:
    #     print(item)
    return event
    

'''
Extract type and name of the rule start from line i in lines
Input: 
    lines: string list of file 1;
    i: start line index
Output:
    rule_name
'''
def extract_rule_name(lines, i):
    # 1. get the rule text from line i
    rule_text, j = get_stmt_from(lines, i)
    # 2 rule name
    name, i = get_text_between(rule_text, 2, '[', ']')
    rule_name = name.strip("[ ]")
    return rule_name
    

