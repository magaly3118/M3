from typing import Union
from .dtnode import DTNode
from .leafnode import LeafNode

class InternalNode(DTNode):
    def __init__(self, predicate:str, true_branch:Union["InternalNode", LeafNode], false_branch:Union["InternalNode", "LeafNode"]):
        super().__init__()
        self.pred = predicate
        self.true_branch = true_branch
        self.false_branch = false_branch

    def predict(self, pt:tuple, params:list[str]) -> str:
        if self.evaluate_predicate(params, pt):
            return self.left.predict(pt, params)
        else:
            return self.right.predict(pt, params)
    
    def fprint(self, offset:str=""):
        print(f"{self.pred.str} \n{offset}{self.tab*(self.depth + 1)}T: ", end="")
        self.true_branch.fprint(offset)
        print(f"{offset}{self.tab*(self.depth + 1)}F: ", end="")
        self.false_branch.fprint(offset)

    def set_depth(self, depth:int=0):
        self.depth = depth
        [branch.set_depth(depth + 1) for branch in [self.true_branch, self.false_branch]]

    def __repr__(self):
        indent = self.get_indent()
        return f"{indent}if {self.pred.str}: \n{self.true_branch} \n{indent}else: \n{self.false_branch}"
    
    def evaluate_predicate(self, params:list[str], pt:tuple):
        """"""
        from ..utils import evaluate_predicate
        return evaluate_predicate(self.pred, params, pt)