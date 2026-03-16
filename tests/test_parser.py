"""Tests for the ROOPL++ parser."""
import pytest
from pyrooplpp.parser import parse, ParseError
from pyrooplpp.syntax import *


class TestParseExpressions:
    def _parse_exp(self, src: str) -> Exp:
        """Helper: parse a minimal program and extract the expression from x ^= <exp>."""
        prog = parse(f"class Program\n    int x\n    method main()\n        x ^= {src}")
        stm = prog.classes[0].methods[0].body[0]
        assert isinstance(stm, Assign)
        return stm.exp

    def test_const(self):
        assert self._parse_exp("42") == Const(42)

    def test_nil(self):
        assert self._parse_exp("nil") == Nil()

    def test_var(self):
        assert self._parse_exp("y") == Var("y")

    def test_binary_add(self):
        e = self._parse_exp("1 + 2")
        assert isinstance(e, Binary)
        assert e.op == BinOp.Add

    def test_binary_precedence(self):
        e = self._parse_exp("1 + 2 * 3")
        # Should be 1 + (2 * 3)
        assert isinstance(e, Binary)
        assert e.op == BinOp.Add
        assert isinstance(e.right, Binary)
        assert e.right.op == BinOp.Mul

    def test_parenthesized(self):
        e = self._parse_exp("(1 + 2) * 3")
        assert isinstance(e, Binary)
        assert e.op == BinOp.Mul
        assert isinstance(e.left, Binary)

    def test_unary_minus(self):
        e = self._parse_exp("0 - 1")
        assert isinstance(e, Binary)
        assert e.op == BinOp.Sub

    def test_comparison(self):
        e = self._parse_exp("1 < 2")
        assert isinstance(e, Binary)
        assert e.op == BinOp.Lt

    def test_logical_and(self):
        e = self._parse_exp("1 && 2")
        assert isinstance(e, Binary)
        assert e.op == BinOp.And

    def test_array_element(self):
        e = self._parse_exp("a[0]")
        assert isinstance(e, ArrayElement)
        assert e.name == "a"


class TestParseStatements:
    def _parse_stm(self, src: str) -> Stm:
        prog = parse(f"class Program\n    int x\n    int y\n    int[] a\n    method main()\n        {src}")
        return prog.classes[0].methods[0].body[0]

    def test_skip(self):
        assert isinstance(self._parse_stm("skip"), Skip)

    def test_assign_add(self):
        s = self._parse_stm("x += 1")
        assert isinstance(s, Assign)
        assert s.op == ModOp.ModAdd

    def test_assign_sub(self):
        s = self._parse_stm("x -= 1")
        assert isinstance(s, Assign)
        assert s.op == ModOp.ModSub

    def test_assign_xor(self):
        s = self._parse_stm("x ^= 1")
        assert isinstance(s, Assign)
        assert s.op == ModOp.ModXor

    def test_swap(self):
        s = self._parse_stm("x <=> y")
        assert isinstance(s, Swap)

    def test_conditional(self):
        s = self._parse_stm("if x = 1 then\n            y += 1\n        else\n            skip\n        fi x = 1")
        assert isinstance(s, Conditional)

    def test_for_loop(self):
        s = self._parse_stm("for i in (1..10) do\n            x += 1\n        end")
        assert isinstance(s, For)
        assert s.var == "i"

    def test_show(self):
        s = self._parse_stm("show(x)")
        assert isinstance(s, Show)

    def test_print(self):
        s = self._parse_stm('print("hello")')
        assert isinstance(s, Print)
        assert s.text == "hello"


class TestParseProgram:
    def test_minimal_program(self):
        prog = parse("class Program\n    int x\n    method main()\n        x ^= 1")
        assert len(prog.classes) == 1
        assert prog.classes[0].name == "Program"
        assert len(prog.classes[0].fields) == 1
        assert len(prog.classes[0].methods) == 1

    def test_two_classes(self):
        src = """class Foo
    method bar()
        skip

class Program
    int x
    method main()
        x ^= 1"""
        prog = parse(src)
        assert len(prog.classes) == 2
        assert prog.classes[0].name == "Foo"
        assert prog.classes[1].name == "Program"

    def test_inheritance(self):
        src = """class Base
    int x
    method foo()
        skip

class Sub inherits Base
    int y
    method bar()
        skip

class Program
    int z
    method main()
        z ^= 1"""
        prog = parse(src)
        assert prog.classes[1].inherits == "Base"

    def test_method_params(self):
        src = """class Foo
    method bar(int a, int b)
        skip

class Program
    int x
    method main()
        x ^= 1"""
        prog = parse(src)
        m = prog.classes[0].methods[0]
        assert len(m.params) == 2

    def test_loop_do_and_loop(self):
        src = """class Program
    int x
    method main()
        from x = 0 do
            x += 1
        loop
            x += 1
        until x = 10"""
        prog = parse(src)
        stm = prog.classes[0].methods[0].body[0]
        assert isinstance(stm, Loop)

    def test_local_delocal(self):
        src = """class Program
    int x
    method main()
        local int y = 0
        x += y
        delocal int y = 0"""
        prog = parse(src)
        stm = prog.classes[0].methods[0].body[0]
        assert isinstance(stm, LocalBlock)

    def test_object_construction(self):
        src = """class Foo
    method bar()
        skip

class Program
    int x
    method main()
        local Foo f = nil
        new Foo f
        delete Foo f
        delocal Foo f = nil"""
        prog = parse(src)
        body = prog.classes[1].methods[0].body
        assert isinstance(body[0], LocalBlock)

    def test_parse_error(self):
        with pytest.raises(Exception):
            parse("class")


class TestParseExampleFiles:
    """Test that example files parse without error (sampled)."""

    SAMPLES = ["fib.rplpp", "factor.rplpp", "sqrt.rplpp", "for.rplpp", "switch.rplpp"]

    @pytest.fixture(params=SAMPLES)
    def example_source(self, request):
        import os
        path = os.path.join(os.path.dirname(__file__), "..", "example", request.param)
        if not os.path.exists(path):
            pytest.skip(f"{request.param} not found")
        with open(path) as f:
            return f.read()

    def test_parse_example(self, example_source):
        prog = parse(example_source)
        assert isinstance(prog, Prog)
        assert len(prog.classes) >= 1
