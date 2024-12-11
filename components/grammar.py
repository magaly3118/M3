from itertools import product
from typing import Generator, Callable, Union
from .utils import predicate_sort_key

class Grammar:
    def __init__(self, terms:list[str], conditions:list[str]):
        """Initialize a grammar with a set terms and conditions."""
        self.terms = terms
        self.conditions = conditions

    def identifiers(self, as_list:bool=False) -> Union[str, list[str]]:
        """Returns a sorted list of identifiers from the grammar's terms"""
        identifiers = [term for term in self.terms if term.isidentifier()]
        identifiers.sort()

        if as_list:
            return identifiers
        
        return ", ".join(identifiers)
    
    def non_recursive_terms(self) -> list[str]:
        """Returns a list of base terms (aka non-recursive)"""
        return [term for term in self.terms if term.isdigit() or term.isidentifier()]
    
    def _make_str_from_parts_and_combination(self, parts:list[str], combination:tuple):
        """Substitutes combination into string, which is passed in parts"""
        string = "".join(p + (c if i < len(combination) else "")
            for i, (p, c) in enumerate(zip(parts, combination + ("",))))
        return string

    def enumerate_predicates(self, terms:set) -> list[str]:
        """Enumerates predicates using the given terms"""
        # get non-recursive predicates
        predicates = set()
        nr_conditions = [condition for condition in self.conditions if "C" not in condition]
        for condition in nr_conditions:
            parts = condition.split("T")
            for combination in product(terms, repeat=len(parts) - 1):
                # skip self comparisons
                if any(combination[i] == combination[i + 1] for i in range(len(combination) - 1)):
                    continue

                pred = self._make_str_from_parts_and_combination(parts, combination)
                predicates.add(pred)

        # get recursive predicates
        recursive_conditions = [condition for condition in self.conditions if "C" in condition]
        for condition in recursive_conditions:
            parts = condition.split("C")
            for combination in product(predicates, repeat=len(parts) - 1):
                # prune predicate
                if len(parts) == 3 and self._prune_predicates(parts, combination):
                    continue

                # substitute the combinations into the rule to form a new predicate
                pred_with_c = self._make_str_from_parts_and_combination(parts, combination)

                # check for terms and handle them
                final_parts = pred_with_c.split("T")
                for term_combination in product(terms, repeat=len(final_parts) - 1):
                    final_pred = self._make_str_from_parts_and_combination(final_parts, term_combination)
                    predicates.add(final_pred)

        predicates = list(predicates)
        sorted_preds = sorted(predicates, key=predicate_sort_key, reverse=True) # order by length then alphabetically, reversed to pop candidates from end of list
        
        return sorted_preds

    def _prune_predicates(self, parts:list[str], combination:tuple):
        """"""
        or_ing = "or" in parts[1] # check if or'ing predicates
        and_ing = "and" in parts[1] # check if and'ing predicates
        same_preds = combination[0] == combination[1] # check for same preds 

        # check for direct opposite preds (i.e. "not x" and "x")
        opposite_preds = any([
        comb_a.replace("not", "", 1) == comb_b 
        for comb_a in [combination[0], combination[1]] 
            for comb_b in [combination[1], combination[0]] 
            if "not" in comb_a
        ])

        # final checks to prune as needed
        same_and = same_preds and and_ing
        opposite_and = opposite_preds and and_ing
        same_or = opposite_preds and or_ing
        opposite_or = opposite_preds and or_ing
        same_operator_and_flipped = self._prune_parts(combination[0], combination[1])
        return any([same_and, opposite_and, same_or, opposite_or, same_operator_and_flipped])

    def _prune_parts(self, part1:str, part2:str):
        """"""
        part1, part2 = part1.split(" "), part2.split(" ")
        
        same_operator = part1[1] == part2[1] 
        flipped = part1[0] == part2[2] and part1[2] == part2[0]

        return same_operator and flipped

    def enumerate_terms(self) -> Generator:
        """Generates terms and returns them as an iterable object"""
        # yield non-recursive terms  
        for term in self.non_recursive_terms():
            yield term

        # yield recursive terms
        seen_terms = set(self.non_recursive_terms())
        recursive_terms = [term for term in self.terms if "T" in term] # like T+T
        while True:
            for term in recursive_terms:
                parts = term.split("T")
                for combination in product(seen_terms, repeat=len(parts) - 1):
                    expr = self._make_str_from_parts_and_combination(parts, combination)
                    seen_terms.add(expr)
                    yield expr
        
    def code_to_func(self, code:str, func_name:str="my_func") -> Callable:
        """Makes the given code into a function"""
        local_scope = {}
        params = self.identifiers()
        code = code.replace("\n", "\n\t")
        func = f"def {func_name}({params}): {code}"

        exec(func, {}, local_scope)
        return local_scope[func_name]

# Example usage
if __name__ == "__main__":
    grammar = Grammar(["T", "\nif C: \n\treturn T \nelse: \n\treturn T"], ["0", "1", "x", "y", "T + T"], ["T <= T", "C and C", "not C"])

    # enumerating terms
    enumerated_terms = grammar.enumerate_terms()
    for _ in range(5):
        term = next(enumerated_terms)
        #print(term)
    
    terms_enumerated = grammar.enumerate_terms()
    i = 0
    for term in terms_enumerated:
        #print(term)
        i += 1
        if i >= 30:
            break

    # enumerating predicates
    preds_enumerated = grammar.enumerate_predicates(set(["0", "x"]))
    for pred in preds_enumerated:
        print(pred)

    # testing code_to_func
    term_as_func = grammar.code_to_func("\nif x >= y: \n\treturn x \nelse: \n\treturn y")
    try:
        from EECS700.EECS700_Project.components.specification import Specification
    except:
        from .specification import Specification
    def spec_condition(output, x, y):
        return output >= x and output >= y and (output == x or output == y)
    spec = Specification(spec_condition)
    for pt in [(0, 1), (-1, 3), (2, 1)]:
        print(f"{pt}, {term_as_func(*pt)}: {spec.holds(term_as_func, pt)}")