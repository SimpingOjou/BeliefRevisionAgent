import sympy as s

from beliefbase import Belief, Entailment, Contract, Revise, Expand, show_beliefs
from utils import DoubleImplication

"""
    Test 1 (Testing entailment)
    Entailment of a formula in a knowledge base refers to the logical consequence relationship between the knowledge base and the formula. Formally, a formula F is said to be entailed by a knowledge base KB if and only if, in every model (or interpretation) where all the sentences in KB are true, F is also true.
"""

print("-------------------")
print("Testing the Logical Entailment")
print("-------------------")

A = s.Symbol("A")
B = s.Symbol("B")
C = s.Symbol("C")

# Test 1: is the formula true in the KB?
print("Test 1:")
print("Knowledge base: A => B, A & C")
print("Formula: A & B & C")
KB1 = s.Implies(A, B)
KB2 = A & C
KB = [KB1, KB2]
formula = A & B & C
print("Result: ", Entailment(KB,formula))
print("-------------------")

# Test 2
print("Test 2:")
print("Knowledge base: A <=> ~C, C | ~B")
print("Formula: ~A")
KB1 = DoubleImplication(A, ~C)
KB2 = C | (~B)
KB = [KB1, KB2]
formula = ~A
print("Result: ", Entailment(KB,formula))
print("-------------------")

# Test 3
print("Test 3:")
print("Knowledge base: A <=> (B | C), ~A")
print("Formula: B & C")
KB1 = DoubleImplication(A, B | C)
KB2 = ~A
KB = [KB1, KB2]
formula = B & C
print("Result: ", Entailment(KB,formula))
print("-------------------")

"""
    Test 2 Contraction
    Contraction is a process in which a knowledge base is updated by removing or revising its contents in response to new information or observations.
"""

print("Testing the Contraction")
print("-------------------")
R = s.Symbol("R") # Robert does well in exam
L = s.Symbol("L") # Is Lucky
P = s.Symbol("P") # Is prepared
B = s.Symbol("B")
Q = s.Symbol("Q")

KB_1 = DoubleImplication(R, P | L)    
KB_2 = ~R # Robert does NOT do well in exam

KB=[Belief(KB_1, 1.0), Belief(KB_2, 1.0), Belief(B, 0.5)]
formula = ~P # What I want to entail from the KB
formula2 = R
formula3 = B

print("Intial belief base:")
show_beliefs(KB)
print("Contracting of B, order 0:")
KB_new = Contract(KB, B, 0)
print("Resulting Knowledge Base: ")
show_beliefs(KB_new)
print("-------------------")

"""
    Test 3: Revision
    Logical revision is a process of updating a knowledge base in response to new information while maintaining consistency. 
    It involves revising the existing beliefs or statements in the knowledge base to incorporate the new information without leading to contradictions.
"""

# print("\n\n")
# print("Result  from test 2: Revision")
# KB_new = revise(KB_new, formula3, 0.25)
# show_beliefs(KB_new)

# print("\n\n")
# print("Result  from test 3: Contract")
# KB_new = contract(KB_new, ~P, 0.0)
# show_beliefs(KB_new)

"""
    Test 4: Expansion
    Logical expansion is the process of adding new information to a knowledge base while ensuring that the resulting expanded knowledge base remains consistent and coherent. Logical expansion focuses on incorporating entirely new information into the knowledge base.
"""