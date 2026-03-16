"""Tests for the pretty printer."""
from pyrooplpp.pretty import *
from pyrooplpp.syntax import *


class TestPrettyExp:
    def test_const(self):
        assert pretty_exp(Const(42)) == "42"

    def test_var(self):
        assert pretty_exp(Var("x")) == "x"

    def test_nil(self):
        assert pretty_exp(Nil()) == "nil"

    def test_array_element(self):
        assert pretty_exp(ArrayElement("a", Const(0))) == "a[0]"

    def test_binary(self):
        assert pretty_exp(Binary(BinOp.Add, Const(1), Const(2))) == "1 + 2"

    def test_dot(self):
        assert pretty_exp(Dot(Var("x"), Var("y"))) == "x.y"


class TestPrettyObj:
    def test_var(self):
        assert pretty_obj(VarArray("x")) == "x"

    def test_array(self):
        assert pretty_obj(VarArray("a", Const(0))) == "a[0]"

    def test_inst_var(self):
        assert pretty_obj(InstVar(VarArray("x"), VarArray("y"))) == "x.y"


class TestPrettyStm:
    def test_assign(self):
        s = pretty_stm(Assign(VarArray("x"), ModOp.ModAdd, Const(1)), 0)
        assert s == "x += 1"

    def test_swap(self):
        s = pretty_stm(Swap(VarArray("x"), VarArray("y")), 0)
        assert s == "x <=> y"

    def test_skip(self):
        assert pretty_stm(Skip(), 0) == "skip"

    def test_show(self):
        assert pretty_stm(Show(Var("x")), 0) == "show(x)"

    def test_print(self):
        assert pretty_stm(Print("hello"), 0) == 'print("hello")'

    def test_print_escape_newline(self):
        assert pretty_stm(Print("a\nb"), 0) == 'print("a\\nb")'

    def test_local_call(self):
        s = pretty_stm(LocalCall("foo", [IdArg("x"), IdArg("y")]), 0)
        assert s == "call foo(x, y)"

    def test_object_call(self):
        s = pretty_stm(ObjectCall(VarArray("f"), "bar", [IdArg("x")]), 0)
        assert s == "call f::bar(x)"

    def test_uncall(self):
        s = pretty_stm(LocalUncall("foo", []), 0)
        assert s == "uncall foo()"

    def test_new(self):
        s = pretty_stm(ObjectConstruction("Foo", VarArray("f")), 0)
        assert s == "new Foo f"

    def test_delete(self):
        s = pretty_stm(ObjectDestruction("Foo", VarArray("f")), 0)
        assert s == "delete Foo f"

    def test_array_new(self):
        s = pretty_stm(ArrayConstruction("int", Const(5), VarArray("a")), 0)
        assert s == "new int[5] a"

    def test_copy(self):
        s = pretty_stm(CopyReference(ObjectType("Foo"), VarArray("x"), VarArray("y")), 0)
        assert s == "copy Foo x y"


class TestPrettyDecl:
    def test_int_decl(self):
        assert pretty_decl(Decl(IntegerType(), "x")) == "int x"

    def test_array_decl(self):
        assert pretty_decl(Decl(IntegerArrayType(), "a")) == "int[] a"

    def test_object_decl(self):
        assert pretty_decl(Decl(ObjectType("Foo"), "f")) == "Foo f"


class TestPrettyProg:
    def test_roundtrip(self):
        """Parse -> pretty-print -> parse should yield the same AST."""
        src = """class Program
    int x
    method main()
        x += 1
"""
        from pyrooplpp.parser import parse
        prog1 = parse(src)
        printed = pretty_prog(prog1)
        prog2 = parse(printed)
        assert prog1 == prog2
