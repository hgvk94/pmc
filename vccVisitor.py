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
    def __init__ (self, out = None,func_repl=None,reverse_cond=False):
        super (VCGenVisitor, self).__init__ ()
        self.reverse_cond=reverse_cond
        self.func_repl=func_repl
        if out is None:
            self.out = sys.stdout
        else:
            self.out = out
    def _indent (self, **kwargs):
        self._write (' '*kwargs['indent'])
    def _write (self, v):
        self.out = self.out + str (v)
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
            self._write ('( ' + node.op)
            self.visit (node.arg (0))
            self._write(' )')
        else:
            self._write ('( ')
            self._write (node.op)
            self._write (' ')
            self.visit (node.arg (0))
            for a in node.args [1:]:
                self._write (' ')
                self.visit (a)
            self._write (' )')
        if kwargs['negate']:
            self._write(' )')

    def create_pre_label(self, node):
        if node.pre_label:
            self._write('( rule (=> ( and ')
            self._write(node.pre_label+ ' ')
            self.visit (node)
            self._write(') ' + node.post_label + '))')
        else:
            self._write('( rule (=> ')
            self.visit (node)
            self._write(node.post_label + '))')

    def visit_StmtList (self, node, *args, **kwargs):
        if node.stmts is None or len (node.stmts) == 0:
            return

        indent_lvl = kwargs['indent']

        self._indent (indent=indent_lvl)
        #if stmt0 has precond, assert it
        if node.stmts[0].pre_label and kwargs['create_horn'] and not node.stmts[0].shouldSkip:
                self._write( '( rule ' + node.stmts[0].pre_label +' )\n')
        if kwargs['create_horn'] and not node.stmts[0].shouldSkip :
            self._write('( rule (=> ')
        self.visit (node.stmts[0])
        if kwargs['create_horn'] and not node.stmts[0].shouldSkip:
            #top level statement
            self._write(' '+node.stmts[0].post_label + ' ))')

        if len (node.stmts) > 1:
            for s in node.stmts[1:]:
                #TODO this does not support nested while loops
                if kwargs['create_horn'] and not s.shouldSkip:
                    self._write ('\n')
                    if s.__class__.__name__ == 'WhileStmt':
                        #post label holds after exit
                        self._write('( rule (=> ( and ' + s.inv + ' ')
                        self.visit(s.cond,negate=True)
                        self._write(' ) '+s.post_label+'))\n')
                        #pre label implies inv
                        self._write('( rule (=> ' + s.pre_label + ' ' + s.inv+'))\n')
                        #inv holds after one transition
                        self._write('( rule (=> ( and ' + s.inv + ' ')
                        self.visit (s)
                        self._write(' ) ' + s.inv + ' ))')
                    else : 
                        #pre label and condition implies post label
                        self.create_pre_label(s)
                        
                else:
                    self.visit(s)

    def visit_Func(self,node,*args,**kwargs):
        for f in self.func_repl:
            if f == node:
                if not (f.ub or f.lb):
                    return
                if f.ub and f.lb:
                    self._write('( and ')
                if f.ub:
                    self._write('(< ' + node.var.name + ' ' +str(f.ub) + ') ')
                if f.lb:
                    self._write('(>= ' + node.var.name +' ' +str(f.lb) + ') ')
                if f.ub and f.lb:
                    self._write(' )')

    def visit_AsgnStmt (self, node, *args, **kwargs):
        self._write ('( = ')
        self.visit (node.lhs)
        self._write(' ')
        self.visit (node.rhs, no_brkt=True)
        self._write(' )')

    def visit_AssertStmt (self, node, *args, **kwargs):
        self.visit (node.cond,negate=(not self.reverse_cond))

    def visit_AssumeStmt (self, node, *args, **kwargs):
        sys.stderr.write("Assumes not supported")
        assert(False)
        self._write ('assume ')
        self.visit (node.cond, no_brkt=True)

    def visit_HavocStmt (self, node, *args, **kwargs):
        pass

    def visit_IfStmt (self, node, *args, **kwargs):
        if node.has_else ():
            self._write('( or ')
        self._write('( and ')
        self.visit (node.cond, no_brkt=True)
        self._write(' ')
        self.visit (node.then_stmt,create_horn=False)
        self._write(' )')
        if node.has_else ():
            self._write('( and ')
            self.visit (node.cond, negate=True)
            self._write(' ')
            self.visit (node.else_stmt,create_horn=False)
            self._write(') )')

    def visit_WhileStmt (self, node, *args, **kwargs):
        #TODO does not support nested while loops
        assert(node.body.__class__.__name__!='WhileStmt')
        self._write('( and ')
        self.visit (node.cond, no_brkt=True)
        self._write(' ')
        self.visit (node.body,create_horn=False)
        self._write(' )')