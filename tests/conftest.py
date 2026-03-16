"""Shared test fixtures and helpers."""
import os
import pytest
from pyrooplpp.parser import parse
from pyrooplpp.eval import eval_prog
from pyrooplpp.value import IntVal

EXAMPLE_DIR = os.path.join(os.path.dirname(__file__), "..", "example")


def load_example(name: str) -> str:
    """Read an example .rplpp file and return its source."""
    path = os.path.join(EXAMPLE_DIR, name)
    if not os.path.exists(path):
        pytest.skip(f"{name} not found")
    with open(path) as f:
        return f.read()


def run_src(src: str) -> dict:
    """Parse and evaluate a ROOPL++ source string, return results as a dict."""
    return dict(eval_prog(parse(src)))


def run_example(name: str) -> dict:
    """Load, parse, and evaluate an example file, return results as a dict."""
    return run_src(load_example(name))
