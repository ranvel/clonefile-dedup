#!/usr/bin/env python
import os, sqlite3, subprocess

conn = sqlite3.connect('index.sqlite')

with conn:
    
	cur = conn.cursor()    
    
    # Get files with duplicates
	cur.execute("SELECT chksum, COUNT(*) c FROM files GROUP BY chksum HAVING c > 1;")
	results = cur.fetchall()
	for result in results:
		dupscur = conn.cursor()
		dupscur.execute("select file from files where chksum = '"+ result[0]+"';")
		#Get all duplicate files
		dupesResults = dupscur.fetchall()
		fileIndex = 0 
		#For the first one, treat this as the original even though it doesn't matter which one you use. 
		for dupesResult in dupesResults:
			if fileIndex == 0: 
				print("Original file: " + dupesResult[0])
				originalFile = dupesResult[0]
			else: 
				print("Copy: " + dupesResult[0])
				# The -c parameter is for the `clonefile`
				copyCommand = subprocess.run(['cp', '-cv', originalFile, dupesResult[0]], stdout=subprocess.PIPE)
				print(copyCommand)
			fileIndex += 1

conn.close()
