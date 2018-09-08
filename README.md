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

## Related papers and texts

 * [Jorge Navas](https://jorgenavas.github.io)
"Horn-Clauses as an Intermediate Representation for Program Analysis and Transformation"
 * [Delimited continuations](https://en.wikipedia.org/wiki/Delimited_continuation)

