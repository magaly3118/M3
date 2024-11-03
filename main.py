from itertools import permutations, product
from copy import deepcopy

grammar = {
    'N': ['E', 'C', 'V'],  # Non-terminal symbols
    'T': ['if', 'else', 'return', '>', 'x', 'y'],  # Terminal symbols
    'R': {  # Production rules
        'E': ['if C: return V else: return V'],
        'C': ['V > V'],
        'V': ['x', 'y']
    },
    'S': 'E'  # Start symbol
}
