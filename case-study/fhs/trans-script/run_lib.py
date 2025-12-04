from __future__ import print_function
import os
import sys
import re

global fault_module_map
fault_module_map = { 
	"ml" : "FAULT-MSGLOSS",
	"md" : "FAULT-MSGDUP",
	"pa" : "FAULT-PARTITION",
	"cr" : "FAULT-CRASH",
	"de" : "FAULT-DELAY",
	"ec" : "FAULT-EQUIVOCATION",
	"tp" : "FAULT-TEMPERING"}

fault_number_map = { 
	"ml" : "M1",
	"md" : "M2",
	"pa" : "M3",
	"cr" : "M4",
	"de" : "M5",
	"ec" : "1.0",
	"tp" : "1.0"}


'''
Get the shortest string from index pos,
	where the string begins with char s, ends with char t
	and has the same number of s and t.
Input:
	text: string text;
	pos: start position;
	s: start char;
	t: terminal char
Output:
	output1: shortest string described above;
	right: the index number denoting the last position of output1 in input1
For example, get_text_between("12[[][]][]", 1, '[', ']') = ("[[][]]", 7)
'''
def get_text_between(text, pos, s, t):
	cnt = 0
	i = pos
	left = 0
	right = len(text)
	while i < len(text):
		if text[i] == s:
			if cnt == 0:
				left = i
			cnt += 1
		elif text[i] == t and (t != '>' or text[i-1] != '-'):  # there is "|->" in text, need except it
			cnt -= 1
			if cnt == 0:
				right = i
				break
		i += 1
	if i == len(text):
		return "", -1
	return text[left:right + 1], right


'''
Get a statement from lines[i]
Input:
	lines: string list;
	i: start line index
Output:
	stmt: a statment begin at lines[i];
	j: the index of the last line of the statement
'''
def get_stmt_from(lines, i):
	j = i
	while not is_end_with_dot(lines[j]):
		j += 1
	stmt = ""
	for k in range(i, j + 1):
		stmt += del_comment(lines[k]).strip()
		if k != j:
			stmt += ' '
	return stmt, j


'''
Judge whether a line end with ".",
	omit comment with --- and *** ,
	empty line return False
Input: line: a line text, which is string
Output: True - this line ends with "."; otherwise, False
'''
def is_end_with_dot(line):
	line = del_comment(line).strip()
	l = len(line)
	if l == 0:
		return False
	i = l - 1
	return line[i] == '.'	


"""
delete line's comment at end of line
"""
def del_comment(line):
	c1 = line.find("---")
	c2 = line.find("***")
	if c1 * c2 == 0:  # comment at start, empty line
		return ""
	elif c1 == -1 and c2 == -1:  # no comment
		return line
	elif c1 != -1 and c2 != -1:  # both comment sign appear
		return line[:min(c1,c2)]
	elif c1 != -1:   # one comment
		return line[:c1]
	elif c2 != -1:  #  one comment
		return line[:c2]
	return line


'''
Judge whether a line start with any string in start_list,
	space before first char is omitted
Input:
	line: a line text, which is string;
	start_list: expected start string
Output: True - this line starts with a string in start_list; otherwise, False
'''
def is_start_within_list(line, start_list):
	i = 0
	while(i < len(line)):
		for st in start_list:
			if line.startswith(st,i):
				return True
		if line[i] != ' ' and line[i] != '\t':
			break
		i += 1
	return False


'''
Judge whether a line end with any string in start_list,
	space after last char is omitted
Input:
	line: a line text, which is string;
	start_list: expected start string
Output: True - this line ends with a string in start_list; otherwise, False
'''
def is_end_within_list(line, start_list):
	line=line.strip()
	for st in start_list:
		if line[-1]==st:
			return True
	return False


def find_last(str,substr):
	last_p=-1
	while True:
		p = str.find(substr,last_p+1)
		if p == -1:
			return last_p
		last_p = p