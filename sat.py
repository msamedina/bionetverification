"""
Automated SAT Network Verifier
Michelle Aluf Medina
"""

import random
import re
import datetime
import logging
import sys

if sys.platform.startswith("linux"):
	import pexpect
from cnfgen.families import randomformulas as randform
import scipy.special
import miscfunctions as misc
# import nusmv
import math
import ast
import modcheck


def print_sat_menu():
	"""
	Menu for running SAT samples consecutively or exit the script
	"""
	print('Select an option:\n')
	print('\t[1] Enter sample size for SAT')
	print('\t[2] Main Menu')


# Function to read DIMACS format files
def dimacs_reader(filename):
	"""
	Read DIMACS CNF files and convert to lists for NuSMV network descriptions.
		Inputs:
			filename: The file name to be interpreted
			Output:
				dictionary containing CNF list, num clauses, and number vars
	"""
	# From stack overflow with some editing
	in_data = open(filename, "r")
	# logging.info('Opened dimacs file')
	cnf = list()
	cnf.append(list())
	#maxvar = 0
	unique_var_list = list()
	# For return value
	num_var = 0
	num_clause = 0
	# Run throught the lines of data in the DIMACS file
	for line in in_data:
		tokens = line.split()
		if len(tokens) != 0 and tokens[0].lower() == "p":
			# Use for validation of correct file format
			if tokens[1].lower() == "cnf":
				num_var = int(tokens[2])
				num_clause = int(tokens[3])
			else:
				print("File should be in CNF format. Edit and resubmit.")
				# logging.warning('File should be in CNF format.')
				# logging.warning('Edit and resubmit')
				return -1
		elif len(tokens) != 0 and tokens[0].lower() not in ("p", "c"):
			# if len(tokens) != 4:
			#     print("Not in 3-CNF format. Please edit and resubmit")
			#     # logging.warning('Not in 3-CNF format. Edit and resubmit')
			#     return -1
			for tok in tokens:
				lit = int(tok)
				if (lit not in unique_var_list) and (lit is not 0):
					unique_var_list.append(lit)
				#maxvar = max(maxvar, abs(lit))
				if lit == 0:
					cnf.append(list())
				else:
					cnf[-1].append(lit)
	assert len(cnf[-1]) == 0
	cnf.pop()
	assert (len(cnf) == num_clause), "Incorrect number of clauses. Re-run."
	#assert (maxvar <= num_var), "Incorrect number of variables. Re-run."
	assert (len(unique_var_list) == num_var), "Incorrect number of variables. Re-run."
	print("Your CNF in list format: ", cnf)
	# logging.info('Current CNF in list format: ' + str(cnf))
	#print("Max variable index used: ", maxvar)
	print("Unique variables used: ", len(unique_var_list))
	# logging.info('Max variable index used: ' + str(maxvar))
	return cnf, num_clause, num_var


# Functions for NuSMV files
def file_name_smv(num_clause, num_var, noclau):
	"""
	Generate smv file name for given SAT problem using number of clauses and
	variables, and type
		Input:
			num_clause: number of clauses
			num_var: number of variables
			noClau: True for noClau, False for Clau
		Output:
			filename: smv file name for the SAT network with formatting
	"""
	if noclau is True:
		filename = ("autoSAT_noClau_" + str(num_clause) + "_Clauses_"
					+ str(num_var) + "_Vars_{0}.smv")
	else:
		filename = ("autoSAT_Clau_" + str(num_clause) + "_Clauses_"
					+ str(num_var) + "_Vars_{0}.smv")
	return misc.file_name_cformat(filename)


# Functions for prism files
def file_name_prism(num_clause, num_var, noclau):
	"""
	Generate prism file name for given SAT problem using number of clauses and
	variables, and type
		Input:
			num_clause: number of clauses
			num_var: number of variables
		Output:
			filename: prism file name for the SAT network with formatting
	"""
	filename = ("autoSAT_noClau_" + str(num_clause) + "_Clauses_"
				+ str(num_var) + "_Vars_{0}.pm")
	return misc.file_name_cformat(filename)


def print_smv_noClau(filename, cnf_list, num_clause, num_var):
	"""
	Print out the SAT no clause network description to the smv file
	Tag variable used as an indicator for the clauses rather than using a
	dedicated variable
		Input:
			filename: the smv filename to be used
			cnf_list: The CNF list for the SAT problem
			num_clause: The number of clauses
			num_var: The number of variables
	"""
	# Write header into file
	f = open(filename, 'w')
	# logging.info('SMV file has been opened for editing')
	now = datetime.datetime.now()
	f.write('--Date:\t' + now.strftime("%d-%m-%Y"))
	f.write('\n--SAT Problem\n--' + str(num_clause) + ' Clauses and '
			+ str(num_var) + ' Variables: ' + str(cnf_list)
			+ '\n-------------------------------\n')

	# Write beginning of module and variable definitions
	f.write('MODULE main\nVAR\n')
	f.write('\tjunction: {varble, clause};\n')
	f.write('\tdir: {left, right, dwn};\n')
	f.write('\tvari: 0..' + str(num_var) + ';\n')
	# f.write('\tclau: 0..' + str(num_clause) + ';\n')
	f.write('\tvarval: boolean;\n\n')
	# TAG AS BOOLEAN VALUE
	# f.write('\ttag: array 1..' + str(num_clause) + ' of boolean;\n')
	# TAG AS COUNTER
	f.write('\ttag: array 1..' + str(num_clause) + ' of 0..3;\n')
	f.write('\tflag: boolean;\n\n')

	# Write assignment definitions
	f.write('ASSIGN\n')
	f.write('\tinit(junction) := varble;\n')
	f.write('\tinit(dir) := dwn;\n')
	f.write('\tinit(vari) := 1;\n')
	# f.write('\tinit(clau) := 0;\n')
	f.write('\tinit(varval) := FALSE;\n')
	f.write('\tinit(flag) := FALSE;\n')
	for i in range(1, num_clause + 1):
		if i < num_clause:
			# TAG AS BOOLEAN VALUE
			# f.write('\tinit(tag[' + str(i) + ']) := FALSE;\t')
			# TAG AS COUNTER
			f.write('\tinit(tag[' + str(i) + ']) := 0;\t')
		else:
			# TAG AS BOOLEAN VALUE
			# f.write('\tinit(tag[' + str(i) + ']) := FALSE;\n\n')
			# TAG AS COUNTER
			f.write('\tinit(tag[' + str(i) + ']) := 0;\n\n')

	# Write transitions into file
	# JUNCTIONS
	f.write('\n\n\t--Change junction type according to next clau value\n')
	# f.write('\tnext(junction) := (next(clau) = 0 ? varble : clause);\n')
	f.write('\tnext(junction) := (junction = varble ? clause : varble);\n')

	# DIRECTIONS
	f.write('\n\t--Decide next direction by current junction type\n')
	f.write('\tnext(dir) := \n\t\t\t\t\tcase\n\t\t\t\t\t\t(junction = varble):'
			' {left, right};\n\t\t\t\t\t\t(junction = clause): dwn;\n'
			'\t\t\t\t\t\tTRUE: {left, right, dwn};\n\t\t\t\t\tesac;\n')

	# VARI
	f.write('\n\t--Change vari when reaching \'varble\' junction\n')
	f.write('\tnext(vari) := (next(junction) = varble) ? ((vari + 1) mod '
			+ str(num_var + 1) + ') : vari;\n')

	# VARVAL
	f.write('\n\t--Change varval after direction taken from varble junction\n')
	f.write('\tnext(varval) := \n\t\t\t\t\tcase\n\t\t\t\t\t\t'
			'(next(dir) = left): TRUE;\n\t\t\t\t\t\t(next(dir) = right):'
			' FALSE;\n\t\t\t\t\t\tTRUE: varval;\n\t\t\t\t\tesac;\n')

	# FLAG
	f.write('\n\t--Flag is TRUE when reaching the end of the network\n')
	f.write('\tnext(flag) := (next(vari) = 0 ? TRUE : FALSE);\n')

	# TAG
	f.write('\n\t--Increase tag counter if clause was satistifed')
	for i in range(0, num_clause):
		f.write('\n\t--C' + str(i + 1) + '\n')
		f.write('\tnext(tag[' + str(i + 1) + ']) :=\n\t\t\t\t\tcase\n')
		f.write('\t\t\t\t\t\t(junction = clause) & (')
		for j in range(0, len(cnf_list[i])):#range(0, 3):
			currvar = cnf_list[i][j]
			torf = ''
			if currvar > 0:
				torf = 'TRUE'
			else:
				torf = 'FALSE'
			if j == 0 and j == (len(cnf_list[i]) - 1):
				f.write('(vari = ' + str(abs(currvar)) + ' & next(varval) = '
						+ torf + '))')
			elif j == 0:
				f.write('(vari = ' + str(abs(currvar)) + ' & next(varval) = '
						+ torf + ')')
			elif j == (len(cnf_list[i]) - 1):
				f.write(' | (vari = ' + str(abs(currvar))
						+ ' & next(varval) = ' + torf + '))')
			else:
				f.write(' | (vari = ' + str(abs(currvar))
						+ ' & next(varval) = ' + torf + ')')
		f.write(': (tag[' + str(i + 1) + '] + 1) mod  4;\n\t\t\t\t\t\t'
				+ '(flag = TRUE): 0;\n\t\t\t\t\t\tTRUE: tag[' + str(i + 1)
				+ '];\n\t\t\t\t\tesac;\n')

	# Write specifications to file
	f.write('\n-----SPECS-----\n')
	# Prepare spec strings here
	spec_tag = ''
	for i in range(1, num_clause + 1):
		if i < num_clause:
			spec_tag += '(tag[' + str(i) + '] > 0) & '
		else:
			spec_tag += '(tag[' + str(i) + '] > 0));\n'
	f.write('LTLSPEC\tNAME\tltl_all_c := G! ((flag = TRUE) & ' + str(spec_tag))
	f.write('CTLSPEC\tNAME\tctl_all_c := EF ((flag = TRUE) & ' + str(spec_tag))

	# Close File
	f.close()


def print_smv_clau(filename, cnf_list, num_clause, num_var):
	"""
	Print out the SAT clause network description to the smv file
	Defines a separate variable for indication of clause junctions as tag
	variable only indicates the clauses entered
		Input:
			filename: the smv filename to be used
			cnf_list: The CNF list for the SAT problem
			num_clause: The number of clauses
			num_var: The number of variables
	"""
	# Write header into file
	f = open(filename, 'w')
	now = datetime.datetime.now()
	f.write('--Date:\t' + now.strftime("%d-%m-%Y"))
	f.write('\n--SAT Problem\n--' + str(num_clause) + ' Clauses and '
			+ str(num_var) + ' Variables: ' + str(cnf_list)
			+ '\n-------------------------------\n')

	# Write beginning of module and variable definitions
	f.write('MODULE main\nVAR\n')
	f.write('\tjunction: {varble, clause};\n')
	f.write('\tdir: {left, right, dwn};\n')
	f.write('\tvari: 0..' + str(num_var) + ';\n')
	f.write('\tclau: 0..' + str(num_clause) + ';\n')
	f.write('\tvarval: boolean;\n\n')
	# TAG AS BOOLEAN VALUE
	# f.write('\ttag: array 1..' + str(num_clause) + ' of boolean;\n')
	# TAG AS COUNTER
	f.write('\ttag: array 1..' + str(num_clause) + ' of 0..3;\n')
	f.write('\tflag: boolean;\n\n')

	# Write assignment definitions
	f.write('ASSIGN\n')
	f.write('\tinit(junction) := varble;\n')
	f.write('\tinit(dir) := dwn;\n')
	f.write('\tinit(vari) := 1;\n')
	f.write('\tinit(clau) := 0;\n')
	f.write('\tinit(varval) := FALSE;\n')
	f.write('\tinit(flag) := FALSE;\n')
	for i in range(1, num_clause + 1):
		if i < num_clause:
			# TAG AS BOOLEAN VALUE
			# f.write('\tinit(tag[' + str(i) + ']) := FALSE;\t')
			# TAG AS COUNTER
			f.write('\tinit(tag[' + str(i) + ']) := 0;\t')
		else:
			# TAG AS BOOLEAN VALUE
			# f.write('\tinit(tag[' + str(i) + ']) := FALSE;\n\n')
			# TAG AS COUNTER
			f.write('\tinit(tag[' + str(i) + ']) := 0;\n\n')

	# Write transitions into file
	# JUNCTIONS
	f.write('\n\n\t--Change junction type according to next clau value\n')
	f.write('\tnext(junction) := (next(clau) = 0 ? varble : clause);\n')

	# DIRECTIONS
	f.write('\n\t--Decide next direction by current junction type\n')
	f.write('\tnext(dir) := \n\t\t\t\t\tcase\n\t\t\t\t\t\t'
			'(junction = varble): {left, right};\n\t\t\t\t\t\t'
			'(junction = clause): dwn;\n\t\t\t\t\t\t'
			'TRUE: {left, right, dwn};\n\t\t\t\t\tesac;\n')

	# VARI
	f.write('\n\t--Change vari when reaching \'varble\' junction\n')
	f.write('\tnext(vari) := (next(junction) = varble) ? ((vari + 1) mod '
			+ str(num_var + 1) + ') : vari;\n')

	# VARVAL
	f.write('\n\t--Change varval after direction taken from varble junction\n')
	f.write('\tnext(varval) := \n\t\t\t\t\tcase\n\t\t\t\t\t\t'
			'(next(dir) = left): TRUE;\n\t\t\t\t\t\t(next(dir) = right):'
			' FALSE;\n\t\t\t\t\t\tTRUE: varval;\n\t\t\t\t\tesac;\n')

	# CLAU
	# Run through CNF List to setup rules here.
	# Each sub-list is a clause, so check what variables are contained within
	# and then setup the rules accordingly.
	f.write('\n\t--Change clau by the CNF (vari and varval)\n')
	f.write('\tnext(clau) := \n\t\t\t\t\tcase\n')

	for i in range(0, num_clause):
		for j in range(0, len(cnf_list[i])):#range(0, 3):
			currvar = cnf_list[i][j]
			torf = ''
			if currvar > 0:
				torf = 'TRUE'
			else:
				torf = 'FALSE'
			if j == 0 and j == (len(cnf_list[i]) - 1):
				f.write('\t\t\t\t\t\t(vari = ' + str(abs(currvar))
						+ ' & next(varval) = ' + torf + ' & clau < '
						+ str(i + 1) + '): ' + str(i + 1) + ';\n')
			elif j == 0:
				f.write('\t\t\t\t\t\t(vari = ' + str(abs(currvar))
						+ ' & next(varval) = ' + torf + ' & clau < '
						+ str(i + 1) + ')')
			elif j == (len(cnf_list[i]) - 1):
				f.write(' | (vari = ' + str(abs(currvar))
						+ ' & next(varval) = ' + torf + ' & clau < '
						+ str(i + 1) + '): ' + str(i + 1) + ';\n')
			else:
				f.write(' | (vari = ' + str(abs(currvar))
						+ ' & next(varval) = ' + torf + ' & clau < '
						+ str(i + 1) + ')')

		if i == (num_clause - 1):
			f.write('\t\t\t\t\t\tTRUE: 0;\n\t\t\t\t\tesac;\n')

	# FLAG
	f.write('\n\t--Flag is TRUE when reaching the end of the network\n')
	f.write('\tnext(flag) := (next(vari) = 0 ? TRUE : FALSE);\n')

	# TAG
	f.write('\n\t--Increase tag counter if clause was satistifed')
	for i in range(0, num_clause):
		f.write('\n\t--C' + str(i + 1) + '\n')
		f.write('\tnext(tag[' + str(i + 1) + ']) :=\n\t\t\t\t\tcase\n')
		f.write('\t\t\t\t\t\t(clau = ' + str(i + 1) + '): (tag[' + str(i + 1)
				+ '] + 1) mod  4;\n\t\t\t\t\t\t(flag = TRUE): 0;'
				+ '\n\t\t\t\t\t\tTRUE: tag[' + str(i + 1)
				+ '];\n\t\t\t\t\tesac;\n')

	# Write specifications to file
	f.write('\n-----SPECS-----\n')
	# Prepare spec strings here
	spec_tag = ''
	for i in range(1, num_clause + 1):
		if i < num_clause:
			spec_tag += '(tag[' + str(i) + '] > 0) & '
		else:
			spec_tag += '(tag[' + str(i) + '] > 0));\n'
	f.write('LTLSPEC\tNAME\tltl_all_c := G! ((flag = TRUE) & ' + str(spec_tag))
	f.write('CTLSPEC\tNAME\tctl_all_c := EF ((flag = TRUE) & ' + str(spec_tag))

	# Close File
	f.close()


def print_prism(filename, cnf_list, num_clause, num_var):
	"""
	Print out the SAT network description to the prism file
	Defines a separate variable for indication of clause junctions as tag
	variable only indicates the clauses entered
		Input:
			filename: the prism filename to be used
			cnf_list: The CNF list for the SAT problem
			num_clause: The number of clauses
			num_var: The number of variables
	"""
	# Write header into file
	f = open(filename, 'w')
	now = datetime.datetime.now()
	f.write('// Date:\t' + now.strftime("%d-%m-%Y"))
	f.write('\n// SAT Problem\n// ' + str(num_clause) + ' Clauses and '
			+ str(num_var) + ' Variables: ' + str(cnf_list)
			+ '\n')

	# Write beginning of module and variable definitions
	f.write('dtmc\n\n')
	f.write(f'const numOfClauses = {num_clause};\n')
	f.write(f'const maxsum = {num_clause + 1};\n')
	f.write(f'const maxL = {num_var};\n')
	f.write('module sat\n')

	# Defining variables
	for c in range(num_clause):
		f.write("\n\t")
		for v in range(num_var):
			if (v + 1) in cnf_list[c]:
				value_to_assign = 1
			elif -(v + 1) in cnf_list[c]:
				value_to_assign = 0
			else:
				value_to_assign = 2
			f.write(f'c{c + 1}_{v + 1} : [0..2] init {value_to_assign}; ')

	f.write("\n\n\t")
	for v in range(num_var):
		f.write(f'L{v + 1} : [0..1]; ')

	f.write("\n\n\t")
	f.write('start: bool init true;\n\t')
	f.write('end: bool init false;\n\t')
	f.write('change_L: [0..maxL] init 1;\n\t')
	f.write('clause: [1..numOfClauses] init 1;\n\t')
	f.write('sum: [0..maxsum] init 0;\n')

	# Write the choose vec
	# str_temp = "[] start & change_L = 0 -> (sum' = 0) & (change_L' = mod(change_L + 1, maxL + 1));"
	# f.write('\n\t' + str_temp)

	for l in range(1, num_var, 1):
		str_temp = f"[] start & !end & change_L = {l} -> 0.5: (L{l}' = L{l}) & (change_L' = mod(change_L + 1, maxL + 1)) + 0.5: (L{l}' = mod(L{l} + 1, 2)) & (change_L' = mod(change_L + 1, maxL + 1));"
		f.write('\n\n\t' + str_temp)
	l = l + 1
	str_temp = f"[] start & !end & change_L = {l} -> 0.5: (L{l}' = L{l}) & (change_L' = mod(change_L + 1, maxL + 1)) & (start' = !start) + 0.5: (L{l}' = mod(L{l} + 1, 2)) & (change_L' = mod(change_L + 1, maxL + 1)) & (start' = !start);"
	f.write('\n\n\t' + str_temp + '\n')

	# Write the tagging process
	for c in range(1, num_clause, 1):
		str_temp = f"[] !start & clause = {c} -> (sum' = mod(sum + ((("
		f.write('\n\t' + str_temp)
		for v in range(1, num_var + 1, 1):
			f.write(f"(c{c}_{v} = L{v})")
			if v != num_var:
				f.write(" | ")
		str_temp = "))?1:0), maxsum)) & (clause' = mod(clause, numOfClauses) + 1);"
		f.write(str_temp + '\n')
	c = c + 1
	str_temp = f"[] !start & !end & clause = {c} -> (sum' = mod(sum + ((("
	f.write('\n\t' + str_temp)
	for v in range(1, num_var + 1, 1):
		f.write(f"(c{c}_{v} = L{v})")
		if v != num_var:
			f.write(" | ")
	str_temp = "))?1:0), maxsum)) & (end' = !end);"
	f.write(str_temp + '\n')

	f.write("\nendmodule\n")
	f.write(f"\nlabel	" + '"interesting"' + f'= sum = {num_clause} & start = true;\n')

	# Close File
	f.close()


def cnf_gen(sample_size, n_max, xl_ws, xl_wb, xl_fn):
	"""
	Generate random DIMACS files of 3-SAT problem samples using the cnfformula
	library from the cnfgen generator by Massimo Lauria
	Source: https://massimolauria.net/cnfgen/#org57c5319
		Input:
			sample_size: The number of 3-SAT problems to be created
			n: maximum number of variables allowed
			xl_ws: The current worksheet for saving data
		Output:
			dimacs_fn_list: list of dimacs file names
			n_m: list of (variable, clause) pairs
	"""
	# Number of variables per clause is always 3 for 3-CNF format
	dimacs_fn_list = list()
	k = 3
	n_m = list()

	# Loop through each tuple to generate DIMACS sample
	for i in range(0, sample_size):
		# n = variables, m = clauses
		n = random.randint(k, n_max)
		max_num_clauses = scipy.special.comb(n, 3) * 8
		m = random.randint(1, min(20, max_num_clauses))
		n_m.append((n, m))

		# Generate random 3-CNF for the i-th tuple in n_m
		logging.info('Generating random 3-CNF sample ' + str(i) + ' with '
					 + str(n) + ' variables and ' + str(m) + ' clauses')
		rand3CNF = randform.RandomKCNF(k, n, m)

		# Generate DIMACS file for rand3CNF
		dimacs_filename = misc.file_name_cformat('dimacs_sample_{0}')
		print('Generating ' + dimacs_filename)
		logging.info('Generating ' + dimacs_filename)
		dimacs_file = open(dimacs_filename, "w+")
		# Used internal function, by PEP 8 conventions
		rand3CNF._dimacs_dump_clauses(output=dimacs_file)
		dimacs_file.close()
		dimacs_fn_list.append(dimacs_filename)

		# Enter DIMACS filename for sample into Excel
		__ = xl_ws.cell(column=4, row=(i + 6), value=dimacs_filename)
		xl_wb.save(xl_fn)

		print('Generated ' + dimacs_filename)
		logging.info('Generated ' + dimacs_filename)

	print('All ' + str(sample_size) + ' samples have been generated')
	logging.info('All ' + str(sample_size) + ' samples have been generated')
	return dimacs_fn_list, n_m


def dimacs_to_smv(dimacs_file_list, sample_size, xl_ws, xl_wb, xl_fn):
	"""
	Function that runs through the generated DIMACS samples and generates two
	smv files for each (NoClau, Clau)
		Input:
			dimacs_file_list: List of sample DIMACS file names
			sample_size: The number of 3-SAT problems created
		Outputs:
			smv_nc_fns: List of the NoClau smv file names
			smv_c_fns: List of the Clau smv file names
	"""
	smv_nc_fns = list()
	smv_c_fns = list()
	for i in range(sample_size):
		# Read the i-th DIMACS file
		cnf, num_clause, num_var = dimacs_reader(dimacs_file_list[i])
		num_var_new, cnf = cnf_preprocessing(num_var, num_clause, cnf)
		# Enter new num_var value into excel file
		# Enter number of clauses for sample i into Excel
		__ = xl_ws.cell(column=2, row=(i + 6), value=num_clause)
		xl_wb.save(xl_fn)
		__ = xl_ws.cell(column=3, row=(i + 6), value=num_var_new)
		xl_wb.save(xl_fn)

		# Enter cnf into Excel file            
		__ = xl_ws.cell(column=6, row=(i + 6), value=repr(cnf))
		xl_wb.save(xl_fn)

		print(dimacs_file_list[i] + ' has been read')
		logging.info(dimacs_file_list[i] + ' has been read')

		# Generate smv files
		# NoClau
		noclau_name = file_name_smv(num_clause, num_var_new, True)
		logging.info('NoClau smv file name is:  ' + noclau_name)
		print_smv_noClau(noclau_name, cnf, num_clause, num_var_new)
		smv_nc_fns.append(noclau_name)

		# Enter NoClau filename into Excel file
		__ = xl_ws.cell(column=7, row=(i + 6), value=noclau_name)
		xl_wb.save(xl_fn)

		logging.info('NoClau smv file has been generated')
		# Clau
		clau_name = file_name_smv(num_clause, num_var_new, False)
		logging.info('Clau smv file name is:  ' + clau_name)
		print_smv_clau(clau_name, cnf, num_clause, num_var_new)
		smv_c_fns.append(clau_name)

		# Enter Clau filename into Excel file
		__ = xl_ws.cell(column=20, row=(i + 6), value=clau_name)
		xl_wb.save(xl_fn)

		logging.info('Clau smv file has been generated')

	return smv_nc_fns, smv_c_fns


def smv_run_specs(smv_nc_fns, smv_c_fns, sample_size, xl_ws, xl_wb, xl_fn, str_modcheker, vro='both', verbosity='0'):
	"""
	Function that runs both Clau and NoClau through NuSMV for:
		LTL specification both with and without variable re-ordering
		CTL specification both with and without variable re-ordering
	Captures the run-time of each spec on each network description
		Input:
			smv_nc_fns: List of the NoClau smv file names
			smv_c_fns: List of the Clau smv file names
			sample_size: The number of SAT problems created
			xl_ws: Excel worksheet where to save data
			str_modcheker: string containing name of model checker (NuSMV or nuXmv)
			vro: Flag for using variable re-ordering

	"""
	for i in range(sample_size):
		"""
		NoClau
		"""

		# Get cnf num_v and num_c from excel for variable re-ordering
		num_c = xl_ws.cell(row=(i + 6), column=2).value
		num_v = xl_ws.cell(row=(i + 6), column=3).value
		cnf = ast.literal_eval(xl_ws.cell(row=(i + 6), column=6).value)
		var_ord_fn = []
		# Create Variable Re-Ordering file for sample i noClau
		if vro in ['with', 'both']:
			var_ord_fn = var_order(cnf, i, num_v, num_c, 'noClau')

		# Run NoClau
		print('Running NoClau of sample ' + str(i) + '...')
		logging.info('Running NoClau of sample ' + str(i) + '...')
		output_fn = modcheck.call_nusmv_pexpect_sat(smv_nc_fns[i],
													var_ord_fn, [8, 14], i,
													xl_ws, xl_wb, xl_fn, str_modcheker, vro, verbosity=verbosity)
		# Input collected data to Excel Sheet
		nc_spec_res_col = [9, 12, 15, 18]
		if vro == 'with':
			nc_spec_res_col = [15, 18]
		result = ''
		for j in range(len(output_fn)):
			# Input spec result
			# UNSATISFIABLE -> LTL true or CTL false
			if (((j % 2 == 0) and modcheck.get_spec_res(output_fn[j]) == 'true')
					or ((j % 2 != 0) and
						modcheck.get_spec_res(output_fn[j]) == 'false')):
				result = 'UNSATISFIABLE'
			# Otherwise SATISFIABLE
			else:
				result = 'SATISFIABLE'
			__ = xl_ws.cell(column=(nc_spec_res_col[j]), row=(i + 6),
							value=result)
			xl_wb.save(xl_fn)

		"""
		Clau
		"""
		# Create Variable Re-Ordering file for sample i Clau
		var_ord_fn = None
		if vro in ['with', 'both']:
			var_ord_fn = var_order(cnf, i, num_v, num_c, 'Clau')

		# Run Clau
		print('Running Clau of sample ' + str(i) + '...')
		logging.info('Running Clau of sample ' + str(i) + '...')
		output_fn = modcheck.call_nusmv_pexpect_sat(smv_c_fns[i],
													var_ord_fn, [21, 27],
													i, xl_ws, xl_wb,
													xl_fn, str_modcheker, vro, verbosity=verbosity)

		# Input collected data to Excel Sheet
		c_spec_res_col = [22, 25, 28, 31]
		if vro == 'with':
			c_spec_res_col = [28, 31]
		for j in range(len(output_fn)):
			# Input spec result
			# UNSATISFIABLE -> LTL true or CTL false
			if (((j % 2 == 0) and modcheck.get_spec_res(output_fn[j]) == 'true')
					or ((j % 2 != 0) and
						modcheck.get_spec_res(output_fn[j]) == 'false')):
				result = 'UNSATISFIABLE'
			# Otherwise SATISFIABLE
			else:
				result = 'SATISFIABLE'
			__ = xl_ws.cell(column=(c_spec_res_col[j]), row=(i + 6),
							value=result)
			xl_wb.save(xl_fn)


def dimacs_to_prism(dimacs_file_list, sample_size, xl_ws, xl_wb, xl_fn):
	"""
	Function that runs through the generated DIMACS samples and generates prism files
		Input:
			dimacs_file_list: List of sample DIMACS file names
			sample_size: The number of SAT problems created
		Outputs:
			prism_fns: List of the prism file names
	"""
	prism_fns = list()
	for i in range(sample_size):
		# Read the i-th DIMACS file
		cnf, num_clause, num_var = dimacs_reader(dimacs_file_list[i])
		num_var_new, cnf = cnf_preprocessing(num_var, num_clause, cnf)
		# Enter new num_var value into excel file
		__ = xl_ws.cell(column=3, row=(i + 6), value=num_var_new)
		xl_wb.save(xl_fn)

		# Enter cnf into Excel file
		__ = xl_ws.cell(column=6, row=(i + 6), value=repr(cnf))
		xl_wb.save(xl_fn)

		print(dimacs_file_list[i] + ' has been read')
		logging.info(dimacs_file_list[i] + ' has been read')

		# Generate prism files
		file_name = file_name_prism(num_clause, num_var_new, True)
		logging.info('prism file name is:  ' + file_name)
		print_prism(file_name, cnf, num_clause, num_var_new)
		prism_fns.append(file_name)
		print_prism_spec('spec_sat.pctl', num_clause, num_var)

		# Enter NoClau filename into Excel file
		__ = xl_ws.cell(column=7, row=(i + 6), value=file_name)
		xl_wb.save(xl_fn)

		logging.info('NoClau prism file has been generated')

	return prism_fns


def print_prism_spec(filename, num_c, num_v):
	"""
	Print out the ExCov spec for prism file
		Input:
			filename: name of the spec file
	"""

	# write 2 specifications: 1. check if exist EC. 2. what is the probability to get the EC.
	f = open(filename, 'w')
	f.write('const int k;\n\n')
	max_path = 2 + num_v + num_c
	f.write(f'P>0 [ F<={max_path} sum=numOfClauses ]\n')
	f.write(f'P=? [ F<={max_path} sum=numOfClauses ]\n')
	f.close()


def prism_run_specs(prism_fns, sample_size, xl_ws, xl_wb, xl_fn, str_modcheker):
	"""
	Function that runs through prism files
	Captures the run-time of each spec on each network description
		Input:
			prism_fns: List of the prism file names
			sample_size: The number of 3-SAT problems created
			xl_ws: Excel worksheet where to save data
	"""
	for i in range(sample_size):

		# Run NoClau
		print('Running NoClau of sample ' + str(i) + '...')
		logging.info('Running NoClau of sample ' + str(i) + '...')
		output_fn, output_rt = modcheck.call_prism_pexpect_sat(prism_fns[i], str_modcheker)
		# Input collected data to Excel Sheet

		# Parse output files:
		if output_rt[0] != 'Out of memory':
			exist_res = open(f'{output_fn[0]}', "r").readlines()[1][:-1]
			logging.info('Exist Result: ' + exist_res)
			prob_res = open(f'{output_fn[1]}', "r").readlines()[1][:-1]
			logging.info('Prob Result: ' + prob_res)

			logging.info('Saving data in Excel')
			__ = xl_ws.cell(column=9, row=(i + 6), value=exist_res)
			__ = xl_ws.cell(column=10, row=(i + 6), value=prob_res)
		__ = xl_ws.cell(column=11, row=(i + 6), value=output_rt[0])
		xl_wb.save(xl_fn)


def mini_sat_solver(in_files, sample_size, xl_ws, xl_wb, xl_fn):
	"""
	Run MiniSat SAT Solver on DIMACS samples
		Input:
			in_files: List of DIMACS sample file names
			sample_size: The number of 3-SAT problems created
		Output:
			out_res: List of output results
	"""
	out_res = list()
	res_pat = re.compile("^(SATISFIABLE|UNSATISFIABLE)")
	for i in range(sample_size):
		# Define output file name
		logging.info('Opening process: MiniSat SAT Solver')
		child = pexpect.spawn('minisat', args=[in_files[i]],
							  logfile=sys.stdout, encoding='utf-8',
							  timeout=None)
		# Read output of child
		for line in child:
			logging.info(line)
			res = re.match(res_pat, line)
			if res:
				out_res.append(res.groups()[0])
				__ = xl_ws.cell(column=5, row=(i + 6), value=res.groups()[0])
				xl_wb.save(xl_fn)
				break
		child.close()

	return out_res


def copy_range(start_col, start_row, end_col, end_row, sheet):
	rangeSelected = []
	# Loops through selected Rows
	for i in range(start_row, end_row + 1, 1):
		# Appends the row to a RowSelected list
		rowSelected = []
		for j in range(start_col, end_col + 1, 1):
			rowSelected.append(sheet.cell(row=i, column=j).value)
		# Adds the RowSelected List and nests inside the rangeSelected
		rangeSelected.append(rowSelected)
	return rangeSelected


def cnf_preprocessing(num_v, num_c, cnf):
	"""
	Clears un-used variables from the CNFs
		Inputs:
			num_v: number of variables
			num_c: number of clauses
			cnf: cnf list of clauses and their variables
		Output:
			num_v: new number of variables
			cnf: new cnf formula with no un-used variables
	"""
	all_vars = list(range(1, (num_v + 1)))
	# Find all used variables
	used_vars = list()
	for c in cnf:
		for v in c:
			if abs(v) not in used_vars:
				used_vars.append(abs(v))
	used_vars.sort()
	# Find all not used variables in order to re-map used ones
	nused_vars = list(set(all_vars).difference(used_vars))

	while nused_vars:
		# Get last variable used and first un-used
		first_nused = nused_vars.pop(0)
		last_used = used_vars[-1]
		# Run through CNF and re-map to first un-used variable
		# ONLY WHEN first_nused < last_used
		if first_nused < last_used:
			for i, c in enumerate(cnf):
				for j, v in enumerate(c):
					if abs(v) == last_used:
						cnf[i][j] = int(math.copysign(first_nused, v))
						used_vars.pop(-1)
						used_vars.append(first_nused)
						used_vars.sort()
	return len(used_vars), cnf


def var_order(cnf, sample_id, num_v, num_c, net_type):
	"""
	Build a new variable ordering where the tags appear in by the order of the
	smallest variable they contain.
	This is an attempt to decrease the NuSMV run-time.
		Inputs:
			cnf: cnf list of clauses and their variables
			sample_id: sample being looked at
			num_v: number of variables
			num_c: number of clauses
			net_type: type of network Clau or NoClau
		Output:
			var_order_fn: name of the file hollding the new variable ordering
	"""
	var_order_fn = misc.file_name_cformat('var_ord_sample_' + '_{0}' + str(sample_id)
										  + '_' + net_type)

	# Find index of MSB for defining vari and clau (binary value)
	max_v_bit = math.floor(math.log2(num_v))
	max_c_bit = math.floor(math.log2(num_c))

	# Find order of tags in reference to variables in the cnf
	tag_order = list()
	v = 1
	while len(tag_order) < num_c:
		for i, c in enumerate(cnf):
			if ((v in c) or ((-1 * v) in c)) and ((i + 1) not in tag_order):
				tag_order.append(i + 1)
		v += 1

	f = open(var_order_fn, 'w')

	# Junction
	f.write('junction.0\n')

	# Directions
	f.write('dir.1\ndir.0\n')

	# Variable bits
	for i in range(0, max_v_bit + 1):
		f.write('vari.' + str(max_v_bit - i) + '\n')

	# Clause bits (only in Clau network)
	if net_type == 'Clau':
		for i in range(0, max_c_bit + 1):
			f.write('clau.' + str(max_c_bit - i) + '\n')

	# Varval
	f.write('varval\n')

	for t in tag_order:
		f.write('tag[' + str(t) + '].1\n')
		f.write('tag[' + str(t) + '].0\n')

	# Flag
	f.write('flag')

	# Close File
	f.close()

	return var_order_fn


def cmd_fn_to_dimacs_fns(input_dir, filename):
	"""
	Read input file that contains a list of dimacs file names for SAT parsing
		Inputs:
			input_dir: input file directory for opening dimacs files
			filename: name of file containing list of dimacs file names to be looked at (all in Input directory)
		Output:
			dimacs_fns: list of dimacs file names to be parsed
	"""
	dimacs_fns = []
	f = open(filename, 'r')
	for line in f:
		dimacs_fns.append(input_dir + line.rstrip())
	f.close()

	return dimacs_fns
