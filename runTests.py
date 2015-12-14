import os
import subprocess
import sys

passing = ''
failed = ''
with open('universe') as tests:
	try:
		for line in tests:
			# run the original and faulty program
			process = subprocess.Popen('./mh_tcas_true.exe ' + line, shell=True, stdout=subprocess.PIPE)
			source_output, err = process.communicate()
			process = subprocess.Popen('./mh_tcas.exe ' + line, shell=True, stdout=subprocess.PIPE)
			alt_output, err = process.communicate()
			if source_output == alt_output:
				# test passed - write inputs to passingTests.txt
				passing += line
			else:
				# test failed - write correct output and inputs to failedTests.txt
				failed += source_output.decode("utf-8")[:-1] + ' ' + line
	except Exception as e:
		print(str(e))
f = open('passingTests.txt','w')
f.write(passing)
f.close()
f2 = open('failingTests.txt','w')
f2.write(failed)
f2.close()
