import csv
import sys
import os
import subprocess
import signal

outOfScopeVariablesFile = 'outOfScopeVariables.txt'
passingModifiedFile = 'modifiedPassing.c'
failingModifiedFile = 'modifiedFailing.c'
replacedFailingFile = 'replacedFailing.c'
passingTestsFile = 'passingTests.txt'
failingTestsFile = 'failingTests.txt'

def findOutOfScopeVariables(cFile, faultFxn):
	process = subprocess.Popen('python outOfScopeVariables.py ' + cFile + ' ' + faultFxn, shell=True, stdout=subprocess.PIPE)
	oosVars, err = process.communicate()
	oosVars = oosVars.decode("utf-8")[:-1]
	f = open(outOfScopeVariablesFile,'w')
	f.write(oosVars)
	f.close()

def generatePassingProgram(cFile, faultFxn, varFile, includeStatements, defineStatements):
	process = subprocess.Popen('python addPrints.py ' + cFile + ' ' + faultFxn + ' ' + varFile + ' ' + outOfScopeVariablesFile, shell=True, stdout=subprocess.PIPE)
	passingProgram, err = process.communicate()
	passingProgram = passingProgram.decode("utf-8")[:-1]
	f = open(passingModifiedFile, 'w')
	f.write(includeStatements + defineStatements + passingProgram)
	f.close()

def generateFailingProgram(cFile, faultyLine, expectedOutput, testFxn, initVarsFile, initList, includeStatements, defineStatements):
	process = subprocess.Popen('python failingModification.py ' + cFile + ' ' + faultyLine + ' ' + expectedOutput + ' ' + testFxn + ' ' + initVarsFile + ' ' + initList, shell=True, stdout=subprocess.PIPE)
	failingProgram, err = process.communicate()
	failingProgram = failingProgram.decode("utf-8")[:-1]
	f = open(failingModifiedFile, 'w')
	kleeInclude = "#include <klee/klee.h>\n"
	f.write(includeStatements + kleeInclude + defineStatements + failingProgram)
	f.close()

def replaceFailingProgram(cFile, faultyLine, kleeVal, includeStatements, defineStatements):
	process = subprocess.Popen('python replaceKleeMod.py ' + cFile + ' ' + faultyLine + ' ' + kleeVal, shell=True, stdout=subprocess.PIPE)
	failingProgram, err = process.communicate()
	failingProgram = failingProgram.decode("utf-8")[:-1]
	f = open(replacedFailingFile, 'w')
	f.write(includeStatements + defineStatements + failingProgram)
	f.close()

def compileProgram(filename):
	process = subprocess.Popen('gcc ' + filename + ' -o ' + filename[:-1] + 'exe', shell=True, stdout=subprocess.PIPE)
	process.wait()

def getKleeOutput():
	process = subprocess.Popen('clang -emit-llvm -c -g ' + failingModifiedFile, shell=True, stdout=subprocess.PIPE)
	process.wait()
	signal.signal(signal.SIGALRM, alarm_handler)
	signal.alarm(10)
	try:
		process = subprocess.Popen('klee -entry-point=klee_test_entry ' + failingModifiedFile[:-1] + 'bc', shell=True, stdout=subprocess.PIPE)
		process.wait()
	except Alarm:
		return '0'
	process = subprocess.Popen('ktest-tool --write-ints klee-last/test000001.ktest', shell=True, stdout=subprocess.PIPE)
	result, err = process.communicate()
	result = result.decode("utf-8")[:-1]
	return result[result.rfind(' ')+1:]

class Alarm(Exception):
	pass
def alarm_handler(signum, frame):
	raise Alarm

if __name__=='__main__':
	if len(sys.argv)>6:
		cFile = sys.argv[1] # tcas.c
		testFxn = sys.argv[2] # alt_sep_test
		faultFxn = sys.argv[3] # Non_Crossing_Biased_Climb
		varFile = sys.argv[4] # attrmap.75
		faultyLine = int(sys.argv[5])
		initVarsFile = sys.argv[6]
	else:
		cFile = 'mh_tcas.c'
		testFxn = 'alt_sep_test'
		faultFxn = 'Non_Crossing_Biased_Climb'
		varFile = 'attrmap.75'
		faultyLine = 76
		initVarsFile = 'init_vars.txt'

	# Remove include statements from c file
	includeStatements = ''
	defineStatements = ''
	faultyLineStr = ''
	program = ''
	removedLines = 0
	with open(cFile) as lines:
		i = 0
		for line in lines:
			i += 1
			if ('#include' in line):
				removedLines += 1
				includeStatements += line
			elif ('#define' in line):
				removedLines += 1
				defineStatements += line
			else:
				program += line
			if (i == faultyLine):
				faultyLineStr = line.strip()
				if ('//' in faultyLineStr):
					faultyLineStr = faultyLineStr[:faultyLineStr.index('//')-2]
	faultyLine -= removedLines
	cFile = 'cFileForPyc.c'
	f = open(cFile,'w')
	f.write(program)
	f.close()

	findOutOfScopeVariables(cFile, faultFxn)
	generatePassingProgram(cFile, faultFxn, varFile, includeStatements, defineStatements)
	compileProgram(passingModifiedFile)
	stateTransformer = ''
	with open(passingTestsFile) as lines:
		for line in lines:
			if (len(line) > 1):
				process = subprocess.Popen('./' + passingModifiedFile[:-1] + 'exe ' + line[:-1], shell=True, stdout=subprocess.PIPE)
				result, err = process.communicate()
				result = result.decode("utf-8")[:-1]
				if (len(result) > 5):
					stateTransformer += result

	program = ''
	removedLines = 0
	newFaultyLine = 0
	with open(passingModifiedFile) as lines:
		i = 0
		for line in lines:
			i += 1
			if ('#include' in line):
				i -= 1
				pass
			elif ('#define' in line):
				i -= 1
				pass
			else:
				program += line
			if (faultyLineStr in line):
				newFaultyLine = i
	f = open(passingModifiedFile,'w')
	f.write(program)
	f.close()

	with open(failingTestsFile) as lines:
		for line in lines:
			if (len(line) > 1):
				expectedOutput = line[:line.index(' ')]
				generateFailingProgram(cFile, str(faultyLine), expectedOutput, testFxn, initVarsFile, line[line.index(' ')+1:], includeStatements, defineStatements)
				kleeVal = getKleeOutput()
				replaceFailingProgram(passingModifiedFile, str(newFaultyLine), kleeVal, includeStatements, defineStatements)
				compileProgram(replacedFailingFile)
				inputLine = line[line.index(' ')+1:]
				process = subprocess.Popen('./' + replacedFailingFile[:-1] + 'exe ' + inputLine, shell=True, stdout=subprocess.PIPE)
				result, err = process.communicate()
				result = result.decode("utf-8")[:-1]
				if (len(result) > 5):
					stateTransformer += result

	f = open('v75.complete.csv','w')
	f.write(stateTransformer)
	f.close()
