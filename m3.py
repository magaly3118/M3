from utils import Grammar, Specification, DecisionTree
from utils.decision_tree import LeafNode, InternalNode, Predicate
from typing import Callable, Union

class M3:
    def __init__(self, grammar:Grammar, specification:Specification, name:str="my_func", verbose:bool=False):
        """Initializes an instance of M3 to synthesize a program based on the given grammar and specification"""
        self.grammar = grammar
        self.specification = specification
        self.name = name
        self.verbose = verbose
        self.pts:set[tuple] = set()

    def synthesize(self, max_iter:int=None) -> Callable:
        """
        Synthesize a function that makes the spepcification true when it is substituted into the specification
        
        Returns:
            Callable: the synthesized function
        """
        self.i = 0
        while True:
            # Check iterations
            self.i += 1
            if max_iter and self.i > max_iter:
                if self.verbose: print(f"!!! Max iterations ({max_iter}) reached, stopping synthesis")
                break
            if self.verbose: print(f"\nIteration {self.i}") 

            # Round set up
            self.terms:set[str] = set()
            self.equivalent_terms:dict[str, set[str]] = dict()
            self.preds:list[str] = []
            self.cover:dict[str, tuple] = dict()
            self.decision_tree = None
            self.terms_enumerated = self.grammar.enumerate_terms() # reset to first yield

            # Term Solver - generates terms until all points are covered
            if self.verbose: print("\tTerm Solver:")
            while self._union_cover() != self.pts:
                term = self._next_distinct_term()
                self.terms.add(term)
            if self.verbose: print(f"\t\tGenerated terms: {self.terms if self.terms else "{}"}")
            
            # Unifier - generates predicates and adds additional terms repeatedly to 
            # try to learn a decision tree such that all points are covered
            if self.verbose: print(f"\tUnifier:")
            k = 0
            while self.decision_tree is None:
                # add term
                if k>0 or self.i==1:
                    term = self._next_distinct_term()
                    self.terms.add(term)
                    if self.verbose: print(f"\t\tAdded term {term}, now generating predicates: ", end="")
                elif self.verbose: print(f"\t\tGenerating predicates: ", end="")
                k += 1

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
            cexpt = self._verify(synthesized_expr)

            # if no counter-example found, return callable function
            if cexpt is None:
                print(f"{"\t\t" if self.verbose else ""}Synthesis successfull: \n{self._expr_to_func_str(synthesized_expr)}")

                return self._expr_to_func_callable(synthesized_expr)
            
            # otherwise, add counter-example to pts
            self.pts.add(cexpt)
            if self.verbose: print(f"\t\tFail, counter-example found: {cexpt}")
        
    def _decision_tree_to_expr(self) -> str:
        """Returns decision tree as a pythonic expression"""
        return self.decision_tree.__repr__()
    
    def _expr_to_func_callable(self, expr:str) -> Callable:
        """"""
        raise NotImplementedError("_expr_to_func_callable()")
    
    def _expr_to_func_str(self, expr:str) -> str:
        """Adds function signature based on grammar to the given expression"""
        offset = "\t\t\t" if self.verbose else "   "
        func = f"{offset}def {self.name}({self.grammar.identifiers()}): \n{expr}"

        return func.replace("\n", f"\n{offset}")
    
    def _generate_pt(self) -> tuple:
        """Generates a point for verification of a synthesized expression"""
        raise NotImplementedError("_generate_pt()")
    
    def _learn_decision_tree(self) -> Union[DecisionTree, None]:
        """Learn a decision tree based on the current pts, terms, cover and preds"""
        # recursive helper function to learn dt
        def learn_dt(pts:set, terms:set, cover:dict, preds:list[str]):
            # check if all points are covered by a single term
            for term in terms:
                if pts.issubset(cover.get(term, set())):
                    return LeafNode(term)
                
            # if there are no predicates left return None
            if not preds:
                return None
            
            # pick a predicate
            pred = Predicate(preds.pop())

            # get pts for each branch
            pts_true = {pt for pt in pts if pred.exec(grammar.identifiers(as_list=True), pt)}
            pts_false = {pt for pt in pts if not pred.exec(grammar.identifiers(as_list=True), pt)}
            #print(f"\n\t\t\tdt pts={pts}, terms={terms}, cover={cover}, preds={preds}, pts_true={pts_true}, pts_false={pts_false}", end="\n\t\t")

            # build branches
            true_branch = learn_dt(pts_true, terms, cover, preds.copy())
            false_branch = learn_dt(pts_false, terms, cover, preds.copy())

            # return internal node
            return InternalNode(pred, true_branch, false_branch)
        
        # learn dt and return it
        root = learn_dt(self.pts, self.terms, self.cover, self.preds.copy())
        return DecisionTree(root)

    def _next_distinct_term(self) -> str:
        """Returns the next term that covers a set of points not covered by a term already in self.terms"""
        i=0
        if self.verbose: print(f"\t\tPts={self.pts if self.pts else "{}"}, Cover Pts={[item for item in self.cover.items()] if self.cover else "{}"}")
        while True:
            if i>2:
                raise ValueError("stopping while loop")
            # get next term 
            candidate_term = next(self.terms_enumerated)
            if self.verbose: print(f"\t\tCandidate term={candidate_term}, ", end="")

            # check which points the term covers
            term_as_func = self.grammar.code_to_func(f"\nreturn {candidate_term}", self.name)
            t_cover = {pt for pt in self.pts if self.specification.holds(term_as_func, pt)} if self.pts else set()
            if self.verbose: print(f"term covers: {t_cover if t_cover else "{}"}, ", end="")
            
            # if term doesn't cover any points skip it
            if not t_cover and self.pts:
                if self.verbose: print("term discarded")
                i += 1
                continue

            # check if cover is distinct
            distinct_cover = True
            for existing_t in self.terms:
                # if it isn't, save equivalence
                if t_cover == self.cover[existing_t]:
                    distinct_cover = False
                    if self.verbose: print(f"cover equivalent to {existing_t}")

                    if existing_t not in self.equivalent_terms.keys():
                        self.equivalent_terms[existing_t] = set()

                    self.equivalent_terms[existing_t].add(candidate_term)

                    break

            # save and return term if it covers a different set of points from terms already saved
            if distinct_cover or not self.pts:
                self.cover[candidate_term] = t_cover

                if self.verbose:
                    if not self.pts:
                        print("will add (by b)")
                    else:
                        print("will add (by a)")
                        
                return candidate_term
            
    def _union_cover(self) -> set[str]:
        """Returns the set of all pts covered by terms in self.terms"""
        return set([pt for cover_i in self.cover.values() for pt in cover_i])

    def _verify(self, synthesized_expr:str) -> Union[tuple, None]:
        """
        Verifies a given expression is correct based on the specification
        
        Returns:
            None: if the expression is correct
            tuple: otherwise, a counter-example that proves the expression fails on the specification
        """
        ret = [(1, 0), (0, 2), (2, 0), None]
        return ret[self.i - 1]
        # raise NotImplementedError


# Testing with example from EUSolver paper
if __name__ == "__main__":
    def spec_condition(output, x, y):
        return output >= x and output >= y and (output == x or output == y)
    spec = Specification(spec_condition)

    start_rule = ["T", "\nif C: \n\treturn T \nelse: \n\treturn T"]
    terms_rule = ["0", "1", "x", "y", "T + T"]
    conditions_rule = ["T <= T", "C and C", "not C"]
    grammar = Grammar(start_rule, terms_rule, conditions_rule)

    m3 = M3(grammar, spec, "my_max", verbose=True)

    try:
        m3.synthesize(max_iter=5)
    except NotImplementedError as e:
        print(f"\nNOTE: finish implementing {e.args[0]}")