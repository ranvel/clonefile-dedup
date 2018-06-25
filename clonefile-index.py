#!/usr/bin/env python3
import os, sqlite3, hashlib
from tqdm import tqdm
from os import listdir
from os.path import isfile, join
from multiprocessing import Pool
from pathlib import Path

print("""
	This will index your files. How many processor threads would you like to use?
	This command will show you your the maximum number you should use: sysctl hw.logicalcpu
	""")
threads = input("Number of Threads to use: ")

conn = sqlite3.connect('clonefile-index.sqlite')
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
			try:
				shahash = getSHA256(filelink).split()[0]
				file_info = [filelink,shahash]
				return file_info
			except Exception as e: 
				print(f"Couldn\'t index {filelink}: {e}")

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

def add2sqlite(fileinfo):
	for f in fileinfo:
		if (f != None):
			file_link = f[0]
			file_hash = f[1]
			c.execute("INSERT INTO files (file, chksum) VALUES ('"+file_link.replace('\'', "\'\'") +"', '"+file_hash+"');")
			conn.commit()

# Index all files from within the root
#start script
if __name__ == '__main__':
	allfiles = []
	sqlite_data = []
	print(f"Indexing files in {os.getcwd()}")
	for dirpath, dirnames, filenames in os.walk("."):
		for filename in [f for f in filenames]:
			filelink =  os.path.join(dirpath, filename)
			if (isfile(filelink)):
				allfiles.append(filelink)
	num_of_files = len(allfiles)
	# "threads" at a time, multiprocess delegation
	print("Processing " + str(num_of_files) + " files")
	with Pool(int(threads)) as pool:
		r = list(tqdm(pool.imap_unordered(processFile, allfiles), total = num_of_files))
	#process (r)esults by adding them to sqlite 
	add2sqlite(r)

conn.close()