# The MIT License (MIT)
# Copyright (c) 2016 Arie Gurfinkel

# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:

# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
import ast as myAst
class pProgSemantics (object):
    def __init__ (self):
        pass
    def start (self, ast, *args, **kwargs):
        if len (ast.stmts) == 1:
            return ast.stmts [0]
        return ast

    def stmt_list (self, ast, *args, **kwargs):
        return myAst.StmtList (ast)

    def asgn_stmt (self, ast, *args, **kwargs):
        return myAst.AsgnStmt (ast.lhs, ast.rhs)

    def if_stmt (self, ast, *args, **kwargs):
        return myAst.IfStmt (ast.cond, ast.then_stmt, ast.else_stmt)

    def while_stmt (self, ast, *args, **kwargs):
        return myAst.WhileStmt (ast.cond, ast.body, ast.inv)

    def assert_stmt (self, ast, *args, **kwargs):
        return myAst.AssertStmt (ast.cond,ast.prob)

    def func (self, ast, *args, **kwargs):
        return myAst.Func(ast.var,ast.nm,ast.args)

    def assume_stmt (self, ast, *args, **kwargs):
        return myAst.AssumeStmt (ast.cond)

    def havoc_stmt (self, ast, *args, **kwargs):
        assert len (ast) >= 1
        return myAst.HavocStmt (ast.vars)

    def bool_const (self, ast, *args, **kwargs):
        if str(ast) == 'true':
            val = True
        else:
            val = False
        return myAst.BoolConst (val)

    def bexp (self, ast, *args, **kwargs):
        return self.bterm (ast, args, kwargs)

    def bterm (self, ast, *args, **kwargs):
        if ast.op is None: return ast.args
        assert len (ast.args) > 1
        return myAst.BExp (ast.op, ast.args)

    def bfactor (self, ast, *args, **kwargs):
        if ast.op is not None:
            return myAst.BExp (ast.op, [ast.arg])
        return ast.arg

    def rexp (self, ast, *args, **kwargs):
        return myAst.RelExp (ast.lhs, str (ast.op), ast.rhs)

    def aexp (self, ast, *args, **kwargs):
        return ast

    def addition (self, ast, *args, **kwargs):
        return self.subtraction (ast, *args, **kwargs)

    def subtraction (self, ast, *args, **kwargs):
        return self.mult (ast, *args, **kwargs)

    def term (self, ast, *args, **kwargs):
        return ast

    def mult (self, ast, *args, **kwargs):
        return self.division (ast, *args, **kwargs)

    def division (self, ast, *args, **kwargs):
        return myAst.AExp (str (ast.op), [ast.lhs, ast.rhs])

    def name (self, ast, *args, **kwargs):
        return myAst.FloatVar(ast)

    def number (self, ast, *args, **kwargs):
        if '.' in str(ast):
            num = ''.join(str(d) for a in ast for d in a)
        else:
            num = str(ast)
        return myAst.FloatConst (float (num))

    def func_name ( self, ast, *args,**kwargs):
        print("reached func_name")
        return str(ast)

    def neg_number (self, ast, *args, **kwargs):
        return myAst.FloatConst (-1 * ast.val)
