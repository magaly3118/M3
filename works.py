class Synthesis:
    def __init__(self, grammar, spec):
        self.grammar = grammar
        self.spec = spec
        self.points = set()
        self.terms = set()
        self.preds = set()
        self.cover = {}

    def bottom_up_enumerate_terms(self):
        print("\nEnumerating terms...")
        new_terms = set()
        for t in self.grammar["terms"]:
            if t not in self.cover:
                self.cover[t] = set()
            for pt in self.points:
                if self.verify_point(t, pt):
                    self.cover[t].add(pt)
            if self.cover[t]:
                new_terms.add(t)
        self.terms.update(new_terms)
        print(f"Terms after enumeration: {self.terms}")

    def bottom_up_enumerate_preds(self):
        print("\nEnumerating predicates...")
        self.preds.update(self.grammar["predicates"])
        print(f"Predicates: {self.preds}")

    def verify_point(self, expr, point):
        x, y, expected = point
        try:
            result = eval(expr, {"x": x, "y": y, "max": max, "min": min})
            return result == expected
        except Exception as e:
            return False

    def decision_tree_learning(self):
        print("\nLearning decision tree...")
        if not self.preds or not self.terms:
            return None
        for pred in self.preds:
            for term1 in self.terms:
                for term2 in self.terms:
                    tree = {"root": pred, "branches": {True: term1, False: term2}}
                    print(f"Trying tree: {tree}")
                    result, cex = self.verify(tree)
                    if result:
                        return tree
        return None

    def evaluate_tree(self, tree, point):
        if isinstance(tree, str):  # Leaf node (a term)
            return eval(tree, {"x": point[0], "y": point[1], "max": max, "min": min})
        pred = eval(tree["root"], {"x": point[0], "y": point[1]})
        branch = tree["branches"][pred]
        return self.evaluate_tree(branch, point)

    def verify(self, tree):
        for pt in self.points:
            x, y, expected = pt
            try:
                result = self.evaluate_tree(tree, pt)
                if result != expected:
                    print(f"Failed for input {pt}: Expected {expected}, got {result}")
                    return False, pt
                print(f"Passed for input {pt}: Expected {expected}, got {result}")
            except Exception as e:
                print(f"Error evaluating {tree} for input {pt}: {e}")
                return False, pt
        return True, None

    def add_counterexample(self, cex):
        self.points.add(cex)
        print(f"\nAdded counterexample: {cex}")

    def synthesize(self, max_iterations=20, timeout=60):
        self.points.update([(x, y, expected) for x, y, expected in self.spec])
        for iteration in range(1, max_iterations + 1):
            print(f"\nIteration {iteration}/{max_iterations}")
            self.bottom_up_enumerate_terms()
            self.bottom_up_enumerate_preds()
            tree = self.decision_tree_learning()
            if not tree:
                raise Exception("Failed to synthesize.")
            result, cex = self.verify(tree)
            if result:
                print("\nFinal Decision Tree:")
                return tree
            self.add_counterexample(cex)
        print("\nSynthesis did not finish within the iteration limits.")
        return None


# Updated grammar and specification
grammar = {
    "terms": ["x", "y", "0", "1", "x + y", "y - x", "x - y", "y + x", "x * y", "y * x", "max(x, y)", "min(x, y)"],
    "predicates": ["x <= y", "y <= x", "x == y", "x != y"]
}

spec = [(1, 0, 1), (0, 2, 2), (4, 2, 4), (2, 3, 3), (2, 2, 2), (3, 1, 3), (1, 1, 1), (0, 0, 0), (4, 4, 4)]  # Example specification

# Initialize and run synthesis
synth = Synthesis(grammar, spec)
solution = synth.synthesize()
if solution:
    print("\nSynthesis completed successfully with tree:", solution)
else:
    print("\nSynthesis failed.")
