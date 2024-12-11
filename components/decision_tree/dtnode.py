class DTNode:
    def __init__(self):
        self.tab = "   "
        self.depth = None

    def get_indent(self) -> str:
        if self.depth is None:
            raise ValueError("Node must be a part of a DecisionTree first")
        
        return (self.depth + 1) * "\t"

    def predict(self, pt:tuple, params:list[str]):
        raise NotImplementedError
    
    def fprint(self, offset:str):
        raise NotImplementedError
    
    def set_depth(self, depth:int):
        raise NotImplementedError
    
    def __repr__(self):
        raise NotImplementedError