def demonstration():
    a = Variable()
    b = Variable()
    ret = Variable()
    bn = Variable()
    gcd_a = Procedure('gcd', [a, b], [ret], [
        Operation("!=", [b, Constant(0)], []),
        Operation("mod", [a, b], [bn]),
        Operation("gcd", [b, bn], [ret]),
    ])
    gcd_a.introduce()

    a = Variable()
    b = Variable()
    gcd_b = Procedure('gcd', [a, b], [a], [
        Operation("==", [b, Constant(0)], []),
    ])
    gcd_b.introduce()

    program = {
        "gcd": [gcd_a, gcd_b]
    }

    assert all_eq(gcd_a.inputs, gcd_b.inputs)
    assert is_complementary(gcd_a.body[0], gcd_b.body[0]) 
    return program

class Procedure(object):
    def __init__(self, label, inputs, outputs, body):
        self.label = label
        self.inputs = inputs
        self.outputs = outputs
        self.body = body

    def introduce(self):
        i = 0
        for inp in self.inputs:
            inp.introduce(self, 0, i)
            i += 1
        k = 1
        for operation in self.body:
            operation.introduce(self, k)
            k += 1

class Operation(object):
    def __init__(self, name, inputs, outputs):
        self.name = name
        self.inputs = inputs
        self.outputs = outputs

    def introduce(self, procedure, operation):
        i = 0
        for output in self.outputs:
            output.introduce(procedure, operation, i)
            i += 1

class Constant(object):
    def __init__(self, value):
        self.value = value

    def eq(self, other):
        if not isinstance(other, Constant):
            return False
        return self.value == other.value

class Variable(object):
    def __init__(self):
        self.procedure = None
        self.operation = 0
        self.index     = 0

    def introduce(self, procedure, operation, index):
        if self.procedure is not None:
            match  = (self.procedure == procedure)
            match &= (self.operation == operation)
            match &= (self.index == index)
            assert match, "variable is being reused"
        self.procedure = procedure
        self.operation = operation
        self.index = index

    def eq(self, other):
        if not isinstance(other, Variable):
            return False
        same_op        = (self.operation == other.operation)
        same_index     = (self.index == other.index)
        return same_op and same_index

def all_eq(xs, ys):
    if not len(xs) == len(ys):
        return False
    for i in range(len(xs)):
        if not xs[i].eq(ys[i]):
            return False
    return True

# Some operations are complementary to each other.
# This means that if operation succeeds,
# then the complementary operation with same inputs will fail.
complementary_operations = {
    "==": "!=",
    "<":  ">=",
    "<=": ">",
}

def is_complementary_name(a, b):
    if complementary_operations.get(a, None) == b:
        return True
    if complementary_operations.get(b, None) == a:
        return True
    return False

def is_complementary(a, b):
    if not is_complementary_name(a.name, b.name):
        return False
    return all_eq(a.inputs, b.inputs)

def is_eq(self, other):
    if self.name != other.name:
        return False
    if not all_eq(self.inputs, other.inputs):
        return False
    if not all_eq(self.outputs, other.outputs):
        return False
    return True

if __name__=='__main__':
    demonstration()
