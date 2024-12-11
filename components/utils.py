from typing import Callable
from .decisiontree import DecisionTree
    
def predicate_sort_key(s:str) -> tuple[int, str, str]:
    """Sorts predicates: first by length, then letters, then numbers"""
    letters = [l if l.isalpha() else "z" for l in s]
    numbers = [n if n.isdigit() else "9" for n in s]

    return (len(s), letters, numbers)


def evaluate_predicate(predicate:str, params:list[str], args:tuple):
    """Evaluate the given predicate on the given args"""
    scope = dict(zip(params, args))
    exec(f"ret = {predicate}", scope)
    return scope["ret"]


def decision_tree_to_func(decision_tree:DecisionTree, params:list[int], func_name:str="my_func") -> Callable:
    """Turns the given decision tree into a function"""
    local_scope = {}
    func = f"def {func_name}({params}): \n{decision_tree}"
    exec(func, {}, local_scope)

    return local_scope[func_name]