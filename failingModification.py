from __future__ import print_function
import csv
import collections
import sys

from pycparser import c_ast
from pycparser import c_parser
from pycparser import c_generator
from pycparser import parse_file

class NodeVisitor(object):
    def __init__(self, faultyLine):
        self.faultyLine = faultyLine

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
                    # Replace with symbolic assignment
                    return node
                elif isinstance(node, c_ast.If):
                    # Add variable, make it symbolic
                    return node
                elif isinstance(node, c_ast.Return):
                    # Add variable, make it symbolic
                    return node
                elif isinstance(node, c_ast.Decl):
                    return node

        for c_name, c in node.children():
            # recursively visit child nodes
            res = self.visit(c)
            if (res):
                if isinstance(node, c_ast.FuncDef) or isinstance(node, c_ast.Compound) or isinstance(node, c_ast.FileAST):
                    if isinstance(node, c_ast.FuncDef):
                        items = node.body.block_items
                    elif isinstance(node, c_ast.Compound):
                        items = node.block_items
                    else:
                        items = node.ext
                    for i, n in enumerate(items):
                        if res == n:
                            if isinstance(res, c_ast.Assignment):
                                newNode = c_ast.FuncCall(c_ast.ID('klee_make_symbolic'), c_ast.ExprList([c_ast.ID('&'+res.lvalue.name), c_ast.FuncCall(c_ast.ID('sizeof'), c_ast.ExprList([res.lvalue])), c_ast.Constant('str', '"'+res.lvalue.name+'"')]))
                                items.insert(i+1, newNode)
                                return
                            elif isinstance(res, c_ast.If):
                                newAssign = c_ast.Assignment('=', c_ast.ID('kleeVar'), res.cond)
                                newNode = c_ast.FuncCall(c_ast.ID('klee_make_symbolic'), c_ast.ExprList([c_ast.ID('&kleeVar'), c_ast.FuncCall(c_ast.ID('sizeof'), c_ast.ExprList([c_ast.ID('kleeVar')])), c_ast.Constant('str', '"kleeVar"')]))
                                n.cond = c_ast.ID('kleeVar')
                                items.insert(i, newAssign)
                                items.insert(i+1, newNode)
                                return
                            elif isinstance(res, c_ast.Return):
                                newAssign = c_ast.Assignment('=', c_ast.ID('kleeVar'), res.expr)
                                newNode = c_ast.FuncCall(c_ast.ID('klee_make_symbolic'), c_ast.ExprList([c_ast.ID('&kleeVar'), c_ast.FuncCall(c_ast.ID('sizeof'), c_ast.ExprList([c_ast.ID('kleeVar')])), c_ast.Constant('str', '"kleeVar"')]))
                                n.expr = c_ast.ID('kleeVar')
                                items.insert(i, newAssign)
                                items.insert(i+1, newNode)
                                return
                            elif isinstance(res, c_ast.Decl):
                                newNode = c_ast.FuncCall(c_ast.ID('klee_make_symbolic'), c_ast.ExprList([c_ast.ID('&'+res.name), c_ast.FuncCall(c_ast.ID('sizeof'), c_ast.ExprList([c_ast.ID(res.name)])), c_ast.Constant('str', '"'+res.name+'"')]))
                                items.insert(i+1, newNode)
                                return
                else:
                    return res

def addTestFunction(ast, expectedOutput, testFxn):
    fxnDecl = c_ast.FuncDecl(None, c_ast.TypeDecl('test', [], c_ast.IdentifierType(['void'])))
    fxnCall = c_ast.FuncCall(c_ast.ID(testFxn), c_ast.ExprList([]))
    binaryOp = c_ast.BinaryOp('==', fxnCall, c_ast.Constant('int', expectedOutput))
    ifFalse = c_ast.Compound([c_ast.FuncCall(c_ast.ID('klee_silent_exit'), c_ast.ExprList([c_ast.Constant('int', '0')]))])
    ifTrue = c_ast.Compound([])
    blockItems = [c_ast.If(binaryOp, ifTrue, ifFalse)]
    fxnBody = c_ast.Compound(blockItems)
    fxnNode = c_ast.FuncDef(fxnDecl, None, fxnBody)
    ast.ext.append(fxnNode)

def show_decl_file(cFile, faultyLine, expectedOutput, testFxn):
    ast = parse_file(cFile, use_cpp=True)
    v = NodeVisitor(faultyLine)
    v.visit(ast)
    addTestFunction(ast, expectedOutput, testFxn)
    generator = c_generator.CGenerator()
    print(generator.visit(ast))

if __name__=='__main__':
        if len(sys.argv)>4:
            cFile = sys.argv[1] # tcas.c
            faultyLine = sys.argv[2] # faulty line number
            expectedOutput = sys.argv[3] # expected output
            testFxn = sys.argv[4]
            show_decl_file(cFile, faultyLine, expectedOutput, testFxn)


