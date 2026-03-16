#!/usr/bin/env python3
"""ROOPL++ interpreter CLI."""
import argparse
import sys
import os

from pyrooplpp.parser import parse
from pyrooplpp.eval import eval_prog
from pyrooplpp.printer import print_result
from pyrooplpp.pretty import pretty_prog
from pyrooplpp.invert import invert_prog


def main():
    ap = argparse.ArgumentParser(description="ROOPLPP interpreter")
    ap.add_argument("file", help="ROOPL++ source file")
    ap.add_argument("-inverse", action="store_true", help="print inverted program")
    ap.add_argument("-library", action="store_true", help="load standard library")
    args = ap.parse_args()

    with open(args.file) as f:
        source = f.read()

    try:
        prog = parse(source)
    except Exception as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    if args.inverse:
        print(pretty_prog(invert_prog(prog)), end="")
    else:
        try:
            library = None
            if args.library:
                lib_path = os.path.join(os.path.dirname(args.file), "..", "library", "Library.rplpp")
                if not os.path.exists(lib_path):
                    lib_path = os.path.join(os.path.dirname(__file__), "..", "library", "Library.rplpp")
                with open(lib_path) as f:
                    library = parse(f.read())
            result = eval_prog(prog, library)
            print_result(result)
        except RuntimeError as e:
            print()
            print(str(e))


if __name__ == "__main__":
    main()
