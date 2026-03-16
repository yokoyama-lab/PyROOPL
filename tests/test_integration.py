"""Integration tests: full program execution and example file validation."""
import os
import subprocess
import pytest
from pyrooplpp.parser import parse
from pyrooplpp.eval import eval_prog
from pyrooplpp.value import IntVal
from pyrooplpp.invert import invert_prog
from .conftest import EXAMPLE_DIR, load_example, run_example


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

    # parse error covered by test_parser.py::TestParseProgram::test_parse_error


class TestExamplePrograms:
    """Run a selection of example programs and verify they succeed."""

    # Light smoke tests only; heavy algos tested with value checks in TestSpecificAlgorithms
    SAMPLES = [
        "fib.rplpp", "factor.rplpp", "sqrt.rplpp", "for.rplpp",
        "algo_factorial.rplpp", "algo_gcd.rplpp", "algo_bubble_sort.rplpp",
    ]

    @pytest.fixture(params=SAMPLES)
    def example_file(self, request):
        return load_example(request.param)

    def test_example_runs(self, example_file):
        prog = parse(example_file)
        result = eval_prog(prog)
        assert isinstance(result, list)


class TestInverseRoundtrip:
    """Verify that invert(invert(prog)) == prog for all examples."""

    ROUNDTRIP_EXAMPLES = [
        "fib.rplpp", "factor.rplpp", "sqrt.rplpp", "for.rplpp",
    ]

    @pytest.fixture(params=ROUNDTRIP_EXAMPLES)
    def example_source(self, request):
        return load_example(request.param)

    def test_double_invert(self, example_source):
        prog = parse(example_source)
        assert invert_prog(invert_prog(prog)) == prog


class TestSpecificAlgorithms:
    """Verify specific algorithm outputs."""

    def test_factorial(self):
        r = run_example("algo_factorial.rplpp")
        assert r["result"] == IntVal(5040)

    def test_gcd(self):
        r = run_example("algo_gcd.rplpp")
        assert r["a"] == IntVal(6)

    def test_fib_array(self):
        r = run_example("algo_fib_array.rplpp")
        assert r["fib[9]"] == IntVal(34)

    def test_bubble_sort(self):
        r = run_example("algo_bubble_sort.rplpp")
        assert r["a[0]"] == IntVal(1)
        assert r["a[4]"] == IntVal(5)

    def test_nqueens(self):
        r = run_example("algo_nqueens.rplpp")
        assert r["count"] == IntVal(10)

    def test_ackermann(self):
        r = run_example("algo_ackermann.rplpp")
        assert r["result"] == IntVal(9)

    def test_knapsack(self):
        r = run_example("algo_knapsack.rplpp")
        assert r["dp[44]"] == IntVal(10)

    def test_floyd_warshall(self):
        r = run_example("algo_floyd_warshall.rplpp")
        assert r["dist[3]"] == IntVal(6)  # shortest 0->3 = 6

    def test_rsa(self):
        r = run_example("algo_rsa.rplpp")
        assert r["cipher"] == IntVal(14)  # 42^13 mod 77

    def test_karatsuba(self):
        r = run_example("algo_karatsuba.rplpp")
        assert r["result"] == IntVal(7006652)  # 1234 * 5678

    def test_gauss_elimination(self):
        r = run_example("algo_gauss_elim.rplpp")
        assert r["mat[10]"] == IntVal(-2)  # upper triangular
