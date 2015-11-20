from __future__ import print_function
import sys

from pycparser import c_ast, c_parser, c_generator, parse_file

text= r"""
int global1 = 5;
char global2 = 'g';

int func(void)
{
int inscope1 = 4;
char inscope2 = 2;
return 10;
}

int func2(void)
{
int outofscope1 = 11;
bool outofscope2;
}"""

if __name__=='__main__':
    if len(sys.argv)>1:
        filename = sys.argv[1]
        ast = parse_file(filename, use_cpp=True)
    else:
        parser = c_parser.CParser()
        ast = parser.parse(text)
