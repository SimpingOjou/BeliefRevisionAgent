"""
    Knowledge base class and functions
""" 

import sympy as s
from decimal import Decimal
from utils import Conjunction, Disjunction, DoubleImplication, Connect, Remove

class Belief:
    """
        Belief class. Initialized by assigning a formula and an order.
        It will be inserted in a Knowledge Base
    """
    def __init__(self, formula:s.core.symbol.Symbol = None, order:float = None)->None:
        self.formula = formula # logical expression
        self.order = Decimal(order) # firmness of belief

"""
    Public functions that can be used outside of beliefbase
"""

def Resolve(clause_1:list[s.core.symbol.Symbol], clause_2:list[s.core.symbol.Symbol])->list[s.core.symbol.Symbol]:
    """
        Every clause has a disjunction (|) between its literals (Symbol).
        The function resolves given two clauses
    """
#
    new_clause = []
    literals_1 = Disjunction(clause_1) 
    literals_2 = Disjunction(clause_2)

    for term_1 in literals_1:
        for term_2 in literals_2:
            if term_1 == ~term_2 or ~term_1 == term_2:
                a = Remove(literals_1, term_1)
                b = Remove(literals_2, term_2)

                total = a + b # returns a list with the left literals together

                if total:
                    new_clause_to_add = Connect(total, s.Or) # The elements inside a clause are connected with Or 
                else:
                    new_clause_to_add = [0]

                new_clause += new_clause_to_add

    return new_clause

def Entailment(KB:list[s.core.symbol.Symbol], prove:s.core.symbol.Symbol)->bool:
    """
        Entailment := contradictions in the knowledge base
        Checks and deals for entailment with the Resolution Method. In this method, we negate the formula we want to check for entailment and then perform resolution with the negation of the formula and the knowledge base. If we arrive at an empty clause (i.e., a contradiction), then the formula is entailed by the knowledge base.
    """

    clauses = []

    # Transform into CNF
    for term in KB:
        knowledge_cnf = s.to_cnf(term)
        knowledge_literals = Conjunction(knowledge_cnf)
        
        for x in range(len(knowledge_literals)):
            clauses.append(knowledge_literals[x])

    # Formula negation
    Not_Formula_CNF = Conjunction(s.to_cnf(~prove))

    for i in range(len(Not_Formula_CNF)):
        clauses.append(Not_Formula_CNF[i])

    # Clause resolution
    for i in range(len(clauses)):
        for j in range(i + 1,len(clauses)):
            new_clause = Resolve(clauses[i],clauses[j])  
            
            for x in new_clause:
                if x not in clauses:
                    clauses.append(x)

    # Check for entailment on the clauses
    if 0 in clauses:
        return True
    
    return False
    
def Show_beliefs(KB:list[s.core.symbol.Symbol])->None:
    """
        Prints the belief and the order of each belief in the KB
    """

    for i,belief in enumerate(KB):
        print("Formula ["+ str(i+1) +"]: ", belief.formula, "Order: ", belief.order)

def Expand(KB:list[s.core.symbol.Symbol], formula:s.core.symbol.Symbol, order:float, add_on_finish:bool = True)->list[s.core.symbol.Symbol]:
    """
        Logical expansion is the process of adding new information to a knowledge base. Logical expansion focuses on incorporating entirely new information into the knowledge base.
    """
    cnf_formula = s.to_cnf(formula)
    order_of_entrenchment = Decimal(order)
    belief_queue = []
    
    if not Entailment([], ~(s.to_cnf(formula))):
        if Entailment([], ~(s.to_cnf(formula))):
            order = Decimal(1)
        else:
            for belief in KB:
                kb_formula = belief.formula

                if belief.order > order: 
                    continue  

                d = _entrenchment_degree(KB, s.Implies(cnf_formula, kb_formula))

                if Entailment([], DoubleImplication(cnf_formula, kb_formula)) or belief.order <= order < d:
                    belief_queue.append((belief, Decimal(order)))

            KB_new = _reorder_belief_queue(KB, belief_queue)

        if add_on_finish:
            KB_new = _assert_belief(KB_new, cnf_formula, order_of_entrenchment)

    return KB_new

def Contract(KB:list[s.core.symbol.Symbol], formula:s.core.symbol.Symbol, order:float)->list[s.core.symbol.Symbol]:
    """
        Contraction is a process in which a knowledge base is updated by removing or revising its contents in response to new information or observations.
        When new information contradicts existing beliefs in the knowledge base, contraction involves adjusting the knowledge base to accommodate the new information while preserving consistency and minimizing the loss of existing information.
    """

    x = s.to_cnf(formula)
    belief_queue = []
    order = Decimal(order)

    if not 0 <= order <= 1:
        raise ValueError

    for kb_formula in KB:
        y = kb_formula.formula

        if (order < kb_formula.order) and (_entrenchment_degree(KB, x) == _entrenchment_degree(KB, Connect([x, y], s.Or)[0])):
            belief_queue.append((kb_formula, order))

    return _reorder_belief_queue(KB, belief_queue)

def Revise(KB:list[s.core.symbol.Symbol], formula:s.core.symbol.Symbol, order:float)->list[s.core.symbol.Symbol]:
    """
        Logical revision is a process of updating a knowledge base in response to new information while maintaining consistency. 
        It involves revising the existing beliefs or statements in the knowledge base to incorporate the new information without leading to contradictions.
    """

    cnf_formula = s.to_cnf(formula)
    order_of_entrenchment = Decimal(order)
    degree_of_formula = _entrenchment_degree(KB, cnf_formula)
    KB_new = KB.copy()
    
    if not Entailment([], ~cnf_formula):
        # If an empty set of clauses entails ~cnf_formula is true, 
        # it is a contradiction since ~cnf_formula is always true

        if Entailment([], cnf_formula):
            # if cnf_formula is true for an empty set of clauses, then it is a tautology
            # i.e. cnf_formula is always true
            order = Decimal(1)
        elif order_of_entrenchment <= degree_of_formula:
            Contract(KB, cnf_formula, order)
        else:
            # Levi identity
            KB_contr = Contract(KB, ~cnf_formula, Decimal(0))
            KB_new = Expand(KB_contr, cnf_formula, order_of_entrenchment, add_on_finish=True)
            
    return KB_new

"""
    Private functions used inside beliefbase
"""

def _assert_belief(KB:list[s.core.symbol.Symbol], formula:s.core.symbol.Symbol, order:float):
    """
        Asserting a particular statement as being true or accepted within the context of the knowledge base.
    """

    formula_in_cnf = s.to_cnf(formula)

    if not(0 <= order <= 1):
        raise ValueError("Order must be a value between 0 and 1.")
    
    return KB_r + ([Belief(formula_in_cnf, order)] if order > 0 else []) \
           if (KB_r := _retract_belief(KB, formula_in_cnf)) else KB_r

def _retract_belief(KB:list[s.core.symbol.Symbol], formula:s.core.symbol.Symbol)->list[s.core.symbol.Symbol]:
    """
        Ensures KB consistency.
    """

    belief_queue = []
    KB_new = KB.copy()

    for belief in KB_new:
        if belief.formula == formula:
            belief_queue.append((formula, Decimal(0)))
    
    KB_new = _reorder_belief_queue(KB, belief_queue)

    return KB_new

def _iterate_by_entrenchment(KB:list[s.core.symbol.Symbol]):
    """
        Groups beliefs in the knowledge base by their order, and for each group of beliefs with the same order, it yields the order along with the corresponding list of beliefs
    """

    result = []
    last_order = None

    for belief in KB:
        if last_order is None:
            result.append(belief)
            last_order = belief.order
            continue

        if belief.order == last_order:
            result.append(belief)
        else:
            yield last_order, result
            result = []
            result.append(belief)
            last_order = belief.order

    # Yield last result
    yield last_order, result

def _entrenchment_degree(KB:list[s.core.symbol.Symbol], formula:s.core.symbol.Symbol)->Decimal:
    """
        Logical entrenchment refers to the degree of resistance to change that certain beliefs or propositions have within a knowledge base or logical framework. It is a measure of how firmly entrenched or deeply rooted certain beliefs are compared to others.
        It helps determine which beliefs are more resistant to revision or contraction when new information is introduced.
    """
    formula_cnf = s.to_cnf(formula)

    if Entailment([], formula_cnf):
        # Tautologies have order of entrenchment = 1
        return Decimal(1)

    base = []
    for order, group in _iterate_by_entrenchment(KB):
        # Get formulas from beliefs
        base += [belief.formula for belief in group]

        if Entailment(base, formula_cnf):
            return order
    return Decimal(0)

def _reorder_belief_queue(KB:list[s.core.symbol.Symbol], belief_queue:list[s.core.symbol.Symbol])->list[s.core.symbol.Symbol]:
    KB_new = KB.copy()

    for formula, order in belief_queue:
        KB_new.remove(formula)
        if order > 0.0:
            formula.order = order
            KB_new.append(formula)

    return KB_new