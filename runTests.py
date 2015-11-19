import os
import subprocess

total = ''
failed = ''
with open('testplans/universe') as tests:
	try:
		for line in tests:
			# run the original and faulty program
			source_output = subprocess.check_output(os.getcwd() + '/source/tcas.exe ' + line, shell=True)
			alt_output = subprocess.check_output(os.getcwd() + '/versions/tcas.exe ' + line, shell=True)
			if source_output == alt_output:
				# test passed - run modified program and write attrmap vars to v75.complete.csv
				res = subprocess.check_output(os.getcwd() + '/versions/tcas_mod.exe ' + line, shell=True)
				total += res.decode("utf-8")
			else:
				# test failed - write correct output and inputs to failedTests.txt
				failed += source_output.decode("utf-8")[:-1] + line
	except Exception as e:
		print(str(e))
f = open('v75.complete.csv','w')
f.write(total)
f.close()
f2 = open('failedTests.txt','w')
f2.write(failed)
f2.close()