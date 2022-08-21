from src.avoscript import *
import unittest


class MyTestCase(unittest.TestCase):
    @staticmethod
    def test_0_lexer():
        i = 0
        for token in Lexer.lex_file('test_code.avo'):
            print(token, i)
            i += 1
        i = 0
        for token in Lexer.lex_file('main.avo'):
            print(token, i)
            i += 1

    @staticmethod
    def test_0_stmt_list():
        print(stmt_list()(Lexer.lex('a = 1; b = 1; c = 3;'), 0))

    @staticmethod
    def test_1_a_expr():
        print(a_expr()(Lexer.lex('1 + 2 * (5 + 6)'), 0))
        print(expr()(Lexer.lex('-q * (a*a) / (2*i + 1)*(2*i);'), 0))

    @staticmethod
    def test_2_b_expr():
        print(Exp(b_expr(), None)(Lexer.lex('2 > 3 and 3 > 2 or true'), 0))
        print(b_expr()(Lexer.lex('pow(2, 10) - s > 0.02'), 0))

    @staticmethod
    def test_3_if_stmt():
        print(if_stmt()(Lexer.lex('if 1 == 1 {a = 1} else {a = 2}'), 0))
        print(if_stmt()(Lexer.lex('if 1 == 1 {a = 1} else {}'), 0))
        print(if_stmt()(Lexer.lex('if 1 == 1 {} else {a = 1}'), 0))
        print(if_stmt()(Lexer.lex('if (1 == 1) and (2 == 2) {} else {}'), 0))

    @staticmethod
    def test_4_while_stmt():
        print(while_stmt()(Lexer.lex('while 5 > 1 {}'), 0))

    @staticmethod
    def test_5_func_stmt():
        print(func_stmt()(Lexer.lex('func f(){}'), 0))
        print(func_stmt()(Lexer.lex('func f(n){}'), 0))
        print(func_stmt()(Lexer.lex('func f(a, b, c){}'), 0))
        print(func_stmt()(Lexer.lex('func f(n, a=1,b=2,c=3){}'), 0))
        print(func_stmt()(Lexer.lex('func f(a=1,b=2,c=3){}'), 0))

    @staticmethod
    def test_6_call_stmt():
        print(call_stmt()(Lexer.lex('function()'), 0))
        print(call_stmt()(Lexer.lex('function(1, 2, 3)'), 0))
        print(call_stmt()(Lexer.lex('function(a=1, b=2, c=3)'), 0))
        print(call_stmt()(Lexer.lex('function(2, 4, 8, d=16, e=32, f=64)'), 0))

    @staticmethod
    def test_7_eval():
        parsed = imp_parser(Lexer.lex_file('test_code.avo'))
        env = []
        consts = []
        lvl = LevelIndex()
        modules = {}
        parsed.value.eval(env, consts, lvl, modules, Signal())

    @staticmethod
    def test_8_module_call():
        print(module_obj_expr()(Lexer.lex('some.asd'), 0))

    @staticmethod
    def test_9_switch_case():
        print(switch_case_stmt()(Lexer.lex('switch s {case 0 {} case 1{} case 10{} else {}}'), 0))

    @staticmethod
    def test_a_if_else_expr():
        print(assign_stmt()(Lexer.lex('var a = 0 if false else 1;'), 0))
        print(assign_stmt()(Lexer.lex('var a = true ? 1 : 0;'), 0))
        env = []
        consts = []
        lvl = LevelIndex()
        modules = {}
        echo_stmt()(Lexer.lex('echo(100 if 2*2 == 4 else 0);'), 0).value.eval(env, consts, lvl, modules, Signal())
        echo_stmt()(Lexer.lex('echo(2*2 == 4 ? true : false);'), 0).value.eval(env, consts, lvl, modules, Signal())

    @staticmethod
    def test_b_assign_class_stmt():
        print(assign_class_stmt()(Lexer.lex('class A { }'), 0))
        env = []
        consts = []
        lvl = LevelIndex()
        modules = {}
        print(assign_class_stmt()(Lexer.lex('class B : A { var a = 0;  func main() {} }'), 0))
        imp_parser(Lexer.lex_file('objects.avo')).value.eval(env, consts, lvl, modules, Signal())

    @staticmethod
    def test_c_lambda_stmt():
        print(assign_stmt()(Lexer.lex('var a = () => {}'), 0))
        env = []
        consts = []
        lvl = LevelIndex()
        modules = {}
        imp_parser(
            Lexer.lex('var a = (a) => {echo(a, "lambda is cool");}; a(5);')
        ).value.eval(env, consts, lvl, modules, Signal())

    @staticmethod
    def test_d_modules():
        parsed = imp_parser(Lexer.lex_file('main.avo'))
        env = []
        consts = []
        lvl = LevelIndex()
        modules = {}
        parsed.value.eval(env, consts, lvl, modules, Signal())

    @staticmethod
    def test_e_builtins():
        parsed = imp_parser(Lexer.lex_file('builtins_test.avo'))
        env = []
        consts = []
        lvl = LevelIndex()
        modules = {}
        parsed.value.eval(env, consts, lvl, modules, Signal())

    @staticmethod
    def test_f_try_catch_stmt():
        parsed = imp_parser(Lexer.lex_file('try_catch.avo'))
        env = []
        consts = []
        lvl = LevelIndex()
        modules = {}
        parsed.value.eval(env, consts, lvl, modules, Signal())


if __name__ == '__main__':
    unittest.main(verbosity=2)
