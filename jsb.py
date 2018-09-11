import forms
from forms import *

def demonstration():
    program = forms.demonstration()
    generate_function("gcd", program)

def generate_function(name, program):
    procs = program[name]
    tree = construct_choice_tree(procs)
    symtab = SymbolTable()
    arguments = []
    for var in procs[0].inputs:
        arguments.append(symtab.get_symbol(var))
    statements = []
    statements.append( build_from_tree(tree, 0, symtab) )
    print "function {} ({}) {{\n  {}\n}}".format(name,
        ", ".join(arguments), 
        "\n  ".join(statements))

# The first step in building the function is to
# construct a binary tree.
def construct_choice_tree(procs):
    first = procs[0]
    branch = ('leaf', first)
    for proc in procs[1:]:
        branch = add_choice_point(branch, proc, 0)
    return branch

def add_choice_point(branch, proc, start=0):
    if branch[0] == 'leaf':
        _, first = branch
        index = find_split_point(first, proc, start)
        return ('branch', index, first, branch, ('leaf', proc))
    if branch[1] == 'branch':
        _, first, left, right, cutoff = branch
        index = find_split_point(first, proc, start)
        if index < cutoff:
            return ('branch', index, branch, ('leaf', proc))
        elif index > cutoff:
            left = add_choice_point(left, proc, index)
            return ('branch', cutoff, first, left, right)
        else:
            right = add_choice_point(right, proc, index)
            return ('branch', cutoff, first, left, right)
    assert False

def find_split_point(a, b, index):
    length = min(len(a.body), len(b.body))
    while index < length:
        if is_eq(a.body[index], b.body[index]):
            index += 1
            continue
        if is_complementary(a.body[index], b.body[index]):
            return index
        break
    # The binary tree construction fails if
    # the input is not in the form that was expected.
    assert False, "input is not in a normalized form"

# When producing the output we will need a symbol table
# to translate the variable names into something cleaner. 
# It's a bit unnecessary as the symbols themselves already
# have very good names.
class SymbolTable(object):
    def __init__(self):
        self.labels = {}
        self.num = 0

    def get_symbol(self, variable):
        if isinstance(variable, Constant):
            # TODO: We got to hook a js-stringifier here.
            return repr(variable.value)
        key = (variable.operation, variable.index)
        if key in self.labels:
            return self.labels[key]
        else:
            num = self.num
            label = "v_"
            while num > 26:
                label += chr(97 + num%26)
                num = num // 26
            label += chr(97 + num%26)
            self.num = num + 1
            self.labels[key] = label
            return label

def build_from_tree(branch, index, symtab):
    if branch[0] == 'leaf':
        _, first = branch
        out = []
        for operation in first.body[index:]:
            out.append("[{2}] = {0}({1});".format(
                operation.name,
                ", ".join(symtab.get_symbol(var)
                    for var in operation.inputs),
                ", ".join(symtab.get_symbol(var)
                    for var in operation.outputs)))
        retvars = []
        for var in first.outputs:
            retvars.append(symtab.get_symbol(var))
        if len(retvars) == 1:
            out.append("return {};".format(retvars[0]))
        elif len(retvars) >= 1:
            out.append("return [{}];".format(", ".join(retvars)))
        return "\n  ".join(out)
    if branch[0] == 'branch':
        _, cutoff, first, left, right = branch
        out = []
        for operation in first.body[index:cutoff]:
            out.append("[{2}] = {0}({1});".format(
                operation.name,
                ", ".join(symtab.get_symbol(var)
                    for var in operation.inputs),
                ", ".join(symtab.get_symbol(var)
                    for var in operation.outputs)))
        operation = first.body[cutoff]
        cond = "{0}({1})".format(
            operation.name,
            ", ".join(symtab.get_symbol(var)
                for var in operation.inputs))
        last = "if ({}) {{\n    {}\n  }} else {{\n    {}\n  }}".format(
            cond,
            build_from_tree(left, cutoff+1, symtab).replace('\n', '\n  '),
            build_from_tree(right, cutoff+1, symtab).replace('\n', '\n  '),
        )
        out.append(last)
        return "\n  ".join(out)
    assert False, branch

# For computing relooping, we have to determine
# which other labels each label can reach.
def transitive_closure(program):
    trc = {}
    for label in program.iterkeys():
        trc[label] = set()
    fixed_point = False
    while not fixed_point:
        fixed_point = True
        for label, procs in program.iteritems():
            c = trc[label]
            m = len(c)
            for proc in procs:
                if len(proc.body) == 0:
                    continue
                operation = proc.body[len(proc.body)-1]
                if operation.name in program:
                    c.add(operation.name)
                    c.update(trc[operation.name])
            n = len(c)
            if m < n:
                fixed_point = False
    return trc

# The relooper comes here.

if __name__=='__main__':
    demonstration()
