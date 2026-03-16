# PyROOPL

A Python implementation of **ROOPL++**, a Reversible Object-Oriented Programming Language.

## Overview

ROOPL++ is a reversible programming language where every program can be
automatically run in reverse. All computations are bijective, meaning that
outputs can be uniquely mapped back to inputs. This property is guaranteed by
the language design: only reversible operators (`+=`, `-=`, `^=`, `<=>`), assertion-guarded
control flow, and symmetric `call`/`uncall` method invocation are allowed.

PyROOPL is a pure-Python interpreter that faithfully implements the ROOPL++
semantics, including:

- **Lexer, parser, and evaluator** for the full ROOPL++ language
- **Program inverter** (`-inverse` flag) that automatically reverses any program
- **Pretty printer** that reconstructs source code from the AST
- **Standard library** with List, Stack, Queue, and Tree data structures

## Requirements

- Python 3.10+
- No external dependencies

## Quick Start

```bash
# Run a program
python main.py example/fib.rplpp

# Print the inverted (reversed) program
python main.py -inverse example/fib.rplpp

# Run with standard library
python main.py -library example/LinkedList.rplpp
```

## Language Features

| Feature | Syntax | Description |
|---------|--------|-------------|
| Reversible assignment | `x += e`, `x -= e`, `x ^= e` | Add, subtract, XOR (no destructive `=`) |
| Swap | `x <=> y` | Self-inverse exchange |
| Conditional | `if e1 then S else S fi e2` | Entry/exit assertions for reversibility |
| Loop | `from e1 do S loop S until e2` | Assertion-guarded loop |
| For loop | `for i in (e1..e2) do S end` | Counted reversible loop |
| Switch | `switch x case ... hctiws x` | Multi-way branch |
| Method call | `call obj::method(args)` | Forward execution |
| Uncall | `uncall obj::method(args)` | Reverse execution |
| Object lifecycle | `new C x` / `delete C x` | Symmetric allocation |
| Local scoping | `local T x = e1 ... delocal T x = e2` | Scoped with cleanup assertion |

## Example

```
// Fibonacci: computes n-th Fibonacci number
class Fib
    int[] xs
    method init()
        new int[2] xs
    method fib(int n)
        if n = 0 then
            xs[0] ^= 1
            xs[1] ^= 1
        else
            n -= 1
            call fib(n)
            xs[0] += xs[1]
            xs[0] <=> xs[1]
        fi xs[0] = xs[1]

class Program
    int result
    int n
    method main()
        n ^= 4
        local Fib f = nil
        new Fib f
        call f::init()
        call f::fib(n)
        call f::get(result)
        uncall f::fib(n)       // reverse execution cleans up
        uncall f::init()
        delete Fib f
        delocal Fib f = nil
// Output: result = 5, n = 4
```

## Included Examples

The `example/` directory contains **139 programs**:

- **25 original examples**: Fibonacci, factorization, square root, permutation encoding, linked lists, binary trees, depth-first search, tree traversal, reversible Turing machine, etc.
- **114 reversible algorithm implementations** covering 15 categories:

| Category | Count | Highlights |
|----------|-------|------------|
| Sorting | 5 | Bubble, insertion, counting, radix, bitonic sort |
| Dynamic programming | 9 | Knapsack, LCS, LIS, edit distance, Kadane, coin change |
| Number theory / Crypto | 14 | GCD, RSA, Miller-Rabin, NTT, CRT, discrete logarithm |
| Linear algebra | 9 | Matrix multiply, Strassen, Gaussian elimination, matrix power |
| Graph algorithms | 3 | Topological sort, Bellman-Ford, Floyd-Warshall |
| Signal processing | 5 | Walsh-Hadamard, FFT butterfly, integer DCT, convolution |
| Recursion | 5 | Hanoi, Ackermann, N-Queens, subset sum |
| Combinatorics | 5 | Pascal's triangle, Catalan, Stirling numbers, lattice paths |
| Bit manipulation | 6 | Popcount, bit reversal, parity, full adder |
| Encoding | 4 | RLE, Gray code, prefix-free codes, Euclidean rhythm |
| Array operations | 16 | Reverse, rotate, prefix sum, interleave, shuffle |
| Searching | 5 | Linear search, Boyer-Moore majority, tournament |
| Arithmetic | 11 | Power, factorial, binomial, Karatsuba, Horner |
| Geometry / Statistics | 5 | Euclidean distance, histogram, palindrome, convolution |
| Fast multiplication | 3 | Karatsuba, Karatsuba polynomial, Vandermonde |

## Architecture

```
Source (.rplpp)  -->  Lexer (lexer.py)  -->  Parser (parser.py)  -->  AST (syntax.py)
                                                                          |
                                                              +-----------+-----------+
                                                              |                       |
                                                     Evaluator (eval.py)    Inverter (invert.py)
                                                              |                       |
                                                         Result              Inverted Program
                                                                         (via pretty.py)
```

| Module | Lines | Role |
|--------|-------|------|
| `syntax.py` | 309 | AST type definitions (dataclasses) |
| `lexer.py` | 188 | Tokenizer |
| `parser.py` | 563 | Recursive descent parser with Pratt expression parsing |
| `eval.py` | 727 | Evaluator: environment + store model |
| `invert.py` | 120 | Program inverter |
| `pretty.py` | 178 | AST pretty printer |
| `value.py` | 34 | Runtime value types |
| `printer.py` | 35 | Output formatter |

## References

- Yokoyama, T., Axelsen, H.B., Gluck, R.: *Principles of a reversible programming language*. CF '08, pp.43-54, ACM (2008).
- Haulund, T.: *Design and Implementation of a Reversible Object-Oriented Programming Language*. Master's thesis, University of Copenhagen (2017). [arXiv:1707.07845](https://arxiv.org/abs/1707.07845)
- Cservenka, M.H.: *Design and Implementation of Dynamic Memory Management in a Reversible Object-Oriented Programming Language*. Master's thesis, University of Copenhagen (2018).

## License

GNU General Public License v3.0. See [LICENSE](LICENSE).
