"""Tests for AST data types."""
from pyrooplpp.syntax import *


class TestASTTypes:
    def test_const_creation(self):
        c = Const(42)
        assert c.value == 42

    def test_var_creation(self):
        v = Var("x")
        assert v.name == "x"

    def test_binary_creation(self):
        b = Binary(BinOp.Add, Const(1), Const(2))
        assert b.op == BinOp.Add
        assert b.left == Const(1)
        assert b.right == Const(2)

    def test_frozen_dataclass(self):
        """AST nodes should be immutable."""
        c = Const(1)
        with __import__("pytest").raises(AttributeError):
            c.value = 2

    def test_assign_statement(self):
        a = Assign(VarArray("x"), ModOp.ModAdd, Const(5))
        assert a.op == ModOp.ModAdd

    def test_swap_statement(self):
        s = Swap(VarArray("x"), VarArray("y"))
        assert s.left == VarArray("x")
        assert s.right == VarArray("y")

    def test_class_decl(self):
        c = CDecl("Foo", None, [Decl(IntegerType(), "x")], [])
        assert c.name == "Foo"
        assert c.inherits is None
        assert len(c.fields) == 1

    def test_class_with_inheritance(self):
        c = CDecl("Sub", "Super", [], [])
        assert c.inherits == "Super"

    def test_prog(self):
        p = Prog([CDecl("P", None, [], [])])
        assert len(p.classes) == 1

    def test_method_decl(self):
        m = MDecl("main", [Decl(IntegerType(), "n")], [Skip()])
        assert m.name == "main"
        assert len(m.params) == 1
        assert len(m.body) == 1

    def test_all_modops(self):
        assert ModOp.ModAdd != ModOp.ModSub
        assert ModOp.ModSub != ModOp.ModXor

    def test_all_binops(self):
        ops = list(BinOp)
        assert len(ops) == 16  # 16 binary operators
