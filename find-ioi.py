#!/usr/bin/python

import sys
import re
import subprocess

if len(sys.argv)==1:
	UsageString = "Usage:  " + sys.argv[0] + " <text file (IoIs)> <source code dir> <output file (CSV)>"
	sys.exit(UsageString)

### Comamnd line args ###

InFile = sys.argv[1]
LogDir = sys.argv[2]	
OutFile = sys.argv[3]

### Constants ###

SPLIT_REGEX = re.compile("^(.+?):(.+?):(.+)$")

### Main routine ###

# Open results file & write header
OutFileObj = open(OutFile,"w")
OutFileObj.write('File,Word,LineNum,PosNum,Line\r\n')

# Jump in.
InFileObj = open(InFile,"r")
for Word in InFileObj:
	Chomped = Word.replace('\r','')
	Chomped = Chomped.replace('\n','')
	Chomped = Chomped.replace('\\','\\\\')
	BashCommand = "grep -inrHF \"" + Chomped + "\" " + LogDir
	#print ">>> " + BashCommand + " <<<"
	if not Chomped=='':
		Output = subprocess.check_output(BashCommand, shell=True).split('\n')
		#print "Number of results:  " + str(len(Output))
		for Line in Output:
			#print Line
			if Line[0:11]=='Binary file':
				SplitLine = Line.split(':')
				OutFileObj.write(SplitLine[0][12:-8]+','+Chomped+',,,\'<Binary file>\'\r\n')
			elif len(Line)==0:
				pass #Do nothing
			else:
				Result = SPLIT_REGEX.findall(Line)
				Chomped = Chomped.replace('\\\\','\\')
				#print Result
				OutFileObj.write(Result[0][0]+','+Chomped+','+Result[0][1]+',,\''+Result[0][2]+'\'\r\n')
InFileObj.close
OutFileObj.close

