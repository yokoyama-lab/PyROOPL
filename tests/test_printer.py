"""Tests for the output printer."""
from pyrooplpp.printer import show_val, show_val_rec, print_result, show_vec
from pyrooplpp.value import *
import io
import sys


class TestShowVal:
    def test_intval(self):
        assert show_val(IntVal(42)) == "42"

    def test_negative(self):
        assert show_val(IntVal(-5)) == "-5"

    def test_locsval(self):
        assert show_val(LocsVal(10)) == "<location> 10"

    def test_locsvec(self):
        result = show_val(LocsVec([1, 2, 3]))
        assert "1" in result
        assert "2" in result
        assert "3" in result


class TestShowValRec:
    def test_intval(self):
        assert show_val_rec(IntVal(42)) == "<int> 42"

    def test_objval(self):
        result = show_val_rec(ObjVal("Foo", {"x": 1}))
        assert "<object>" in result
        assert "Foo" in result

    def test_locsval(self):
        assert show_val_rec(LocsVal(5)) == "<location> 5"

    def test_locsvec(self):
        result = show_val_rec(LocsVec([10, 20]))
        assert "<vector>" in result


class TestPrintResult:
    def test_output(self, capsys):
        print_result([("x", IntVal(42)), ("y", IntVal(7))])
        out = capsys.readouterr().out
        assert "x = 42" in out
        assert "y = 7" in out


class TestShowVec:
    def test_show_vec(self):
        assert show_vec([1, 2, 3]) == "[123]"
