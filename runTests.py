import os
import subprocess
import sys

passing = ''
failed = ''
with open('testplans/universe') as tests:
	try:
		for line in tests:
			# run the original and faulty program
			try:
				source_output = subprocess.check_output(os.getcwd() + '/source/tcas.exe ' + line, shell=True)
				alt_output = subprocess.check_output(os.getcwd() + '/versions/tcas.exe ' + line, shell=True)
			except subprocess.CalledProcessError as e:
				pass
			if source_output == alt_output:
				# test passed - write inputs to passingTests.txt
				passing += line
			else:
				# test failed - write correct output and inputs to failedTests.txt
				failed += source_output.decode("utf-8")[:-1] + line
	except Exception as e:
		print(str(e))
f = open('passingTests.txt','w')
f.write(passing)
f.close()
f2 = open('failingTests.txt','w')
f2.write(failed)
f2.close()