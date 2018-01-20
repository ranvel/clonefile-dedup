#!/usr/bin/env python
import sqlite3, subprocess

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
			print("Verifying file: " + dupesResult[0])
			chksumRaw = subprocess.run(['shasum', '-a', '256', dupesResult[0]], stdout=subprocess.PIPE)
			chksum = chksumRaw.stdout.split()[0].decode("utf-8")
			print("Original checksum: \t \t "+ result[0])
			print("New file: \t \t \t "+ chksum)			
			# I should probably add some logic here to ignore Spotlight search files. 
			if chksum == result[0]:
				print("\033[1;32mVerified!!\033[1;m")
			else:
				input("Failed to verify: " + dupesResult[0])

conn.close()
