#!/usr/bin/env python
import os, subprocess, sqlite3
from os import listdir
from os.path import isfile, join

conn = sqlite3.connect('index.sqlite')

def processFile(filelink):
	# Don't worry about tiny files:
	if (os.path.getsize(filelink) > 1024):
		print(filelink)
		shahash = getSHA256(filelink).split()[0]
		print(shahash.decode("utf-8"))
		conn.execute("INSERT INTO files (file, chksum) VALUES ('"+filelink.replace('\'', "\'\'") +"', '"+shahash.decode("utf-8")+"');")
		conn.commit()
		print("\n")

def getSHA256(currentFile):
	#Using commandline `shasum` because I couldn't get the same performance out of python's hashlib 
	#Removing the '-a 256' parameter is probably a lot faster, but maybe less safe?
	result = subprocess.run(['shasum', '-a', '256', currentFile], stdout=subprocess.PIPE)
	return result.stdout

# Index all files from within the root
for dirpath, dirnames, filenames in os.walk("."):
	for filename in [f for f in filenames]:
		filelink =  os.path.join(dirpath, filename)
		if (isfile(filelink)):
			processFile(filelink)

conn.close()