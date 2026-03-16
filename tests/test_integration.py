"""Integration tests: full program execution and example file validation."""
import os
import subprocess
import pytest
from pyrooplpp.parser import parse
from pyrooplpp.eval import eval_prog
from pyrooplpp.value import IntVal
from pyrooplpp.invert import invert_prog
from pyrooplpp.pretty import pretty_prog

EXAMPLE_DIR = os.path.join(os.path.dirname(__file__), "..", "example")


class TestCLI:
    """Test the CLI entry point."""

    def test_run_fib(self):
        result = subprocess.run(
            ["python3", "main.py", "example/fib.rplpp"],
            capture_output=True, text=True, cwd=os.path.join(os.path.dirname(__file__), ".."),
        )
        assert result.returncode == 0
        assert "result = 8" in result.stdout

    def test_run_inverse(self):
        result = subprocess.run(
            ["python3", "main.py", "-inverse", "example/fib.rplpp"],
            capture_output=True, text=True, cwd=os.path.join(os.path.dirname(__file__), ".."),
        )
        assert result.returncode == 0
        assert "uncall" in result.stdout

    def test_parse_error(self):
        result = subprocess.run(
            ["python3", "-c", "from pyrooplpp.parser import parse; parse('class')"],
            capture_output=True, text=True, cwd=os.path.join(os.path.dirname(__file__), ".."),
        )
        assert result.returncode != 0


class TestExamplePrograms:
    """Run a selection of example programs and verify they succeed."""

    SAMPLES = [
        "fib.rplpp", "factor.rplpp", "sqrt.rplpp", "for.rplpp",
        "algo_factorial.rplpp", "algo_gcd.rplpp", "algo_bubble_sort.rplpp",
        "algo_nqueens.rplpp", "algo_knapsack.rplpp", "algo_ackermann.rplpp",
        "algo_floyd_warshall.rplpp", "algo_gauss_elim.rplpp",
    ]

    @pytest.fixture(params=SAMPLES)
    def example_file(self, request):
        path = os.path.join(EXAMPLE_DIR, request.param)
        if not os.path.exists(path):
            pytest.skip(f"{request.param} not found")
        return path

    def test_example_runs(self, example_file):
        with open(example_file) as f:
            source = f.read()
        prog = parse(source)
        result = eval_prog(prog)
        assert isinstance(result, list)


class TestInverseRoundtrip:
    """Verify that invert(invert(prog)) == prog for all examples."""

    ROUNDTRIP_EXAMPLES = [
        "fib.rplpp", "factor.rplpp", "sqrt.rplpp", "for.rplpp",
    ]

    @pytest.fixture(params=ROUNDTRIP_EXAMPLES)
    def example_source(self, request):
        path = os.path.join(EXAMPLE_DIR, request.param)
        if not os.path.exists(path):
            pytest.skip(f"{request.param} not found")
        with open(path) as f:
            return f.read()

    def test_double_invert(self, example_source):
        prog = parse(example_source)
        double_inv = invert_prog(invert_prog(prog))
        assert prog == double_inv


class TestSpecificAlgorithms:
    """Verify specific algorithm outputs."""

    def _run(self, filename):
        path = os.path.join(EXAMPLE_DIR, filename)
        with open(path) as f:
            prog = parse(f.read())
        return dict(eval_prog(prog))

    def test_factorial(self):
        r = self._run("algo_factorial.rplpp")
        assert r["result"] == IntVal(5040)

    def test_gcd(self):
        r = self._run("algo_gcd.rplpp")
        assert r["a"] == IntVal(6)

    def test_fib_array(self):
        r = self._run("algo_fib_array.rplpp")
        assert r["fib[9]"] == IntVal(34)

    def test_bubble_sort(self):
        r = self._run("algo_bubble_sort.rplpp")
        assert r["a[0]"] == IntVal(1)
        assert r["a[4]"] == IntVal(5)

    def test_nqueens(self):
        r = self._run("algo_nqueens.rplpp")
        assert r["count"] == IntVal(10)

    def test_ackermann(self):
        r = self._run("algo_ackermann.rplpp")
        assert r["result"] == IntVal(9)

    def test_knapsack(self):
        r = self._run("algo_knapsack.rplpp")
        assert r["dp[44]"] == IntVal(10)

    def test_floyd_warshall(self):
        r = self._run("algo_floyd_warshall.rplpp")
        assert r["dist[3]"] == IntVal(6)  # shortest 0->3 = 6

    def test_rsa(self):
        r = self._run("algo_rsa.rplpp")
        assert r["cipher"] == IntVal(14)  # 42^13 mod 77

    def test_karatsuba(self):
        r = self._run("algo_karatsuba.rplpp")
        assert r["result"] == IntVal(7006652)  # 1234 * 5678

    def test_gauss_elimination(self):
        r = self._run("algo_gauss_elim.rplpp")
        assert r["mat[10]"] == IntVal(-2)  # upper triangular
