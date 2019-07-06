#!/usr/bin/env python3
import os, sqlite3, hashlib, json
from tqdm import tqdm
from os import listdir
from os.path import isfile, join
from multiprocessing import Pool
from pathlib import Path

BLOCKSIZE = 65536

print("""
	This will index your files. How many processor threads would you like to use?
	This command will show you your the maximum number you should use: sysctl hw.logicalcpu
	""")
threads = input("Number of Threads to use: ")

conn = sqlite3.connect('clonefile-index.sqlite')
c = conn.cursor()
c.execute('''CREATE TABLE files (file, chksum64k, chksumfull, size, stat)''')

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
				file_info = (
					filelink, shahash, os.path.getsize(filelink),
					json.dumps(os.stat(filelink)),
				)
				return file_info
			except Exception as e: 
				print(f"Couldn\'t index {filelink}: {e}")

def processFileFull(filelink):
	shahash = getSHA256(filelink, full=True).split()[0]
	file_info = (shahash, filelink)
	return file_info

def getSHA256(currentFile, full=False):
	#Read the 64k at a time, hash the buffer & repeat till finished. 
	#By default only checksum the first block
	hasher = hashlib.sha256()
	with open(currentFile, 'rb') as file:
		buf = file.read(BLOCKSIZE)
		while len(buf) > 0:
			hasher.update(buf)
			if not full:
				break
			buf = file.read(BLOCKSIZE)
	return hasher.hexdigest()

def add2sqlite(fileinfo):
	for f in fileinfo:
		if (f != None):
			if f[2]>BLOCKSIZE:
				c.execute(
					"INSERT INTO files (file, chksum64k, chksumfull, size, stat) VALUES (?,?,?,?,?)",
					(f[0], f[1], '',   f[2], f[3]) )
			else:
				c.execute(
					"INSERT INTO files (file, chksum64k, chksumfull, size, stat) VALUES (?,?,?,?,?)",
					(f[0], f[1], f[1], f[2], f[3]) )

# Index all files from within the root
#start script
if __name__ == '__main__':
	allfiles = []
	sqlite_data = []
	print(f"Indexing files in {os.getcwd()}")
	print(f"Reading file list")
	for dirpath, dirnames, filenames in os.walk("."):
		for filename in [f for f in filenames]:
			filelink =  os.path.join(dirpath, filename)
			if (isfile(filelink)):
				allfiles.append(filelink)
	num_of_files = len(allfiles)
	# "threads" at a time, multiprocess delegation
	print(f'Checksumming {num_of_files} files (fast)')
	with Pool(int(threads)) as pool:
		r = list(tqdm(pool.imap_unordered(processFile, allfiles), total = num_of_files))
	#process (r)esults by adding them to sqlite 
	add2sqlite(r)

	conn.commit()
	print('Indexing database')
	c.execute('''CREATE INDEX index64k ON files(chksum64k ASC)''')
	c.execute('''CREATE INDEX indexfile ON files(file ASC)''')
	c.execute('''CREATE INDEX indexsize ON files(size ASC)''')

	c.execute('''SELECT chksum64k, COUNT(*) c FROM files GROUP BY chksum64k HAVING c > 1''')
	results = c.fetchall()

	allfiles = []
	sqlite_data = []

	print(f'Found {len(results)} non-unique checksums, fetching files')
	for result in tqdm(results):
		c.execute("SELECT file FROM files WHERE chksum64k = ? AND chksumfull == ''", (result[0],))
		for f in c.fetchall():
			allfiles.append(f[0])

	num_of_files = len(allfiles)
	print(f"Calculating full checksum for {num_of_files} files")
	with Pool(int(threads)) as pool:
		r = list(tqdm(pool.imap_unordered(processFileFull, allfiles), total = num_of_files))

	print("Updating database")
	for x in tqdm(r):
		c.execute("UPDATE files SET chksumfull = ? WHERE file = ?", x )

	conn.commit()
	print('Indexing database')
	c.execute('''CREATE INDEX indexfull ON files(chksum64k ASC, chksumfull ASC)''')

conn.commit()
conn.close()
