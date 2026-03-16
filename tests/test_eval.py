"""Tests for the ROOPL++ evaluator."""
import pytest
from pyrooplpp.parser import parse
from pyrooplpp.eval import (
    eval_prog, eval_exp, eval_state, ext_envs, ext_st, ext_st_zero,
    lookup_envs, lookup_st, lookup_val, lookup_vec,
    safe_div, safe_mod, bin_op, gen_locsvec, max_locs,
)
from pyrooplpp.value import *
from pyrooplpp.syntax import *


# --- Environment/Store unit tests ---

class TestEnvOps:
    def test_ext_envs_new(self):
        env = ext_envs({}, "x", 1)
        assert env["x"] == 1

    def test_ext_envs_overwrite(self):
        env = ext_envs({"x": 1}, "x", 2)
        assert env["x"] == 2

    def test_ext_envs_preserve_others(self):
        env = ext_envs({"y": 10}, "x", 1)
        assert env["y"] == 10
        assert env["x"] == 1

    def test_lookup_envs_found(self):
        assert lookup_envs("x", {"x": 1, "y": 2}) == 1

    def test_lookup_envs_not_found(self):
        with pytest.raises(RuntimeError, match="unbound variable"):
            lookup_envs("z", {"x": 1})


class TestStoreOps:
    def test_ext_st(self):
        st = ext_st({}, 1, IntVal(42))
        assert st[1] == IntVal(42)

    def test_ext_st_overwrite(self):
        st = ext_st({1: IntVal(10)}, 1, IntVal(20))
        assert st[1] == IntVal(20)

    def test_lookup_st_found(self):
        assert lookup_st(1, {1: IntVal(5)}) == IntVal(5)

    def test_lookup_st_not_found(self):
        with pytest.raises(RuntimeError, match="unbound locations"):
            lookup_st(99, {})

    def test_ext_st_zero(self):
        st = ext_st_zero({}, 1, 3)
        assert st[1] == IntVal(0)
        assert st[2] == IntVal(0)
        assert st[3] == IntVal(0)

    def test_ext_st_zero_empty(self):
        st = ext_st_zero({5: IntVal(9)}, 1, 0)
        assert st == {5: IntVal(9)}

    def test_lookup_val(self):
        assert lookup_val("x", {"x": 1}, {1: IntVal(7)}) == IntVal(7)

    def test_lookup_vec(self):
        assert lookup_vec(0, [10, 20, 30]) == 10
        assert lookup_vec(2, [10, 20, 30]) == 30

    def test_lookup_vec_oob(self):
        with pytest.raises(RuntimeError, match="out of bounds"):
            lookup_vec(5, [10, 20])

    def test_lookup_vec_negative(self):
        with pytest.raises(RuntimeError, match="negative index"):
            lookup_vec(-1, [10, 20])

    def test_store_with_objval(self):
        st = ext_st({}, 1, ObjVal("Foo", {"x": 2}))
        assert lookup_st(1, st) == ObjVal("Foo", {"x": 2})

    def test_store_with_locsval(self):
        st = ext_st({}, 1, LocsVal(5))
        assert lookup_st(1, st) == LocsVal(5)

    def test_store_with_locsvec(self):
        st = ext_st({}, 1, LocsVec([2, 3, 4]))
        assert lookup_st(1, st) == LocsVec([2, 3, 4])


class TestArithmetic:
    def test_safe_div(self):
        assert safe_div(10, 3) == 3
        assert safe_div(-7, 2) == -3  # truncate toward zero

    def test_safe_div_by_zero(self):
        with pytest.raises(RuntimeError, match="division by zero"):
            safe_div(1, 0)

    def test_safe_mod(self):
        assert safe_mod(10, 3) == 1
        assert safe_mod(-7, 2) == -1  # sign follows dividend

    def test_safe_mod_by_zero(self):
        with pytest.raises(RuntimeError, match="modulo by zero"):
            safe_mod(1, 0)

    def test_bin_op_add(self):
        assert bin_op(lambda a, b: a + b, IntVal(3), IntVal(4)) == IntVal(7)

    def test_bin_op_type_error(self):
        with pytest.raises(RuntimeError, match="integer values expected"):
            bin_op(lambda a, b: a + b, IntVal(1), LocsVal(2))


class TestHelpers:
    def test_gen_locsvec(self):
        assert gen_locsvec(3, 10) == [10, 11, 12]
        assert gen_locsvec(0, 5) == []

    def test_max_locs_empty(self):
        assert max_locs({}) == 0

    def test_max_locs(self):
        assert max_locs({1: IntVal(0), 5: IntVal(0), 3: IntVal(0)}) == 5


# --- Expression evaluation ---

class TestEvalExp:
    def test_const(self):
        assert eval_exp(Const(42), {}, {}) == IntVal(42)

    def test_nil(self):
        assert eval_exp(Nil(), {}, {}) == IntVal(0)

    def test_var(self):
        assert eval_exp(Var("x"), {"x": 1}, {1: IntVal(7)}) == IntVal(7)

    def test_binary_add(self):
        assert eval_exp(Binary(BinOp.Add, Const(3), Const(4)), {}, {}) == IntVal(7)

    def test_binary_sub(self):
        assert eval_exp(Binary(BinOp.Sub, Const(10), Const(3)), {}, {}) == IntVal(7)

    def test_binary_mul(self):
        assert eval_exp(Binary(BinOp.Mul, Const(6), Const(7)), {}, {}) == IntVal(42)

    def test_binary_xor(self):
        assert eval_exp(Binary(BinOp.Xor, Const(5), Const(3)), {}, {}) == IntVal(6)

    def test_binary_div(self):
        assert eval_exp(Binary(BinOp.Div, Const(10), Const(3)), {}, {}) == IntVal(3)

    def test_binary_mod(self):
        assert eval_exp(Binary(BinOp.Mod, Const(10), Const(3)), {}, {}) == IntVal(1)

    def test_binary_and(self):
        assert eval_exp(Binary(BinOp.And, Const(1), Const(1)), {}, {}) == IntVal(1)
        assert eval_exp(Binary(BinOp.And, Const(1), Const(0)), {}, {}) == IntVal(0)

    def test_binary_or(self):
        assert eval_exp(Binary(BinOp.Or, Const(0), Const(1)), {}, {}) == IntVal(1)
        assert eval_exp(Binary(BinOp.Or, Const(0), Const(0)), {}, {}) == IntVal(0)

    def test_binary_eq(self):
        assert eval_exp(Binary(BinOp.Eq, Const(5), Const(5)), {}, {}) == IntVal(1)
        assert eval_exp(Binary(BinOp.Eq, Const(5), Const(6)), {}, {}) == IntVal(0)

    def test_binary_ne(self):
        assert eval_exp(Binary(BinOp.Ne, Const(1), Const(2)), {}, {}) == IntVal(1)

    def test_binary_lt(self):
        assert eval_exp(Binary(BinOp.Lt, Const(1), Const(2)), {}, {}) == IntVal(1)
        assert eval_exp(Binary(BinOp.Lt, Const(2), Const(1)), {}, {}) == IntVal(0)

    def test_binary_le(self):
        assert eval_exp(Binary(BinOp.Le, Const(2), Const(2)), {}, {}) == IntVal(1)

    def test_binary_gt(self):
        assert eval_exp(Binary(BinOp.Gt, Const(3), Const(2)), {}, {}) == IntVal(1)

    def test_binary_ge(self):
        assert eval_exp(Binary(BinOp.Ge, Const(2), Const(2)), {}, {}) == IntVal(1)

    def test_binary_band(self):
        assert eval_exp(Binary(BinOp.Band, Const(6), Const(3)), {}, {}) == IntVal(2)

    def test_binary_bor(self):
        assert eval_exp(Binary(BinOp.Bor, Const(6), Const(3)), {}, {}) == IntVal(7)

    def test_array_element(self):
        env = {"a": 1}
        st = {1: LocsVec([2, 3, 4]), 2: IntVal(10), 3: IntVal(20), 4: IntVal(30)}
        assert eval_exp(ArrayElement("a", Const(0)), env, st) == IntVal(10)
        assert eval_exp(ArrayElement("a", Const(2)), env, st) == IntVal(30)

    def test_array_out_of_bounds(self):
        env = {"a": 1}
        st = {1: LocsVec([2, 3]), 2: IntVal(10), 3: IntVal(20)}
        with pytest.raises(RuntimeError, match="out of bounds"):
            eval_exp(ArrayElement("a", Const(5)), env, st)


# --- Full program evaluation ---

class TestEvalProg:
    def test_simple_xor(self):
        prog = parse("class Program\n    int x\n    method main()\n        x ^= 42")
        result = eval_prog(prog)
        assert ("x", IntVal(42)) in result

    def test_assign_add(self):
        prog = parse("class Program\n    int x\n    method main()\n        x ^= 3\n        x += 7")
        result = eval_prog(prog)
        assert ("x", IntVal(10)) in result

    def test_swap(self):
        prog = parse("class Program\n    int x\n    int y\n    method main()\n        x ^= 3\n        y ^= 7\n        x <=> y")
        result = eval_prog(prog)
        assert ("x", IntVal(7)) in result
        assert ("y", IntVal(3)) in result

    def test_conditional_true(self):
        src = """class Program
    int x
    int y
    method main()
        x ^= 1
        if x = 1 then
            y += 10
        else
            y += 20
        fi y = 10"""
        result = eval_prog(parse(src))
        assert ("y", IntVal(10)) in result

    def test_conditional_false(self):
        src = """class Program
    int x
    int y
    method main()
        if x = 1 then
            y += 10
        fi x = 1"""
        result = eval_prog(parse(src))
        assert ("y", IntVal(0)) in result

    def test_for_loop(self):
        src = """class Program
    int x
    method main()
        for i in (1..5) do
            x += 1
        end"""
        result = eval_prog(parse(src))
        assert ("x", IntVal(5)) in result

    def test_local_delocal(self):
        src = """class Program
    int x
    method main()
        local int y = 10
        x += y
        delocal int y = 10"""
        result = eval_prog(parse(src))
        assert ("x", IntVal(10)) in result

    def test_object_lifecycle(self):
        src = """class Foo
    method bar(int n)
        n += 1

class Program
    int x
    method main()
        local Foo f = nil
        new Foo f
        call f::bar(x)
        delete Foo f
        delocal Foo f = nil"""
        result = eval_prog(parse(src))
        assert ("x", IntVal(1)) in result

    def test_array_operations(self):
        src = """class Program
    int[] a
    method main()
        new int[3] a
        a[0] += 10
        a[1] += 20
        a[2] += 30"""
        result = eval_prog(parse(src))
        assert ("a[0]", IntVal(10)) in result
        assert ("a[1]", IntVal(20)) in result
        assert ("a[2]", IntVal(30)) in result

    def test_loop(self):
        src = """class Program
    int x
    method main()
        x ^= 1
        from x = 1 do
            x += 1
        until x = 5"""
        result = eval_prog(parse(src))
        assert ("x", IntVal(5)) in result

    def test_fib_example(self):
        """Test the classic Fibonacci example file."""
        import os
        fib_path = os.path.join(os.path.dirname(__file__), "..", "example", "fib.rplpp")
        if os.path.exists(fib_path):
            with open(fib_path) as f:
                prog = parse(f.read())
            result = eval_prog(prog)
            result_dict = dict(result)
            assert result_dict["result"] == IntVal(8)  # fib(4) pair -> 8
