# -*- coding: utf-8 -*-

"""
Semantics for the Pophery Programming Language, Version Minus One.

These are the original semantics I devised for Pophery, but ended up not
liking.  But I couldn't bear to throw them away either, so I stuffed them
into this (basically throw-away) language.

I don't think these semantics are Turing-complete.

Actually getting this to run will take a little hacking around with this file
and pophery.py, but should not be very hard.

"""


from pophery import Program


class Semantics(Program):
    def execute(self, instruction):
        """Apply the semantics of the given instruction to this Program.

        >>> p = Semantics("(^?)(?$)")
        >>> p.execute('0')
        >>> print str(p)
        (^?)0(?$)

        >>> p = Semantics("(^@)(@$)")
        >>> p.execute('@')
        >>> print str(p)
        (^@)@(@$)
        >>> p = Semantics("(^`@)Jim(`@$)(^Jim)?(Jim$)")
        >>> p.execute('@')
        >>> print str(p)
        (^`@)Jim(`@$)(^Jim)Jim(Jim$)

        >>> p = Semantics("(^?)(?$)(^@)0(@$)(^0)Seven(0$)")
        >>> p.execute('G')
        >>> print str(p)
        (^?)Seven(?$)(^@)0(@$)(^0)Seven(0$)

        >>> p = Semantics("(^?)Meerkat(?$)(^@)0(@$)(^0)Seven(0$)")
        >>> p.execute('P')
        >>> print str(p)
        (^?)Meerkat(?$)(^@)0(@$)(^0)Meerkat(0$)

        >>> p = Semantics("(^?)!(?$)(^@)0(@$)(^0)Fenesrate(0$)")
        >>> p.execute('A')
        >>> print str(p)
        (^?)!(?$)(^@)0(@$)(^0)!Fenesrate(0$)
        >>> p.execute('Z')
        >>> print str(p)
        (^?)!(?$)(^@)0(@$)(^0)!Fenesrate!(0$)

        >>> p = Semantics("(^@)0(@$)(^0)Seven(0$)")
        >>> p.execute('X')
        >>> print str(p)
        (^@)0(@$)(^0)(0$)

        >>> p = Semantics("(^@)0(@$)(^0)Licorice(0$)(^%)(%$)")
        >>> p.execute('C')
        >>> print str(p)
        (^@)0(@$)(^0)Licorice(0$)(^%)Licorice(%$)

        >>> p = Semantics("(^@)0(@$)(^0)Rock(0$)(^%)well(%$)")
        >>> p.execute('V')
        >>> print str(p)
        (^@)0(@$)(^0)Rockwell(0$)(^%)well(%$)

        >>> p = Semantics("(^@)0(@$)(^0)Rock(0$)(^%)well(%$)")
        >>> p.execute('V')
        >>> print str(p)
        (^@)0(@$)(^0)Rockwell(0$)(^%)well(%$)

        >>> p = Semantics("(^?)Hello, world!(?$)")
        >>> p.execute('O')
        Hello, world!
        >>> print str(p)
        (^?)Hello, world!(?$)

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

        """
        if instruction >= '0' and instruction <= '9':
            self.update_slot(self.get_slot_name('?'), instruction)
        elif instruction == '@':
            self.update_slot(self.get_slot_name('@'), self.get_slot_name('@'))
        elif instruction == 'G':
            self.update_slot(self.get_slot_name('?'), self.read_slot_indirect(self.get_slot_name('@')))
        elif instruction == 'P':
            self.update_slot_indirect(self.get_slot_name('@'), self.read_slot('?'))
        elif instruction == 'A':
            value = self.read_slot('?') + self.read_slot_indirect(self.get_slot_name('@'))
            self.update_slot_indirect(self.get_slot_name('@'), value)
        elif instruction == 'Z':
            value = self.read_slot_indirect(self.get_slot_name('@')) + self.read_slot('?') 
            self.update_slot_indirect(self.get_slot_name('@'), value)
        elif instruction == 'X':
            self.update_slot_indirect(self.get_slot_name('@'), '')
        elif instruction == 'C':
            self.update_slot(self.get_slot_name('%'), self.read_slot_indirect(self.get_slot_name('@')))
        elif instruction == 'V':
            value = self.read_slot_indirect(self.get_slot_name('@')) + self.read_slot('%')
            self.update_slot_indirect(self.get_slot_name('@'), value)
        elif instruction == 'O':
            line = self.read_slot('?') + "\n"
            try:
                self.output.write(line)
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

        >>> p = Semantics("(^?)Hello, world!(?$)(^!)O(!$)")
        >>> p.step()
        Hello, world!
        True
        >>> print str(p)
        (^?)Hello, world!(?$)O(^!)(!$)
        >>> p.step()
        False
        >>> print str(p)
        (^?)Hello, world!(?$)O(^!)(!$)

        """
        return super(Semantics, self).step()

    def run(self):
        """Execute this Pophery program and return only when it terminates.

        >>> p = Semantics("(^?)Hello, world!(?$)(^!)O(!$)OO")
        >>> p.run()
        Hello, world!
        Hello, world!
        Hello, world!

        >>> p = Semantics("(^0)Load Me(0$)(^?)(?$)(^@)(@$) (^!)0(!$)@PG")
        >>> p.run()
        >>> print str(p)
        (^0)Load Me(0$)(^?)Load Me(?$)(^@)0(@$) 0@PG(^!)(!$)

        >>> p = Semantics("(^0)Overwrite Me(0$)(^?)(?$)(^@)(@$) (^!)0(!$)@P1P")
        >>> p.run()
        >>> print str(p)
        (^0)1(0$)(^?)1(?$)(^@)0(@$) 0@P1P(^!)(!$)

        Accessing a slot with a longer name can be done with the help of a free slot:
        
        >>> p = Semantics("(^123)xyz(123$)(^0)(0$)(^?)(?$)(^@)(@$) (^!)0(!$)@P1P2Z3ZG@PG")
        >>> p.run()
        >>> print str(p)
        (^123)xyz(123$)(^0)123(0$)(^?)xyz(?$)(^@)123(@$) 0@P1P2Z3ZG@PG(^!)(!$)

        Let's use the clipboard to construct that name instead:

        >>> p = Semantics("(^123)xyz(123$)(^0)(0$)(^1)(1$)(^?)(?$)(^@)(@$)(^%)(%$) (^!) (!$)0@P1PC1@PV 0@P2PC1@PV 0@P3PC1@PV 1@PG@PG")
        >>> p.run()
        >>> print str(p)
        (^123)xyz(123$)(^0)3(0$)(^1)123(1$)(^?)xyz(?$)(^@)123(@$)(^%)3(%$)  0@P1PC1@PV 0@P2PC1@PV 0@P3PC1@PV 1@PG@PG(^!)(!$)

        To copy from one arbitrary slot to another, we can use the clipboard:

        >>> p = Semantics("(^0)Copy Me(0$)(^1)Overwrite Me(1$)(^?)(?$)(^@)(@$)(^%)(%$) (^!)0(!$)0@PC1@PXV")
        >>> p.run()
        >>> print str(p)
        (^0)Copy Me(0$)(^1)Copy Me(1$)(^?)1(?$)(^@)1(@$)(^%)Copy Me(%$) 00@PC1@PXV(^!)(!$)

        We can also use the clipboard "cut" command to halt the program, like so:

        >>> p = Semantics("(^0)!(0$)(^?)(?$)(^@)(@$) (^!)0(!$)0@PG@PXOOOOO")
        >>> p.run()
        >>> print str(p)
        (^0)!(0$)(^?)!(?$)(^@)!(@$) 00@PG@PO(^!)(!$)OOOO

        """
        return super(Semantics, self).run()
