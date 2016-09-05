#Get log from remote linux server and count the error log number
#error log is generate base on log4j
#log example 2016-09-05 15:01:35 LEVEL [logger] name

#Install paramikno
#get pip based on https://pip.pypa.io/en/latest/installing/
#run command below:
#pip install cryptography
#pip install paramiko
import paramiko
import os
from collections import Counter

servers = ['127.0.0.1']
username = 'username'
password = 'password'
linuxLogDir = '/tmp/'
windowsLogDir = 'C:/'

logs = []
def fetchLog(server):
	client = paramiko.SSHClient()
	client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	client.connect(server, username=username, password=password)
	print "Connect to " + server + "..."
	stdin, stdout, stderr = client.exec_command('ls ' + linuxLogDir)
	fileList = stdout.read().rstrip('\n').split('\n')

	sftpClient = client.open_sftp()
	for file in fileList:
		if file != '':
			print "Fetching log " + file + "..."
			log = server + '-' + file
			sftpClient.get(linuxLogDir + file, windowsLogDir + log)
			logs.append(log)
			print "Fetching log " + file + " done."
	print "All logs fetched to local."
	sftpClient.close()
	client.close()

for server in servers:
	fetchLog(server)

def analysis(file):
	log = open(windowsLogDir + file)
	done = 0
	while not done:
		line = log.readline().rstrip('\n')[20:]	#remove date
		errors[line] += 1
		if line != '':
			if line[0:5] != 'ERROR':			#remove log not ERROR
				continue
			errors[line[6:]] += 1
		else:
			done = 1
	log.close()

errors = Counter()
for log in logs:
	analysis(log)
print errors.items()