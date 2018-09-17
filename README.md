# Horn-clause based IR with delimited continuations

This is an experiment.
The goal is to produce a horn-clause based IR
that uses labelled delimited continuations for
implementing advanced control flow constructs:
Iteration, exception handling and asynchronous waiting.

The plan is a small frontend for testing this system,
and [coyote language](https://coyote-lang.org) as a primary frontend.
In any other case if the design suits your language,
we would like to support you because
it'd be nice to reuse this project rather see the work getting duplicated.

The backend target of this project is Javascript.

## Motivation

Horn-clauses can be used to form an IR that is easy to comprehend
yet sufficient for automatic optimization.
Delimited continuations can implement exception handling, iteration,
backtracking and green threads.
Combining the two results in a language
that has minimal concepts for control flow,
but is just as capable as the most complex languages designed.

If the delimited continuations are given labels
they become equivalent to algebraic effect handlers.

The resulting structure appears to bear simplicity
to the point of being absurd and infectious.

## Progress

The input clause to produce the following output would be:

    gcd(a, b; ret) <- b != 0, gcd(b, a % b, ret).
    gcd(a, b; ret) <- b == 0, ret = a.

The IR parser is not ready, so the structures are built in Python code.

`python jsb.py` produces the following output:

    function gcd (v_a, v_b) {
      var v_c, v_d;
      if (v_b != 0) {
        v_c = v_a % v_b;
        v_d = gcd(v_b, v_c);
        return v_d;
      } else {
        return v_a;
      }
    }

Next the relooper can be introduced.

## Directory contents

 * lexing.py - For sample program inputs and other such things.
 * forms.py - Formats and structured used in the system.
 * jsb.py - Javascript backend.

## Related papers and texts

 * [Jorge Navas](https://jorgenavas.github.io)
"Horn-Clauses as an Intermediate Representation for Program Analysis and Transformation"
 * [Delimited continuations](https://en.wikipedia.org/wiki/Delimited_continuation)
 * [Emscripten's relooper algorithm](https://www.researchgate.net/publication/221320724_Emscripten_an_LLVM-to-JavaScript_compiler)

## Errors made during development

I've kept a small log of errors I've done.
This won't probably be a complete list of all the errors,
but it may be interesting to see where somebody is doing errors.

In the sequence of checking equality between variables, the index
was not checked correctly.

        same_procedure = (self.procedure == other.procedure)
        same_op        = (self.operation == other.operation)
        same_index     = (self.operation == other.operation)

Consequence of the error: The program gave wrong equality between variables.
Detected: Review after writing the code.

In the same operation: We incorrectly checked equality between procedures,
although this operation is used to check that two clauses have an
equivalent prefix.
