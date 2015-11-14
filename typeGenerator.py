from __future__ import print_function
import sys

from pycparser import c_ast
from pycparser import c_parser
from pycparser import c_generator
from pycparser import parse_file

text = r"""
int func(void)
{
  int x = 1;
  return x;
}
"""
class TypeDeclVisitor(c_ast.NodeVisitor):
    def __init__(self):
        pass
    def visit_TypeDecl(self,node):
        childList = node.children()
        varName = node.declname
        if varName==None:
            return
        print (childList[0][1].names[0] + " " + varName)

class IdentifierTypeVisitor(c_ast.NodeVisitor):
    def __init__(self,IDType):
        self.IDType = IDType
    def visit_IdentifierType(self,node):
        if node.names[0] == self.IDType:
            print (self.IDType)

def show_id_type(code, typ):
    parser = c_parser.CParser()
    ast = parser.parse(code)
    v = IdentifierTypeVisitor(typ)
    v.visit(ast)

def show_decl(code):
    parser = c_parser.CParser()
    ast = parser.parse(code)
    v = TypeDeclVisitor()
    v.visit(ast)
def show_decl_file(filename):
    ast = parse_file(filename, use_cpp=True)
    v = TypeDeclVisitor()
    v.visit(ast)

if __name__=='__main__':
    if len(sys.argv)>1:
        filename = sys.argv[1]
        show_decl_file(filename)
    else:
        code = text
        #typ = 'int'
        #show_id_type(code,typ)
        show_decl(code)


