from typing import Union, Callable
from .decision_tree.leafnode import LeafNode
from .decision_tree.internalnode import InternalNode
from .decision_tree.predicate import Predicate
    
class DecisionTree:
    def __init__(self, root:Union[LeafNode, InternalNode], params:list[int]):
        """"""
        root.set_depth()
        self.root = root
        self.params = params

    def predict(self, pt:tuple) -> str:
        """"""
        if self.root is None:
            raise ValueError("Decision tree is empty")
        
        return self.root.predict(pt, self.params)
    
    def fprint(self, offset:str=""):
        """Resembles the tree structure"""
        print(offset, end="")
        self.root.fprint(offset=offset)

    def __repr__(self):
        """Prints code representation"""
        return self.root.__repr__()

    def decision_tree_to_func(self, func_name:str="my_func") -> Callable:
        """Returns a function representative of the decision tree"""
        local_scope = {}
        func = f"def {func_name}({self.params}): \n{self.__repr__}"
        exec(func, {}, local_scope)

        return local_scope[func_name]
    
    def specification_holds(self, spec_condition:Callable, pt:tuple):
        """Checks if the given specification holds for the given pt and the decision tree"""
        try:
            output = self.predict(pt)
            return spec_condition(output, *pt)
        
        except Exception as e:
            print(f"Error evaluating program: {e}")
            return False

# testing
if __name__ == "__main__":
    node0 = LeafNode(0)
    node1 = LeafNode(1)
    node2 = LeafNode(2)
    node_p1 = InternalNode(Predicate("x < y"), node0, node1)
    node_p2 = InternalNode(Predicate("x < y + 1"), node2, node_p1)
    tree = DecisionTree(node_p2)
    tree.fprint()
    print()
    print(tree)

    def example_spec(output, x, y):
        return output <= y and output < x