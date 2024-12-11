class Predicate:
    def __init__(self, expr:str):
        self.str = expr

    def exec(self, params:list[str], args:int):
        """"""
        #print(f"\t\tpred: {self.str}, params: {params}, args: {args}")
        scope = dict(zip(params, args))
        exec(f"ret = {self.str}", scope)
        return scope["ret"]
    

def predicate_sort_key(s:str) -> tuple[int, str, str]:
    """"""
    letters = [l if l.isalpha() else "z" for l in s]
    numbers = [n if n.isdigit() else "9" for n in s]

    return (len(s), letters, numbers)