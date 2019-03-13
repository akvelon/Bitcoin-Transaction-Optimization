# Transaction optimization algorithm
## Case 1. fee1≤fee2
In this case, we build only one transaction – one bin.

1.	Filter pay request. Ensure that transaction value exceeds transaction fee. Drop low value pay requests if needed. To calculate fee, assume that target transaction contains at least 3 inputs and a change.

1.	Prepare utxos. Reduce each utxo by fee*input-size. Exclude inputs under 1 satoshi.

1.	Look up solution with single input. Take smallest utxo among utxo’s large than the target amount.

1.	Update utxos. Exclude utxo’s over the target amount.

1.	Look up solution with 2 inputs by means of full enumeration of all pairs.

1. Sort utxo’s in descending order.

1. 	Branch and bound enumeration. Enumerate utxo’s in a nested fashion in the order of decreasing amounts. First check the case when utxo is used, then – skipped. Descending continues until a limit is reached. The limit may be in maximum number of inputs, sum of inputs exceeds target amount or sum of remaining utxo’s is too small to build the target amount. In such cases, descending stops and algorithm backtracks canceling former decisions. Current solution is updated if the new solution is better than the best solution so far.

## Case 2. fee1>fee2
In this case, we build two transactions – two bins.

1. Assign pay request to bins. Decision is based on the result of evaluating of the following expressions (t<sub>i</sub>+600)/fee<sub>1</sub>   t<sub>i</sub>/fee<sub>2</sub>  that originate from the objective function. Pay request is assigned into the bin with larger value.

2. Apply single bin algorithm to bins in turn.
