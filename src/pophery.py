#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Interpreter for the Pophery Programming Language v0.1 or something.

"""

LICENSE = """\
Copyright (c)2011 Chris Pressey, Cat's Eye Technologies.
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:

  1. Redistributions of source code must retain the above copyright
     notices, this list of conditions and the following disclaimer.
  2. Redistributions in binary form must reproduce the above copyright
     notices, this list of conditions, and the following disclaimer in
     the documentation and/or other materials provided with the
     distribution.
  3. Neither the names of the copyright holders nor the names of their
     contributors may be used to endorse or promote products derived
     from this software without specific prior written permission. 

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE
COPYRIGHT HOLDERS OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
"""


import sys
from optparse import OptionParser


class UndefinedLocatorError(Exception):
    """Indicates a given locator was not found in a MutableString."""
    pass


class MutableString(object):
    """String-like object which may be updated in place.

    A MutableString emulates a Python unicode datatype in many ways,
    with the most notable exception being that its contents may
    change over time.  In addition, it supports a rich set of operations
    for enacting these changes.

    Changes are often made relative to one or more locators.
    A locator string uniquely locates a position within a MutableString.
    A locator is a substring which is unique within the MutableString.
    If the locator is not unique, the behaviour of a change made
    relative to it is undefined.

    """
    def __init__(self, initial):
        self.string = unicode(initial)

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return self.string

    def __len__(self):
        return len(self.string)
    
    def __getitem__(self, index):
        return self.string[index]

    def __getslice__(self, i, j):
        return self.string[i:j]

    def find(self, sub):
        return self.string.find(sub)
    
    def set(self, string):
        self.string = unicode(string)

    def pos_left(self, locator, delta):
        """Return the 0-based position within this MutableString of the
        first character of the given locator, plus the given offset.

        Note that the returned value is ephemeral and should not be
        stored, as it is subject to change at any time the MutableString
        is changed.

        >>> a = MutableString("Mom(*)entous")
        >>> print a.pos_left("(*)", 0)
        3

        """
        pos = self.find(locator)
        if pos == -1:
            raise UndefinedLocatorError(locator)
        return pos - delta

    def pos_right(self, locator, delta):
        """Return the 0-based position within this MutableString of the
        first character to the right of the given locator, plus the given
        offset.

        Note that the returned value is ephemeral and should not be
        stored, as it is subject to change at any time the MutableString
        is changed.

        >>> a = MutableString("Mom(*)entous")
        >>> print a.pos_right("(*)", 0)
        6

        """
        pos = self.find(locator)
        if pos == -1:
            raise UndefinedLocatorError(locator)
        return pos + len(locator) + delta

    def insert_locator(self, locator, pos):
        """Insert the given locator at the given position in this string.

        Note that this will blithely insert the new locator inside an
        existing locator.

        >>> a = MutableString("Momentous")
        >>> a.insert_locator("(*)", 3)
        >>> print str(a)
        Mom(*)entous

        """
        self.set(self[:pos] + unicode(locator) + self[pos:])

    def remove_locator(self, locator):
        """Remove the given locator from this string.

        >>> a = MutableString("Mom(*)entous")
        >>> a.remove_locator("(*)")
        >>> print str(a)
        Momentous

        """
        locator = unicode(locator)
        posl = self.pos_left(locator, 0)
        posr = self.pos_right(locator, 0)
        self.set(self[:posl] + self[posr:])

    def move_locator(self, locator, delta):
        """Change the position of the given locator by the given delta.

        Note that this will not skip over intervening locators; i.e. it will
        allow the locator to end up inside another locator.

        >>> a = MutableString("Mom(*)entous")
        >>> a.move_locator("(*)", +3)
        >>> print str(a)
        Moment(*)ous

        """
        locator = unicode(locator)
        posl = self.pos_left(locator, 0)
        posr = self.pos_right(locator, 0)
        self.set(self[:posl] + self[posr:])
        posl = posl + delta
        self.set(self[:posl] + locator + self[posl:])

    def slide_locator(self, locator, delta):
        """Slide the position of the given locator by the given delta.

        Note that this will skip over intervening locators; i.e. it will
        avoid having the locator end up inside another locator.
        
        Delta must be +1 or -1.

        >>> a = MutableString("Mom(*)en(+)tous")
        >>> a.slide_locator("(*)", +1)
        >>> print str(a)
        Mome(*)n(+)tous
        >>> a.slide_locator("(*)", -1)
        >>> print str(a)
        Mom(*)en(+)tous

        >>> b = MutableString("(-)Cassowary(+)")
        >>> b.slide_locator("(+)", +1)
        >>> print str(b)
        (-)Cassowary(+)
        >>> b.slide_locator("(-)", -1)
        >>> print str(b)
        (-)Cassowary(+)

        >>> c = MutableString("Imb(+)r(%)oglio")
        >>> c.slide_locator("(+)", +1)
        >>> print str(c)
        Imbr(+)(%)oglio

        """
        locator = unicode(locator)
        if delta == +1:
            matching = True
            target = self.pos_right(locator, 0)
            advance = 1
            while matching is not None and target < len(self):
                matching = self.find_matching(target)
                if matching is not None:
                    advance += (matching - target) + 1
                    target = matching + 1
            if target < len(self):
                self.move_locator(locator, advance)
        elif delta == -1:
            matching = True
            target = self.pos_left(locator, 0) - 1
            advance = -1
            while matching is not None and target >= 0:
                matching = self.find_matching(target)
                if matching is not None:
                    advance -= (target - matching) + 1
                    target = matching - 1
            if target >= 0:
                self.move_locator(locator, advance)
        else:
            raise NotImplementedError

    def read(self, left, right):
        """Retrieve the substring between the two given locators.

        >>> a = MutableString("This is (a)my string(b) you know.")
        >>> print a.read("(a)", "(b)")
        my string

        """
        a = self.pos_right(left, 0)
        b = self.pos_left(right, 0)
        return self.string[a:b]

    def update(self, left, right, string):
        """Change the substring between the two given locators.

        >>> a = MutableString("This is (a)my string(b) you know.")
        >>> a.update("(a)", "(b)", "crazy talk")
        >>> print str(a)
        This is (a)crazy talk(b) you know.

        """
        a = self.pos_right(left, 0)
        b = self.pos_left(right, 0)
        self.set(self.string[:a] + unicode(string) + self.string[b:])

    def find_matching(self, pos):
        """Find the parenthesis which matches the parenthesis at the given
        position.

        Returns the position of the matching parenthesis, or None if no
        matching parenthesis was found, or if the character at the given
        position isn't a parenthesis.

        >>> a = MutableString("This (is (my[))] string.")
        >>> a.find_matching(5)
        14
        >>> a.find_matching(9)
        13
        >>> a.find_matching(12) is None
        True
        >>> a.find_matching(14)
        5
        >>> a.find_matching(13)
        9
        >>> a.find_matching(15) is None
        True

        >>> a = MutableString("a(")
        >>> a.find_matching(0) is None
        True
        >>> a.find_matching(1) is None
        True

        """
        opener = self.string[pos]
        if opener == u'(':
            closer = u')'
            dir = +1
        elif opener == u')':
            closer = u'('
            dir = -1
        else:
            return None
        level = 0
        while pos < len(self.string):
            if self.string[pos] == opener:
                level += 1
            elif self.string[pos] == closer:
                level -= 1
                if level == 0:
                    return pos
            pos += dir
        return None


class SlottedString(MutableString):

    def __init__(self, initial):
        super(SlottedString, self).__init__(initial)

    def read_slot(self, slot_name):
        """
        
        >>> a = SlottedString("This is (^a)my slot(a$) you know.")
        >>> a.update_slot('a', 'good stuff')
        >>> print str(a)
        This is (^a)good stuff(a$) you know.
        >>> a.update_slot('z', 'bad stuff')
        Traceback (most recent call last):
        ...
        UndefinedLocatorError: (^z)

        """
        slot_name = unicode(slot_name)
        return self.read(u"(^%s)" % slot_name, u"(%s$)" % slot_name)

    def read_slot_indirect(self, slot_name):
        """
        >>> p = SlottedString("...(^A)M(A$)...(^R)A(R$)...")
        >>> print p.read_slot_indirect('R')
        M
        >>> print p.read_slot_indirect('A')
        Traceback (most recent call last):
        ...
        UndefinedLocatorError: (^M)

        """
        slot_name = unicode(slot_name)
        slot_name = self.read_slot(slot_name)
        return self.read_slot(slot_name)

    def update_slot(self, slot_name, string):
        """

        >>> a = SlottedString("This is (^a)my slot(a$) you know.")
        >>> a.update_slot('a', 'good stuff')
        >>> print str(a)
        This is (^a)good stuff(a$) you know.
        >>> a.update_slot('a', MutableString('mutable stuff'))
        >>> print str(a)
        This is (^a)mutable stuff(a$) you know.
        >>> a.update_slot('z', 'bad stuff')
        Traceback (most recent call last):
        ...
        UndefinedLocatorError: (^z)

        """
        slot_name = unicode(slot_name)
        string = unicode(string)
        return self.update(u"(^%s)" % slot_name, u"(%s$)" % slot_name, string)

    def update_slot_indirect(self, slot_name, string):
        """
        >>> p = SlottedString("Dolphin(^A)M(A$)Dolphin(^R)A(R$)Dolphin")
        >>> p.update_slot_indirect('R', 'Porphyry')
        >>> print str(p)
        Dolphin(^A)Porphyry(A$)Dolphin(^R)A(R$)Dolphin

        """
        slot_name = self.read_slot(slot_name)
        self.update_slot(slot_name, string)

    def get_slot_name(self, slot_name):
        """

        >>> a = SlottedString("(^G)?(G$) (^P)_(P$) (^`P)Q(`P$) (^`K)(^/)Madge(/$)(`K$)")
        >>> print a.get_slot_name('M')
        M
        >>> print a.get_slot_name('G')
        G
        >>> print a.get_slot_name('P')
        Q
        >>> print a.get_slot_name('K')
        Madge

        """
        slot_name = unicode(slot_name)
        name_slot = u"`%s" % slot_name
        try:
            slot_name = self.read_slot(name_slot)
        except (UndefinedLocatorError):
            pass
        slot_name = self.strip_all_locators(slot_name)
        return slot_name

    def strip_all_locators(self, content):
        """
        >>> p = Program('')
        >>> print p.strip_all_locators('')
        None
        >>> print p.strip_all_locators('X')
        X
        >>> print p.strip_all_locators('Well-tempered')
        Well-tempered
        >>> print p.strip_all_locators('(^8)(^7)(7$)CAT(8$)')
        CAT
        >>> print p.strip_all_locators('(^8(beat))D')
        D
        >>> print p.strip_all_locators('(^8)(^7)(7$)(8$)')
        None

        """
        if len(content) == 0:
            return None
        else:
            pos = 0
            level = 0
            acc = ''
            while pos < len(content):
                if content[pos] == '(':
                    level += 1
                elif content[pos] == ')':
                    level -= 1
                elif level == 0:
                    acc += content[pos]
                pos += 1
            return acc or None

    def slide_slot(self, slot_name, delta):
        """

        >>> a = SlottedString("This is my (^a)slot(a$) (^b)y(b$)ou know.")
        >>> a.slide_slot('a', +1)
        >>> print str(a)
        This is my s(^a)lot (a$)(^b)y(b$)ou know.
        >>> a.slide_slot('b', -1)
        >>> print str(a)
        This is my s(^a)lot(^b) (a$)(b$)you know.

        """
        slot_name = unicode(slot_name)
        if delta > 0:
            self.slide_locator("(%s$)" % slot_name, delta)
            self.slide_locator("(^%s)" % slot_name, delta)
        else:
            self.slide_locator("(^%s)" % slot_name, delta)
            self.slide_locator("(%s$)" % slot_name, delta)


class Program(SlottedString):

    def __init__(self, initial):
        super(Program, self).__init__(initial)
        self.input = sys.stdin
        self.output = sys.stdout

    def load(self, filename):
        """Load the program source from a Tranzy file."""
        file = open(filename, 'r')
        done = False
        string = ''
        for line in file.readlines():
            line = unicode(line, 'utf-8')  # for now
            if line.endswith('\n'):
                line = line[:-1]
            if line.startswith('#'):
                pass
            else:
                string += line
        self.set(string)
        file.close()

    def advance(self):
        """Slide the instruction slot rightward.

        >>> p = Program("(^!)A(!$)B(^M)C(M$)D")
        >>> p.advance()
        >>> print str(p)
        A(^!)B(!$)(^M)C(M$)D
        >>> p.advance()
        >>> print str(p)
        AB(^!)(^M)C(!$)(M$)D
        >>> p.advance()
        >>> print str(p)
        AB(^M)C(^!)(M$)D(!$)
        >>> p.advance()
        >>> print str(p)
        AB(^M)C(M$)D(^!)(!$)

        >>> p = Program("(^!)A(!$)(^Moo)(^Gar)(Gar$)B(Moo$)")
        >>> p.advance()
        >>> print str(p)
        A(^!)(^Moo)(^Gar)(Gar$)B(!$)(Moo$)
        >>> p.advance()
        >>> print str(p)
        A(^Moo)(^Gar)(Gar$)B(^!)(!$)(Moo$)

        """
        self.slide_slot(self.get_slot_name('!'), +1)

    def clean_instruction(self, instruction):
        """
        >>> p = Program('')
        >>> print p.clean_instruction('')
        None
        >>> print p.clean_instruction('X')
        X
        >>> print p.clean_instruction('Well-tempered')
        W
        >>> print p.clean_instruction('(^8)(^7)(7$)CAT(8$)')
        C
        >>> print p.clean_instruction('(^8(beat))D')
        D
        >>> print p.clean_instruction('(^8)(^7)(7$)(8$)')
        None

        """
        if len(instruction) == 0:
            return None
        else:
            pos = 0
            level = 0
            while instruction[pos] == '(':
                while True:
                    if instruction[pos] == '(':
                        level += 1
                    elif instruction[pos] == ')':
                        level -= 1
                    pos += 1
                    if level == 0 or pos >= len(instruction):
                        break
                if pos >= len(instruction):
                    return None
            return instruction[pos]
    
    def execute(self, instruction):
        raise NotImplementedError

    def step(self):
        """Execute one step of this Pophery program."""
        instruction = self.read_slot(self.get_slot_name('!'))
        instruction = self.clean_instruction(instruction)
        if instruction is None:
            return False
        else:
            self.execute(instruction)
            self.advance()
            return True

    def run(self):
        """Execute this Pophery program and return only when it terminates."""
        keep_going = self.step()
        while keep_going:
            keep_going = self.step()


class Semantics(Program):
    def deselect(self):
        locator_name = self.get_slot_name('/')
        try:
            self.remove_locator('(^%s)' % locator_name)
        except UndefinedLocatorError:
            pass
        try:
            self.remove_locator('(%s$)' % locator_name)
        except UndefinedLocatorError:
            pass

    def execute(self, instruction):
        """Apply the semantics of the given instruction to this Program.

        * 0 through 9 update the accumulator to the literal strings 0 through
          9, respectively.

        >>> p = Semantics("(^?)(?$)")
        >>> p.execute('0')
        >>> print str(p)
        (^?)0(?$)

        * X ("cut") erases (updates with the zero-length string) the selection.

        >>> p = Semantics("(^/)hi(/$)")
        >>> p.execute('X')
        >>> print str(p)
        (^/)(/$)
        >>> p = Semantics("(^`/)X(`/$)(^X)hi(X$)")
        >>> p.execute('X')
        >>> print str(p)
        (^`/)X(`/$)(^X)(X$)

        * C ("copy") updates the contents of the clipboard with the contents
          of the selection.

        >>> p = Semantics("(^/)hi(/$)(^%)lo(%$)")
        >>> p.execute('C')
        >>> print str(p)
        (^/)hi(/$)(^%)hi(%$)
        >>> p = Semantics("(^/)hi(/$)(^J)lo(J$)(^`%)J(`%$)")
        >>> p.execute('C')
        >>> print str(p)
        (^/)hi(/$)(^J)hi(J$)(^`%)J(`%$)

        * V ("paste") updates the contents of the selection with the contents
          of the clipboard.

        >>> p = Semantics("(^/)hi(/$)(^%)lo(%$)")
        >>> p.execute('V')
        >>> print str(p)
        (^/)lo(/$)(^%)lo(%$)
        >>> p = Semantics("(^C)lo(C$)(^J)hi(J$)(^`/)J(`/$)(^`%)C(`%$)")
        >>> p.execute('V')
        >>> print str(p)
        (^C)lo(C$)(^J)lo(J$)(^`/)J(`/$)(^`%)C(`%$)

        * S ("select") selects the contents of the slot indirect by the
          accumulator.

        >>> p = Semantics("(^/)foo(/$)(^?)A(?$)(^A)Some text.(A$)")
        >>> p.execute('S')
        >>> print str(p)
        foo(^?)A(?$)(^A)(^/)Some text.(/$)(A$)
        >>> p = Semantics("(^`/)k(`/$)(^k)foo(k$)(^?)A(?$)(^A)Some text.(A$)")
        >>> p.execute('S')
        >>> print str(p)
        (^`/)k(`/$)foo(^?)A(?$)(^A)(^k)Some text.(k$)(A$)

        * A ("select all") selects the contents of the accumulator.

        >>> p = Semantics("(^/)foo(/$)(^?)A(?$)(^A)Some text.(A$)")
        >>> p.execute('A')
        >>> print str(p)
        foo(^?)(^/)A(/$)(?$)(^A)Some text.(A$)
        >>> p = Semantics("(^`/)r(`/$)(^r)foo(r$)(^?)A(?$)(^A)Some text.(A$)")
        >>> p.execute('A')
        >>> print str(p)
        (^`/)r(`/$)foo(^?)(^r)A(r$)(?$)(^A)Some text.(A$)

        * L ("left") slides the left locator of the selection leftward.

        >>> p = Semantics("foo(^/)bar(/$)")
        >>> p.execute('L')
        >>> print str(p)
        fo(^/)obar(/$)
        >>> p = Semantics("(^/)foobar(/$)")
        >>> p.execute('L')
        >>> print str(p)
        (^/)foobar(/$)
        >>> p = Semantics("foo(^C)bar(C$)(^`/)C(`/$)")
        >>> p.execute('L')
        >>> print str(p)
        fo(^C)obar(C$)(^`/)C(`/$)
        >>> p = Semantics("The last time I saw Charlie")
        >>> p.execute('L')
        Traceback (most recent call last):
        ...
        UndefinedLocatorError: (^/)

        * R ("right") slides the left locator of the selection rightward.

        >>> p = Semantics("foo(^/)bar(/$)")
        >>> p.execute('R')
        >>> print str(p)
        foob(^/)ar(/$)
        >>> p = Semantics("foo(^/)(/$)bar")
        >>> p.execute('R')
        >>> print str(p)
        foo(^/)(/$)bar
        >>> p = Semantics("foo(^C)bar(C$)(^`/)C(`/$)")
        >>> p.execute('R')
        >>> print str(p)
        foob(^C)ar(C$)(^`/)C(`/$)
        >>> p = Semantics("The last time I saw Charlie")
        >>> p.execute('R')
        Traceback (most recent call last):
        ...
        UndefinedLocatorError: (^/)

        * E ("end") moves the left locator of the selection to immediately
          to the left of the right locator of the selection, resulting in
          the selection containing the zero-length string.

        >>> p = Semantics("foo(^/)bar(/$)baz")
        >>> p.execute('E')
        >>> print str(p)
        foobar(^/)(/$)baz
        >>> p = Semantics("foo(^a)b(^`/)a(`/$)r(a$)baz")
        >>> p.execute('E')
        >>> print str(p)
        foob(^`/)a(`/$)r(^a)(a$)baz
        >>> p = Semantics("The last time I saw Charlie")
        >>> p.execute('E')
        Traceback (most recent call last):
        ...
        UndefinedLocatorError: (^/)

        * F ("find") searches everywhere in the contents of the accumulator
          for the contents of the clipboard. If found, that substring is
          selected.

        >>> p = Semantics("(^?)By hook or by crook, we will.(?$)(^%)ook(%$)")
        >>> p.execute('F')
        >>> print str(p)
        (^?)By h(^/)ook(/$) or by crook, we will.(?$)(^%)ook(%$)

        * D ("drag-and-drop") moves the selection to the accumulator.

        >>> p = Semantics("(^/)hi(/$)(^?)lo(?$)")
        >>> p.execute('D')
        >>> print str(p)
        hi(^?)(^/)hi(/$)(?$)
        >>> p = Semantics("(^C)lo(C$)(^J)hi(J$)(^`/)J(`/$)(^`?)C(`?$)")
        >>> p.execute('D')
        >>> print str(p)
        (^C)(^J)hi(J$)(C$)hi(^`/)J(`/$)(^`?)C(`?$)

        * I ("input") waits for a line to appear on standard input, then
          places it (sans newline) in the accumulator.

        >>> from StringIO import StringIO
        >>> p = Semantics("(^?)(?$)")
        >>> p.input = StringIO(chr(10).join(["Line.", "Line!", "LINE!"]))
        >>> p.execute('I')
        >>> print str(p)
        (^?)Line.(?$)
        >>> p.execute('I')
        >>> print str(p)
        (^?)Line!(?$)
        >>> p.execute('I')
        >>> print str(p)
        (^?)LINE!(?$)
        >>> p.execute('I')
        >>> print str(p)
        (^?)(?$)

        * O ("output") outputs the string in the accumulator to standard
          output, followed by a newline.

        >>> p = Semantics("(^?)Hello, world!(?$)")
        >>> p.execute('O')
        Hello, world!
        >>> print str(p)
        (^?)Hello, world!(?$)

        Now we demonstrate some idioms.

        Assume the inital program defines some slots to contain initial
        data.  That data can then be loaded into the accumulator:

        >>> p = Semantics("(^0)data(0$)(^%)(%$)(^?)(?$)(^!)0(!$)SCAV")
        >>> p.run()
        >>> print str(p)
        (^0)data(0$)(^%)data(%$)(^?)(^/)data(/$)(?$)0SCAV(^!)(!$)

        New data, say the literal string 1, can be stored into slot 0 with:

        >>> p = Semantics("(^0)data(0$)(^%)(%$)(^?)(?$)(^!)1(!$)AC0SV")
        >>> p.run()
        >>> print str(p)
        (^0)(^/)1(/$)(0$)(^%)1(%$)(^?)0(?$)1AC0SV(^!)(!$)

        To copy from any arbitrary slot (say 0) to another (say 1), we can say:

        >>> p = Semantics("(^0)hi(0$)(^1)(1$)(^%)(%$)(^?)(?$)(^!)0(!$)SC1SV")
        >>> p.run()
        >>> print str(p)
        (^0)hi(0$)(^1)(^/)hi(/$)(1$)(^%)hi(%$)(^?)1(?$)0SC1SV(^!)(!$)

        Accessing a slot with a longer name, such as (^123)xyz(123$), can be
        done with the help of a free slot like 0:

        >>> p = Semantics("(^0)(0$)(^123)xyz(123$)(^%)(%$)(^?)(?$)(^!)1(!$)AC0SV2AC0SEV3AC0SEV0SCAVSD")
        >>> p.run()
        >>> print str(p)
        (^0)123(0$)(^123)xyz(123$)(^%)123(%$)(^?)(^/)xyz(/$)(?$)1AC0SV2AC0SEV3AC0SEV0SCAVSD(^!)(!$)

        To write data, say (^8)foo(8$), into a slot whose name is stored in
        another slot, such as (^9)jim(9$), we can say:

        >>> p = Semantics("(^8)foo(8$)(^9)jim(9$)(^jim)(jim$)(^%)(%$)(^?)(?$)(^!)8(!$)SC9SDSV")
        >>> p.run()
        >>> print str(p)
        (^8)foo(8$)(^9)jim(9$)(^jim)(^/)foo(/$)(jim$)(^%)foo(%$)(^?)jim(?$)8SC9SDSV(^!)(!$)

        Finally, a complete, if simple, program:

        >>> p = Semantics("(^?)Hello, world!(?$)(^!)O(!$)")
        >>> p.run()
        Hello, world!

        """
        if instruction >= '0' and instruction <= '9':
            self.update_slot(self.get_slot_name('?'), instruction)
        elif instruction == 'X':
            self.update_slot(self.get_slot_name('/'), '')
        elif instruction == 'C':
            self.update_slot(self.get_slot_name('%'), self.read_slot(self.get_slot_name('/')))
        elif instruction == 'V':
            self.update_slot(self.get_slot_name('/'), self.read_slot(self.get_slot_name('%')))
        elif instruction == 'S':
            self.deselect()
            locator_name = self.get_slot_name('/')
            new_selection = '(^%s)%s(%s$)' % (
                locator_name,
                self.read_slot_indirect(self.get_slot_name('?')),
                locator_name
            )
            self.update_slot_indirect(self.get_slot_name('?'), new_selection)
        elif instruction == 'A':
            self.deselect()
            locator_name = self.get_slot_name('/')
            new_selection = '(^%s)%s(%s$)' % (
                locator_name,
                self.read_slot(self.get_slot_name('?')),
                locator_name
            )
            self.update_slot(self.get_slot_name('?'), new_selection)
        elif instruction == 'L':
            locator_name = self.get_slot_name('/')
            self.slide_locator('(^%s)' % locator_name, -1)
        elif instruction == 'R':
            locator_name = self.get_slot_name('/')
            if self.read_slot(locator_name) != '':
                self.slide_locator('(^%s)' % locator_name, +1)
        elif instruction == 'E':
            locator_name = self.get_slot_name('/')
            self.remove_locator('(^%s)' % locator_name)
            pos = self.pos_left('(%s$)' % locator_name, 0)
            self.insert_locator('(^%s)' % locator_name, pos)
        elif instruction == 'F':
            accumulator = self.read_slot(self.get_slot_name('?'))
            clipboard = self.read_slot(self.get_slot_name('%'))
            pos = accumulator.find(clipboard)
            if pos >= 0:
                self.deselect()
                locator_name = self.get_slot_name('/')
                accumulator = MutableString(accumulator)
                accumulator.insert_locator('(^%s)' % locator_name, pos)
                pos_right = accumulator.pos_right('(^%s)' % locator_name, 0)
                accumulator.insert_locator('(%s$)' % locator_name,
                    pos_right + len(clipboard))
                self.update_slot(self.get_slot_name('?'), accumulator)
            else:
                pass
        elif instruction == 'D':
            locator_name = self.get_slot_name('/')
            selection = self.read_slot(locator_name)
            self.deselect()
            new_selection = '(^%s)%s(%s$)' % (
                locator_name,
                selection,
                locator_name
            )
            self.update_slot(self.get_slot_name('?'), new_selection)
        elif instruction == 'O':
            line = self.read_slot('?') + "\n"
            try:
                self.output.write(line.encode('UTF-8'))
            except UnicodeEncodeError:
                self.output.write(line.encode('ascii', 'xmlcharrefreplace'))
        elif instruction == 'I':
            text = self.input.readline()
            if text.endswith('\n'):
                text = text[:-1]
            self.update_slot(self.get_slot_name('?'), text)
        else:
            pass

    def step(self):
        """Execute one step of this Pophery program.

        """
        return super(Semantics, self).step()

    def run(self):
        """Execute this Pophery program and return only when it terminates.

        """
        return super(Semantics, self).run()


class TracedProgram(Semantics):
    """

    >>> p = TracedProgram("(^?)Hello, world!(?$)(^!)O(!$)OO")
    >>> p.run()
    [(^?)Hello, world!(?$)(^!)O(!$)OO]
    Hello, world!
    [(^?)Hello, world!(?$)O(^!)O(!$)O]
    Hello, world!
    [(^?)Hello, world!(?$)OO(^!)O(!$)]
    Hello, world!
    [(^?)Hello, world!(?$)OOO(^!)(!$)]

    """

    def __init__(self, initial):
        super(TracedProgram, self).__init__(initial)

    def run(self):
        print "[%s]" % str(self)
        super(TracedProgram, self).run()

    def step(self):
        result = super(TracedProgram, self).step()
        if result:
            print "[%s]" % str(self)
        return result



def main(argv):
    optparser = OptionParser("[python] %prog {options} {source.tranzy}\n" + __doc__)
    optparser.add_option("-e", "--evaluate",
                         action="store", type="string", dest="program", default=None,
                         help="evaluate Pophery program on command line")
    optparser.add_option("-l", "--show-license",
                         action="store_true", dest="show_license", default=False,
                         help="show product license and exit")
    optparser.add_option("-t", "--trace",
                         action="store_true", dest="trace", default=False,
                         help="trace execution during run")
    optparser.add_option("-T", "--run-tests",
                         action="store_true", dest="run_tests", default=False,
                         help="run self-tests and exit")
    (options, args) = optparser.parse_args(argv[1:])
    exit_code = None
    if options.show_license:
        print sys.argv[0]
        print __doc__
        print LICENSE
        exit_code = 0
    if options.run_tests:
        import doctest
        (fails, something) = doctest.testmod()
        if fails == 0:
            print "All tests passed."
            exit_code = 0
        else:
            exit_code = 1

    if exit_code is not None:
        sys.exit(exit_code)

    klass = Semantics
    if options.trace:
        klass = TracedProgram

    if options.program is not None:
        klass(options.program).run()

    for filename in args:
        program = klass('')
        program.load(filename)
        program.run()


if __name__ == "__main__":
    main(sys.argv)
