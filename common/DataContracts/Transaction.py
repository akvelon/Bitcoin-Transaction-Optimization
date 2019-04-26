class Transaction:
    inputs = []
    outputs = []
    change = None

    def __input__(self, inputs, outputs, change):
        self.inputs = inputs
        self.outputs = outputs
        self.change = change