"""Advanced inversion tests for switch and complex structures."""
import pytest
from pyrooplpp.syntax import *
from pyrooplpp.invert import invert, invert_stm, invert_prog, _invert_cases
from pyrooplpp.parser import parse
from pyrooplpp.eval import eval_prog
from pyrooplpp.value import IntVal


class TestInvertSwitch:
    def test_simple_switch_inversion(self):
        src = """class Program
    int x
    method main()
        x ^= 1
        switch x
            case 0 skip esac 0 break
            case 1 skip esac 1 break
            default skip break
        hctiws x"""
        prog = parse(src)
        inv = invert_prog(prog)
        assert isinstance(inv, Prog)

    def test_switch_eval_and_invert(self):
        src = """class Program
    int x
    method main()
        x ^= 7
        switch x
            case 0 skip esac 0 break
            case 5 skip esac 5 break
            default skip break
        hctiws x"""
        r = dict(eval_prog(parse(src)))
        assert r["x"] == IntVal(7)


class TestInvertComplexPrograms:
    def test_invert_for_with_body(self):
        stms = [For("i", Const(1), Const(10), [
            Assign(VarArray("x"), ModOp.ModAdd, Const(1))
        ])]
        inv = invert(stms)
        assert isinstance(inv[0], For)
        assert inv[0].start == Const(10)
        assert inv[0].end == Const(1)
        assert inv[0].body[0].op == ModOp.ModSub

    def test_invert_nested_conditional(self):
        inner = Conditional(Const(1), [Skip()], [Skip()], Const(2))
        outer = Conditional(Const(3), [inner], [Skip()], Const(4))
        inv = invert_stm(outer)
        assert inv.test == Const(4)
        assert isinstance(inv.then_branch[0], Conditional)
        assert inv.then_branch[0].test == Const(2)

    def test_invert_loop_with_both_bodies(self):
        loop = Loop(Const(1),
                    [Assign(VarArray("x"), ModOp.ModAdd, Const(1))],
                    [Assign(VarArray("y"), ModOp.ModSub, Const(2))],
                    Const(3))
        inv = invert_stm(loop)
        assert inv.from_exp == Const(3)
        assert inv.until == Const(1)
        assert inv.do_body[0].op == ModOp.ModSub  # was Add
        assert inv.loop_body[0].op == ModOp.ModAdd  # was Sub


class TestInvertCases:
    def test_empty(self):
        assert _invert_cases([]) == []

    def test_single_break(self):
        entry = ((Case.Case, [Const(1)]), [Skip()], (Esac.Esac, [Const(1)], Break.Break))
        result = _invert_cases([entry])
        assert len(result) == 1
