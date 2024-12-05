from typing import Union
from .leafnode import LeafNode
from .internalnode import InternalNode
from .predicate import Predicate
    
class DecisionTree:
    def __init__(self, root:Union[LeafNode, InternalNode]):
        root.set_depth()
        self.root = root


    def predict(self, pt:tuple) -> str:
        if self.root is None:
            raise ValueError("Decision tree is empty")
        
        return self.root.predict(pt)
    
    def fprint(self, offset:str=""):
        print(offset, end="")
        self.root.fprint(offset=offset)

    def __repr__(self):
        return self.root.__repr__()

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