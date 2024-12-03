class Grammar:
    def __init__(self, start_rule:list[str], terms_rule:list[str], conditions_rule:list[str]):
        """
        Initialize the grammar with a set of production rules.

        Arguments:
            start_rule (list[str]): production rules for start symbol
            terms_rule (list[str]): production rules for terms 
            conditions_rule (list[str]): production rules for conditions
        """
        self.start_rule = start_rule
        self.terms_rule = terms_rule
        self.conditions_rule = conditions_rule

    def rules(self):
        """Reutrns a dictionary with all rules, where the key is the symbol and the value is a list of production rules"""
        rules = {
            "S": self.start_rule,
            "T": self.terms_rule,
            "C": self.conditions_rule
        }

        return rules