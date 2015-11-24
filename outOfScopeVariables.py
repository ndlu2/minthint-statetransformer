#Assumes declarations of functions happen at same time as definition - no prototype

from __future__ import print_function
import sys

from pycparser import c_ast, c_parser, c_generator, parse_file

text= r"""
int global1 = 5;
char global2 = 'g';

int func(int inparamA, char inparamB)
{
int inscope1 = 4;
char inscope2 = 2;
return 10;
}

int func2(void)
{
int outofscope1 = 11;
char outofscope2;
}"""

ast = None
allVar = []
scopedVars = []

class FuncDefVisitor(c_ast.NodeVisitor):
    def __init__(self, function):
        self.name = ""
        self.function = function
    def visit_FuncDef(self,node):
        self.name=node.decl.name

        if (self.name == function):
            getScopedVariables(node)
            

class DeclVisitor(c_ast.NodeVisitor):
    def __init__(self):
        self.name =""
    def visit_Decl(self,node):
        self.name = node.name
        allVar.append(self.name)


def getScopedVariables(node):
    getGlobalVariables()
    getLocalVariables(node)

def getLocalVariables(node):
    if (node.decl.type.args != None):
        for param_decl in node.decl.type.args.params:
            scopedVars.append(param_decl.name)
    for decl in node.body.block_items:
        if (decl.__class__.__name__=="Decl"):
            scopedVars.append(decl.name)
    
def getGlobalVariables():
    for node in ast.ext:
        if (node.__class__.__name__=="Decl"):
            scopedVars.append(node.name)
    


if __name__=='__main__':
    if len(sys.argv)>2:
        filename = sys.argv[1]
        function = sys.argv[2]
        ast = parse_file(filename, use_cpp=True)
    else:
        function = "func"
        parser = c_parser.CParser()
        ast = parser.parse(text)

    v2 = DeclVisitor()
    v2.visit(ast)
    v = FuncDefVisitor(function)
    v.visit(ast)
    scopedVars.append(function)
    outOfScopeVar = [obj for obj in allVar if obj not in scopedVars]
    print (",".join(outOfScopeVar))
