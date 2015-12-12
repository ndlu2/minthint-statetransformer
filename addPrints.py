from __future__ import print_function
import csv
import sys

from pycparser import c_ast
from pycparser import c_parser
from pycparser import c_generator
from pycparser import parse_file

class FuncDefVisitor(c_ast.NodeVisitor):
    def __init__(self, function, varList, outOfScopeVarList):
        self.name = ''
        self.function = function
        self.varList = varList
        self.outOfScopeVarList = outOfScopeVarList

    def visit_FuncDef(self,node):
        if (len(self.varList) < 1):
            return

        self.name = node.decl.name

        # find the correct function name
        if (self.name== self.function):
            for idx, item in enumerate(node.body.block_items):
                # find the return statement within that function
                if (isinstance(item, c_ast.Return)):
                    returnStatement = item
                    for var in self.varList:
                        outOfScope = False
                        varArr = var.split(' ')
                        # make sure all variables of the expression are in-scope
                        for v in varArr:
                            if any(scopeV in v for scopeV in self.outOfScopeVarList) and v != '':
                                outOfScope = True
                                break
                        if outOfScope:
                            # replace the return statement with a print of 0
                            node.body.block_items[idx] = c_ast.FuncCall(c_ast.ID('fprintf'), c_ast.ExprList([c_ast.ID('stdout'), c_ast.Constant('int', "0")]))
                            break
                        else:
                            # replace the return statement with the first printed variable
                            node.body.block_items[idx] = c_ast.FuncCall(c_ast.ID('fprintf'), c_ast.ExprList([c_ast.ID('stdout'), c_ast.Constant('str', '"%d,"'), c_ast.Constant('str', var)]))
                            break
            # add the remaining print statements
            for var in self.varList[1:]:
                # make sure all variables of the expression are in-scope
                outOfScope = False
                varArr = var.split(' ')
                for v in varArr:
                    if any(scopeV in v for scopeV in self.outOfScopeVarList) and v != '':
                        outOfScope = True
                        break
                # print 0 if a variable is out of scope
                if outOfScope:
                    node.body.block_items.append(c_ast.FuncCall(c_ast.ID('fprintf'), c_ast.ExprList([c_ast.ID('stdout'), c_ast.Constant('int', '0')])))
                # print the expression if all variables are in scope
                else:
                    if ('/' in var):
                        denom = var[var.index('/')+1:]
                        binaryOp = c_ast.BinaryOp('==', c_ast.Constant('str', denom), c_ast.Constant('int', '0'))
                        ifTrue = c_ast.Compound([c_ast.FuncCall(c_ast.ID('fprintf'), c_ast.ExprList([c_ast.ID('stdout'), c_ast.Constant('str', '"%d,"'), c_ast.Constant('int', '0')]))])
                        ifFalse = c_ast.Compound([c_ast.FuncCall(c_ast.ID('fprintf'), c_ast.ExprList([c_ast.ID('stdout'), c_ast.Constant('str', '"%d,"'), c_ast.Constant('str', var)]))])
                        node.body.block_items.append(c_ast.If(binaryOp, ifTrue, ifFalse))
                    else:
                        node.body.block_items.append(c_ast.FuncCall(c_ast.ID('fprintf'), c_ast.ExprList([c_ast.ID('stdout'), c_ast.Constant('str', '"%d,"'), c_ast.Constant('str', var)])))
            # add a newline character and the original return statement at the end
            node.body.block_items.append(c_ast.FuncCall(c_ast.ID('fprintf'), c_ast.ExprList([c_ast.ID('stdout'), c_ast.Constant('str', '"\\n"')])))
            node.body.block_items.append(returnStatement)

def show_decl_file(cFile, function, varFile, scopeVarFile):
    varList = importVars(varFile)
    outOfScopeVarList = importOutOfScopeVars(scopeVarFile)
    ast = parse_file(cFile, use_cpp=True)
    v = FuncDefVisitor(function, varList, outOfScopeVarList)
    v.visit(ast)
    generator = c_generator.CGenerator()
    print(generator.visit(ast))

def importVars(varFile):
    varList = []
    with open(varFile) as varLines:
        try:
            for line in varLines:
                varList.append(line[line.index(' ')+1:-1])
            return varList
        except Exception as e:
            print(str(e))

def importOutOfScopeVars(scopeVarFile):
    with open(scopeVarFile, 'rt') as f:
        reader = csv.reader(f)
        lists = list(reader)
        return lists[0]

if __name__=='__main__':
        if len(sys.argv)>4:
            cFile = sys.argv[1] # tcas.c
            function = sys.argv[2] # alt_sep_test
            varFile = sys.argv[3] # attrmap.75
            scopeVarFile = sys.argv[4] # outOfScopeVariables output
            show_decl_file(cFile, function, varFile, scopeVarFile)


