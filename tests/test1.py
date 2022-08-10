from src.lexer import *
import unittest


class MyTestCase(unittest.TestCase):
    def test_0_lexer(self):
        src: str
        with open('test_code.avo', 'r', encoding='utf-8') as f:
            src = f.read()
        i = 0
        for token in lex(src):
            print(token, i)
            i += 1

    def test_0_stmt_list(self):
        print(stmt_list()(lex('a = 1; b = 1; c = 3;'), 0))

    def test_1_a_expr(self):
        print(a_expr()(lex('1 + 2 * (5 + 6)'), 0))

    def test_2_b_expr(self):
        print(Exp(b_expr(), None)(lex('2 > 3 and 3 > 2 or true'), 0))

    def test_3_if_stmt(self):
        print(if_stmt()(lex('if 1 == 1 {a = 1} else {a = 2}'), 0))
        print(if_stmt()(lex('if 1 == 1 {a = 1} else {}'), 0))
        print(if_stmt()(lex('if 1 == 1 {} else {a = 1}'), 0))
        print(if_stmt()(lex('if (1 == 1) and (2 == 2) {} else {}'), 0))

    def test_4_while_stmt(self):
        print(while_stmt()(lex('while 5 > 1 {}'), 0))

    def test_5_func_stmt(self):
        print(func_stmt()(lex('func f(){}'), 0))
        print(func_stmt()(lex('func f(n){}'), 0))
        print(func_stmt()(lex('func f(a, b, c){}'), 0))
        print(func_stmt()(lex('func f(n, a=1,b=2,c=3){}'), 0))
        print(func_stmt()(lex('func f(a=1,b=2,c=3){}'), 0))

    def test_6_call_stmt(self):
        print(call_stmt()(lex('function()'), 0))
        print(call_stmt()(lex('function(1, 2, 3)'), 0))
        print(call_stmt()(lex('function(a=1, b=2, c=3)'), 0))
        print(call_stmt()(lex('function(2, 4, 8, d=16, e=32, f=64)'), 0))

    def test_7_eval(self):
        src: str
        with open('test_code.avo', 'r', encoding='utf-8') as f:
            src = f.read()
        parsed = imp_parser(lex(src))
        parsed.value.eval()


if __name__ == '__main__':
    unittest.main(verbosity=2)
