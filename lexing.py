
def main():
    s = ParserState("hello world 12.3")
    tok = TokenState()
    skip_spaces(s)
    while not s.eol:
        gettoken(s, tok)
        print tok.name, tok.string

def gettoken(s, tok):
    tok.start_col = s.col
    tok.start_lno = s.lno
    gettoken_a(s, tok)
    tok.stop_col = s.col
    tok.stop_lno = s.lno
    skip_spaces(s)

def skip_spaces(s):
    if s.eol:
        if s.col < len(line):
            nextch(s)
            skip_spaces(s)
        return
    ch = peekch(s)
    while ch in " \n":
        nextch(s)
        if s.eol:
            return
        ch = peekch(s)
    if ch == "#":
        nextch(s)
        while not s.eol:
            nextch(s)
        return
    return

def gettoken_a(s, tok):
    ch = peekch(s)
    if ch.isalpha() or ch == "_":
        tok.name = "symbol"
        nextch(s)
        string = ch
        if s.eol:
            tok.string = string
            return
        ch = peekch(s)
        while ch.isalpha() or ch.isdigit() or ch == "_":
            string += ch
            nextch(s)
            if s.eol:
                tok.string = string
                return
            ch = peekch(s)
        tok.string = string
        return
    elif ch == '"' or ch == "'":
        tok.name = "string"
        string   = ch
        terminal = ch
        nextch(s)
        if s.eol:
            tok.string = string
            tok.failure = True
            return
        ch = peekch(s)
        while ch != terminal:
            string += ch
            nextch(s)
            if s.eol:
                tok.string = string
                tok.failure = True
                return
            ch = peekch(s)
        nextch(s)
        tok.string = string + terminal
        return
    elif ch.isdigit():
        tok.name = "number"
        nextch(s)
        string = ch
        if s.eol:
            tok.string = string
            return
        ch = peekch(s)
        while ch.isdigit():
            string += ch
            nextch(s)
            if s.eol:
                tok.string = string
                return
            ch = peekch(s)
        if ch == ".":
            p = savepoint(s)
            nextch(s)
            if s.eol:
                resumepoint(s, p)
                tok.string = string
                return
            ch = peekch(s)
            if not ch.isdigit():
                resumepoint(s, p)
                tok.string = string
                return
            string += "."
            while ch.isdigit():
                string += ch
                nextch(s)
                if s.eol:
                    tok.string = string
                    return
                ch = peekch(s)
        if ch == "e" or ch == "E":
            p = savepoint(s)
            e = ch
            nextch(s)
            if s.eol:
                resumepoint(s, p)
                tok.string = string
                tok.failure = True
                return
            ch = peekch(s)
            if ch == "+" or ch == "-":
                e += ch
                nextch(s)
                if s.eol:
                    resumepoint(s, p)
                    tok.string = string
                    tok.failure = True
                    return
                ch = peekch(s)
            if not ch.isdigit():
                resumepoint(s, p)
                tok.string = string
                tok.failure = True
                return
            string += e
            while ch.isdigit():
                string += ch
                nextch(s)
                if s.eol:
                    tok.string = string
                    return
                ch = peekch(s)
        tok.string = string
        return
    else:
        nextch(s)
        tok.name = "symbol"
        tok.string = ch
        return

def peekch(s):
    assert not s.eol, "end of file reached"
    return s.line[s.col]

def savepoint(s):
    return s.col

def resumepoint(s, p):
    s.col = p
    s.eol = (len(s.line) <= s.col or s.line[s.col] == "\n")

def nextch(s):
    s.col += 1
    s.eol = (len(s.line) <= s.col or s.line[s.col] == "\n")

class ParserState:
    def __init__(self, line):
        self.line = line
        self.col = 0
        self.lno = 1
        self.eol = (len(self.line) <= self.col or self.line[self.col] == "\n")

class TokenState:
    def __init__(self):
        self.name = ''
        self.string = ''
        self.failure = False
        self.start_col = 0
        self.start_lno = 0
        self.stop_col = 0
        self.stop_lno = 0

if __name__=="__main__":
    main()
