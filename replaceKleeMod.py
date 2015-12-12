from __future__ import print_function
import csv
import collections
import sys

from pycparser import c_ast
from pycparser import c_parser
from pycparser import c_generator
from pycparser import parse_file

class NodeVisitor(object):
    def __init__(self, faultyLine, kleeVal):
        self.faultyLine = faultyLine
        self.kleeVal = kleeVal

    def visit(self, node):
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        if (node.coord):
            # Extract and check line number
            lineNum = str(node.coord)[str(node.coord).index(':')+1:]
            if (lineNum == self.faultyLine):
                if isinstance(node, c_ast.Assignment):
                    node.rvalue = c_ast.Constant('int', self.kleeVal)
                    return
                elif isinstance(node, c_ast.If):
                    node.cond = c_ast.Constant('int', self.kleeVal)
                    return
                elif isinstance(node, c_ast.Return):
                    node.expr = c_ast.Constant('int', self.kleeVal)
                    return
                elif isinstance(node, c_ast.Decl):
                    node.init = c_ast.Constant('int', self.kleeVal)

        for c_name, c in node.children():
            # recursively visit child nodes
            self.visit(c)

def show_decl_file(cFile, faultyLine, kleeVal):
    ast = parse_file(cFile, use_cpp=True)
    v = NodeVisitor(faultyLine, kleeVal)
    v.visit(ast)
    generator = c_generator.CGenerator()
    print(generator.visit(ast))

if __name__=='__main__':
        if len(sys.argv)>3:
            cFile = sys.argv[1] # tcas.c - modified with print statements
            faultyLine = sys.argv[2] # faulty line number
            kleeVal = sys.argv[3] # output from klee
            show_decl_file(cFile, faultyLine, kleeVal)


