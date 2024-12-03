from utils import Grammar, Specification, Callable, DecisionTree

class M3:
    def __init__(self, grammar:Grammar, specification:Specification, name:str="my_func"):
        """Initializes an instance of M3 to synthesize a program based on the given grammar and specification"""
        self.grammar = grammar
        self.specification = specification
        self.name = name
        self.pts = set()


    def synthesize(self) -> Callable:
        """
        Synthesize a function that makes the spepcification true when it is substituted into the specification
        
        Returns:
            Callable: the synthesized function
        """
        while True:
            self.terms = set()
            self.preds = set()
            self.cover = dict()
            self.decision_tree = DecisionTree()

            # Term Solver
            while self._union_cover() != self.pts:
                term = self._next_distinct_term()
                self.terms.add(term)
            
            # Unifier
            while self.decision_tree is None:
                term = self._next_distinct_term()
                self.terms.add(term)

                for pred in self._enumerate_predicates():
                    self.preds.add(pred)

                self.decision_tree = self._learn_decision_tree()

            # Verifier
            synthesized_expr = self._expr_from_dt()
            cexpt = self._verify(synthesized_expr)

            if cexpt is None:
                return synthesized_expr
            
            self.pts.add(cexpt)

    def _enumerate_predicates(self):
        """"""
        

    def _expr_from_dt(self):
        """"""
        

    def _learn_decision_tree(self):
        """"""
        

    def _next_distinct_term(self):
        """"""
        

    def _union_cover(self):
        """"""
        

    def _verify(self, synthesized_expr):
        """"""