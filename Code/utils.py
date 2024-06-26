"""
Various functions used to work with the KB
"""

import sympy as s

def Conjunction(expression:list[s.core.symbol.Symbol])->list[s.core.symbol.Symbol]:
    """
        Conjunction := logical AND (v)
        Input: list of expressions
        Output: expression without a logical AND
    """

    return _Split(expression, s.And)

def Disjunction(expression:list[s.core.symbol.Symbol])->list[s.core.symbol.Symbol]: 
    """
        Disjunction := logical OR (^)
        Input: list of expressions
        Output: expression without a logical OR
    """

    return _Split(expression, s.Or)

def _Split(expression:list[s.core.symbol.Symbol], LogicalOperation:s.core.symbol.Symbol)->list[s.core.symbol.Symbol]:
    """
        Splits the characters from the logical operation
        Input: list of expressions and logical operation
        Output: expression list without logical operator
    """
    def _Collect(exp:list)->None:
        """
            Collects every item in the list that's not a logical operation
            Input: expression list
            Output: expression list without logical operation 
        """
        for term in exp:
            if type(term) == LogicalOperation:
                _Collect(term.args)
            else:
                output.append(term)

    output=[]
    _Collect([expression])

    return output

def DoubleImplication(left_part:list[s.core.symbol.Symbol], right_part:list[s.core.symbol.Symbol])->list[s.core.symbol.Symbol]:
    """
        Implement double implication <=>
        Input: left side and right side of the expression
        Output: combined expression
    """

    return (s.Implies(left_part, right_part) & s.Implies(right_part, left_part))

def Connect(expression:list[s.core.symbol.Symbol], operator:s.core.symbol.Symbol)->list[s.core.symbol.Symbol]:
    """
        Connects expressions with a given operator
        Input: expression and operator
        Output: returns the connected expression
    """

    result = []

    for term in expression:
        if result:
            # avoid duplicates
            result[0] = operator(result[0], term)
        else:
            result.append(term)

    return result

def Remove(my_list:list[s.core.symbol.Symbol], element:s.core.symbol.Symbol)->list[s.core.symbol.Symbol]:
    """
        Removes a given element from the list
        Input: list and element
        Output: returns the list without the element
    """

    return [x for x in my_list if x != element]