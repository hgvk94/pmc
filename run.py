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
class PD ():
	def __init__ (self,nm ,p1=None,p2=None):
		#pd_obj can only be norm for now. change depending on nm
		self.pd_obj = scipy.stats.norm
		self.mean=p1
		self.sd=p2
	#partition into k spaces
	def partition(self,k):
		delta=1/float(k)
		return [self.pd_obj.ppf(delta*float(x)) for x in xrange(1,k+1)]

def main ():
	a = ast.parse_file (sys.argv [1])
	agg_prob=0.0
	#initial run of the visitor. Label each node, figure out prob distibutions and error prob
	lv=labelVisitor.LabelVisitor()
	b=lv.visit(a,createLabel=True)
	#collect error prob
	error_prob = lv.prob
	assert(error_prob<=1)
	assert(error_prob>0)
	k=1
	while agg_prob<error_prob:
		agg_prob=0
		pd=PD(lv.pd[0].name,lv.pd[0].args[0],lv.pd[0].args[1])
		#since we are computing prob(X<x), the last element would be infinity
		parts=pd.partition(k)
		print(parts)
		new_func=[]
		for f in xrange(len(parts)):
			if(f==0):
				lb=None
				if scipy.isinf(parts[f]):
					ub=None
				else:
					ub=parts[f]
			elif(f==len(parts)-1):
				ub=None
				lb=parts[f-1]
			else:
				lb=parts[f-1]
				ub=parts[f]
			#compute lb and ub
			lv.pd[0].add_bounds(lb,ub)
			new_func.append(lv.pd[0])
			print(new_func[0].lb)
			print(new_func[0].ub)
			#can use update_rule to make these incremental
			#initialize fixed point engine
			s=Fixedpoint()
			s.set(engine="spacer")
			#register relation err
			err=Bool('Error')
			s.register_relation(err.decl())
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
			#pass relations and variables and rules to the solver
			s.parse_string(st)
			#query error
			#sat is defined as an element of checkSatResult in z3
			if s.query(err)==sat:
				print("satisfiable")
				print(s.get_answer())
			else:
				print("unsatisfiable")
				agg_prob=agg_prob+1/float(k)
			if(agg_prob>=error_prob):
				break
		k=k+1
if __name__ == '__main__':
	main ()
