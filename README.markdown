Pophery
=======

Version 0.1 or something
Chris Pressey, Cat's Eye Technologies

Introduction
------------

_Pophery_ is an imperative string-rewriting language.  I know right?

In Pophery, each program state is a single string, and a program is simply
the initial program state.  As execution proceeds, the string is rewritten
based on instructions found within the string.  Pophery is a "visible"
programming language, in the sense that there is no program state that is
not part of the string.

Pophery provides primitive instructions which allow the programmer to
construct their own control flow mechanisms, including at least conventional
backwards-branch looping, but possibly also permitting alternative
techniques such as [SMITH](http://catseye.tc/projects/smith/)-style
program-extension and [Muriel](http://catseye.tc/projects/muriel/)-style
quine-continuation.

As a reaction against the proliferation of stack-based esolangs, Pophery's
design explicitly avoids having a stack, preferring instead register-like
storage in the form of delimited substrings, called _slots_, which may be
accessed directly and indirectly, updated, created, destroyed, and moved
about.

Additionally, Pophery has, incidentally during the course of its design,
become centrally oriented around the editing metaphors provided both by
classic word processors and modern graphical user interfaces — the
so-called "copy and paste" operations.

Program Structure
-----------------

All program state (instructions and variables) are encoded in a single
string, which is a finite but unbounded sequence of non-combining Unicode
code points.  The string may contain any number of _locators_, which
take the form `(α)` where `α` is any string which does not contain `(` or
`)` symbols.  (In the sequel, Greek letters will denote variables for
similar such strings.)  Only the rightmost occurrence of the sequence `(α)`
is regarded as the locator, for the purposes of operations on that locator —
any other occurrences are ignored.

A pair of locators of the form `(^α)` and `(α$)`, where `(^α)` occurs to the
left of `(α$)`, is caled a _slot_.  In the sequence `(^α)β(α$)`, `α` is
called the _name_ of the slot, and `β` is called the _contents_ of the slot.

A slot may contain any number of other locators.  In fact, slots can overlap,
in the sense that a slot may contain one locator of another slot, but not the
other.

A slot can also be referenced indirectly, in which case the contents of the
slot gives the name of another slot which is the actual subject of the
operation.  For example, `(^α)β(α$)` might refer to a slot `(^β)(β$)`
elsewhere in the same string.  We use the terminology _slot β_ to refer to
direct access to the slot named `β`, and _slot indirect by β_ to refer to
access to a slot named by the contents of the slot named `β`.

While the programmer may define, create, and destroy slots as they like,
some slots have meaning to Pophery's execution model.  Each of these
_built-in_ slots has a default name by which it is accessed.  However, if a
_name slot_ for the built-in slot is present in the program, access is
indirect by the name slot.  The name slot of a built-in slot named `β` is
named `` `β ``.  (A clarifying example will appear shortly.)

A single locator can also sometimes be referenced indirectly; in this case,
a slot contains the substring `β` identifying the locator `(β)`.  Locators
also support an operation called _sliding_; they may slide leftward or slide
rightward.  When sliding rightward (resp. leftward), the character
immediately to the right (resp. left) of the locator is transferred to
immediately left (resp. right) of that locator.   However, there are two
exceptions: other locators are disregarded when sliding (they are slid over,
and not counted as characters); and when there are no characters to the
right of the locator when sliding rightward (resp. left and leftward),
neither the locator nor any character moves.

Examples follow. In the program `J(X)A`, if `(X)` were to slide leftward the
result would be `(X)JA` and if it were to slide rightward the result would
be `JA(X)`.

In `J(X)(C)A(D)`, if `(X)` were to slide rightward we would have
`J(C)A(D)(X)`.

In `JA(X)`, if `(X)` were to slide rightward, we would still have
`JA(X)`.

Finally, in `JA(X)(Y)`, if `(X)` were to slide rightward, we would still
have `JA(X)(Y)`.

An entire slot slides leftward (resp. rightward) when both of its locators
slide leftward (resp. rightward.)

Built-in Slots
--------------

The most central built-in slot is the _instruction slot_, from which is
fetched the instruction to be executed on any particular rewrite step.  The
default name of the instruction slot is `!`.  Therefore, in the program
`(^!)M(!$)`, the next instruction to be executed will be `M`.  Further, in
the program ``(^`!)k(`!$)(^k)b(k$)``, the instruction slot, accessed
indirectly by `` `! ``, is named `k`, and the next instruction to be executed
is `b`.

Other built-in slots are:

* The _accumulator_, by default named `?`;
* The _clipboard_, by default named `%`; and
* The _selection_, by default named `/`.

Pursuant to this last built-in slot, when we say a substring is _selected_,
we mean that the selection locators are inserted on either side of it
(`(^/)` on the left and `(/$)` on the right), and that all other occurrences
of these locators elsewhere in the string are removed.

Execution Model
---------------

At each rewriting step, the contents of the instruction slot, called the
_current instruction_, are examined.  The string is rewritten according to
the current instruction.  The instruction slot then slides rightward in the
string.

Execution halts when there is no instruction slot in the program, or when
the contents of the instruction slot have zero length.

When examining the current instruction to determine the command which is
executed and how the string will be re-written, we interpret it as follows.
We ignore any locators in the current instruction, and we assume it to be
one character long — if it is longer, we only regard the leftmost
character in it.

### Commands ###

* `0` through `9` update the accumulator to the literal strings `0` through
  `9`, respectively.
* `X` ("cut") erases (updates with the zero-length string) the selection.
* `C` ("copy") updates the contents of the clipboard with the contents of
  the selection.
* `V` ("paste") updates the contents of the selection with the contents of
  the clipboard.
* `S` ("select") selects the contents of the slot indirect by the
  accumulator.
* `A` ("select all") selects the contents of the accumulator.
* `L` ("left") slides the left locator of the selection leftward.
* `R` ("right") slides the left locator of the selection rightward.
* `E` ("end") moves the left locator of the selection to immediately to the
  left of the right locator of the selection, resulting in the selection
  containing the zero-length string.
* `F` ("find") searches everywhere in the contents of the accumulator for the
  contents of the clipboard.  If found, that substring is selected.
* `D` ("drag-and-drop") updates the contents of the accumulator with the
  contents of the selection, then selects the contents of the accumulator.
* `I` ("input") waits for a line to appear on standard input, then places it
  (sans newline) in the accumulator.
* `O` ("output") outputs the string in the accumulator to standard output,
  followed by a newline.

Note that the concepts "standard input" and "standard output" are defined
solely by the operating system.

### Idioms ###

We pause to consider some useful idioms constructed from the commands
presented thus far.

Assume the inital program defines some slots such as `(^0)data(0$)` to
contain initial data.  That data can then be loaded into the accumulator
with the sequence `0SCAV`, and new data, say the literal string `1`, can be
stored into slot `0` with `1AC0SV`.

To copy from any arbitrary slot (say `0`) to another (say `1`), we can say
`0SC1SV`.

Accessing a slot with a longer name, such as `(^123)xyz(123$)`, can be done
with the help of a free slot like `0` and a program fragment such as
`1AC0SV2AC0SEV3AC0SEV0SCAVSD`.

To write data, say `(^8)foo(8$)`, into a slot whose name is stored in
another slot, such as `(^9)jim(9$)`, we can say: `8SC9SDSV`.

Finally, a complete, if simple, program: the ubiquitous "Hello, world!" can
be accomplished very simply like so: `(^?)Hello, world!(?$)(^!)O(!$)`.

Constructing Control Flow Mechanisms
------------------------------------

To perform a conditional branch in the program, one would ensure there are
slots at the start of each alternative block of code to execute: call them
`α` and `β`.  One would then update slot `` `! `` to contain either `α` or
`β`, making that slot the new instruction slot.

Unfortunately, you can't do that in Pophery as it stands, basically because
there aren't enough built-in slots to say "put the value from slot blah
into the slot named by the accumulator."  TODO: add another built-in slot,
and an instruction to either swap its contents with, or copy its contents
to or from, and existing slot.

The slots `α` (and of course `β` as well) could be anywhere in the program,
so a backward branch, and thus a loop, may be affected.  The only issue is
that the `α` slot must be re-inserted each time, as, when it is used as the
instruction slot, it will begin to move rightward through the program.  Also,
as it needs to have a different name from the instruction slot currently in
use, switching back and forth between two instruction slot names would be a
necessity of such a loop.

Pophery Carrier Format: "Tranzy"
--------------------------------

Pophery also defines a file format for Pophery programs and their metadata;
this file format is called _Tranzy_.  A Tranzy file is a text file consisting
of a number of lines.  The encoding of characters is not specified.  Each
line may begin with a `#` character, or not.  Lines which do begin with `#`
are "comment" lines in which metadata may be embedded; these are lines which
are being carried in the Tranzy file, but which do not form any part of the
Pophery program.  The non-comment lines are concatenated (sans newlines, but
including other whitespace) to form the Pophery program.

Tranzy does not currently define any metadata which can reside in comment
lines, but acknowledges and permits metadata defined by external standards
(de facto or otherwise).  An example Tranzy file is depicted below.

    #!/usr/bin/my-pophery-interpreter -w
    # encoding: UTF-8
    0@SLX1@SL@SXS
    (^0)(0$)(^1)!(1$)

Notes
-----

Pophery came more or less into its present form on or about September 6th,
2010.  It has lain about since then, collecting dust.

The name _Pophery_ is a mutant hybrid of the ancient Greek _Porphyry_,
meaning "purple", and _Poreef_, itself a mutant hybrid of pork and beef
featured in a certain _The Kids in the Hall_ skit.  (Arguably, my
[Unlikely](http://catseye.tc/projects/unlikely/) language would have been a
better candidate for the moniker "Poreef", but unfortunately, I missed that
opportunity, and this is the way things turned out.)

While working up to the current design, a design plateau was reached; it had
a more machine-language-like feel to it, with slots called the _accumulator_,
the _index slot_, and the _ancillary slot_.  (For posterity, I've called the
language that follows this design _Pophery version -1.0_, and have retained
its implementation in this distribution as `minus-one.py`, but it is not my
focus of interest and will discuss it no further here.)  The ancillary slot
happened to have operations devised for it which resembled cut, copy, and
paste, and was renamed the clipboard for this reason; then everything you
see now kind of followed from that.

The "string rewriting" part of the description kind of has a double meaning
now.  Not only is the imperative execution described in terms of string
rewriting (to the point where you could probably implement it
straightforwardly, or nearly so, in a language like
[Thue](http://catseye.tc/projects/thue/),) but the imperative instructions
also perform operations which are recognizably text editing — which is just
a politically correct way of saying "string rewriting", *n'est-ce pas*?

TODO: Find a way to manipulate data satisfactorily.

One of the original goals of the language design was to support the
construction of multiple control flow mechanisms from simple primitives.
Due to time and concentration constraints, only the conventional
looping-by-backwards-branching mechanism of control flow was explored.
However, we will speculate on two other mechanisms, which may be
implementable in Pophery or a modest extension thereof, in the next two
paragraphs.

To affect SMITH-style self-extension, one would need only make sure there is
a slot named `β` located to the right of the currently-executing code, and
then write instructions into it.  The instruction slot will eventually slide
rightward into it.  For authentic SMITH-like behavior, the instructions would
be written into `β` by having a slot `ζ` encompass the currently executing
block of code, and copying the contents of `ζ` wholesale into `β`.

To affect Muriel-style quine-continuation, one would need to establish a
buffer slot named `β`, write instructions into it piecemeal until it looks
like the desired next leg of the program, and then replace the entire
running program with it.  This can be done by having a slot named `ζ`
encompass the entire program, and copying `β` into it.  The only subtlety is
the instruction slot; once the contents of `β` have become the entire
program, you will want the intended instruction slot in `β` to become the
active instruction slot, which means switching the instruction slot at the
same time `β` is copied into `ζ`.  This would probably necessitate an
extension to Pophery.

Happy re: righting!  
Chris Pressey  
September 6, 2010  
Evanston, IL
