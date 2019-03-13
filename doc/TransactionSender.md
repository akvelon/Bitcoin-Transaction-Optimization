# Transaction sender
This is application which listen for the `Amazon SQS` and if there is any prepared transaction just pack it and push into mempool via connected full node (using `RPC` connection).

The code here is pretty straightforward: there is main.py file which contains the application loop which at single moment of time attempting to get the message from the queue and if one found, then it proceessed, converted to format suitable for making transaction, sighed and sent to mempool. After that the main application loop going to sleep for 5 sec.

The app itself is really raw, there are a lot of things to improve: particularly we may want batching, processing all the messages from the queue and sleep only after and provide more configuration.