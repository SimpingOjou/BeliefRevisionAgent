"""
Knowledge base class and functions
"""
import sympy as s
from decimal import Decimal
from utils import Conjunction, Disjunction, DoubleImplication, Connect, Remove

# Belief class
class Belief:
    """
        Belief class. Initialized by assigning a formula and an order.
        It will be inserted in a Knowledge Base
    """
    def __init__(self, formula = None, order = None)->None:
        self.formula = formula # logical expression
        self.order = Decimal(order) # plausibility order

def Resolve(clause_1:list, clause_2:list)->list:
    """
        Every clause has a disjunction (|) between its literals (Symbol).
        The function resolves given two clauses
    """

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

def Entailment(KB, prove):
    """
        Entailment := contradictions in the knowledge base
        Checks and deals for entailment with the Resolution Method. In this method, we negate the formula we want to check for entailment and then perform resolution with the negation of the formula and the knowledge base. If we arrive at an empty clause (i.e., a contradiction), then the formula is entailed by the knowledge base.
    """

    clauses = []

    #Step 1: Take the elements of the KB in CNF 
    for i in KB:
        knowledge_cnf = s.to_cnf(i)
        knowledge_literals = Conjunction(knowledge_cnf)
        
        for x in range(len(knowledge_literals)):
            clauses.append(knowledge_literals[x])

    #Step 2: Add to the clauses the contradiction(opposite) of the formula
    Not_Formula_CNF = Conjunction(s.to_cnf(~prove))

    for i in range(len(Not_Formula_CNF)):
        clauses.append(Not_Formula_CNF[i])

    #Step 3:Resolve the clauses
    for i in range(len(clauses)):
        for j in range(i + 1,len(clauses)):
            new_clause = Resolve(clauses[i],clauses[j])  
            
            for x in new_clause:
                if x not in clauses:
                    clauses.append(x)

    if 0 in clauses:
        return True
    else:
        return False
    
def show_beliefs(KB):
    """
        Prints the belief and the order of each belief in the KB
    """

    for belief in KB:
        print("Formula: ", belief.formula, "Order: ", belief.order)

def assert_belief(KB, formula, order):
    """

    """

    formula_in_cnf = s.to_cnf(formula)
    print("--------------------")
    print(formula_in_cnf)
    print(formula)
    print(order)
    if not(0 <= order <= 1):
        raise ValueError("Order must be a value between 0 and 1.")
    
    return KB_r + ([Belief(formula_in_cnf, order)] if order > 0 else []) \
           if (KB_r := retract_belief(KB, formula_in_cnf)) else KB_r

def retract_belief(KB, formula):
    belief_queue = []
    KB_new = KB.copy()
    for belief in KB_new:
        if belief.formula == formula:
            belief_queue.append((formula, Decimal(0)))
    
    KB_new = reorder_belief_queue(KB, belief_queue)
    return KB_new

def iterate_by_entrenchment(KB):
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

def entrenchment_degree(KB, formula):
    formula_cnf = s.to_cnf(formula)

    if Entailment([], formula_cnf):
        # Tautologies have order of entrenchment = 1
        return Decimal(1)

    base = []
    for order, group in iterate_by_entrenchment(KB):
        # Get formulas from beliefs
        base += [belief.formula for belief in group]

        if Entailment(base, formula_cnf):
            return order
    return Decimal(0)

def reorder_belief_queue(KB, belief_queue):
    KB_new = KB.copy()
    for formula, order in belief_queue:
        KB_new.remove(formula)
        if order > 0.0:
            formula.order = order
            KB_new.append(formula)
    return KB_new

def Expand(KB, formula, order, add_on_finish:bool = True):
    cnf_formula = s.to_cnf(formula)
    belief_queue = []
    order_of_entrenchment = Decimal(order)
    
    if not Entailment([], ~(s.to_cnf(formula))):
        if Entailment([], ~(s.to_cnf(formula))):
            order = Decimal(1)
        else:
            for belief in KB:
                kb_formula = belief.formula

                if belief.order > order: 
                    continue  

                d = entrenchment_degree(KB, s.Implies(cnf_formula, kb_formula))

                if Entailment([], DoubleImplication(cnf_formula, kb_formula)) or belief.order <= order < d:
                    belief_queue.append((belief, Decimal(order)))

            KB_new = reorder_belief_queue(KB, belief_queue)

        if add_on_finish:
            KB_new = assert_belief(KB_new, cnf_formula, order_of_entrenchment)

    return KB_new

def Contract(KB, formula, order):
    x = s.to_cnf(formula)
    belief_queue = []
    order = Decimal(order)

    if not 0 <= order <= 1:
        raise ValueError
    
    for kb_formula in KB:
        y = kb_formula.formula
        
        if order < kb_formula.order and entrenchment_degree(KB, x) == entrenchment_degree(KB, Connect([x, y], s.Or)[0]):
            belief_queue.append((kb_formula, order))
    
    return reorder_belief_queue(KB, belief_queue)

def Revise(KB, formula, order):
    cnf_formula = s.to_cnf(formula)
    order_of_entrenchment = Decimal(order)
    degree_of_formula = entrenchment_degree(KB, cnf_formula)
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
            KB_new = Expand(KB_contr, cnf_formula, order_of_entrenchment, add_on_finish=False)
            
    return KB_new