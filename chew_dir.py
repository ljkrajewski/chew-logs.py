#!/usr/bin/python

import sys
import re
import os
import subprocess

if len(sys.argv)==1:
	UsageString = "Usage:  " + sys.argv[0] + " <source code dir> <output file>"
	sys.exit(UsageString)

### Comamnd line args ###

LogDir = sys.argv[1]
OutFile = sys.argv[2]
WordList = []

### Constants ###

Alphanum = "[0-9a-zA-Z][0-9a-zA-Z\-\']+[0-9a-zA-Z]"
MacAddress = "[[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}|[0-9a-fA-F]{12}]"
WebAddress = "http[|s]\:\/\/[a-z0-9\/\.\-_]+"
Ip4 = "\d{1,3}[\.|:]\d{1,3}[\.|:]\d{1,3}[\.|:]\d{1,3}"  #Some Avaya formats use colons for delimiters
Word_RegexString = "("+Alphanum+"|"+Ip4+"|"+WebAddress+"|"+MacAddress+")+"
WORD_REGEX = re.compile(Word_RegexString)
DRIVE_REGEX = re.compile("([a-zA-Z]:[\\\/])+")

### Globals ###

### Functions ###

def remove_timestamps(Line):
	Newline = re.sub(r"\d{8}-\d{1,2}\:\d{2}\:\d{2}\.\d{6}","_", Line)
	Newline = re.sub(r"\d{1,2}\:\d{2}\:\d{2} (AM|PM)","_", Newline)
	Newline = re.sub(r"\d{2}\:\d{2}\:\d{2}(\.|\,)\d{3}","_", Newline)
	Newline = re.sub(r"\d{1,2}\:\d{2}\:\d{2}","_", Newline)
	Newline = re.sub(r"\d{1,2}\/\d{1,2}\/\d{4}","_", Newline)
	Newline = re.sub(r"\d{2,4}\/\d{2,4}\/\d{2,4}","_", Newline)
	Newline = re.sub(r"\d{2,4}-\d{2,4}-\d{2,4}","_", Newline)
	return Newline

def read_logline(Line):
	global WORD_REGEX
	global DRIVE_REGEX
	global LogResult
	CleanLine = remove_timestamps(Line).lower()
	#print(CleanLine)
	Result = []
	for Item in WORD_REGEX.findall(CleanLine):
		Result = Result + [Item]
		#print(Item[0])
	for Item in DRIVE_REGEX.findall(CleanLine):
		Result = Result + [Item]
	#print(Result)
	
	return Result

def chew_file(Log):
	global WordList
	CharsSoFar = 0
	LogSize = os.path.getsize(Log)
	CurrPercent = 0
	DotCount = 13

	# Test for direcotry first
	if os.path.isfile(Log):
		print "Reading",Log
		LogFileObj = open(Log,"r")
		for Line in LogFileObj:
			#print(Line)
			CharsSoFar = CharsSoFar + len(Line)
			PercentComplete = CharsSoFar / LogSize
			if PercentComplete >= CurrPercent:
				#print("{:4.2%}".format(PercentComplete)," complete.",end="\r")
				#print("\r{:4.2%}".format(PercentComplete)," complete.",)
				CurrPercent = PercentComplete + 0.001
			LineList = read_logline(Line)
			#print(LineList)
			for Word in LineList:
				if (re.match("^\d+($|s$|ms$)",Word) == None):
					if not Word in WordList:
						WordList = WordList + [Word]

### Main routine ###

BashCommand = "find " + LogDir + " -print"
Output = subprocess.check_output(BashCommand, shell=True).split()
for Log in Output:
	chew_file(Log)
WordList.sort()
print "Writing",OutFile
OutFileObj = open(OutFile,"w")
for Word in WordList:
	OutFileObj.write(Word+'\r\n')
OutFileObj.close()
