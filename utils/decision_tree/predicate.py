class Predicate:
    def __init__(self, expr:str):
        self.str = expr

    def exec(self, params:list[str], args:int):
        """"""
        #print(f"\t\tpred: {self.str}, params: {params}, args: {args}")
        scope = dict(zip(params, args))
        exec(f"ret = {self.str}", scope)
        return scope["ret"]