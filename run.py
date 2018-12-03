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

import parser as parser
import ast as ast
import vccVisitor
import labelVisitor
import semantics as sem

import sys

def main ():
    a = ast.parse_file (sys.argv [1])
    print('(set-option :fixedpoint.engine spacer)')
    lv=labelVisitor.LabelVisitor()
    b=lv.visit(a,createLabel=True)
    rels = lv.get_rel_declr()
    for f in rels:
    	print(f)
    decl_vars = lv.get_var_declr()
    for f in decl_vars:
    	print(f)
    pv = vccVisitor.VCGenVisitor (out=sys.stdout)
    pv.visit (b)
    print('(query Error)')
  
if __name__ == '__main__':
    main ()
