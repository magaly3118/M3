from .dtnode import DTNode

class LeafNode(DTNode):
    def __init__(self, value:str):
        super().__init__()
        self.value = value

    def predict(self, pt:tuple) -> str:
        return self.value
    
    def fprint(self, offset:str=""):
        print(f"{self.value}")

    def set_depth(self, depth:int=0):
        self.depth = depth

    def __repr__(self):
        return f"{self.get_indent()}return {self.value}"