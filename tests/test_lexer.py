"""Tests for the ROOPL++ lexer."""
import pytest
from pyrooplpp.lexer import tokenize, TT, Token


class TestTokenizeBasics:
    def test_empty_source(self):
        tokens = tokenize("")
        assert len(tokens) == 1
        assert tokens[0].type == TT.EOF

    def test_whitespace_only(self):
        tokens = tokenize("   \n\t\r  ")
        assert len(tokens) == 1
        assert tokens[0].type == TT.EOF

    def test_integer_constant(self):
        tokens = tokenize("42")
        assert tokens[0].type == TT.CONST
        assert tokens[0].value == 42

    def test_zero_constant(self):
        tokens = tokenize("0")
        assert tokens[0].type == TT.CONST
        assert tokens[0].value == 0

    def test_large_number(self):
        tokens = tokenize("1000000007")
        assert tokens[0].value == 1000000007

    def test_identifier(self):
        tokens = tokenize("myVar")
        assert tokens[0].type == TT.ID
        assert tokens[0].value == "myVar"

    def test_identifier_with_underscore(self):
        tokens = tokenize("my_var")
        assert tokens[0].type == TT.ID
        assert tokens[0].value == "my_var"

    def test_identifier_with_prime(self):
        tokens = tokenize("x'")
        assert tokens[0].type == TT.ID
        assert tokens[0].value == "x'"


class TestTokenizeKeywords:
    @pytest.mark.parametrize("keyword,expected", [
        ("class", TT.CLASS), ("inherits", TT.INHERITS), ("method", TT.METHOD),
        ("call", TT.CALL), ("uncall", TT.UNCALL),
        ("if", TT.IF), ("then", TT.THEN), ("else", TT.ELSE), ("fi", TT.FI),
        ("from", TT.FROM), ("do", TT.DO), ("loop", TT.LOOP), ("until", TT.UNTIL),
        ("for", TT.FOR), ("in", TT.IN), ("end", TT.END),
        ("local", TT.LOCAL), ("delocal", TT.DELOCAL),
        ("new", TT.NEW), ("delete", TT.DELETE),
        ("copy", TT.COPY), ("uncopy", TT.UNCOPY),
        ("nil", TT.NIL), ("int", TT.INT), ("skip", TT.SKIP),
        ("show", TT.SHOW), ("print", TT.PRINT),
        ("switch", TT.SWITCH), ("hctiws", TT.HCTIWS),
        ("case", TT.CASE), ("esac", TT.ESAC), ("default", TT.DEFAULT),
        ("break", TT.BREAK),
        ("construct", TT.CONSTRUCT), ("destruct", TT.DESTRUCT),
    ])
    def test_keyword(self, keyword, expected):
        tokens = tokenize(keyword)
        assert tokens[0].type == expected


class TestTokenizeOperators:
    @pytest.mark.parametrize("op,expected", [
        ("+=", TT.MODADD), ("-=", TT.MODSUB), ("^=", TT.MODXOR),
        ("<=>", TT.SWAP), ("<=", TT.LE), (">=", TT.GE),
        ("!=", TT.NE), ("&&", TT.AND), ("||", TT.OR),
        ("::", TT.WCOLON), ("..", TT.WDOT),
        ("+", TT.ADD), ("-", TT.SUB), ("*", TT.MUL), ("/", TT.DIV),
        ("%", TT.MOD), ("<", TT.LT), (">", TT.GT), ("=", TT.EQ),
        ("&", TT.BAND), ("^", TT.XOR), ("|", TT.BOR),
        (".", TT.DOT), (":", TT.COLON), (",", TT.COMMA),
        ("(", TT.LPAREN), (")", TT.RPAREN),
        ("[", TT.LBRA), ("]", TT.RBRA),
    ])
    def test_operator(self, op, expected):
        tokens = tokenize(op)
        assert tokens[0].type == expected


class TestTokenizeStrings:
    def test_simple_string(self):
        tokens = tokenize('"hello"')
        assert tokens[0].type == TT.STRING
        assert tokens[0].value == "hello"

    def test_string_with_newline_escape(self):
        tokens = tokenize(r'"line\n"')
        assert tokens[0].value == "line\n"

    def test_string_with_tab_escape(self):
        tokens = tokenize(r'"a\tb"')
        assert tokens[0].value == "a\tb"

    def test_string_with_escaped_quote(self):
        tokens = tokenize(r'"say \"hi\""')
        assert tokens[0].value == 'say "hi"'


class TestTokenizeComments:
    def test_line_comment(self):
        tokens = tokenize("42 // this is a comment\n100")
        assert tokens[0].type == TT.CONST
        assert tokens[0].value == 42
        assert tokens[1].type == TT.CONST
        assert tokens[1].value == 100

    def test_comment_at_end(self):
        tokens = tokenize("x // end")
        assert len(tokens) == 2  # ID + EOF


class TestTokenizeLineCol:
    def test_line_tracking(self):
        tokens = tokenize("x\ny\nz")
        assert tokens[0].line == 1
        assert tokens[1].line == 2
        assert tokens[2].line == 3

    def test_column_tracking(self):
        tokens = tokenize("  x")
        assert tokens[0].col == 3


class TestTokenizeErrors:
    def test_unknown_character(self):
        with pytest.raises(SyntaxError, match="unknown token"):
            tokenize("@")


class TestTokenizeProgram:
    def test_minimal_program(self):
        src = "class Program\n    int x\n    method main()\n        x ^= 1"
        tokens = tokenize(src)
        types = [t.type for t in tokens if t.type != TT.EOF]
        assert TT.CLASS in types
        assert TT.ID in types
        assert TT.INT in types
        assert TT.METHOD in types
        assert TT.MODXOR in types
