'''
Created on Nov 7, 2015

@author: ndlu2
for some reason result is number 1
Note: upward_preffered is defined as an int, but used as a boolean
Note: Positive_RA_Alt_Thresh[Alt_Layer_Value] is in the int list because it is an int return value
'''

from __future__ import print_function
import itertools
import os


def enumerate_bools(bools, max_size):
    value_combinations = itertools.combinations(bools, max_size)
    return enumerate_values(value_combinations, [" && ", " || "], max_size)

def enumerate_arithmetic(ints, max_size):
    value_combinations = itertools.permutations(ints, max_size)
    return enumerate_values(value_combinations, [" + ", " - ", " * ", " / "], max_size)

def enumerate_values(value_combinations, operators, max_size):
    return_val = []
    for combinations in value_combinations:
        for operators in itertools.product(operators, repeat=max_size - 1):
            val = ""
            for i in range(0, max_size - 1):
                val += combinations[i] + operators[i]
            val += combinations[max_size - 1]
            return_val.append(val)

    return return_val

'''

'''
def enumerate_int_comparisons(ints):
    return_val = []
    with_zero = list(ints)
    ''' constants must be hard coded since the minthint example selects defines by hand '''
    constants = ["0", "OLEV", "MAXALTDIFF", "MINSEP", "NOZCROSS"]

    with_zero.extend(constants)
    int_combinations = itertools.combinations(with_zero, 2)
    operators = [" == ", " != ", " > ", " < ", " >= ", " <= "]

    for combinations in int_combinations:
        for operator in operators:
            return_val.append(combinations[0] + operator + combinations[1])

    return return_val

def enumerate_boolean_negates(boolean_statements):
    return_val = []
    for statement in boolean_statements:
        return_val.append("! " + statement)
    return return_val

if __name__ == '__main__':
    f = open('attrmap.75', 'w')
    
    bools = []
    ints = []
    
    types = open('type.75', 'r')
    for line in types:
        thing = line[:-2].split(' ')
        if thing[0] == 'bool':
            bools.append(thing[1])
        elif thing[0] == 'int':
            ints.append(thing[1])
        
    repair_space = []
    
    max_size_bools = 2
    max_size_aritmetic = 2
    
    bools.extend(enumerate_boolean_negates(bools))
    
    for i in range(1, max_size_bools + 1):
        repair_space.extend(enumerate_bools(bools, i))
    
    
    for i in range(1, max_size_aritmetic + 1):
        repair_space.extend(enumerate_arithmetic(ints, i))
    
    repair_space.extend(enumerate_int_comparisons(ints))
    
    line_num = 1
    for statement in repair_space:  
        print(str(line_num) + ": " + statement, file = f)
        line_num += 1
    
    



    
    
