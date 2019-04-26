class Utxo:
    id = ""
    amount = 0

    def __init__(self, id, amount):
        self.id = id # txid_vout
        self.amount = amount