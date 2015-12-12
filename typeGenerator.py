from __future__ import print_function
import sys

from pycparser import c_ast
from pycparser import c_parser
from pycparser import c_generator
from pycparser import parse_file

text = r"""

int func(void)
{
  char x = 'h';
  return x;
}
"""
varTypes = []
funcs = []
class TypeDeclVisitor(c_ast.NodeVisitor):
    def __init__(self):
        self.types = ['int','bool','char','void']
        self.exclude = ['argc', 'argv','main']

    def visit_TypeDecl(self,node):
        childList = node.children()
        varName = node.declname

        if varName == None:
            return

        varType = childList[0][1].names[0] + " " + varName

        if ((childList[0][1].names[0] in self.types and varName in self.types) or varName in self.exclude):
            return
	
	if (varName in funcs):
	    if (childList[0][1].names[0] =='bool'):
                return	
	    varType = varType + "()"

        varTypes.append(varType)


class FuncDefVisitor(c_ast.NodeVisitor):
    def _init__(self,node):
	pass
    def visit_FuncDef(self,node):		
	funcName = node.children()[0][1].name
	funcs.append(funcName)

class IdentifierTypeVisitor(c_ast.NodeVisitor):
    def __init__(self,IDType):
        self.IDType = IDType
    def visit_IdentifierType(self,node):
        if node.names[0] == self.IDType:
            print (self.IDType)

def printTypes():
    for var in varTypes:
	
        print (var + ";")


def show_id_type(code, typ):
    parser = c_parser.CParser()
    ast = parser.parse(code)
    v = IdentifierTypeVisitor(typ)
    v.visit(ast)

def show_decl(code):
    parser = c_parser.CParser()
    ast = parser.parse(code)
    v = FuncDefVisitor()
    v.visit(ast)
    v = TypeDeclVisitor()
    v.visit(ast)
    printTypes()

def show_decl_file(filename):
    ast = parse_file(filename, use_cpp=True)
    v = FuncDefVisitor()
    v.visit(ast)
    v = TypeDeclVisitor()
    v.visit(ast)
    printTypes()


if __name__=='__main__':
    if len(sys.argv)>1:
        filename = sys.argv[1]
        show_decl_file(filename)
    else:
        code = text
        #typ = 'int'
        #show_id_type(code,typ)
        show_decl(code)


