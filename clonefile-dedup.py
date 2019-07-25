#!/usr/bin/env python3
import os, sqlite3, subprocess, xattr, pickle

cwd = os.path.abspath(os.path.curdir)
conn = sqlite3.connect('clonefile-index.sqlite')

with conn:
    
	cur = conn.cursor()    
    
    # Get files with duplicates
	cur.execute("SELECT chksumfull, COUNT(*) c FROM files WHERE chksumfull != '' GROUP BY chksumfull HAVING c > 1 ORDER BY size DESC")
	results = cur.fetchall()
	for result in results:
		dupscur = conn.cursor()
		dupscur.execute("SELECT file FROM files WHERE chksumfull = ?", (result[0],) )
		#Get all duplicate files
		dupesResults = dupscur.fetchall()
		fileIndex = 0 
		#For the first one, treat this as the original even though it doesn't matter which one you use. 
		for dupesResult in dupesResults:
			if not os.path.isfile(dupesResult[0]):
				continue
			if os.path.islink(dupesResult[0]):
				continue
			if fileIndex == 0:
				print(f"Original file: {dupesResult[0]}    size {os.path.getsize(dupesResult[0])}")
				originalFile = dupesResult[0]
			else:
				fname = dupesResult[0]
				fnameNew = fname + ".cfdnew"
				print(f"    replacing: {fname}")

				oldStat = os.stat(fname)
				oldAttr = dict(xattr.xattr(fname))

				dirName = os.path.abspath(os.path.dirname(fname))
				oldDirStat = os.stat(dirName)

				# The -c parameter is for the `clonefile`
				copyCommand = subprocess.run(['cp', '-cvp', originalFile, fnameNew], stdout=subprocess.PIPE)
				#print(copyCommand)

				newStat = os.stat(fnameNew) 
				newAttr = dict(xattr.xattr(fnameNew))

				if newStat.st_uid != oldStat.st_uid or newStat.st_gid != oldStat.st_gid:
					os.chown(fnameNew, oldStat.st_uid, oldStat.st_gid)

				if newStat.st_mode != oldStat.st_mode:
					os.chmod(fnameNew, oldStat.st_mode)

				if pickle.dumps(oldAttr)!=pickle.dumps(newAttr):
					for k,v in oldAttr.items():
						xattr.setxattr(fnameNew, k, v)

				if newStat.st_mtime != oldStat.st_mtime or newStat.st_atime != oldStat.st_atime:
					os.utime(fnameNew, (oldStat.st_atime, oldStat.st_mtime) )

				moveCommand = subprocess.run(['mv', '-f', fnameNew, fname], stdout=subprocess.PIPE)
				#print(moveCommand)

				fnameNew = fname
				newStat = os.stat(fnameNew) 
				newAttr = dict(xattr.xattr(fnameNew))
				newDirStat = os.stat(dirName)

				# additional fixup, just in case:
				if newStat.st_uid != oldStat.st_uid or newStat.st_gid != oldStat.st_gid:
					os.chown(fnameNew, oldStat.st_uid, oldStat.st_gid)

				if newStat.st_mode != oldStat.st_mode:
					os.chmod(fnameNew, oldStat.st_mode)

				if pickle.dumps(oldAttr)!=pickle.dumps(newAttr):
					for k,v in oldAttr.items():
						xattr.setxattr(fnameNew, k, v)

				if newStat.st_mtime != oldStat.st_mtime or newStat.st_atime != oldStat.st_atime:
					os.utime(fnameNew, (oldStat.st_atime, oldStat.st_mtime) )

				if newDirStat.st_mtime != oldDirStat.st_mtime or newDirStat.st_atime != oldDirStat.st_atime:
					os.utime(dirName, (oldDirStat.st_atime, oldDirStat.st_mtime) )

			fileIndex += 1

conn.close()
