from components import Grammar, Specification, DecisionTree
from components.decision_tree import LeafNode, InternalNode, Predicate
from typing import Callable, Union, Generator
import random, sys

class M3:
    def __init__(self, grammar:Grammar, specification:Specification, name:str="my_func", verbose:bool=False):
        """
        This function initializes an instance of M3 to syntesize a program based on the specified grammar and
        specification.
        
        :param grammar: The `grammar` parameter is expected to be an object of the `Grammar` class. It is
        used to define the grammar rules or structure that will be used in the functionality of the class or
        method where this `__init__` method is defined
        :param name: The `name` parameter in the `__init__` method is a string that represents the name of
        the function being initialized. In this case, the default value for the `name` parameter is
        "my_func", defaults to my_func
        :param verbose: The `verbose` parameter is a boolean flag that indicates whether additional
        information or details should be displayed during the execution of the function. If `verbose` is set
        to `True`, the function will print out more information to help with debugging or understanding the
        process. If `verbose` is set to `, defaults to False
        """
        self.grammar = grammar
        self.specification = specification
        self.name = name
        self.verbose = verbose
        self.pts:set[tuple] = set()

    def synthesize(self, max_synth_iter:int=None, max_verify_checks:int=500) -> Callable:
        """
        This function `synthesize` takes in two optional parameters `max_synth_iter` and
        `max_verify_checks`
        Synthesizes a function that makes the spepcification true when it is substituted into the specification
        
        Returns:
            Callable: the synthesized function

        :param max_synth_iter: The `max_synth_iter` parameter specifies the maximum number of synthesis
        iterations that can be performed during the synthesis process. If this parameter is not
        provided, it defaults to `None`, meaning there is no specific limit set on the number of
        synthesis iterations
        :param max_verify_checks: The `max_verify_checks` parameter specifies the maximum number of
        verification checks that can be performed during the synthesis process. This parameter helps
        control the computational resources used during the synthesis operation. By setting a limit on
        the number of verification checks, you can prevent the synthesis process from running indefinitely 
        or consuming excessive resources, defaults to 500
        """
 
        self.i = 0
        # Check if a maximum number iterations is set and if the current iteration count exceeds it. If the
        # maximum is reached, it prints a message indicating the max iterations have been reached and 
        # breaks out of the loop.
        while True:
            self.i += 1
            if max_synth_iter and self.i > max_synth_iter:
                if self.verbose: print(f"!!! Max iterations ({max_synth_iter}) reached, stopping synthesis")
                break
            if self.verbose: print(f"\nIteration {self.i}") 

            # Iteration set up
            self.terms:set[str] = set()
            self.equivalent_terms:dict[str, set[str]] = dict()
            self.preds:list[str] = []
            self.cover:dict[str, tuple] = dict()
            self.decision_tree = None
            self.terms_enumerated = self.grammar.enumerate_terms() # reset to first yield

            # Term Solver - generates terms until all points are covered
            if self.verbose: print("\tTerm Solver:")
            # Checking if the result of the `_cover_union()` method is not equal to `self.pts`. Within the 
            # loop, the code is calling the `_next_distinct_term()` method and adding the result to the 
            # `self.terms` set.
            while self._cover_union() != self.pts:
                term = self._next_distinct_term()
                self.terms.add(term)
            if self.verbose: print(f"\t\tGenerated terms: {self.terms if self.terms else '{}'}")
            
            # Unifier - generates predicates and adds additional terms repeatedly to 
            # try to learn a decision tree such that all points are covered
            if self.verbose: print(f"\tUnifier:")
            while self.decision_tree is None:
                # add term
                term = self._next_distinct_term()
                if term: self.terms.add(term)
                if self.verbose and term: print(f"\t\tAdded term {term}, now generating predicates: ", end="")
                elif self.verbose: print(f"\t\tGenerating predicates: ", end="")
                
                # generate predicates
                self.preds = self.grammar.enumerate_predicates(self.terms)
                preds = "{" + ", ".join(self.preds) + "}"
                if self.verbose: print(f"{preds}")

                # try to learn decision tree
                self.decision_tree = self._learn_decision_tree()
                if self.verbose and self.decision_tree: 
                    print("\t\tDecision tree learning successful:")
                    self.decision_tree.fprint("\t\t\t")
                elif self.verbose: 
                    print("\t\tDecision tree learning failed")

            # Verifier 
            # synthesize expresion from dt and verify
            if self.verbose: print(f"\tVerifying:")
            synthesized_expr = self._decision_tree_to_expr()
            cexpt = self._verify(synthesized_expr, max_verify_checks)

            # if no counter-example found, return callable function
            if cexpt is None:
                tab = "\t\t" if self.verbose else ""
                print(f"{tab}Synthesis successfull: \n{self._expr_to_func_str(synthesized_expr)}")

                return self._expr_to_func_callable(synthesized_expr)
            
            # otherwise, add counter-example to pts
            self.pts.add(cexpt)
            if self.verbose: print(f"\t\tCounter-example found: {cexpt}")
            
    def _cover_union(self) -> set[str]:
        """
        This function returns the set of all points covered by terms in the `self.terms` attribute.
        :return: The function `_cover_union` returns a set of all points covered by terms in the
        `self.terms` attribute.
        """
        return set([pt for cover_i in self.cover.values() for pt in cover_i])
        
    def _decision_tree_to_expr(self) -> str:
        """
        The function `_decision_tree_to_expr` returns the decision tree as a Pythonic expression.
        :return: The method `_decision_tree_to_expr` returns the decision tree as a pythonic expression
        by calling the `__repr__` method on the `decision_tree` object.
        """
        return self.decision_tree.__repr__()
    
    def _expr_to_func_callable(self, expr:str) -> Callable:
        """
        The function `_expr_to_func_callable` is not implemented and raises a `NotImplementedError`.
        
        :param expr: `_expr_to_func_callable` that takes an expression as a string input. The function is not 
        implemented and raises a `NotImplementedError`.
        :type expr: str
        """
        return
        raise NotImplementedError("_expr_to_func_callable()")
    
    def _expr_to_func_str(self, expr:str) -> str:
        """
        The function `_expr_to_func_str` adds a function signature based on grammar to a given expression.
        
        :param expr: The `expr` parameter is a string representing an expression that you want to convert into 
        a function
        :type expr: str
        :return: The function `_expr_to_func_str` returns a string that includes the function signature based 
        on grammar followed by the given expression. The function signature includes the function name and 
        identifiers from the grammar. The returned string is formatted with proper indentation based on the 
        verbose setting.
        """
        offset = "\t\t\t" if self.verbose else "   "
        func_str = f"{offset}def {self.name}({self.grammar.identifiers()}): \n{expr}"

        return func_str.replace("\n", f"\n{offset}")

    def _generate_test_pts(self, args_num:int) -> Generator:
        """
        The function generates random test points infinitely within specified ranges and steps.
        
        :param args_num: The `args_num` parameter in the `_generate_test_pts` method represents the number of 
        arguments to be generated for each test point. This value determines the length of the list `pt` that 
        is generated with random integer values within the specified range :type args_num: int
        """
        range_max = sys.maxsize
        current_range_max = 10
        range_step = 10
        pts_generated = 0
 
        def comlement_min(max:int) -> int:
            """
            The function returns the corresponding minimum integer for a given maximum integer.
            
            :param max: The `max` parameter in the `complement_min` function represents the maximum integer 
            value for which you want to find the corresponding minimum integer value
            :type max: int
            :return: the corresponding minimum integer for a given maximum integer by calculating -max - 1.
            """
            return -max - 1

        while True:
            # generate point
            pt = []
            for _ in range(args_num):
                val = random.randint(comlement_min(current_range_max), current_range_max)
                pt.append(val)

            yield tuple(pt)

            # adjust range and range step
            pts_generated += 1
            if pts_generated % 5 == 0:
                current_range_max = current_range_max + range_step if current_range_max + range_step <= range_max else range_max
                range_step *= 2
    
    def _learn_decision_tree(self) -> Union[DecisionTree, None]:
        """
        The function recursively learns a decision tree based on given data points, terms, cover, and predicates.
        :return: The function `_learn_decision_tree` is returning a learned decision tree based on the current 
        points, terms, cover, and predicates. It first defines a helper function `learn_dt` to recursively 
        learn the decision tree. The function then calls `learn_dt` with the initial parameters and returns the 
        resulting decision tree.
        """
        # recursive helper function to learn dt
        def learn_dt(pts:set, terms:set, cover:dict, preds:list[str]):
            # check if all points are covered by a single term
            for term in terms:
                if pts.issubset(cover.get(term, set())):
                    return LeafNode(term)
                
            # unable to learn a tree if there are no predicates left 
            if not preds:
                return None
            
            pred = Predicate(preds.pop()) # pick a predicate

            # get pts for each branch
            pts_true = {pt for pt in pts if pred.exec(grammar.identifiers(as_list=True), pt)}
            pts_false = {pt for pt in pts if not pred.exec(grammar.identifiers(as_list=True), pt)}

            # build branches
            true_branch = learn_dt(pts_true, terms, cover, preds.copy())
            false_branch = learn_dt(pts_false, terms, cover, preds.copy())

            # return internal node
            return InternalNode(pred, true_branch, false_branch)
        
        # learn dt and return it
        root = learn_dt(self.pts, self.terms, self.cover, self.preds.copy())
        return DecisionTree(root, self.grammar.identifiers(as_list=True))

    def _next_distinct_term(self) -> str:
        """
        The function iterates through candidate terms, checking if they cover a set of points not already 
        covered by existing terms, and saves equivalent terms if their covers are not distinct.
        :return: The `_next_distinct_term` method returns the next term that covers a set of points not covered 
        by a term already in `self.terms`.
        """
        if self.verbose: print(f"\t\tPts={self.pts if self.pts else '{}'}, Cover Pts={[item for item in self.cover.items()] if self.cover else '{}'}")
        
        while True:
            # get next term 
            candidate_term = next(self.terms_enumerated)
            if self.verbose: print(f"\t\tCandidate term={candidate_term}, ", end="")

            # check which points the term covers
            term_as_func = self.grammar.code_to_func(f"\nreturn {candidate_term}", self.name)
            t_cover = {pt for pt in self.pts if self.specification.holds(term_as_func, pt)} if self.pts else set()
            if self.verbose: print(f"term covers: {t_cover if t_cover else '{}'}, ", end="")
            
            # if term doesn't cover any points skip it
            if not t_cover and self.pts:
                if self.verbose: print("term discarded")
                continue

            # if cover isn't distinct, save the term as an equivalent one
            distinct_cover = True
            for existing_t in self.terms:
                if t_cover == self.cover[existing_t]:
                    distinct_cover = False
                    if self.verbose: print(f"cover equivalent to term {existing_t}")

                    if existing_t not in self.equivalent_terms.keys():
                        self.equivalent_terms[existing_t] = set()

                    self.equivalent_terms[existing_t].add(candidate_term)

                    # if terms cover all points stop enumerating, otherwise keep looking
                    if self._cover_union() == self.pts:
                        return 
                    break

            # save and return term if it covers a different set of points from terms already saved
            if distinct_cover or not self.pts:
                self.cover[candidate_term] = t_cover

                if self.verbose:
                    if not self.pts:
                        print("will add (standard)")
                    else:
                        print("will add (forced)")
                        
                return candidate_term

    def _verify(self, synthesized_expr:str, max_checks:int) -> Union[tuple, None]:
        """
        Verifies a given expression is correct based on the specification
        
        Returns:
            None: if the expression is correct
            tuple: otherwise, a counter-example that proves the expression fails on the specification
        """
        args_num = len(self.grammar.identifiers(as_list=True))
        test_pts = self._generate_test_pts(args_num) 
        synthesized_func = grammar.code_to_func("\n"+synthesized_expr)

        for check_i in range(max_checks):
            pt_i = next(test_pts)
            if not self.specification.holds(synthesized_func, pt_i):
                return pt_i
        
        return


# Testing with example from EUSolver paper
if __name__ == "__main__":
    # Max
    print("\nMax Test")
    def spec_condition(output, x, y):
        return output >= x and output >= y and (output == x or output == y)
    spec = Specification(spec_condition)

    terms = ["0", "1", "x", "y", "T + T"]
    conditions = ["T <= T", "C and C", "not C"]
    grammar = Grammar(terms, conditions)

    m3 = M3(grammar, spec, "my_max", verbose=True)
    m3.synthesize(max_synth_iter=50)
    test = input()

    # Min
    print("\nMin Test")
    def spec_condition(output, x, y):
        return output <= x and output <= y and (output == x or output == y)
    spec = Specification(spec_condition)

    terms = ["0", "1", "x", "y", "T + T"]
    conditions = ["T <= T", "C and C", "not C"]
    grammar = Grammar(terms, conditions)

    m3 = M3(grammar, spec, "my_min", verbose=True)
    m3.synthesize(max_synth_iter=50)
    test = input()


    # Abs
    print("\nAbs Test")
    def spec_condition(output, x):
        return (x >= 0 and output == x) or (x < 0 and output == -x)
    spec = Specification(spec_condition)

    terms = ["0", "1", "x", "T + T", "-T"]
    conditions = ["T <= T", "C and C", "not C"]
    grammar = Grammar(terms, conditions)

    m3 = M3(grammar, spec, "my_abs", verbose=True)
    m3.synthesize(max_synth_iter=50, max_verify_checks=100)
