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



def BTC_KnapFallBack(utxos, pay_req, fee_per_byte = 22, oneBTC = 8582):

    '''
    Parameters:

    utxos: (list) list of UTXOs in UTXO pool (usually given as a NumPy array as in the notebooks)
    pay_reqs: (list) payment requests to process
    fee_per_byte: (int) the fee-per-byte rate to use (in Satoshi)
    oneBTC: (float) the value of one BTC in USD
    
    '''

	# Constant
	dust_thres = (input_bytes + output_bytes)*fee_per_byte


	sorted_utxos = sorted(utxos, reverse=True)

	# Determine optimal number of UTXOs to use.
	opt_num_inputs = None
	for k in range(len(sorted_utxos)):
		if (np.sum(sorted_utxos[:k]) > np.sum(pay_req)):
			opt_num_inputs = k
			break



	used_utxos = sorted_utxos[:opt_num_inputs]

	rem_utxos = np.delete(utxos, [np.where(utxos == u)[0][0] for u in sorted_utxos[:opt_num_inputs]])

	transaction_fee = (tx_metadata_bytes+input_bytes*opt_num_inputs+output_bytes*len(pay_req)+output_bytes)*fee_per_byte

	change = np.sum(sorted_utxos[:k]) - np.sum(pay_req) - transaction_fee

	alg_report = {}

	alg_report['used_utxos'] = used_utxos
	alg_report['unused_utxos'] = rem_utxos
	alg_report['transaction_fee'] = Satoshi_to_USD(transaction_fee, oneBTC)
	alg_report['change'] = Satoshi_to_USD(change, oneBTC)
	alg_report['total_cost'] = Satoshi_to_USD(transaction_fee, oneBTC)
	alg_report['overpayment'] = Satoshi_to_USD(output_bytes*fee_per_byte, oneBTC)

	print(str(len(pay_req)) + " Payment Requests Processed via Fallback Solution")

	return alg_report