class PayRequest:
    id = ""
    address = ""
    amount = 0

    def __init__(self, id, address, amount):
        self.id = id
        self.address = address
        self.amount = amount