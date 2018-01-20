#!/usr/bin/env python
import os, sqlite3, subprocess

conn = sqlite3.connect('index.sqlite')

with conn:
    
	cur = conn.cursor()    
    
	cur.execute("SELECT chksum, COUNT(*) c FROM files GROUP BY chksum HAVING c > 1;")
	results = cur.fetchall()
	for result in results:
		dupscur = conn.cursor()
		dupscur.execute("select file from files where chksum = '"+ result[0]+"';")
		# print(result)		
		dupesResults = dupscur.fetchall()
		fileIndex = 0 
		for dupesResult in dupesResults:
			if fileIndex == 0: 
				print("Original file: " + dupesResult[0])
				originalFile = dupesResult[0]
			else: 
				print("Copy: " + dupesResult[0])
				copyCommand = subprocess.run(['cp', '-cv', originalFile, dupesResult[0]], stdout=subprocess.PIPE)
				print(copyCommand)
			fileIndex += 1

conn.close()
