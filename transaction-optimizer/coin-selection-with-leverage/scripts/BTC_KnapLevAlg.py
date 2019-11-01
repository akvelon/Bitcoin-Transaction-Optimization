import numpy as np
import time
import random, math
import datetime
from pulp import *

from BTC_Utils import *

# Constants
tx_metadata_bytes = 10
input_bytes = 148
output_bytes = 34
change_bytes = 34


def BTC_KnapLevAlg(utxos, high_urgency, pay_reqs, time_limit=15, solver='COIN' \
				,print_details = False, fee_per_byte = 22, oneBTC = 8582, t1lb = 10, t1ub = 10, boost_factor = 1):
	
	'''
	Parameters:

	utxos: (list) list of UTXOs in UTXO pool (usually given as a NumPy array as in the notebooks)
	high_urgency: (list) list of payment requests for which the first transaction will process
	pay_reqs: (list) payment request pool
	time_limit: (int) time limit (in seconds) for PuLP to solve optimization problem
	solver: (str) solver to use when utilizing PuLP
	print_details: (bool) If True, will print out details of the solution (see below)
	fee_per_byte: (int) the fee-per-byte rate to use (in Satoshi)
	oneBTC: (float) the value of one BTC in USD
	t1lb = (int) lower bound on number of pay reqs second transaction will process (Note: in code below transactions are labeled by 0 and 1 rather than 1 and 2)
	t1ub = (int) upper bound on number of pay reqs second transaction will process (Note: in code below transactions are labeled by 0 and 1 rather than 1 and 2)
	boost_factor = (float) value between 0 and 1, lower value enforces lower overpayment for second transaction. This is the beta value from the paper.

	'''


	# Constants
	num_utxos = len(utxos)
	num_pay_reqs = len(pay_reqs)
	num_high_urgency = len(high_urgency)

	dust_thres = (input_bytes + output_bytes)*fee_per_byte
	makeChangeThres = (output_bytes)*fee_per_byte*boost_factor

	# Find optimal number of UTXOs to process high_urgency requests

	utxos_sorted = sorted(utxos, reverse=True)


	opt_num_inputs0 = None
	for k in range(num_utxos):
		if (np.sum(utxos_sorted[:k]) - np.sum(high_urgency)) > 0:
			opt_num_inputs0 = k
			break


	# PuLP code
	# Define problem and decision variables

	prob = pulp.LpProblem("BTC_KnapLevAlg", pulp.LpMinimize)

	x = [None, None]

	x[0] = [ pulp.LpVariable("x0_" + str(k), cat="Binary") for k in range(num_utxos) ]
	x[1] = [ pulp.LpVariable("x1_" + str(k), cat="Binary") for k in range(num_utxos) ]
	y = [pulp.LpVariable("y_" + str(k), cat="Binary") for k in range(num_pay_reqs)]


	# Objective function and constraints

	# Shorthands
	trans0_tot_input = LpAffineExpression([(x[0][i], utxos[i]) for i in range(num_utxos)])
	trans1_tot_input_woChange = LpAffineExpression([(x[1][i], utxos[i]) for i in range(num_utxos)])

	high_urg_tot = np.sum(high_urgency)

	trans1_tot_output = LpAffineExpression([(y[i], pay_reqs[i]) for i in range(num_pay_reqs)])

	trans0_size = tx_metadata_bytes + input_bytes*opt_num_inputs0 + output_bytes*num_high_urgency + change_bytes
	trans1_size = tx_metadata_bytes + input_bytes*lpSum(x[1]) + input_bytes + output_bytes*lpSum(y)

	trans0_min_fee = trans0_size*fee_per_byte
	trans1_min_fee = trans1_size*fee_per_byte

	trans0_ovr_pay = trans0_tot_input - high_urg_tot - trans0_min_fee
	trans1_change_target =  trans1_tot_output + trans1_min_fee - trans1_tot_input_woChange
	final_overpayment = trans0_ovr_pay - trans1_change_target
	


	# Objective Function
	obj_fcn = lpSum(x[1])
	prob += obj_fcn

	obj_fcn_plus1 = obj_fcn + 1


	#Constraints

	# Use a utxo at most once
	for j in range(num_utxos):
		use_utxo_once_cons = x[0][j] + x[1][j] <= 1
		prob += use_utxo_once_cons

	# optimal number of inputs for transaction 0
	trans0_inputs_cons = lpSum(x[0]) == opt_num_inputs0
	prob += trans0_inputs_cons

	# fixed number of payrequests per transaction (re-visit and adjust the number 10)
	num_pay_req_cons_lb = lpSum(y) >= t1lb # used to be num_pay_reqs_per_transaction
	num_pay_req_cons_ub = lpSum(y) <= t1ub # used to be 2*num_pay_reqs_per_transaction
	prob += num_pay_req_cons_lb
	prob += num_pay_req_cons_ub

	# Make trans0 valid with change
	trans0_valid_cons = trans0_ovr_pay >= 0
	prob += trans0_valid_cons

	# Make trans1 "Need a change UTXO"
	trans1_need_change_utxo_cons = trans1_change_target >= 0
	prob += trans1_need_change_utxo_cons

	# Enforce change needed for trans1
	change_needed_cons_lb = trans0_ovr_pay >= trans1_change_target
	change_needed_cons_ub = trans0_ovr_pay <= trans1_change_target + makeChangeThres
	prob += change_needed_cons_lb
	prob += change_needed_cons_ub


	# Solve the problem
	start_time = time.time()

	if solver == 'COIN':
		prob.solve(pulp.PULP_CBC_CMD(maxSeconds=time_limit))
	else:
		prob.solve(pulp.GLPK_CMD(options=["--tmlim", str(time_limit)]))


	print("Problem Status: " + pulp.LpStatus[prob.status])
	print("The problem took " + str(time.time() - start_time) + " seconds to solve")



	pay_reqs_processed = [ pay_reqs[int(str(v)[2:])] for v in prob.variables() if v.varValue==1 and  str(v)[0] == 'y']
	pay_reqs_unprocessed = [ pay_reqs[int(str(v)[2:])] for v in prob.variables() if v.varValue==0 and  str(v)[0] == 'y']



	trans0_utxos = [(v, v.varValue, utxos[int(str(v)[3:])]) for v in prob.variables() if v.varValue==1 and str(v)[1] == '0' ]
	trans0_utxos_only = [ utxos[int(str(v)[3:])] for v in prob.variables() if v.varValue==1 and str(v)[1] == '0' ]

	trans1_utxos = [(v, v.varValue, utxos[int(str(v)[3:])]) for v in prob.variables() if v.varValue==1 and str(v)[1] == '1' ]
	trans1_utxos_only = [ utxos[int(str(v)[3:])] for v in prob.variables() if v.varValue==1 and str(v)[1] == '1' ]

	unused_utxos = np.delete(utxos, [ np.where(utxos == u)[0][0] for u in trans0_utxos_only ])
	unused_utxos = np.delete(unused_utxos, [ np.where(unused_utxos == u)[0][0] for u in trans1_utxos_only ])

	pay_reqs_processed_extended = [(v, v.varValue, pay_reqs[int(str(v)[2:])]) for v in prob.variables() if v.varValue==1 and str(v)[0] == 'y' ]


	# Check if optimal number of inputs are used in transaction 1
	opt_num_inputs1 = None

	utxos_rem_after_trans0 = sorted([ utxos[int(str(v)[3:])] for v in prob.variables() if v.varValue == 0 and (str(v)[1] in ['0', '1']) ], reverse=True)

	for k in range(len(utxos_rem_after_trans0)):
		if (np.sum(utxos_rem_after_trans0[:k]) - np.sum(pay_reqs_processed)) > 0:
			opt_num_inputs1 = k
			break



	trans0_valid_flag = pulp.value(trans0_ovr_pay) >= 0
	trans1_valid_flag = pulp.value(final_overpayment) >= 0
	small_final_overpayment_flag = pulp.value(final_overpayment) <= makeChangeThres


	trans0_full_utxos_only_flag = np.sum([v[2] for v in trans0_utxos]) == pulp.value(trans0_tot_input)
	trans1_full_utxos_only_flag = np.sum([v[2] for v in trans1_utxos]) == pulp.value(trans1_tot_input_woChange)
	pay_reqs_full_only_flag = np.sum(v[2] for v in pay_reqs_processed_extended) == pulp.value(trans1_tot_output)

	trans1_opt_num_inputs_flag = pulp.value(obj_fcn_plus1) == opt_num_inputs1



	success_flag = trans0_valid_flag*trans1_valid_flag*small_final_overpayment_flag*trans0_full_utxos_only_flag \
						*trans1_full_utxos_only_flag*pay_reqs_full_only_flag*trans1_opt_num_inputs_flag


	print("Success: " + str(success_flag))


	if print_details == True:
		print("--------------------------------------------------------------------------------")
		print("--------------------------------------------------------------------------------")

		print("Transaction 0 Details:")
		print("UTXOs used in Transaction 0:")
		for v, _, val in trans0_utxos:
			print(str(v) + ": Value = $" + str(Satoshi_to_USD(val, oneBTC)))
		print("Input Total: $" + str(Satoshi_to_USD(pulp.value(trans0_tot_input), oneBTC)))
		print("High Urgency Pay Requests Processed:")
		for num, val in enumerate(high_urgency):
			print(str(num) + ": Value = $" + str(Satoshi_to_USD(val, oneBTC)))
		print("Output Total (High Urgency): $" + str(Satoshi_to_USD(high_urg_tot, oneBTC)))
		print("Transaction Fee: $" + str(Satoshi_to_USD(pulp.value(trans0_min_fee), oneBTC)))
		print("Maximum Change Available: $" + str(Satoshi_to_USD(pulp.value(trans0_ovr_pay), oneBTC)))
		print("Optimal Number of Inputs: " + str(opt_num_inputs0))

		print("--------------------------------------------------------------------------------")
		print("--------------------------------------------------------------------------------")

		print("Transaction 1 Details:")
		print("UTXOs used in Transaction 1:")
		for v, _, val in trans1_utxos:
			print(str(v) + ": Value = $" + str(Satoshi_to_USD(val, oneBTC)))
		print("Input Total: $" + str(Satoshi_to_USD(pulp.value(trans1_tot_input_woChange), oneBTC)))
		print("Pay Requests Processed:")
		for v, _, val in pay_reqs_processed_extended:
			print(str(v) + ": Value = $" + str(Satoshi_to_USD(val, oneBTC)))
		print("Optimal Number of Inputs: " + str(opt_num_inputs1))
		print("Number of Inputs Used: " + str(pulp.value(obj_fcn_plus1)))	
		print("Output Total: $" + str(Satoshi_to_USD(pulp.value(trans1_tot_output), oneBTC)))
		print("Transaction Fee: $" + str(Satoshi_to_USD(pulp.value(trans1_min_fee), oneBTC)))
		print("Change UTXO: $" + str(Satoshi_to_USD(pulp.value(trans1_change_target), oneBTC)))
		print("Transaction 0 Overpayment: $" + str(Satoshi_to_USD(pulp.value(final_overpayment), oneBTC)))




	alg_report = {}

	alg_report['trans0_full_utxos_only'] = np.sum([v[2] for v in trans0_utxos]) == pulp.value(trans0_tot_input)
	alg_report['trans1_full_utxos_only'] = np.sum([v[2] for v in trans1_utxos]) == pulp.value(trans1_tot_input_woChange)
	alg_report['pay_reqs_full_only'] = np.sum(v[2] for v in pay_reqs_processed_extended) == pulp.value(trans1_tot_output)
	alg_report['overpayment'] = Satoshi_to_USD(pulp.value(final_overpayment), oneBTC) + Satoshi_to_USD(output_bytes*fee_per_byte, oneBTC)
	alg_report['trans0_total_cost'] = Satoshi_to_USD(trans0_size*fee_per_byte, oneBTC)
	alg_report['trans1_total_cost'] = Satoshi_to_USD(pulp.value(trans1_size)*fee_per_byte, oneBTC) + Satoshi_to_USD(pulp.value(final_overpayment), oneBTC)
	alg_report['total_cost'] = alg_report['trans0_total_cost'] + alg_report['trans1_total_cost']
	alg_report['trans0_utxos'] = trans0_utxos
	alg_report['trans1_utxos'] = trans1_utxos
	alg_report['trans0_valid_flag'] = trans0_valid_flag
	alg_report['trans1_valid_flag'] = trans1_valid_flag
	alg_report['small_final_overpayment_flag'] = small_final_overpayment_flag
	alg_report['Success'] = success_flag 
	alg_report['pay_reqs_processed'] = pay_reqs_processed
	alg_report['pay_reqs_unprocessed'] = pay_reqs_unprocessed
	alg_report['unused_utxos'] = unused_utxos


	return alg_report
