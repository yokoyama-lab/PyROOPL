"""Tests for runtime value types."""
from pyrooplpp.value import *


class TestValues:
    def test_intval(self):
        v = IntVal(42)
        assert v.value == 42

    def test_intval_equality(self):
        assert IntVal(1) == IntVal(1)
        assert IntVal(1) != IntVal(2)

    def test_objval(self):
        v = ObjVal("Foo", {"x": 1, "y": 2})
        assert v.type_id == "Foo"
        assert v.env == {"x": 1, "y": 2}

    def test_locsval(self):
        v = LocsVal(10)
        assert v.locs == 10

    def test_locsvec(self):
        v = LocsVec([1, 2, 3])
        assert v.locs == [1, 2, 3]

    def test_intval_zero(self):
        assert IntVal(0) == IntVal(0)

    def test_intval_negative(self):
        v = IntVal(-5)
        assert v.value == -5
