from __future__ import print_function
import os
import time


PORT_P = "49046"
PATH_TO_PVESTA = "../pvesta/"
CLIENT_P = "pvesta-client.jar"
SERVER_P = "pvesta-server.jar"
SERVER_OUTPUT = "server-output.txt"
CLIENT_OUTPUT = "pvesta-output.txt"
MEM_OUTPUT = "memory-output.txt"
MEM_LOG = "memory-output.log"
MON_OUTPUT = "monitor-output.txt"
OUTFILE = "result.txt"
SPACE = [' ', '\n', '\t']
'''
Global flag for brief terminal display
0: All details, including F-trans, time, memory in terminal and result
10: Only info about calling pvesta in terminal and brief result 
2023.8.13 18:05
'''
BRIEF_PRINT = 0


'''
Call pvesta without parallel monitor
'''
def call_pvesta(para):
	call_pvesta_mode(para, 0)


'''
Call pvesta with parallel monitor
'''
def call_pvesta_with_monitor(para, mlog):
	if mlog == 0:
		# no monitor log
		call_pvesta_mode(para, 1)
	else:
		# with monitor log
		call_pvesta_mode(para, 2)


'''
Call pvesta with para
Input:
	para: a list containing f, a, m and serverlist
	mode: 0-without parallel monitor; 1-parallel monitor without log; 2-parallel monitor with log
Output: 0: no error; otherwise, error code
	result file is OUTFILE
'''
def call_pvesta_mode(options, mode):
	
	# 1. start pvesta server
	command = "java -jar " + PATH_TO_PVESTA + SERVER_P + " > " + SERVER_OUTPUT + " &"
	err_code = os.system(command)
	# print(command)
	if err_code == 0:
		print("Calling PVeStA: server started successfully.")
	else:
		print("Calling PVeStA: fail to start server. %d" % err_code)
		return err_code
	
	# 2. start client
	command = "rm -rf " + MEM_LOG
	os.system(command)  # delete old log
	command = "java -jar " + PATH_TO_PVESTA + CLIENT_P + \
	    " -l " + options["-l"] + \
	    " -m " + options["-m"] + \
	    " -f " + options["-f"] + \
	    " -a " + options["-a"] + " > " + CLIENT_OUTPUT
	# print(command)
	print("Calling PVeStA: client is running ...")
	if mode == 0:
		# no parallel monitor
		err_code = os.system(command)
		if err_code == 0:
			print("Calling PVeStA: client ran successfully.")
		else:
			print("Calling PVeStA: fail to run client. %d" % err_code)
			return err_code
	else:
		# with parallel monitor
		pid_moni = os.fork()
		if pid_moni != 0:
			# main process
			err_code = os.system(command)
			command = "kill -9 " + str(pid_moni)
			os.system(command)
			if err_code == 0:
				print("Calling PVeStA: client ran successfully.")
			else:
				print("Calling PVeStA: fail to run client. %d" % err_code)
				return err_code
		else:
			# son monitor process
			monitor_process()
	
	# 3. calculate memory usage
	# get memory usage and kill pvesta server
	mem = 0
	mem, pid_server, pls = get_memory_usage()
	if pid_server != -1:
		command = "kill -9 " + pid_server
		os.system(command)
	# get memory usage from parallel monitor
	if mode != 0:
		mem2 = get_memory_usage_from_monitor()
		#print("Mem: %d, %d" % (mem, mem2))
		mem = max(mem, mem2)

	# 3. output result
	rp = read_client_output()
	rp.memory = mem / 1024.0  # unit: KB to MB
	fwp = open(OUTFILE, "w")
	fwp.write("Confidence (alpha): %s\n" % rp.alpha)
	fwp.write("Threshold (delta): %s\n" % rp.delta1)
	fwp.write("Samples generated: %s\n" % rp.samples)
	fwp.write("SMC result: %s\n" % rp.result)
	if BRIEF_PRINT <= 0:
		if rp.memory != 0:
			fwp.write("Memory usage: %.3f MB\n" % rp.memory)
		else:
			print("Calling PVeStA: Warning: get memory usage failed.")
	# fwp.write("Running time: %s seconds\n" % rp.time)
	fwp.close()
	
	# 4. delete intermediate output and log
	command = "rm -rf " + SERVER_OUTPUT
	os.system(command)
	command = "rm -rf " + CLIENT_OUTPUT
	os.system(command)
	command = "rm -rf " + MEM_OUTPUT
	os.system(command)
	command = "rm -rf " + MON_OUTPUT
	os.system(command)
	command = "rm -rf " + MEM_LOG
	if mode != 2:
		os.system(command)
	return 0


class ResultPvesta:
	def __init__(self):
		self.model = ""
		self.formula = ""
		self.alpha = ""
		self.delta1 = ""
		self.samples = ""
		self.result = ""
		self.time = ""
		self.memory = ""
	def show(self):
		print("MFAD: %s, %s, %s, %s" % (self.model, self.formular, self.alpha, self.delta1))
		print("SRT: %s, %s, %s" % (self.samples, self.result, self.time))


class Process:
	def __init__(self, p, m, n):
		self.pid = p
		self.mem = m
		self.name = n
	def show(self):
		print("%s, %s, %s KB" % (self.pid, self.name, self.mem))
	def write(self,wp):
		wp.write("%s,%s,%s\n" % (self.pid, self.mem, self.name))


'''
Get memory usage from monitor output MON_OUTPUT
Input: no parameter, but file MON_OUTPUT is needed
Output:
	mem: the number of memory usage in file MON_OUTPUT; if error, mem is -1
'''
def get_memory_usage_from_monitor():
	mem = -1
	try:
		rp = open(MON_OUTPUT, "r")
		line = rp.readlines()[0]
	except:
		mem = -1
	else:
		mem = eval(line.strip())
		rp.close()
	return mem


'''
Monitor the memory usage parallelly
Input: no parameter
Output: no return value, but memory usage number is in file MON_OUTPUT
'''
def monitor_process():
	print("Calling PVeStA: monitor started.")
	m = 0
	m, p, pls = get_memory_usage()
	n = 0
	st = time.time()
	while True:
		t = time.time()
		if t - st < 5:
			time.sleep(0.5)
			n, p, pls = get_memory_usage()
		elif t - st < 60:
			time.sleep(5)
			n, p, pls = get_memory_usage()
		else:
			time.sleep(10)
			n, p, pls = get_memory_usage()
		wp = open(MON_OUTPUT, "w")
		t = max(m, n)
		wp.write("%d\n" % t)
		wp.close()
		#print("Monitor wrote")


'''
Get memory usage by ps order
Input: no parameter
Output:
	mem: the sum of rss memory usage of pvesta server and maude process
	pid_server: the process id of pvesta server	
	ls: the process list related
'''
def get_memory_usage():
	ls = []
	# get pvesta process info
	command = "ps -eo pid,rss,cmd | grep java > " + MEM_OUTPUT
	os.system(command)
	pro = None
	rp = open(MEM_OUTPUT, "r")
	for line in rp:
		if line.find("java -jar " + PATH_TO_PVESTA + SERVER_P) >=0:
			line = line.strip()
			t = line.index(' ')
			p = line[0:t]
			line = line[t+1:-1].strip()
			m = line[0:line.index(' ')]
			ls.append(Process(p, m, SERVER_P))
		if line.find("java -jar " + PATH_TO_PVESTA + CLIENT_P) >=0:
			line = line.strip()
			t = line.index(' ')
			p = line[0:t]
			line = line[t+1:-1].strip()
			m = line[0:line.index(' ')]
			pro = Process(p, m, CLIENT_P)
	rp.close()
	if pro != None:
		ls.append(pro)
	# get maude process info
	command = "ps -eo pid,rss,cmd | grep maude > " + MEM_OUTPUT
	os.system(command)
	rp = open(MEM_OUTPUT, "r")
	pro = None
	for line in rp:
		if line.find("maude -random-seed=") >=0:
			line = line.strip()
			t = line.index(' ')
			p = line[0:t]
			line = line[t+1:-1].strip()
			m = line[0:line.index(' ')]
			pro = Process(p, m, "maude")
	rp.close()
	if pro != None:
		ls.append(pro)
	# add memory usage sum
	pid_server = -1
	mem = 0
	wp = open(MEM_LOG, "a")
	wp.write("\n%f\n" % time.time())
	for item in ls:
		if item.name == SERVER_P:
			pid_server = item.pid
		# if item.name == SERVER_P or item.name == "maude":
		mem += eval(item.mem)
		item.write(wp)
	wp.close()
	return mem, pid_server, ls


'''
Read the output file of pvesta client
Input: no parameter, but pvesta output file CLIENT_OUTPUT neeeded
Output:
	rp: a ResultPvesta instance, containing info of pvesta output
'''
def read_client_output():
	frp = open(CLIENT_OUTPUT, "r")
	rp = ResultPvesta()
	lines = frp.readlines()
	for line in lines:
		if line.startswith("model:"):
			rp.model = get_text_until(line, SPACE, 6)
		elif line.startswith("formula:"):
			rp.formular = get_text_until(line, SPACE, 8)
		elif line.startswith("alpha:"):
			rp.alpha = get_text_until(line, SPACE, 6)
		elif line.startswith("delta1:"):
			rp.delta1 = get_text_until(line, SPACE, 7)
		elif line.startswith("samples generated ="):
			rp.samples = get_text_until(line, SPACE, 19)
		elif line.startswith("Result:"):
			rp.result = get_text_until(line, SPACE, 7)
		elif line.startswith("Running time:"):
			rp.time = get_text_until(line, ['s'], 13).strip()
	frp.close()
	return rp


'''
Get text from st_index to char in end_list without SPACE
Input:
	line: a string
	end_list: list of chars, denoting the char after extracted text
	st_index: the start index of line, default 0
Output:
	rt: string, extracted text from line[st_index] to any char in end_list without SPACE
'''
def get_text_until(line, end_list, st_index = 0):
	i = st_index
	rt = ""
	while i < len(line):
		c = line[i]
		if c in end_list and rt != "":
			break
		elif c not in SPACE:
			rt = rt + c
		i += 1
	return rt
