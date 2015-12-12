import csv
import sys
import os
import subprocess

outOfScopeVariablesFile = 'outOfScopeVariables.txt'
passingModifiedFile = 'modifiedPassing.c'
failingModifiedFile = 'modifiedFailing.c'
replacedFailingFile = 'replacedFailing.c'
passingTestsFile = 'passingTests.txt'
failingTestsFile = 'failingTests.txt'

def findOutOfScopeVariables(cFile, testFxn):
	oosVars = subprocess.check_output('python outOfScopeVariables.py ' + cFile + ' ' + testFxn, shell=True)
	oosVars = oosVars.decode("utf-8")[:-1]
	f = open(outOfScopeVariablesFile,'w')
	f.write(oosVars)
	f.close()

def generatePassingProgram(cFile, testFxn, varFile, includeStatements, defineStatements):
	try:
		passingProgram = subprocess.check_output('python addPrints.py ' + cFile + ' ' + testFxn + ' ' + varFile + ' ' + outOfScopeVariablesFile, shell=True)
	except subprocess.CalledProcessError as e:
		print(e.output)
	passingProgram = passingProgram.decode("utf-8")[:-1]
	f = open(passingModifiedFile, 'w')
	f.write(includeStatements + defineStatements + passingProgram)
	f.close()

def generateFailingProgram(cFile, faultyLine, expectedOutput, testFxn, includeStatements, defineStatements):
	try:
		failingProgram = subprocess.check_output('python failingModification.py ' + cFile + ' ' + faultyLine + ' ' + expectedOutput + ' ' + testFxn, shell=True)
	except subprocess.CalledProcessError as e:
		print(e.output)
	failingProgram = failingProgram.decode("utf-8")[:-1]
	f = open(failingModifiedFile, 'w')
	f.write(includeStatements + defineStatements + failingProgram)
	f.close()

def replaceFailingProgram(cFile, faultyLine, kleeVal, includeStatements, defineStatements):
	try:
		failingProgram = subprocess.check_output('python replaceKleeMod.py ' + cFile + ' ' + faultyLine + ' ' + kleeVal, shell=True)
	except subprocess.CalledProcessError as e:
		print(e.output)
	failingProgram = failingProgram.decode("utf-8")[:-1]
	f = open(replacedFailingFile, 'w')
	f.write(includeStatements + defineStatements + failingProgram)
	f.close()

def compileProgram(filename):
	process = subprocess.Popen('gcc ' + filename + ' -o ' + filename[:-1] + 'exe', shell=True, stdout=subprocess.PIPE)
	process.wait()

if __name__=='__main__':
	if len(sys.argv)>4:
		cFile = sys.argv[1] # tcas.c
		testFxn = sys.argv[2] # alt_sep_test
		varFile = sys.argv[3] # attrmap.75
		faultyLine = int(sys.argv[4])
	else:
		cFile = 'tcas.c'
		testFxn = 'alt_sep_test'
		varFile = 'attrmap.75'
		faultyLine = 120

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
	faultyLine -= removedLines
	cFile = 'cFileForPyc.c'
	f = open(cFile,'w')
	f.write(program)
	f.close()

	findOutOfScopeVariables(cFile, testFxn)
	generatePassingProgram(cFile, testFxn, varFile, includeStatements, defineStatements)
	compileProgram(passingModifiedFile)
	stateTransformer = ''
	with open(passingTestsFile) as lines:
		for line in lines:
			try:
				result = subprocess.check_output(passingModifiedFile[:-1] + 'exe ' + line[:-1], shell=True)
				stateTransformer += result.decode("utf-8")[:-1]
			except subprocess.CalledProcessError as e:
				print(e.output)

	program = ''
	removedLines = 0
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
				faultyLine = i
	f = open(passingModifiedFile,'w')
	f.write(program)
	f.close()

	with open(failingTestsFile) as lines:
		for line in lines:
			expectedOutput = line[:line.index(' ')]
			generateFailingProgram(cFile, str(faultyLine), expectedOutput, testFxn, includeStatements, defineStatements)
			#compileProgram(failingModifiedFile)
			# run klee
			kleeVal = '0'
			replaceFailingProgram(passingModifiedFile, str(faultyLine), kleeVal, includeStatements, defineStatements)
			compileProgram(replacedFailingFile)
			try:
				result = subprocess.check_output(replacedFailingFile[:-1] + 'exe ' + line[:-1], shell=True)
				stateTransformer += result.decode("utf-8")[:-1]
			except subprocess.CalledProcessError as e:
				print(e.output)

	f = open('v75.complete.csv','w')
	f.write(stateTransformer[:-1])
	f.close()
