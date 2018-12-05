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

from __future__ import print_function
from z3 import *
import parser as parser
import ast as ast
import vccVisitor
import labelVisitor
import semantics as sem
import scipy.stats
import sys

def main ():
    a = ast.parse_file (sys.argv [1])
    #initialize fixed point engine
    s=Fixedpoint()
    s.set(engine="spacer")
    #register relation err
    err=Bool('Error')
    s.register_relation(err.decl())
    #initial run of the visitor. Label each node, figure out prob distibutions and error prob
    lv=labelVisitor.LabelVisitor()
    b=lv.visit(a,createLabel=True)
    #collect error prob
    error_prob = lv.prob
   	#compute lb and ub
   	#needs to be inside a while loop
    new_func=[]
    for f in lv.pd:
    	f.add_bounds(5,6)
    	new_func.append(f)
	#begin creating horn clauses 
	#st='(set-option :fixedpoint.engine spacer)\n'
	st=''
	#declare relations in SMT2
    rels = lv.get_rel_declr()
    for f in rels:
    	st=st+f+'\n'
	#declare vars in SMT2
    decl_vars = lv.get_var_declr()
    for f in decl_vars:
    	st=st+f+'\n'
	#declare rules in SMT2 
    pv = vccVisitor.VCGenVisitor (out=st,func_repl=new_func)
    pv.visit (b)
    st=pv.out
    #query error
    #st=st+'\n(query Error)\n'
    #print(st)
    #pass relations and variables and rules to the solver
    s.parse_string(st)
    #query error
    #sat is defined as an element of checkSatResult in z3
    if s.query(err)==sat:
    	print("satisfiable")
    	print(s.get_answer())
    else:
    	print("unsatisfiable")
if __name__ == '__main__':
    main ()
