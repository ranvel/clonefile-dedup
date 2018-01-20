## 'clonefile' deduplication

This is a rough project that I wanted to do to ensure that I wasn't wasting space by having deplicate files on my drives. YMMV and it is largely untested and so I caution potenial users to review the code and run tests before running this on your full drive, as it could possibly result in data loss. 

Normal deduplication is done at the block level and requires a special filesystem such as zfs as well as enormous amounts of memory to store the checksums. This script aims to catalog all of your files with the sha-256 algorithm and then deduplicate any files with matching signatures. 

You'll need:
 - python 3.6
 - python sqlite3 module
 - a Mac with APFS (to utilize the clonefile syscall)

This program could easily be combined into one program, but it's not a lot of work to run this as separate scripts, so I will leave it as is. 

Instructions: 

1. Run `clonefile-index.py` which will create an `index.sqlite` database with all of the files and chksums at the scriptroot. 
2. Run `clonefile-dedup.py` which will copy the first instance of a file to all of the other instances using the 'clonefile' syscall. This isn't a link but an APFS reference to the same data on the drive that is used by a file with that chksum. 
3. (optional) Run `clonefile-verify.py` to verify that the files bear the same chksum after as they did before the process. If you use Spotlight on this drive, it will definitely display an error on these files. 

Let me know how it works out for you! 
Twitter: @ranvel