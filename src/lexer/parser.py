# -*- coding: utf-8 -*-
from functools import reduce
from pprint import pprint

from .ast import *
from .combinator import *
from .types import Token, Type


def keyword(kw: str) -> Reserved:
    return Reserved(kw, Type.RESERVED)


def operator(kw: str) -> Reserved:
    return Reserved(kw, Type.OPERATOR)


def process_boolean(op):
    match op:
        case 'on' | 'true' | 'enable':
            return True
        case 'off' | 'false' | 'disable':
            return False
        case _:
            raise RuntimeError(f'unknown boolean value: {op}')


id_tag = Tag(Type.ID)
num = Tag(Type.INT) ^ (lambda x: int(x))
float_num = Tag(Type.FLOAT) ^ (lambda x: float(x))
boolean = Tag(Type.BOOL) ^ process_boolean
string = Tag(Type.STRING) ^ (lambda x: StringAST(x[1:-1]))
a_expr_precedence_levels = [
    ['*', '/'],
    ['+', '-'],
]
relational_operators = ['==', '!=', '>=', '<=', '<', '>']
unary_operators = ['--', '++']
assign_operators = ['+=', '-=', '*=', '/=', '=']
b_expr_precedence_levels = [
    ['and', '&&'],
    ['or', '||']
]


def array_expr():
    def process(p):
        (_, data), _ = p
        return ArrayAST(data)
    return keyword('[') + Opt(Rep(Lazy(expr) + Opt(keyword(',')))) + keyword(']') ^ process


def a_expr_value():
    return (
            (num ^ (lambda x: IntAST(x))) |
            (float_num ^ (lambda x: FloatAST(x))) |
            (id_tag ^ (lambda x: VarAST(x))) |
            (boolean ^ (lambda x: BoolAST(x))) |
            string
    )


def process_group(p):
    (_, r), _ = p
    return r


def a_expr_group():
    return keyword('(') + Lazy(a_expr) + keyword(')') ^ process_group


def a_expr_term():
    return a_expr_value() | a_expr_group()


def process_binop(op):
    return lambda l, r: BinOpAST(op, l, r)


def any_op_in_list(ops):
    op_parsers = [operator(op) for op in ops]
    return reduce(lambda l, r: l | r, op_parsers)


def precedence(val_parser, levels, combine):
    def op_parser(level):
        return any_op_in_list(level) ^ combine
    p = val_parser * op_parser(levels[0])
    for lvl in levels[1:]:
        p = p * op_parser(lvl)
    return p


def a_expr():
    return precedence(a_expr_term(), a_expr_precedence_levels, process_binop)


# --== Boolean conditions ==-- #
def process_relop(p):
    (l, op), r = p
    return RelativeOp(op, l, r)


def b_expr_relop():
    return (a_expr() + any_op_in_list(relational_operators) + a_expr()) ^ process_relop


def b_expr_not():
    return (keyword('not') + Lazy(b_expr_term)) ^ (lambda p: NotOp(p[1]))


def b_expr_group():
    return (keyword('(') + Lazy(b_expr) + keyword(')')) ^ process_group


def b_expr_term():
    return b_expr_group() | b_expr_not() | b_expr_relop() | (boolean ^ (lambda x: BoolAST(x)))


def process_logic(op):
    match op:
        case 'and' | '&&':
            return lambda l, r: AndOp(l, r)
        case 'or' | '||':
            return lambda l, r: OrOp(l, r)
        case _:
            raise RuntimeError(f'unknown logic operator: {op}')


def b_expr():
    return precedence(b_expr_term(), b_expr_precedence_levels, process_logic)


def brace_expr():
    def process(p):
        (((obj), _), v), _ = p
        return BraceAST(obj, v)
    return (Lazy(array_expr) | Lazy(call_stmt) | string | id_tag) + keyword('[') + Lazy(expr) + keyword(']') ^ process


def expr():
    return (
            brace_expr() |
            Lazy(array_expr) |
            Lazy(call_stmt) |
            b_expr() |
            a_expr()
    )


# --== statements ==-- #
def assign_stmt():
    def process(p):
        ((_, name), _), e = p
        return AssignStmt(name, e, False, True)
    return (keyword('var') + id_tag + operator('=') + expr()) ^ process


def assign_const_stmt():
    def process(p):
        ((_, name), _), e = p
        return AssignStmt(name, e, True, True)
    return (keyword('const') + id_tag + operator('=') + expr()) ^ process


def reassign_stmt():
    def process(p):
        (name, op), e = p
        return AssignStmt(name, e, False, False, op)
    return (id_tag + any_op_in_list(assign_operators) + expr()) ^ process


def unary_op_stmt():
    def process(p):
        sym, name = p
        if sym not in unary_operators:
            name, sym = sym, name
        return UnaryOpAST(sym, VarAST(name))
    return Alt(any_op_in_list(unary_operators) + id_tag, id_tag + any_op_in_list(unary_operators)) ^ process


def stmt_list():
    def process(rep):
        return StmtList(rep)
    return Rep(Lazy(stmt) + Opt(keyword(';')) ^ (lambda x: x[0])) ^ process


def block_stmt():
    def process(rep):
        (_, l), _ = rep
        return l
    return keyword('{') + Opt(Lazy(stmt_list)) + keyword('}') ^ process


def if_stmt():
    def process(p):
        (((((_, condition), _), body), _), elif_array), false_p = p
        if false_p:
            (_, false_body), _ = false_p
        else:
            false_body = None
        if elif_array:
            elif_array = [i.value for i in elif_array]
        return IfStmt(condition, body, elif_array, false_body)
    result = keyword('if') + Exp(b_expr(), None) + keyword('{') + Opt(Lazy(stmt_list)) + keyword('}')
    result += Opt(
        Rep(
            keyword('elif') + Exp(b_expr(), None) + keyword('{') + Opt(Lazy(stmt_list)) + keyword('}')
        )
    )
    result += Opt(
            keyword('else') + keyword('{') + Opt(Lazy(stmt_list)) + keyword('}')
    )
    return result ^ process


def while_stmt():
    def process(p):
        (((_, condition), _), body), _ = p
        return WhileStmt(condition, body)
    result = keyword('while') + Exp(b_expr(), None) + keyword('{') + Opt(Lazy(stmt_list)) + keyword('}')
    return result ^ process


def break_stmt():
    return keyword('break') ^ (lambda x: BreakStmt())


def continue_stmt():
    return keyword('continue') ^ (lambda x: ContinueStmt())


def echo_stmt():
    def process(p):
        _, data = p
        return EchoStmt(data)
    return (
            keyword('echo') +
            Opt(
                Rep(
                    expr() + Opt(keyword(',')) ^ (lambda x: x[0])
                ) ^ (lambda x: [i.value for i in x])
            ) ^ process
    )


def func_stmt():
    def process(p):
        ((((((_, func_name), _), args), _), _), statements), _ = p
        return FuncStmt(func_name, args, statements)
    return (
            keyword('func') + id_tag + keyword('(') +
            Opt(Rep(id_tag + Opt(operator('=') + Lazy(expr)) + Opt(keyword(',')))) +
            keyword(')') + keyword('{') + Opt(Lazy(stmt_list)) + keyword('}')
    ) ^ process


def call_stmt():
    def process(p):
        ((func_name, _), args), _ = p
        return CallStmt(func_name, args)
    return (
        id_tag + keyword('(') +
        Opt(Rep(Opt(id_tag + operator('=')) + expr() + Opt(keyword(',')))) +
        keyword(')')
    ) ^ process


def return_stmt():
    def process(p):
        _, return_value = p
        return ReturnStmt(return_value)
    return keyword('return') + Opt(expr()) ^ process


def for_stmt():
    def process(p):
        (((((((_, var), _), cond), _), action), _), body), _ = p
        return ForStmt(var, cond, action, body)
    return (
            keyword('for') + Lazy(assign_stmt) + keyword(';') +
            Exp(b_expr(), None) + keyword(';') +
            (Lazy(reassign_stmt) | Lazy(unary_op_stmt)) + keyword('{') + Opt(Lazy(stmt_list)) + keyword('}')
    ) ^ process


def foreach_stmt():
    def process(p):
        (((((_, var), _), val), _), body), _ = p
        return ForStmt(var, val, body, None)
    return (
            keyword('for') + id_tag + keyword('in') + expr() +
            keyword('{') + Opt(Lazy(stmt_list)) + keyword('}')
    ) ^ process


def stmt():
    return (
            for_stmt() |
            foreach_stmt() |
            func_stmt() |
            call_stmt() |
            assign_stmt() |
            assign_const_stmt() |
            reassign_stmt() |
            if_stmt() |
            while_stmt() |
            echo_stmt() |
            unary_op_stmt() |
            break_stmt() |
            continue_stmt() |
            block_stmt() |
            return_stmt() |
            expr()
    )


def parser() -> Phrase:
    return Phrase(stmt_list())


def imp_parser(tokens: List[Token]):
    return parser()(tokens, 0)