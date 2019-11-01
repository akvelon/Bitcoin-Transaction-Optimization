# Run simulation file

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import random, math, time, os, datetime

from BTC_KnapAlg import *
from BTC_KnapLevAlg import *
from BTC_KnapFallBack import *
from BTC_Utils import *

def BTC_Simulation_KnapLev(utxos, pay_req, num_high_urg=10, leverage=False, print_details=False, solver='COIN', \
					time_limit_knap=10, time_limit_lev=10, iterations=10, fee_per_byte = 22, oneBTC = 8582, lev_t1lb = 10, lev_t1ub = 10, \
					lev_boost_factor = 1):

	'''
	Parameters:

	utxos: (list) list of UTXOs in UTXO pool (usually given as a NumPy array as in the notebooks)
	pay_reqs: (list) payment request pool
	num_high_urg: (int) number of payments requests which are guranteed to be proccessed. Will take the first num_high_urg payment requests from pay_req
	leverage: (bool) True to use leverage technique
	print_details: (bool) If True, will print out details of the solution
	solver: (str) solver to use when utilizing PuLP
	time_limit_knap: (int) time limit (in seconds) for PuLP to solve BTC_KnapAlg optimization problem
	time_limit_lev: (int) time limit (in seconds) for PuLP to solve BTC_KnapLevAlg optimization problem
	iterations: (int) number of iterations to perform simulations
	fee_per_byte: (int) the fee-per-byte rate to use (in Satoshi)
	oneBTC: (float) the value of one BTC in USD
	lev_t1lb = (int) (for use of leverage technique) lower bound on number of pay reqs second transaction will process (Note: in code below transactions are labeled by 0 and 1 rather than 1 and 2)
	lev_t1ub = (int) (for use of leverage technique) upper bound on number of pay reqs second transaction will process (Note: in code below transactions are labeled by 0 and 1 rather than 1 and 2)
	lev_boost_factor = (float) (for use of leverage technique) value between 0 and 1, lower value enforces lower overpayment for second transaction. This is the beta value from the paper.

	'''

	startTime = time.time()

	# Constants
	num_utxos = len(utxos)
	num_pay_req = len(pay_req)


	# Setup
	iteration = 0

	running_tot_cost = 0

	tot_costs = []

	running_overpayment = 0
	overpayments = []

	num_knap_solns = 0
	num_lev_solns = 0
	num_fallback_solns = 0

	all_reps = {}

	# Begin simulations
	while len(pay_req) > 0 and iteration < iterations:
		iteration += 1
		print("/////////////////////////////////////////////////////////////////////")
		print("/////////////////////////////////////////////////////////////////////")
		print("Iteration : " + str(iteration))
		print("UTXO Pool Size: " + str(len(utxos)))
		print("Pay Requests Left: " + str(len(pay_req)))
		
		print("/////////////////////////////////////////////////////////////////////")
		print("Trying Knapsack Solution:")
		high_urg = pay_req[:num_high_urg]
		alg_report = BTC_Knapsack(utxos, high_urg, time_limit=time_limit_knap, print_details=print_details, solver=solver, \
									fee_per_byte = fee_per_byte, oneBTC = oneBTC)

		if alg_report['Success'] == True:
			num_knap_solns += 1
			all_reps[iteration] = alg_report
			print("/////////////////////////////////////////////////////////////////////")
			print("Using Knapsack Solution")
			print("/////////////////////////////////////////////////////////////////////")
			utxos = alg_report['unused_utxos'] # Update Utxo pool
			pay_req = pay_req[num_high_urg:] # Drop processed pay requests from pay request pool

			# Add code to keep track of overpayment and total cost
			running_tot_cost += alg_report['total_cost']
			tot_costs.append(alg_report['total_cost'])

			running_overpayment += alg_report['overpayment']
			overpayments.append(alg_report['overpayment'])

		elif leverage:
			print("/////////////////////////////////////////////////////////////////////")
			print("Trying Leverage Solution:")
			alg_report = BTC_KnapLevAlg(utxos, high_urg, pay_req[num_high_urg:], print_details=print_details, time_limit=time_limit_lev, solver=solver, \
				num_pay_reqs_per_transaction = num_high_urg, fee_per_byte = fee_per_byte, oneBTC = oneBTC, t1lb = lev_t1lb, t1ub = lev_t1ub, \
				boost_factor = lev_boost_factor)

			if alg_report['Success'] == True:
				num_lev_solns += 1
				all_reps[iteration] = alg_report
				print("/////////////////////////////////////////////////////////////////////")
				print("Using Leverage Solution")
				print("/////////////////////////////////////////////////////////////////////")
				utxos = alg_report['unused_utxos'] # Update UTXO pool
				pay_req = alg_report['pay_reqs_unprocessed'] # Update pay request pool

				# Add code to keep track of overpayment and total cost
				running_tot_cost += alg_report['total_cost']
				tot_costs.append(alg_report['total_cost'])

				running_overpayment += alg_report['overpayment']
				overpayments.append(alg_report['overpayment'])

			else: # Using Fallback Solution
				num_fallback_solns += 1
				print("/////////////////////////////////////////////////////////////////////")
				print("Using Fallback Solution")
				print("/////////////////////////////////////////////////////////////////////")
				alg_report = BTC_KnapFallBack(utxos, high_urg, fee_per_byte = fee_per_byte, oneBTC = oneBTC)
				all_reps[iteration] = alg_report

				utxos = alg_report['unused_utxos']
				pay_req = pay_req[num_high_urg:]

				# Add code to keep track of overpayment and total cost
				running_tot_cost += alg_report['total_cost']
				tot_costs.append(alg_report['total_cost'])

				running_overpayment += alg_report['overpayment']
				overpayments.append(alg_report['overpayment'])


				print('Success')
				print("/////////////////////////////////////////////////////////////////////")
				print("/////////////////////////////////////////////////////////////////////")

		else: # Using Fallback solution
			num_fallback_solns += 1
			print("/////////////////////////////////////////////////////////////////////")
			print("Using Fallback Solution")
			print("/////////////////////////////////////////////////////////////////////")
			alg_report = BTC_KnapFallBack(utxos, high_urg, fee_per_byte = fee_per_byte, oneBTC = oneBTC)
			all_reps[iteration] = alg_report

			utxos = alg_report['unused_utxos']
			pay_req = pay_req[num_high_urg:]

			# Add code to keep track of overpayment and total cost
			running_tot_cost += alg_report['total_cost']
			tot_costs.append(alg_report['total_cost'])

			running_overpayment += alg_report['overpayment']
			overpayments.append(alg_report['overpayment'])


			print('Success')
			print("/////////////////////////////////////////////////////////////////////")
			print("/////////////////////////////////////////////////////////////////////")



		

	# Summary Statistics
	print("/////////////////////////////////////////////////////////////////////")
	print("/////////////////////////////////////////////////////////////////////")
	print("/////////////////////////////////////////////////////////////////////")
	print("Summary Statistics:")
	print("/////////////////////////////////////////////////////////////////////")

	num_utxos_used = num_utxos - len(utxos)
	num_pay_req_processed = num_pay_req - len(pay_req)

	print("Number of UTXOs Used: " + str(num_utxos_used))
	print("Number of Pay Requests Processed: " + str(num_pay_req_processed))

	cost_per_pay_req = running_tot_cost/(num_pay_req_processed)
	print("Cost Per Pay Request Processed: $" + str(cost_per_pay_req))
	print("Total Cost to Process Payments: $" + str(running_tot_cost))

	print('# of Knapsack Successful Solutions: ' + str(num_knap_solns))
	print('# of Leverage Successful Solutions: ' + str(num_lev_solns))
	print('# of Fallback Successful Solutions: ' + str(num_fallback_solns))

	endTime = time.time()

	fullSummary = {}
	fullSummary['costPerPayRequest'] = cost_per_pay_req
	fullSummary['totalCost'] = running_tot_cost
	fullSummary['numUTXOsUsed'] = num_utxos_used
	fullSummary['numPayRequestsProcessed'] = num_pay_req_processed
	fullSummary['numKnapsackSolns'] = num_knap_solns
	fullSummary['numLeverageSolns'] = num_lev_solns
	fullSummary['numFallbackSolns'] = num_fallback_solns
	fullSummary['feePerByte'] = fee_per_byte
	fullSummary['oneBTC'] = oneBTC
	fullSummary['executionTime'] = endTime - startTime
	fullSummary['boostFactor'] = lev_boost_factor
	fullSummary['numPayRequestsPerTX'] = num_high_urg
	fullSummary['Iterations'] = iterations


	return all_reps, fullSummary