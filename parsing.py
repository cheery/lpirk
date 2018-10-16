# Convert the text into tree-structured compounds.
# Every text input cannot convert into a compound.

# Explanation of the algorithm used here:
# http://boxbase.org/entries/2018/oct/15/layout-sensitive-pratt-parsing/

def main():
    with open('example_0.txt', 'r') as fd:
        reading = Reading(fd)
        token = CurrentToken()
        parsing = Parsing(reading, token)
        parsing.advance()
        parsing.line_begin = True
        result = expression(parsing, 0, 0)
        assert parsing.eof, ('eof', parsing.token.name, parsing.token.string)
    print result

#   Tested tokenizer with this before the previous text:
#        parsing.advance()
#        while not parsing.eof:
#            print token.start, token.stop
#            print token.name, repr(token.string)
#            if token.name == "rational":
#                print "  ", token.fraction, token.exponent
#            parsing.advance()

# These structures are output by the parser.
class Compound(object):
    def __init__(self, name, terms):
        self.name = name
        self.terms = terms

    def __repr__(self):
        if len(self.terms) == 0:
            return "{}".format(self.name)
        else:
            return "{}({})".format(
                self.name,
                ", ".join(repr(t) for t in self.terms))

def expression(parsing, rbp, vcol):
    stacking = (rbp == 0 and parsing.line_begin)
    if stacking:
        vcol = parsing.token.start[0]
    # advancing with null denotation
    left = nud[parsing.token.name](parsing)
    while (rbp < lbp.get(parsing.token.name, 0) and
        not (parsing.line_begin and parsing.token.start[0] <= vcol)):
        # advancing with left denotation
        left = led[parsing.token.name](parsing, left)
    if stacking and parsing.line_begin and parsing.token.start[0] == vcol:
        left = Compound("\\\\", [left, expression(parsing, rbp, vcol)])
    return left

def expect(parsing, name):
    assert parsing.token.name == name, (
        'expected', parsing.token.name, parsing.token.string)
    parsing.advance()

symbol_table = {
    "(": ("(", {}),
    ")": (")", {}),
    ",": (",", {}),
    "=": ("=", {
        "=": ("==", {}),
    }),
    "+": ("+", {}),
    "<": ("<", {
        "-": ("<-", {}),
    }),
}

nud = {} # Null denotation
led = {} # Left denotation
lbp = {} # Left binding power

def nud_symbol(parsing):
    name = parsing.token.string
    parsing.advance()
    if parsing.token.name == "(":
        terms = expression_group(parsing, ",", ")")
    else:
        terms = []

    return Compound(name, terms)
nud['symbol'] = nud_symbol

lbp['+'] = 10
def led_infix(parsing, left):
    name = parsing.token.name
    parsing.advance()
    right = expression(parsing, 10, 0)
    return Compound(name, [left, right])
led['+'] = led_infix

lbp['<-'] = 1
def led_infix_arrow(parsing, left):
    name = parsing.token.name
    parsing.advance()
    right = expression(parsing, 0, 0)
    return Compound(name, [left, right])
led['<-'] = led_infix_arrow

def nud_grouping(parsing):
    parsing.advance()
    group = expression(parsing, 0, 0)
    expect(parsing, ')')
    return group
nud['('] = nud_grouping

def expression_group(parsing, separator, terminal):
    parsing.advance()
    if parsing.token.name == terminal:
        parsing.advance()
        return []
    else:
        terms = [expression(parsing, 0, 0)]
        while parsing.token.name == separator:
            parsing.advance()
            terms.append(expression(parsing, 0, 0))
        expect(parsing, terminal)
        return terms

#lbp['('] = 1000
#def led_call(parsing, left):
#    terms = expression_group(parsing, ",", ")")
#    return Compound("()", [left] + terms)
#led['('] = led_call

# We need to lookahead one token.
class Parsing(object):
    def __init__(self, reading, token):
        self.reading = reading
        self.token = token
        self.eof = False
        self.line_begin = False

    def advance(self):
        lno = self.reading.lno
        self.reading.skip_spaces()
        self.line_begin = (lno != self.reading.lno)
        if self.reading.peek(0) != "":
            gettoken(self.reading, self.token)
            self.eof = False
        else:
            self.token.name = ''
            self.eof = True

# Assume the input is UTF-8 unix formatted text file.

# There is a point where you commit to the reading
# from the stream. Reading tracks that point.
# Lookahead is treated as if we didn't read the stream.
class Reading(object):
    def __init__(self, fd, col=1, lno=1):
        self.fd = fd
        self.lookahead = []
        self.col = col # Col/Lno starts from '1', like in a text editor.
        self.lno = lno
    
    def next(self):
        if len(self.lookahead) > 0:
            nextch = self.lookahead.pop(0)
        else:
            nextch = self.fd.read(1)
        if nextch == "\n":
            self.col = 1
            self.lno += 1
        else:
            self.col += 1
        return nextch

    def take(self, count):
        output = []
        for i in range(count):
            output.append(self.next())
        return output

    def peek(self, index):
        while not (index < len(self.lookahead)):
            self.lookahead.append(self.fd.read(1))
        return self.lookahead[index]

    def skip_spaces(self):
        ch = self.peek(0)
        while (ch in " \n" and ch != "") or ch == "#":
            while ch in " \n" and ch != "":
                self.next()
                ch = self.peek(0)
            if ch == "#":
                while ch not in "\n":
                    self.next()
                    ch = self.peek(0)

class CurrentToken(object):
    def __init__(self):
        self.name = ''
        self.string = ''
        self.fraction = ''
        self.exponent = ''
        self.terminal = ''
        self.start = (0, 0)
        self.stop  = (0, 0)

def gettoken(reading, output):
    ch = reading.peek(0)
    output.start = (reading.col, reading.lno)
    if ch.isalpha() or ch == "_":
        output.name = 'symbol'
        string = reading.next()
        ch = reading.peek(0)
        while ch.isalpha() or ch.isdigit() or ch == "_":
            string += reading.next()
            ch = reading.peek(0)
        output.string = string
    elif ch == '"' or ch == "'":
        output.name = 'string'
        string = ''
        terminal = reading.next()
        ch = reading.peek(0)
        while ch != terminal and ch != "\n" and ch != "":
            string += reading.next() 
            ch = reading.peek(0)
        if ch == terminal:
            reading.next()
        output.terminal = terminal
        output.string = string
    elif ch.isdigit():
        output.name = 'integer'
        string = reading.next()
        ch = reading.peek(0)
        while ch.isdigit():
            string += reading.next()
            ch = reading.peek(0)
        if ch == "." and reading.peek(1).isdigit():
            output.name = 'rational'
            dot = reading.next()
            fraction = ''
            ch = reading.peek(0)
            while ch.isdigit():
                fraction += reading.next()
                ch = reading.peek(0)
            output.fraction = fraction
            ch = reading.peek(0)
        else:
            output.fraction = '0'
        if (ch == "e" or ch == "E") and starts_exponent(reading):
            output.name = 'rational'
            letter = reading.next()
            exponent = reading.next()
            ch = reading.peek(0)
            while ch.isdigit():
                exponent += reading.next()
                ch = reading.peek(0)
            output.exponent = exponent
        else:
            output.exponent = '0'
        output.string = string
    else:
        n = 1
        k = 1
        name  = 'failure'
        state = symbol_table
        while ch in state:
            perhaps_name, state = state[ch]
            if perhaps_name != 'failure':
                name = perhaps_name
                k = n
            ch = reading.peek(n)
            n += 1
        output.name = name
        output.string = "".join(reading.take(k))
    output.stop = (reading.col, reading.lno)

def starts_exponent(reading):
    if reading.peek(1) in "+-" and reading.peek(2).isdigit():
        return True
    if reading.peek(1).isdigit():
        return True
    return False

if __name__=='__main__':
    main()
