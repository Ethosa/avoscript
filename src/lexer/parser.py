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
    ['+', '-', '%'],
]
relational_operators = ['==', '!=', '>=', '<=', '<', '>']
unary_operators = ['--', '++', '-']
assign_operators = ['+=', '-=', '*=', '/=', '=']
b_expr_precedence_levels = [
    ['and', '&&'],
    ['or', '||'],
    ['in']
]


def array_expr():
    def process(p):
        (_, data), _ = p
        return ArrayAST(data)
    return keyword('[') + Opt(Rep(Lazy(expr) + Opt(keyword(',')))) + keyword(']') ^ process


def if_else_expr():
    def process(p):
        (((body, op1), condition), op2), else_body = p
        return TernaryOpAST(body, op1, condition, op2, else_body)
    return (
            Lazy(expr) + Alt(keyword('if'), operator('?')) + Lazy(expr) +
            Alt(keyword('else'), operator(':')) + Lazy(expression)
    ) ^ process


def module_obj_expr():
    def process(p):
        (module, _), var = p
        return ModuleCallAST(module, var)
    return id_tag + Alt(operator('.'), operator('::')) + id_tag ^ process


def id_or_module():
    return module_obj_expr() | id_tag


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
    return Lazy(call_stmt) | a_expr_value() | a_expr_group() | unary_op_stmt()


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
    return (
            a_expr() + any_op_in_list(relational_operators) + a_expr()
    ) ^ process_relop


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
        case 'in':
            return lambda l, r: InOp(l, r)
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
            module_obj_expr() |
            brace_expr() |
            Lazy(array_expr) |
            b_expr() |
            a_expr()
    )


def expression():
    return if_else_expr() | Lazy(switch_case_stmt) | expr()


# --== statements ==-- #
def assign_stmt():
    def process(p):
        ((_, name), _), e = p
        return AssignStmt(name, e, False, True)
    return (keyword('var') + id_tag + operator('=') + expression()) ^ process


def assign_const_stmt():
    def process(p):
        ((_, name), _), e = p
        return AssignStmt(name, e, True, True)
    return (keyword('const') + id_tag + operator('=') + expression()) ^ process


def reassign_stmt():
    def process(p):
        (name, op), e = p
        return AssignStmt(name, e, False, False, op)
    return (id_tag + any_op_in_list(assign_operators) + expression()) ^ process


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
                    expression() + Opt(keyword(',')) ^ (lambda x: x[0])
                ) ^ (lambda x: [i.value for i in x])
            ) ^ process
    )


def func_stmt():
    def process(p):
        ((((((_, func_name), _), args), _), _), statements), _ = p
        arguments = []
        for arg in args:
            if arg.value[0][1] is None:
                arguments.append(ArgumentAST(arg.value[0][0], None))
            else:
                arguments.append(ArgumentAST(arg.value[0][0], arg.value[0][1][1]))
        return FuncStmt(func_name, arguments, statements)
    return (
            keyword('func') + id_tag + keyword('(') +
            Rep(id_tag + Opt(operator('=') + Lazy(expression)) + Opt(keyword(','))) +
            keyword(')') + keyword('{') + Opt(Lazy(stmt_list)) + keyword('}')
    ) ^ process


def call_stmt():
    def process(p):
        ((func_name, _), args), _ = p
        arguments = []
        for arg in args:
            if arg.value[0][0] is None:
                arguments.append(ArgumentAST(None, arg.value[0][1]))
            else:
                arguments.append(ArgumentAST(arg.value[0][0][0], arg.value[0][1]))
        return CallStmt(func_name, arguments)
    return (
        id_or_module() + keyword('(') +
        Rep(Opt(id_tag + operator('=')) + expression() + Opt(keyword(','))) +
        keyword(')')
    ) ^ process


def return_stmt():
    def process(p):
        _, return_value = p
        return ReturnStmt(return_value)
    return keyword('return') + Opt(expression()) ^ process


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
            keyword('for') + id_tag + operator('in') + expression() +
            keyword('{') + Opt(Lazy(stmt_list)) + keyword('}')
    ) ^ process


def import_stmt():
    def process(p):
        return ImportStmt(p[1])
    return keyword('import') + id_tag ^ process


def switch_case_stmt():
    def process(p):
        ((((_, var), _), cases), else_body), _ = p
        cases_list = []
        for c in cases:
            (((_, cond), _), body), _ = c.value
            cases_list.append(CaseStmt(cond, body))
        if else_body:
            ((_, _), else_body), _ = else_body
            cases_list.append(CaseStmt(None, else_body))
        return SwitchCaseStmt(var, cases_list)
    return (
            keyword('switch') + expression() + keyword('{') +
            Rep(
                keyword('case') + expression() + keyword('{') + Opt(Lazy(stmt_list)) + keyword('}')
            ) + Opt(
               keyword('else') + keyword('{') + Opt(Lazy(stmt_list)) + keyword('}')
           ) + keyword('}')
    ) ^ process


def stmt():
    return (
            func_stmt() |
            call_stmt() |
            for_stmt() |
            echo_stmt() |
            foreach_stmt() |
            assign_stmt() |
            assign_const_stmt() |
            reassign_stmt() |
            if_stmt() |
            while_stmt() |
            unary_op_stmt() |
            break_stmt() |
            continue_stmt() |
            block_stmt() |
            return_stmt() |
            import_stmt() |
            expression()
    )


def parser() -> Phrase:
    return Phrase(stmt_list())


def imp_parser(tokens: List[Token]):
    return parser()(tokens, 0)
