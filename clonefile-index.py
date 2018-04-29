#!/usr/bin/env python3
import os, sqlite3, hashlib
from os import listdir
from os.path import isfile, join
from multiprocessing import Pool

print("""
	This will index your files. How many processor threads would you like to use?
	This command will show you your the maximum number you should use: sysctl hw.logicalcpu
	""")
threads = input("Number of Threads to use: ")

conn = sqlite3.connect('index.sqlite')
c = conn.cursor()
c.execute('''CREATE TABLE files (file, chksum)''')

def processFile(filelink):
	try: 
		os.path.getsize(filelink)
	except:
		pass
	else: 
		# Don't worry about tiny files:
		if (os.path.getsize(filelink) > 1024):
			print(filelink)
			shahash = getSHA256(filelink).split()[0]
			print(shahash)
			c.execute("INSERT INTO files (file, chksum) VALUES ('"+filelink.replace('\'', "\'\'") +"', '"+shahash+"');")
			conn.commit()
			print("\n")

def getSHA256(currentFile):
	#Read the 64k at a time, hash the buffer & repeat till finished. 
	BLOCKSIZE = 65536
	hasher = hashlib.sha256()
	with open(currentFile, 'rb') as file:
		buf = file.read(BLOCKSIZE)
		while len(buf) > 0:
			hasher.update(buf)
			buf = file.read(BLOCKSIZE)
	return hasher.hexdigest()

# Index all files from within the root
#start script
if __name__ == '__main__':
	allfiles = []
	print("Indexing files in root")
	for dirpath, dirnames, filenames in os.walk("."):
		for filename in [f for f in filenames]:
			filelink =  os.path.join(dirpath, filename)
			if (isfile(filelink)):
				allfiles.append(filelink)
	# "threads" at a time, multiprocess delegation
	print("Processing " + str(len(allfiles)) + " files")
	with Pool(int(threads)) as pool:
		# parallel process "sleepTest", using the workload "workPool" as an argument AND as the tasks to divide up.
		pool.map(processFile, allfiles, chunksize = 1)

conn.close()