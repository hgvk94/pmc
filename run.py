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
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import parser as parser
import ast as ast
import vccVisitor
import labelVisitor
import semantics as sem
import scipy.stats
import numpy
import sys
class PD ():
	def __init__ (self,nm ,p1=None,p2=None):
		#pd_obj can only be norm for now. change depending on nm
		self.pd_obj = scipy.stats.norm(loc=p1,scale=p2)
		self.mean=p1
		self.sd=p2
	#partition into k spaces
	def partition(self,k):
		delta=1/float(k)
		return [self.pd_obj.ppf(delta*float(x)) for x in xrange(1,k+1)]
def model_check_labelled_prog(rel_decl,vars_decl,labelled_ast,replacement_func,toggle):
	#initialize fixed point engine
	s=Fixedpoint()
	s.set(engine="spacer")
	#register relation err
	err=Bool('Error')
	s.register_relation(err.decl())
	#begin creating horn clauses 
	st=''
	#declare relations in SMT2
	for f in rel_decl:
		st=st+f+'\n'
	#declare vars in SMT2
	for f in vars_decl:
		st=st+f+'\n'
	#declare rules in SMT2 
	pv = vccVisitor.VCGenVisitor (out=st,func_repl=replacement_func,reverse_cond=toggle)
	pv.visit (labelled_ast)
	st=pv.out
	#pass relations and variables and rules to the solver
	s.parse_string(st)
	#query error
	return s.query(err)

def main ():
	ini_ast= ast.parse_file (sys.argv [1])
	agg_prob_safe=-1
	agg_prob_unsafe=-1
	#initial run of the visitor. Label each node, figure out prob distibutions and error prob
	lv=labelVisitor.LabelVisitor()
	lb_ast=lv.visit(ini_ast,createLabel=True)
	#no random variables. Either the property holds or does not.
	if(not lv.pd):
		print("no random variables, treating all variables as non deterministic")
		res=model_check_labelled_prog(lv.get_rel_declr(),lv.get_var_declr(),lb_ast,[],False)
		if res==unsat:
			print("Safe with probability 1")
		elif res==sat:
			print("Unsafe with unknown probability")
		else:
			print("unknown")
		return 0
	#collect error prob
	error_prob = lv.prob
	assert(error_prob<=1)
	assert(error_prob>0)
	k=1
	while agg_prob_safe<error_prob and agg_prob_unsafe<(1-error_prob):
		print("trying " + str(k) + " partitions")
		agg_prob_safe=0
		agg_prob_unsafe=0
		#TODO handle cases when we have more than one random variable
		assert(len(lv.pd)==1)
		pd=PD(lv.pd[0].name,lv.pd[0].args[0],lv.pd[0].args[1])
		#since we are computing prob(X<x), the last element would be infinity
		parts=pd.partition(k)
		new_func=[]
		red_points=[]
		blue_points=[]
		for f in xrange(len(parts)):
			prop_valid=True
			if(f==0):
				lb=None
				if scipy.isinf(parts[f]):
					ub=None
				else:
					ub=float(parts[f])
			elif(f==len(parts)-1):
				ub=None
				lb=float(parts[f-1])
			else:
				lb=float(parts[f-1])
				ub=float(parts[f])
			if lb:
				lbp=lb
			else:
				lbp=-100000
			if ub:
				ubp=ub
			else:
				ubp=100000
			print("trying bounds "+str(lbp)+" "+str(ubp))
			#compute lb and ub
			lv.pd[0].add_bounds(lb,ub)
			new_func.append(lv.pd[0])
			#check the complement of the property
			toggle=True
			#can use update_rule to make these incremental
			res=model_check_labelled_prog(lv.get_rel_declr(),lv.get_var_declr(),lb_ast,new_func,toggle)
			#unsat is defined as an element of checkSatResult in z3
			if res==unsat:
				agg_prob_unsafe=agg_prob_unsafe+1/float(k)
				print("Unsafe with probability " + str(agg_prob_unsafe))
				for x in numpy.arange(lbp,ubp,(float(ubp)-float(lbp))/100):
					red_points.append(x)
				prop_valid=False
			if(agg_prob_unsafe>=(1-error_prob)):
				print("system is NOT SAFE with the desired propbability")
				break
			#check the property
			toggle=False
			#can use update_rule to make these incremental
			res=model_check_labelled_prog(lv.get_rel_declr(),lv.get_var_declr(),lb_ast,new_func,toggle)
			#unsat is defined as an element of checkSatResult in z3
			if  res==unsat:
				assert(prop_valid)
				agg_prob_safe=agg_prob_safe+1/float(k)
				print("Safe with probability " + str(agg_prob_safe))
				for x in numpy.arange(lbp,ubp,(float(ubp)-float(lbp))/100):
					blue_points.append(x)
			if(agg_prob_safe>=error_prob):
				print("system is SAFE with the desired propbability")
				break
		if(len(red_points)>0):
			print_bounds(red_points,1/float(k),'red')
		if(len(blue_points)>0):
			print_bounds(blue_points,1/float(k),'blue')
		k=k+1
def print_bounds(points,height,col):
	plt.xlabel('X values')
	plt.ylabel('Probabilities')
	y_values=[height for x in points]
	plt.plot(points,y_values,'o',color=col)
	plt.show()
if __name__ == '__main__':
	main ()
