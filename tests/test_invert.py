"""Tests for program inversion."""
import pytest
from pyrooplpp.syntax import *
from pyrooplpp.invert import invert, invert_stm, invert_prog
from pyrooplpp.parser import parse


class TestInvertStatements:
    def test_skip(self):
        assert invert_stm(Skip()) == Skip()

    def test_assign_add_to_sub(self):
        s = invert_stm(Assign(VarArray("x"), ModOp.ModAdd, Const(1)))
        assert isinstance(s, Assign)
        assert s.op == ModOp.ModSub

    def test_assign_sub_to_add(self):
        s = invert_stm(Assign(VarArray("x"), ModOp.ModSub, Const(1)))
        assert s.op == ModOp.ModAdd

    def test_assign_xor_self_inverse(self):
        s = invert_stm(Assign(VarArray("x"), ModOp.ModXor, Const(1)))
        assert s.op == ModOp.ModXor

    def test_swap_self_inverse(self):
        s = invert_stm(Swap(VarArray("x"), VarArray("y")))
        assert isinstance(s, Swap)
        assert s.left == VarArray("x")
        assert s.right == VarArray("y")

    def test_conditional_swap_assertions(self):
        s = invert_stm(Conditional(Const(1), [Skip()], [Skip()], Const(2)))
        assert isinstance(s, Conditional)
        assert s.test == Const(2)  # entry and exit assertions swapped
        assert s.fi == Const(1)

    def test_loop_swap_assertions(self):
        s = invert_stm(Loop(Const(1), [Skip()], [Skip()], Const(2)))
        assert isinstance(s, Loop)
        assert s.from_exp == Const(2)
        assert s.until == Const(1)

    def test_for_swap_bounds(self):
        s = invert_stm(For("i", Const(1), Const(10), [Skip()]))
        assert isinstance(s, For)
        assert s.start == Const(10)
        assert s.end == Const(1)

    def test_call_to_uncall(self):
        s = invert_stm(LocalCall("foo", []))
        assert isinstance(s, LocalUncall)
        assert s.method == "foo"

    def test_uncall_to_call(self):
        s = invert_stm(LocalUncall("foo", []))
        assert isinstance(s, LocalCall)

    def test_object_call_to_uncall(self):
        s = invert_stm(ObjectCall(VarArray("f"), "bar", []))
        assert isinstance(s, ObjectUncall)

    def test_new_to_delete(self):
        s = invert_stm(ObjectConstruction("Foo", VarArray("f")))
        assert isinstance(s, ObjectDestruction)

    def test_delete_to_new(self):
        s = invert_stm(ObjectDestruction("Foo", VarArray("f")))
        assert isinstance(s, ObjectConstruction)

    def test_copy_to_uncopy(self):
        s = invert_stm(CopyReference(IntegerType(), VarArray("x"), VarArray("y")))
        assert isinstance(s, UncopyReference)

    def test_uncopy_to_copy(self):
        s = invert_stm(UncopyReference(IntegerType(), VarArray("x"), VarArray("y")))
        assert isinstance(s, CopyReference)

    def test_array_new_to_delete(self):
        s = invert_stm(ArrayConstruction("int", Const(5), VarArray("a")))
        assert isinstance(s, ArrayDestruction)

    def test_show_unchanged(self):
        s = invert_stm(Show(Var("x")))
        assert isinstance(s, Show)

    def test_print_unchanged(self):
        s = invert_stm(Print("hello"))
        assert isinstance(s, Print)

    def test_local_block_swap_init_final(self):
        s = invert_stm(LocalBlock(IntegerType(), "x", Const(1), [Skip()], Const(2)))
        assert isinstance(s, LocalBlock)
        assert s.init == Const(2)
        assert s.final == Const(1)

    def test_object_block(self):
        s = invert_stm(ObjectBlock("Foo", "f", [Skip()]))
        assert isinstance(s, ObjectBlock)


class TestInvertList:
    def test_reverses_order(self):
        stms = [
            Assign(VarArray("x"), ModOp.ModAdd, Const(1)),
            Assign(VarArray("y"), ModOp.ModSub, Const(2)),
        ]
        inv = invert(stms)
        assert len(inv) == 2
        # Order reversed
        assert inv[0].obj == VarArray("y")
        assert inv[1].obj == VarArray("x")
        # Operations inverted
        assert inv[0].op == ModOp.ModAdd  # was Sub
        assert inv[1].op == ModOp.ModSub  # was Add

    def test_double_invert_identity(self):
        stms = [
            Assign(VarArray("x"), ModOp.ModAdd, Const(1)),
            Assign(VarArray("y"), ModOp.ModXor, Const(3)),
            Swap(VarArray("a"), VarArray("b")),
        ]
        assert invert(invert(stms)) == stms


class TestInvertProg:
    def test_inverts_all_methods(self):
        src = """class Program
    int x
    method main()
        x += 1"""
        prog = parse(src)
        inv = invert_prog(prog)
        assert isinstance(inv, Prog)
        body = inv.classes[0].methods[0].body
        assert body[0].op == ModOp.ModSub

    def test_inverted_preserves_structure(self):
        """Inverted program preserves class/method structure."""
        src = """class Program
    int x
    int y
    method main()
        x ^= 5
        y ^= 3
        x += y"""
        prog = parse(src)
        inv = invert_prog(prog)
        assert len(inv.classes) == len(prog.classes)
        assert inv.classes[0].name == prog.classes[0].name
        assert len(inv.classes[0].methods) == len(prog.classes[0].methods)
