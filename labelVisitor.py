import ast
"""
ASSUMPTION : Program is in SSA
Approach : go top down the program.
keep track of active variables upto each statement
label each top level statement
"""
class LabelVisitor (ast.AstVisitor):
    """Labels each statement"""
    def __init__ (self, out = None):
        self.vars=[]
        self.count=0
        self.pre=None
        super (LabelVisitor, self).__init__ ()
        self.labels=[]

    def print_vars(self):
        st=self.vars[0]
        for v in self.vars[1:]:
            st=st+' '+v
        return st
    def add_var(self,v):
        if not v in self.vars:
            self.vars.append(v)
    def visit (self, node,createLabel=False):
        return super (LabelVisitor, self).visit (node,createLabel=createLabel)

    def visit_FloatVar (self, node, *args, **kwargs):
        return node

    def visit_BoolConst (self, node, *args, **kwargs):
        return node

    def visit_FloatConst (self, node, *args, **kwargs):
        return node

    def visit_Exp (self, node, *args, **kwargs):
        return node

    def get_var_declr(self):
        #all variables are Int
        #TODO support types as well
        declare_var_strings=[]
        for v in self.vars:
            declare_var_strings.append('(declare-var '+v + ' Int)')
        return declare_var_strings

    def get_rel_declr(self):
        return self.labels

    def createLabel(self,label='h',error=False):
        if error :
            label_string='Error'
            label_def='(declare-rel Error ( ))'
            self.labels.append(label_def)
            return label_string
        label_string='( '+label+str(self.count)+' '+self.print_vars()+' )'
        self.pre=label_string
        label_def='(declare-rel ' + label+str(self.count)+' (Int'
        for f in self.vars[1:]:
            label_def=label_def+' Int'
        label_def=label_def+') )'
        self.labels.append(label_def)
        return label_string

    def visit_StmtList (self, node, *args, **kwargs):
        new_stmt_lists=[]
        if node.stmts is None or len (node.stmts) == 0:
            return
    
        stmt=self.visit(node.stmts[0])
        if kwargs['createLabel']:
            self.count=self.count+1
            if stmt.__class__.__name__=='WhileStmt':
                inv=self.createLabel(label='inv')
                stmt.addPre(inv)
                stmt.addInv(inv)
            else:
                stmt.addPre(None)
            #the order matters :(
            post=self.createLabel()
            stmt.addPost(post)
        new_stmt_lists.append(stmt)
        if len (node.stmts) > 1:
            for s in node.stmts[1:]:
                stmt=self.visit(s)
                if kwargs['createLabel']:
                    stmt.addPre(self.pre)
                    self.count=self.count+1 
                    if stmt.__class__.__name__=='WhileStmt':
                        stmt.addInv(self.createLabel(label='inv'))
                    #the order matters :(
                    if stmt.__class__.__name__=='AssertStmt':
                        l=self.createLabel(error=True)
                    else:
                        l=self.createLabel()
                    stmt.addPost(l)
                new_stmt_lists.append(stmt)
        return ast.StmtList(new_stmt_lists)

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

    def visit_AsgnStmt (self, node, *args, **kwargs):
        self.add_var(node.lhs.name)
        return node

    def visit_AssertStmt (self, node, *args, **kwargs):
        #what if Assert occurs inside while loop??
        return node

    def visit_AssumeStmt (self, node, *args, **kwargs):
        #what if Assume occurs inside while loop??
        return node

    def visit_HavocStmt (self, node, *args, **kwargs):
        for v in node.vars:
            self.add_var(node.vars)
        return node

    def visit_IfStmt (self, node, *args, **kwargs):
        self.visit (node.cond)
        self.visit (node.then_stmt)
        if node.has_else ():
            self.visit (node.else_stmt)
        return node

    def visit_WhileStmt (self, node, *args, **kwargs):
        #TODO does not support nested while loops
        assert(node.body.__class__.__name__!='WhileStmt')
        self.visit (node.cond)
        self.visit (node.body)
        return node