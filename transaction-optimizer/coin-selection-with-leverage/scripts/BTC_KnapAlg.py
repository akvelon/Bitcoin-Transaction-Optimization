
import numpy as np
import time
from pulp import *

from BTC_Utils import *

# Constants
tx_metadata_bytes = 10
input_bytes = 148
output_bytes = 34
change_bytes = 34


def BTC_Knapsack(utxos, pay_reqs, time_limit=15, solver='COIN', print_details = False, fee_per_byte = 22, oneBTC = 8582):
    
    '''
    Parameters:

    utxos: (list) list of UTXOs in UTXO pool (usually given as a NumPy array as in the notebooks)
    pay_reqs: (list) payment requests to process
    time_limit: (int) time limit (in seconds) for PuLP to solve optimization problem
    solver: (str) solver to use when utilizing PuLP
    print_details: (bool) If True, will print out details of the solution (see below)
    fee_per_byte: (int) the fee-per-byte rate to use (in Satoshi)
    oneBTC: (float) the value of one BTC in USD
    
    '''


    # Constants
    num_utxos = len(utxos)
    num_pay_reqs = len(pay_reqs)

    dust_thres = (input_bytes + output_bytes)*fee_per_byte
    makeChangeThres = (output_bytes)*fee_per_byte
    
    # optimal number of utxos needed for given pay_reqs

    opt_num_inputs = None
    utxos_sorted = sorted(utxos, reverse=True)

    for k in range(len(utxos_sorted)):
        if (np.sum(utxos_sorted[:k]) - np.sum(pay_reqs)) > 0:
            opt_num_inputs = k
            break
    
    # PuLP code
    # Define problem with constraints

    # Decision variables
    x = [ pulp.LpVariable("x_" + str(k), cat="Binary") for k in range(num_utxos) ]


    # Shorthands
    transaction_size = tx_metadata_bytes + input_bytes*opt_num_inputs + output_bytes*num_pay_reqs
    min_transaction_fee = transaction_size*fee_per_byte
    
    total_input = LpAffineExpression([(x[i], utxos[i]) for i in range(num_utxos)])
    overpayment = total_input - np.sum(pay_reqs) - min_transaction_fee
    total_cost = overpayment + min_transaction_fee

    # Define problem
    prob = pulp.LpProblem("BTC_KnapSack", pulp.LpMinimize)

    # Objective function
    obj_fcn = overpayment
    prob += obj_fcn

    # Constraints

    # opt_num_inputs constraint
    opt_num_inputs_cons = lpSum(x) == opt_num_inputs
    prob += opt_num_inputs_cons

    # Valid transaction
    valid_trans_cons = overpayment >= 0
    prob += valid_trans_cons

    # makeChangeThres Threshold
    makeChangeThres_cons = LpAffineExpression([(x[i], utxos[i]) for i in range(num_utxos)]) - np.sum(pay_reqs) - min_transaction_fee <= makeChangeThres
    prob += makeChangeThres_cons
    
    # Solve the problem
    start_time = time.time()
    
    if solver == 'COIN':
        prob.solve(pulp.PULP_CBC_CMD(maxSeconds=time_limit))
    else:
        prob.solve(pulp.GLPK_CMD(options=["--tmlim", str(time_limit)]))
    

    print("Problem Status: " + str(pulp.LpStatus[prob.status]))
    print("The problem took " + str(time.time() - start_time) + " seconds to solve")
    
    
    used_utxos = [(v, v.varValue, utxos[int(str(v)[2:])]) for v in prob.variables() if v.varValue==1]
    unused_utxos = [ utxos[int(str(v)[2:])] for v in prob.variables() if v.varValue == 0 ]


    # Manual check if solution is feasible
    opt_inputs_flag = len(used_utxos) == opt_num_inputs
    suf_funds_flag = pulp.value(total_input) - np.sum(pay_reqs) - min_transaction_fee >= 0
    under_dust_flag = pulp.value(total_input) - np.sum(pay_reqs) - min_transaction_fee <= makeChangeThres
    valid_trans_flag = opt_inputs_flag*suf_funds_flag*under_dust_flag
    fallback_soln_flag = False

    if valid_trans_flag == False:
        # Fall back to backup soln with max change
        big_utxos = utxos_sorted[:opt_num_inputs]
        big_input = np.sum(big_utxos)
        max_change = big_input - np.sum(pay_reqs) - min_transaction_fee
        fallback_soln_flag = True


    print("Sucess: " + str(valid_trans_flag))


    if print_details == True:
        print("--------------------------------------------------------------------------------")
        print("--------------------------------------------------------------------------------")

        print("Transaction Details:")
        print("UTXOs used in Transaction:")
        for v,_,val in used_utxos:
            print(str(v) + ": Value = $" + str(Satoshi_to_USD(val, oneBTC)))
        print("Input Total: $" + str(Satoshi_to_USD(pulp.value(total_input), oneBTC)))
        print("Payment Requests Processed:")
        for idx, val in enumerate(pay_reqs):
            print("p_" + str(idx) + ": Value = $" + str(Satoshi_to_USD(val, oneBTC)))
        print("Output Total: $" + str(Satoshi_to_USD(np.sum(pay_reqs), oneBTC)))
        print("Transaction Fee: $" + str(Satoshi_to_USD(pulp.value(min_transaction_fee), oneBTC)))
        print("Overpayment: $" + str(Satoshi_to_USD(pulp.value(overpayment), oneBTC)))
        print("Optimal Number of Inputs: " + str(opt_num_inputs))

        print("--------------------------------------------------------------------------------")
        print("--------------------------------------------------------------------------------")



    if print_details == True:
        print("Manual Feasibility Check:")
        print("Optimal Number of Inputs Used: " + str(opt_inputs_flag))
        print("Sufficient Funds: " + str(suf_funds_flag))
        print("Overpayment Less than Dust: " + str(under_dust_flag))
        print("Valid Transaction: " + str(valid_trans_flag))
        print("Fall Back Solution: " + str(fallback_soln_flag))


    alg_report = {}
    alg_report['dust_thres'] = Satoshi_to_USD(dust_thres, oneBTC)
    alg_report['makeChangeThres'] = Satoshi_to_USD(makeChangeThres, oneBTC)

    if fallback_soln_flag:
        alg_report['overpayment'] = makeChangeThres
        alg_report['valid_transaction'] = valid_trans_flag
        alg_report['used_utxos_indices'] = [ k for k in range(opt_num_inputs)]
        alg_report['used_utxos_values'] = utxos_sorted[:opt_num_inputs]
        alg_report['fallback_solution'] = fallback_soln_flag
        alg_report['Success'] = valid_trans_flag
        alg_report['unused_utxos'] = utxos
    
    else:
        alg_report['overpayment'] = Satoshi_to_USD(pulp.value(overpayment), oneBTC)
        alg_report['valid_transaction'] = valid_trans_flag
        alg_report['used_utxos_indices'] = [ int(str(v)[2:]) for v in prob.variables() if v.varValue == 1]
        alg_report['used_utxos_values'] = [ utxos[int(str(v)[2:])] for v in prob.variables() if v.varValue == 1]
        alg_report['fallback_solution'] = fallback_soln_flag
        alg_report['Success'] = valid_trans_flag
        alg_report['unused_utxos'] = unused_utxos
        alg_report['total_cost'] = Satoshi_to_USD(pulp.value(total_cost), oneBTC)
    
    return alg_report





