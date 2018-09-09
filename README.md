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

## Directory contents

 * lexing.py - For sample program inputs and other such things.
 * forms.py - Formats and structured used in the system.

## Related papers and texts

 * [Jorge Navas](https://jorgenavas.github.io)
"Horn-Clauses as an Intermediate Representation for Program Analysis and Transformation"
 * [Delimited continuations](https://en.wikipedia.org/wiki/Delimited_continuation)

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
