import ast
"""
ASSUMPTION : Program is in SSA, each top level statement has a label
Approach : go top down the program.
for each statement, generate horn clauses of the form
h-post-label(vars) <- h-pre-label(vars) & cond(body)
for now, just print the horn clauses.
"""
class VCGenVisitor (ast.AstVisitor):
    """A VC gen visitor"""
    def __init__ (self, out = None):
        super (VCGenVisitor, self).__init__ ()
        #TODO change this to (ordered) mappings from variables to their SSA
        if out is None:
            self.out = sys.stdout
        else:
            self.out = out

    def _indent (self, **kwargs):
        self._write (' '*kwargs['indent'])
    def _write (self, v):
        self.out.write (str (v))
    def _open_brkt (self, **kwargs):
        if not kwargs['no_brkt']:
            self._write ('(')
    def _close_brkt (self, **kwargs):
        if not kwargs['no_brkt']:
            self._write (')')

    def visit (self, node, indent=0, no_brkt=False,negate=False,create_horn=True):
        super (VCGenVisitor, self).visit (node,
                                          indent=indent, no_brkt=no_brkt,negate=negate,create_horn=create_horn)

    def visit_FloatVar (self, node, *args, **kwargs):
        self._write (node.name)

    def visit_BoolConst (self, node, *args, **kwargs):
        if node.val:
            self._write ('True')
        else:
            self._write ('False')

    def visit_FloatConst (self, node, *args, **kwargs):
        self._write (node.val)

    def visit_Exp (self, node, *args, **kwargs):
        if kwargs['negate']:
            self._write(' ( not')
        if node.is_unary ():
            self._write (node.op)
            self.visit (node.arg (0))
        else:
            self._open_brkt (**kwargs)
            self.visit (node.arg (0))
            for a in node.args [1:]:
                self._write (' ')
                self._write (node.op)
                self._write (' ')
                self.visit (a)
            self._close_brkt (**kwargs)
        if kwargs['negate']:
            self._write(' )')

    def visit_StmtList (self, node, *args, **kwargs):
        if node.stmts is None or len (node.stmts) == 0:
            return

        indent_lvl = kwargs['indent']
        if len (node.stmts) > 1:
            self._indent (**kwargs)
            self._write('{\n')
            indent_lvl = indent_lvl + 2

        self._indent (indent=indent_lvl)
        self.visit (node.stmts [0], indent=kwargs['indent'] + 2)
        self._write(' -->' + node.stmts[0].post_label)


        if len (node.stmts) > 1:
            for s in node.stmts[1:]:
                self._write (';\n')
                self._indent (indent=indent_lvl)
                #TODO this does not support nested while loops
                if s.__class__.__name__ == 'WhileStmt':
                    self._write(s.pre_label + ' and ')
                    self.visit(s.cond,negate=True) 
                    self._write(' --> '+s.post_label)
                self._write(s.pre_label + ' and ')
                self.visit (s, indent=indent_lvl)
                if s.__class__.__name__ == 'WhileStmt':
                    self._write(' -->' + s.pre_label_next)
                else : 
                    self._write(' -->' + s.post_label)

        if len (node.stmts) > 1:
            self._write ('\n')
            self._indent (**kwargs)
            self._write ('}')

    def visit_Func(self,node,*args,**kwargs):
        self._write(node.name+'(')
        if node.args is None or len(node.args) == 0 :
            self._write(')')
        else:
            for s in node.args[0:-1]:
                self.visit(s)
                self._write(',')
            self.visit(node.args[-1])
            self._write(')')

    def create_horn_head (self,create_prev=True):
        if self.prev_horn:
            self._write(' and ' + self.prev_horn)
        new_horn_head='h'+str(self.count)+'( '
        var_list=list(self.vars)
        new_horn_head = new_horn_head + var_list[0]
        for f in var_list[1:]:
            new_horn_head = new_horn_head + ',' + f
        new_horn_head = new_horn_head + ' )'
        self._write(' --> ' + new_horn_head + '\n')
        if create_prev:
            self.prev_horn=new_horn_head

    def visit_AsgnStmt (self, node, *args, **kwargs):
        self.visit (node.lhs)
        self._write (' = ')
        self.visit (node.rhs, no_brkt=True)

    def visit_AssertStmt (self, node, *args, **kwargs):
        self.visit (node.cond, no_brkt=True,negate=True)

    def visit_AssumeStmt (self, node, *args, **kwargs):
        self._write ('assume ')
        self.visit (node.cond, no_brkt=True)

    def visit_HavocStmt (self, node, *args, **kwargs):
        pass

    def visit_IfStmt (self, node, *args, **kwargs):
        if node.has_else ():
            self._write('( ( ')
        self.visit (node.cond, no_brkt=True)
        self._write(' and ')
        self.visit (node.then_stmt)
        if node.has_else ():
            self._write(') or ( ')
            self.visit (node.cond, negate=True)
            self._write(' and ')
            self.visit (node.else_stmt)
            self._write(') )')

    def visit_WhileStmt (self, node, *args, **kwargs):
        #TODO does not support nested while loops
        self.visit (node.cond, no_brkt=True)
        if node.body.__class__.__name__=='StmtList':
            for s in node.body.stmts:
                self._write(' and ')
                self.visit(s)
        else:
            self._write(' and ')
            self.visit(node.body)