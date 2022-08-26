# -*- coding: utf-8 -*-
from functools import reduce
from pprint import pprint

from .combinator import *
from ..ast import expressions, statements
from ..lexer.types import Token, TokenType


def keyword(kw: str) -> Reserved:
    return Reserved(kw, TokenType.RESERVED)


def operator(kw: str) -> Reserved:
    return Reserved(kw, TokenType.OPERATOR)


def process_boolean(op):
    match op:
        case 'on' | 'true' | 'enable':
            return True
        case 'off' | 'false' | 'disable':
            return False
        case _:
            raise RuntimeError(f'unknown boolean value: {op}')


id_tag = Tag(TokenType.ID)
num = Tag(TokenType.INT) ^ (lambda x: int(x))
float_num = Tag(TokenType.FLOAT) ^ (lambda x: float(x))
boolean = Tag(TokenType.BOOL) ^ process_boolean
null = keyword('null') ^ (lambda x: expressions.NullAST())
string = Tag(TokenType.STRING) ^ (lambda x: expressions.StringAST(x[1:-1]))
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
    """Array expression
    [x, y, z, ...]
    """
    def process(p):
        (_, data), _ = p
        return expressions.ArrayAST(data)
    return keyword('[') + Opt(Rep(Lazy(expression) + Opt(keyword(',')))) + keyword(']') ^ process


def array_generator_expr():
    """Array generator expression
    [i for i in object if i > x]
    """
    def process(p):
        ((((((_, var), _), val), _), obj), condition), _ = p
        if condition is not None:
            _, condition = condition
        return expressions.GeneratorAST(var, val, obj, condition)
    return (
            keyword('[') + expression() + keyword('for') + id_tag + operator('in') + expression() +
            Opt(keyword('if') + Exp(b_expr(), None)) + keyword(']')
    ) ^ process


def if_else_expr():
    """Ternary operator
    condition ? x : y
    x if condition else y
    """
    def process(p):
        (((body, op1), condition), op2), else_body = p
        return expressions.TernaryOpAST(body, op1, condition, op2, else_body)
    return (
            Lazy(expr) + Alt(keyword('if'), operator('?')) + Lazy(expr) +
            Alt(keyword('else'), operator(':')) + Lazy(expression)
    ) ^ process


def lambda_stmt():
    """Lambda statement
    (a, b, c) => {...}
    """
    def process(p):
        (((((_, args), _), _), _), stmts), _ = p
        arguments = []
        for arg in args:
            if arg.value[0][1] is None:
                arguments.append(expressions.ArgumentAST(arg.value[0][0], None))
            else:
                arguments.append(expressions.ArgumentAST(arg.value[0][0], arg.value[0][1][1]))
        return statements.LambdaStmt(arguments, stmts)
    return (
            keyword('(') + Rep(id_tag + Opt(operator('=') + Lazy(expression)) + Opt(keyword(','))) +
            keyword(')') + operator('=>') + keyword('{') + Opt(Lazy(stmt_list)) + keyword('}')
    ) ^ process


def module_obj_expr():
    """Module object expression
    x.y
    """
    def process(p):
        (module, _), var = p
        return expressions.ModuleCallAST(module, var)
    return id_tag + operator('.') + id_tag ^ process


def id_or_module():
    return class_property_expr() | module_obj_expr() | id_tag


def a_expr_value():
    return (
            Lazy(call_stmt) |
            Lazy(array_generator_expr) |
            Lazy(array_expr) |
            Lazy(read_stmt) |
            brace_expr() |
            module_obj_expr() |
            Lazy(class_property_expr) |
            (num ^ (lambda x: expressions.IntAST(x))) |
            (float_num ^ (lambda x: expressions.FloatAST(x))) |
            (id_tag ^ (lambda x: expressions.VarAST(x))) |
            (boolean ^ (lambda x: expressions.BoolAST(x))) |
            string |
            null
    )


def process_group(p):
    (_, r), _ = p
    return r


def a_expr_group():
    return keyword('(') + Lazy(a_expr) + keyword(')') ^ process_group


def a_expr_term():
    return (
            a_expr_value() |
            a_expr_group() |
            unary_op_stmt()
    )


def process_binop(op):
    return lambda l, r: expressions.BinOpAST(op, l, r)


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
    return expressions.RelativeOp(op, l, r)


def b_expr_relop():
    """Relation operation expression
    x >= y
    x == y
    x != y
    etc
    """
    return (
            a_expr() + any_op_in_list(relational_operators) + a_expr()
    ) ^ process_relop


def b_expr_not():
    """Not expression
    not x
    !x
    """
    return (Alt(keyword('not'), operator('!')) + Lazy(b_expr_term)) ^ (lambda p: expressions.NotOp(p[1]))


def b_expr_group():
    return (keyword('(') + Lazy(b_expr) + keyword(')')) ^ process_group


def b_expr_term():
    return b_expr_group() | b_expr_not() | b_expr_relop() | (boolean ^ (lambda x: expressions.BoolAST(x)))


def process_logic(op):
    match op:
        case 'and' | '&&':
            return lambda l, r: expressions.AndOp(l, r)
        case 'or' | '||':
            return lambda l, r: expressions.OrOp(l, r)
        case 'in':
            return lambda l, r: expressions.InOp(l, r)
        case _:
            raise RuntimeError(f'unknown logic operator: {op}')


def b_expr():
    return precedence(b_expr_term(), b_expr_precedence_levels, process_logic)


def brace_expr():
    """Brace expression
    x[y][z]
    """
    def process(p):
        (((obj, _), v), _), v_arr = p
        arr = []
        for i in v_arr:
            (_, i), _ = i.value
            arr.append(i)
        return expressions.BraceAST(obj, [v] + arr)
    return (
            (Lazy(array_expr) | Lazy(call_stmt) | string | id_or_module()) + keyword('[') +
            Lazy(expr) + keyword(']') + Rep(keyword('[') + Lazy(expr) + keyword(']'))
    ) ^ process


def expr():
    return (
            b_expr() |
            a_expr()
    )


def class_property_expr():
    """Class property statement
    x::y
    """
    def process(p):
        ((is_super, name), _), var = p
        if is_super is not None:
            is_super = True
        return expressions.ClassPropAST(name, var, is_super)
    return Opt(keyword('super')) + Alt(id_tag, keyword('this')) + operator('::') + id_tag ^ process


def expression():
    return lambda_stmt() | if_else_expr() | Lazy(switch_case_stmt) | expr()


# --== statements ==-- #
def assign_stmt():
    """Assign statement
    var x = y
    """
    def process(p):
        ((_, name), _), e = p
        return statements.AssignStmt(name, e, False, True)
    return (
            keyword('var') + id_tag + operator('=') + expression()
    ) ^ process


def assign_const_stmt():
    """Assign constant statement
    let x = y
    """
    def process(p):
        ((_, name), _), e = p
        return statements.AssignStmt(name, e, True, True)
    return (keyword('let') + id_tag + operator('=') + expression()) ^ process


def reassign_stmt():
    """Reassign statement
    x = y
    """
    def process(p):
        (name, op), e = p
        return statements.AssignStmt(name, e, False, False, op)
    return ((brace_expr() | id_or_module()) + any_op_in_list(assign_operators) + expression()) ^ process


def unary_op_stmt():
    """Unary operator statement
    x++
    ++x
    """
    def process(p):
        sym, name = p
        if sym not in unary_operators:
            name, sym = sym, name
        return expressions.UnaryOpAST(sym, expressions.VarAST(name))
    return Alt(
        any_op_in_list(unary_operators) + id_or_module(), id_or_module() + any_op_in_list(unary_operators)
    ) ^ process


def stmt_list():
    def process(rep):
        return statements.StmtList(rep)
    return Rep(Lazy(stmt) + Opt(keyword(';')) ^ (lambda x: x[0])) ^ process


def block_stmt():
    def process(rep):
        (_, l), _ = rep
        return l
    return keyword('{') + Opt(Lazy(stmt_list)) + keyword('}') ^ process


def if_stmt():
    """if-elif-else statement
    if condition1 {
        body1
    } elif condition2 {
        body2
    } elif condition3 {
        body3
    } else {
        body4
    }
    """
    def process(p):
        (((((_, condition), _), body), _), elif_array), false_p = p
        if false_p:
            (_, false_body), _ = false_p
        else:
            false_body = None
        if elif_array:
            elif_array = [i.value for i in elif_array]
        return statements.IfStmt(condition, body, elif_array, false_body)
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
    """While statement
    while condition {
        body
    }
    """
    def process(p):
        (((_, condition), _), body), _ = p
        return statements.WhileStmt(condition, body)
    result = keyword('while') + Exp(b_expr(), None) + keyword('{') + Opt(Lazy(stmt_list)) + keyword('}')
    return result ^ process


def break_stmt():
    """Break statement
    break
    """
    return keyword('break') ^ (lambda x: statements.BreakStmt())


def continue_stmt():
    """Continue statement
    continue
    """
    return keyword('continue') ^ (lambda x: statements.ContinueStmt())


def echo_stmt():
    """Echo statement
    echo(x, y, z, ...)
    """
    def process(p):
        (_, data), _ = p
        return statements.EchoStmt(data)
    return (
            keyword('echo') + keyword('(') +
            Opt(
                Rep(
                    expression() + Opt(keyword(',')) ^ (lambda x: x[0])
                ) ^ (lambda x: [i.value for i in x])
            ) + keyword(')') ^ process
    )


def read_stmt():
    """Read statement
    x = read(...)
    """
    def process(p):
        _, text = p
        return statements.ReadStmt(text)
    return keyword('read') + expression() ^ process


def func_stmt():
    """Function assign statement
    func name(args) {
        body
    }
    """
    def process(p):
        ((((((_, func_name), _), args), _), _), stmts), _ = p
        arguments = []
        for arg in args:
            if arg.value[0][1] is None:
                arguments.append(expressions.ArgumentAST(arg.value[0][0], None))
            else:
                arguments.append(expressions.ArgumentAST(arg.value[0][0], arg.value[0][1][1]))
        return statements.FuncStmt(func_name, arguments, stmts)
    return (
            keyword('func') + id_tag + keyword('(') +
            Rep(id_tag + Opt(operator('=') + Lazy(expression)) + Opt(keyword(','))) +
            keyword(')') + keyword('{') + Opt(Lazy(stmt_list)) + keyword('}')
    ) ^ process


def interface_func_stmt():
    """Interface function statement
    func name()
    """
    def process(p):
        (((_, func_name), _), args), _ = p
        arguments = []
        for arg in args:
            if arg.value[0][1] is None:
                arguments.append(expressions.ArgumentAST(arg.value[0][0], None))
            else:
                arguments.append(expressions.ArgumentAST(arg.value[0][0], arg.value[0][1][1]))
        return statements.FuncStmt(func_name, arguments, statements.StmtList([]))
    return (
            keyword('func') + id_tag + keyword('(') +
            Rep(id_tag + Opt(operator('=') + Lazy(expression)) + Opt(keyword(','))) +
            keyword(')')
    ) ^ process


def call_stmt():
    """Call statement
    func_name(args)
    func_name(args) with {
        lambda body
    }
    """
    def process(p):
        (((func_name, _), args), _), lambda_body = p
        arguments = []
        for arg in args:
            if arg.value[0][0] is None:
                arguments.append(expressions.ArgumentAST(None, arg.value[0][1]))
            else:
                arguments.append(expressions.ArgumentAST(arg.value[0][0][0], arg.value[0][1]))
        if lambda_body:
            arguments.append(expressions.ArgumentAST(None, statements.LambdaStmt([], lambda_body[0][1])))
        return statements.CallStmt(func_name, arguments)
    return (
        id_or_module() + keyword('(') +
        Rep(Opt(id_tag + operator('=')) + Lazy(expression) + Opt(keyword(','))) +
        keyword(')') + Opt(keyword('with') + keyword('{') + Opt(Lazy(stmt_list)) + keyword('}'))
    ) ^ process


def decorator_stmt():
    """Decorator statement
    @decorator
    func main() {
        ...
    }
    """
    def process(p):
        ((_, name), name_list), function = p
        names = [name]
        if name_list is not None:
            names += [i.value[1] for i in name_list]
        return statements.DecoratorStmt(names, function)
    return (
            operator('@') + Alt(Lazy(call_stmt), id_or_module()) +
            Opt(Rep(operator('@') + Alt(Lazy(call_stmt), id_or_module()))) +
            func_stmt()
    ) ^ process


def return_stmt():
    """Return statement
    return x
    """
    def process(p):
        _, return_value = p
        return statements.ReturnStmt(return_value)
    return keyword('return') + Opt(expression()) ^ process


def for_stmt():
    """For statement
    for var x = y; condition; x++ {
        body
    }
    """
    def process(p):
        (((((((_, var), _), cond), _), action), _), body), _ = p
        return statements.ForStmt(var, cond, action, body)
    return (
            keyword('for') + Lazy(assign_stmt) + keyword(';') +
            Exp(b_expr(), None) + keyword(';') +
            (Lazy(reassign_stmt) | Lazy(unary_op_stmt)) + keyword('{') + Opt(Lazy(stmt_list)) + keyword('}')
    ) ^ process


def foreach_stmt():
    """Foreach statement
    for i in object {
        body
    }
    """
    def process(p):
        (((((_, var), _), val), _), body), _ = p
        return statements.ForStmt(var, val, body, None)
    return (
            keyword('for') + id_tag + operator('in') + expression() +
            keyword('{') + Opt(Lazy(stmt_list)) + keyword('}')
    ) ^ process


def import_stmt():
    """Import statement
    import module
    import a1, a2, a3, ...
    from module_name import a, b, c, ...
    """
    def process(p):
        ((x, module), _), objects = p
        objects = [i.value[0] for i in objects]
        from_import = False
        if isinstance(x, tuple):
            objects = [module] + objects
            (_, module), _ = x
            from_import = True
        return statements.ImportStmt(module, objects, from_import)
    return Alt(
        keyword('import') + id_tag + Opt(keyword(',')) + Rep(id_tag + Opt(keyword(','))),
        keyword('from') + id_tag + keyword('import') + id_tag + Opt(keyword(',')) + Rep(id_tag + Opt(keyword(',')))
    ) ^ process


def switch_case_stmt():
    """Switch-case-else statement
    switch object {
        case x {body1}
        case [y, z, w] {body2}
        else {body3}
    }
    """
    def process(p):
        ((((_, var), _), cases), else_body), _ = p
        cases_list = []
        for c in cases:
            (((_, cond), _), body), _ = c.value
            cases_list.append(statements.CaseStmt(cond, body))
        if else_body:
            ((_, _), else_body), _ = else_body
            cases_list.append(statements.CaseStmt(None, else_body))
        return statements.SwitchCaseStmt(var, cases_list)
    return (
            keyword('switch') + expression() + keyword('{') +
            Rep(
                keyword('case') + expression() + keyword('{') + Opt(Lazy(stmt_list)) + keyword('}')
            ) + Opt(
               keyword('else') + keyword('{') + Opt(Lazy(stmt_list)) + keyword('}')
            ) + keyword('}')
    ) ^ process


def assign_class_stmt():
    """Class assign statement
    [abstract] class MyClass {
        body
    }
    """
    def process(p):
        ((((((prefix, _), name), inherit), interfaces), _), body), _ = p
        if inherit:
            _, inherit = inherit
        if interfaces:
            (_, interface), interfaces = interfaces
            interfaces = [i.value for i in interfaces] + [interface]
        else:
            interfaces = []
        return statements.AssignClassStmt(name, body, inherit, prefix, interfaces)
    return (
            Opt(keyword('abstract')) + keyword('class') + id_tag + Opt(operator(':') + id_tag) +
            Opt(keyword('of') + id_tag + Rep(id_tag)) +
            keyword('{') + Opt(Lazy(class_body)) + keyword('}')
    ) ^ process


def assign_interface_stmt():
    """Interface assign statement
    interface Name {
        body
    }
    """
    def process(p):
        (((_, name), _), body), _ = p
        return statements.InterfaceStmt(name, body)
    return (
            keyword('interface') + id_tag + keyword('{') + Opt(Lazy(interface_body)) + keyword('}')
    ) ^ process


def class_body():
    """Class body"""
    def process(p):
        return statements.StmtList(p)
    return Rep(
        Lazy(class_body_stmt) + Opt(keyword(';')) ^ (lambda x: x[0])
    ) ^ process


def interface_body():
    """Interface body"""
    def process(p):
        return statements.StmtList(p)
    return Rep(
        Lazy(interface_body_stmt) + Opt(keyword(';')) ^ (lambda x: x[0])
    ) ^ process


def init_class_stmt():
    """Assign class init func
    init(args) {
        body
    }
    """
    def process(p):
        (((_, args), _), body), _ = p
        arguments = []
        if args:
            (_, args), _ = args
            for arg in args:
                if arg.value[0][1] is None:
                    arguments.append(expressions.ArgumentAST(arg.value[0][0], None))
                else:
                    arguments.append(expressions.ArgumentAST(arg.value[0][0], arg.value[0][1][1]))
        return statements.InitClassStmt(arguments, body)
    return (
            keyword('init') + Opt(keyword('(') + Rep(
               id_tag + Opt(operator('=') + Lazy(expression)) + Opt(keyword(','))
            ) + keyword(')')) +
            keyword('{') + Opt(Lazy(stmt_list)) + keyword('}')
    ) ^ process


def class_body_stmt():
    return (
        init_class_stmt() |
        decorator_stmt() |
        func_stmt() |
        assign_stmt() |
        assign_const_stmt() |
        assign_class_stmt()
    )


def interface_body_stmt():
    return (
        interface_func_stmt() |
        assign_stmt() |
        assign_const_stmt()
    )


def try_catch_stmt():
    """Try-catch statement
    try {
        error code
    } catch e {
        catch error
    }
    """
    def process(p):
        ((((((_, try_body), _), _), e_name), _), catch_body), _ = p
        return statements.TryCatchStmt(try_body, e_name, catch_body)
    return (
            keyword('try') + keyword('{') + Opt(Lazy(stmt_list)) + keyword('}') +
            keyword('catch') + id_tag + keyword('{') + Opt(Lazy(stmt_list)) + keyword('}')
    ) ^ process


def assign_enum_stmt():
    """Enum statement
    enum CatColor {
        BROWN
        WHITE
        BLACK = "Black"
    }"""
    def process(p):
        (((_, name), _), lets), _ = p
        if lets is not None:
            body = [i.value[0] for i in lets]
        else:
            body = []
        return statements.EnumStmt(name, body)
    return (
        keyword('enum') + id_tag + keyword('{') + Opt(Rep(enum_body() + Opt(keyword(',')))) + keyword('}')
    ) ^ process


def enum_body():
    def process(p):
        if isinstance(p, tuple):
            return statements.EnumLetStmt(p[0][0], p[1])
        return statements.EnumLetStmt(p, None)
    return Alt(id_tag + operator('=') + expression(), id_tag) ^ process


def stmt():
    return (
            assign_class_stmt() |
            assign_interface_stmt() |
            assign_enum_stmt() |
            decorator_stmt() |
            func_stmt() |
            call_stmt() |
            for_stmt() |
            try_catch_stmt() |
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
            expression() |
            (Tag(TokenType.EOF) ^ (lambda x: statements.EOFStmt()))
    )


def parser() -> Phrase:
    return Phrase(stmt_list())


def imp_parser(tokens: List[Token]):
    return parser()(tokens, 0)
