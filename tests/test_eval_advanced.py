"""Advanced evaluator tests to increase coverage."""
import pytest
from pyrooplpp.parser import parse
from pyrooplpp.eval import eval_prog, eval_exp, eval_state, comp_op_eq, rel_op
from pyrooplpp.value import *
from pyrooplpp.syntax import *


class TestEvalDotAccess:
    def test_instance_field(self):
        src = """class Foo
    int val
    method set(int v)
        val += v

class Program
    int result
    method main()
        construct Foo f
            call f::set(result)
            result += f.val
        destruct f"""
        r = dict(eval_prog(parse(src)))
        assert r["result"] == IntVal(0)  # val was set then read


class TestEvalObjectLifecycle:
    def test_new_delete(self):
        src = """class Foo
    int x
    method bar(int n)
        n += 1

class Program
    int result
    method main()
        local Foo f = nil
        new Foo f
        call f::bar(result)
        delete Foo f
        delocal Foo f = nil"""
        r = dict(eval_prog(parse(src)))
        assert r["result"] == IntVal(1)

    def test_new_not_nil_error(self):
        src = """class Foo
    method bar()
        skip

class Program
    int x
    method main()
        x ^= 1
        local Foo f = nil
        new Foo f
        new Foo f
        delete Foo f
        delete Foo f
        delocal Foo f = nil"""
        with pytest.raises(RuntimeError, match="not nil"):
            eval_prog(parse(src))


class TestEvalArrayOps:
    def test_array_new_delete(self):
        src = """class Program
    int[] a
    method main()
        new int[3] a
        a[0] += 5
        a[1] += 10
        a[2] += 15
        a[2] -= 15
        a[1] -= 10
        a[0] -= 5
        delete int[3] a"""
        r = dict(eval_prog(parse(src)))
        # After delete, a should be IntVal(0)

    def test_array_not_nil_error(self):
        src = """class Program
    int[] a
    method main()
        new int[2] a
        new int[2] a
        delete int[2] a
        delete int[2] a"""
        with pytest.raises(RuntimeError, match="not nil"):
            eval_prog(parse(src))


class TestEvalCopyUncopy:
    def test_copy_uncopy(self):
        src = """class Foo
    int x
    method bar()
        skip

class Program
    int result
    method main()
        local Foo a = nil
        new Foo a
        local Foo b = nil
        copy Foo a b
        uncopy Foo a b
        delocal Foo b = nil
        delete Foo a
        delocal Foo a = nil"""
        eval_prog(parse(src))  # should not raise

    def test_uncopy_mismatch_error(self):
        src = """class Foo
    int x
    method bar()
        skip

class Program
    int result
    method main()
        local Foo a = nil
        new Foo a
        local Foo b = nil
        new Foo b
        uncopy Foo a b
        delete Foo b
        delocal Foo b = nil
        delete Foo a
        delocal Foo a = nil"""
        with pytest.raises(RuntimeError, match="not same"):
            eval_prog(parse(src))


class TestEvalCallUncall:
    def test_uncall(self):
        src = """class Adder
    method add(int n)
        n += 5

class Program
    int x
    method main()
        local Adder a = nil
        new Adder a
        call a::add(x)
        uncall a::add(x)
        delete Adder a
        delocal Adder a = nil"""
        r = dict(eval_prog(parse(src)))
        assert r["x"] == IntVal(0)  # call then uncall cancels

    def test_local_call_uncall(self):
        src = """class Program
    int x
    method main()
        call inc()
        uncall inc()
    method inc()
        x += 1"""
        r = dict(eval_prog(parse(src)))
        assert r["x"] == IntVal(0)


class TestEvalLoopVariants:
    def test_from_loop_until(self):
        src = """class Program
    int x
    method main()
        from x = 0 loop
            x += 1
        until x = 3"""
        r = dict(eval_prog(parse(src)))
        assert r["x"] == IntVal(3)

    def test_loop_assertion_fail(self):
        src = """class Program
    int x
    method main()
        x ^= 1
        from x = 0 do
            x += 1
        until x = 2"""
        with pytest.raises(RuntimeError, match="Assertion should be true"):
            eval_prog(parse(src))


class TestEvalLocalBlock:
    def test_delocal_mismatch_error(self):
        src = """class Program
    int x
    method main()
        local int y = 0
        y += 5
        delocal int y = 0"""
        with pytest.raises(RuntimeError, match="should be"):
            eval_prog(parse(src))


class TestEvalShow:
    def test_show(self, capsys):
        src = """class Program
    int x
    method main()
        x ^= 42
        show(x)"""
        eval_prog(parse(src))
        out = capsys.readouterr().out
        assert "42" in out


class TestEvalPrint:
    def test_print(self, capsys):
        src = """class Program
    int x
    method main()
        print("hello")"""
        eval_prog(parse(src))
        out = capsys.readouterr().out
        assert "hello" in out


class TestEvalInheritance:
    def test_method_inheritance(self):
        src = """class Base
    method add(int n)
        n += 1

class Sub inherits Base
    method mul(int n)
        n += n

class Program
    int x
    method main()
        local Sub s = nil
        new Sub s
        call s::add(x)
        delete Sub s
        delocal Sub s = nil"""
        r = dict(eval_prog(parse(src)))
        assert r["x"] == IntVal(1)


class TestHelperFunctions:
    def test_comp_op_eq(self):
        assert comp_op_eq(lambda a, b: a == b, IntVal(1), IntVal(1)) == IntVal(1)
        assert comp_op_eq(lambda a, b: a == b, IntVal(1), IntVal(2)) == IntVal(0)

    def test_rel_op(self):
        assert rel_op(lambda a, b: a and b, IntVal(1), IntVal(1)) == IntVal(1)
        assert rel_op(lambda a, b: a and b, IntVal(0), IntVal(1)) == IntVal(0)
