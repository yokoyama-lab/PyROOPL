"""Tests for the output-declaration / clean-termination mechanism (plan A).

An `output` declaration in the main class names the fields that count as the
program's output. Every *other* top-level field must be clean (0 / nil / all-zero
array) when `main` finishes; otherwise evaluation raises a "Non-clean termination"
RuntimeError. Programs without an `output` declaration keep the legacy behaviour
(all fields are returned, no clean check).
"""
import os
import subprocess
import pytest
from pyrooplpp.parser import parse
from pyrooplpp.pretty import pretty_prog
from pyrooplpp.eval import eval_prog
from pyrooplpp.value import IntVal
from pyrooplpp.syntax import CDecl

ROOT = os.path.join(os.path.dirname(__file__), "..")


def run_src(src: str) -> dict:
    return dict(eval_prog(parse(src)))


def prog_class(src: str, name: str = "Program") -> CDecl:
    return next(c for c in parse(src).classes if c.name == name)


class TestOutputParsing:
    def test_output_field_stored_on_cdecl(self):
        src = """
        class Program
            int r
            int n
            output r
            method main()
                r += 5
        """
        assert prog_class(src).output == ["r"]

    def test_multiple_output_fields(self):
        src = """
        class Program
            int a
            int b
            int c
            output a, b
            method main()
                a += 1
                b += 2
        """
        assert prog_class(src).output == ["a", "b"]

    def test_multiple_output_lines_merge(self):
        src = """
        class Program
            int a
            int b
            int junk
            output a
            output b
            method main()
                a += 1
                b += 2
        """
        assert prog_class(src).output == ["a", "b"]

    def test_no_output_declaration(self):
        src = """
        class Program
            int r
            method main()
                r += 5
        """
        assert prog_class(src).output == []

    def test_pretty_roundtrip_preserves_output(self):
        src = """
        class Program
            int a
            int b
            output a, b
            method main()
                a += 1
                b += 2
        """
        prog = parse(src)
        reparsed = parse(pretty_prog(prog))
        assert prog == reparsed
        assert prog_class(pretty_prog(prog)).output == ["a", "b"]


class TestCleanTermination:
    def test_clean_program_returns_only_output(self):
        # n is consumed back to 0; only r is output.
        src = """
        class Program
            int r
            int n
            output r
            method main()
                n += 3
                r += n
                r += n
                from n = 3 do n -= 1 loop skip until n = 0
        """
        assert run_src(src) == {"r": IntVal(6)}

    def test_multiple_outputs_returned_with_clean_junk(self):
        src = """
        class Program
            int a
            int b
            int junk
            output a, b
            method main()
                junk += 4
                a += junk
                b += junk
                b += junk
                from junk = 4 do junk -= 1 loop skip until junk = 0
        """
        assert run_src(src) == {"a": IntVal(4), "b": IntVal(8)}

    def test_all_fields_output_skips_clean_check(self):
        # When every field is declared output, nothing is checked for cleanliness.
        src = """
        class Program
            int a
            int b
            output a, b
            method main()
                a += 3
                b += 7
        """
        assert run_src(src) == {"a": IntVal(3), "b": IntVal(7)}

    def test_non_output_field_left_dirty_raises(self):
        src = """
        class Program
            int r
            int n
            output r
            method main()
                n += 3
                r += 5
        """
        with pytest.raises(RuntimeError, match="Non-clean termination"):
            run_src(src)

    def test_error_message_names_field_and_value(self):
        src = """
        class Program
            int r
            int k
            output r
            method main()
                k += 3
        """
        with pytest.raises(RuntimeError, match=r"field 'k' = 3 \(expected 0\)"):
            run_src(src)

    def test_output_field_may_be_nonzero(self):
        # The output field itself is exempt from the clean check.
        src = """
        class Program
            int r
            output r
            method main()
                r += 42
        """
        assert run_src(src) == {"r": IntVal(42)}


class TestCleanArray:
    def test_clean_array_ok(self):
        src = """
        class Program
            int r
            int[] xs
            output r
            method main()
                new int[3] xs
                r += 7
                delete int[3] xs
        """
        assert run_src(src) == {"r": IntVal(7)}

    def test_dirty_array_raises_with_index(self):
        src = """
        class Program
            int[] xs
            int r
            output r
            method main()
                new int[3] xs
                xs[1] += 9
                r += 1
        """
        with pytest.raises(RuntimeError, match=r"field 'xs\[1\]' = 9"):
            run_src(src)

    def test_array_as_output_is_returned_flattened(self):
        src = """
        class Program
            int[] xs
            int junk
            output xs
            method main()
                new int[3] xs
                xs[0] += 10
                xs[2] += 30
        """
        r = run_src(src)
        assert r == {"xs[0]": IntVal(10), "xs[1]": IntVal(0), "xs[2]": IntVal(30)}


class TestCleanObject:
    def test_object_deleted_back_to_nil_is_clean(self):
        src = """
        class Cell
            int v
            method noop()
                skip
        class Program
            Cell c
            int r
            output r
            method main()
                new Cell c
                r += 5
                delete Cell c
        """
        assert run_src(src) == {"r": IntVal(5)}

    def test_live_object_reference_raises(self):
        src = """
        class Cell
            int v
            method noop()
                skip
        class Program
            Cell c
            int r
            output r
            method main()
                new Cell c
                r += 5
        """
        with pytest.raises(RuntimeError, match=r"field 'c' is a live object"):
            run_src(src)


class TestInheritance:
    def test_inherited_field_participates_in_clean_check(self):
        # `n` is inherited from Base and is not output -> it must be clean.
        src = """
        class Base
            int n
            method noop()
                skip
        class Program inherits Base
            int r
            output r
            method main()
                n += 2
                r += 5
        """
        with pytest.raises(RuntimeError, match=r"field 'n' = 2"):
            run_src(src)

    def test_inherited_field_cleaned_ok(self):
        src = """
        class Base
            int n
            method noop()
                skip
        class Program inherits Base
            int r
            output r
            method main()
                n += 3
                r += n
                r += n
                from n = 3 do n -= 1 loop skip until n = 0
        """
        assert run_src(src) == {"r": IntVal(6)}


class TestOutputValidation:
    def test_unknown_output_name_raises(self):
        src = """
        class Program
            int r
            output q
            method main()
                r += 1
        """
        with pytest.raises(RuntimeError, match=r"output field 'q' is not a field"):
            run_src(src)


class TestBackwardCompatibility:
    def test_no_output_returns_all_fields(self):
        # Legacy behaviour: without output, every field is returned, no clean check.
        src = """
        class Program
            int r
            int n
            method main()
                n += 3
                r += 5
        """
        assert run_src(src) == {"r": IntVal(5), "n": IntVal(3)}

    def test_no_output_does_not_clean_check_dirty_field(self):
        # Even with leftover garbage, a program without `output` succeeds.
        src = """
        class Program
            int garbage
            method main()
                garbage += 99
        """
        assert run_src(src) == {"garbage": IntVal(99)}


class TestCLIExitCodes:
    """The gen_janus verifier relies on exit codes + stdout for clean-termination."""

    def _run(self, tmp_path, src):
        f = tmp_path / "prog.rplpp"
        f.write_text(src)
        return subprocess.run(
            ["python3", "main.py", str(f)],
            capture_output=True, text=True, cwd=ROOT,
        )

    def test_clean_program_exits_zero_and_shows_only_output(self, tmp_path):
        res = self._run(tmp_path, """
        class Program
            int r
            int n
            output r
            method main()
                n += 3
                r += n
                r += n
                from n = 3 do n -= 1 loop skip until n = 0
        """)
        assert res.returncode == 0
        assert "r = 6" in res.stdout
        assert "n =" not in res.stdout  # non-output field is not printed

    def test_non_clean_termination_exits_nonzero(self, tmp_path):
        res = self._run(tmp_path, """
        class Program
            int r
            int k
            output r
            method main()
                k += 3
        """)
        assert res.returncode == 1
        assert "Non-clean termination" in res.stdout
        assert "field 'k' = 3" in res.stdout

    def test_runtime_error_exits_nonzero(self, tmp_path):
        # A plain runtime error (division by zero) must also exit non-zero.
        res = self._run(tmp_path, """
        class Program
            int r
            method main()
                r += 5 / 0
        """)
        assert res.returncode == 1
        assert "ERROR" in res.stdout
