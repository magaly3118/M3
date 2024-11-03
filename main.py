from itertools import product
from copy import deepcopy

grammar = {
    'N': ['E', 'C', 'V'],  # Non-terminal symbols
    'T': ['if', 'else', 'return', '>', 'x', 'y'],  # Terminal symbols
    'R': {  # Production rules
        'E': ['if C: return V else: return V'],
        'C': ['V > V'],
        'V': ['x', 'y']
    },
    'S': 'E'  # Start symbol
}

def DCSolve(G, Φ):
    pts = set()  # Counterexamples set
    while True:
        terms, preds, cover = set(), set(), {}
        DT = None
        print("\n--- Starting a new DCSolve iteration ---")

        # Main loop for generating distinct terms
        while any(cover.get(t, set()) == pts for t in terms):
            term = NextDistinctTerm(pts, terms, cover, G['R']['V'])
            terms.add(term)
            print(f"Added term: {term} | Current terms set: {terms}")
        
        # Loop to create the decision tree until it's defined
        while DT is None:
            term = NextDistinctTerm(pts, terms, cover, G['R']['V'])
            terms.add(term)
            preds.update(enumerate_predicates(G['R']['V'], pts))
            print(f"Added predicate(s): {preds} | Current predicates set: {preds}")
            DT = LearnDT(terms, preds)
        
        # Generate the expression and verify it
        e = expr(DT)
        print(f"Generated expression from DT: {e}")
        cexpt = verify(e, Φ)
        
        if cexpt is None:  # No counterexample, meaning `e` satisfies `Φ`
            print("Solution found:", e)
            return e
        else:
            print(f"Counterexample found: {cexpt}")
            pts.add(cexpt)  # Add the counterexample to `pts` for further refinement

def NextDistinctTerm(pts, terms, cover, GT):
    checked_terms = set()  # Keep track of terms we've already evaluated for uniqueness
    term_gen = enumerate_terms(GT, pts)  # Create a generator for terms
    while True:
        try:
            t = next(term_gen)
            if t in checked_terms:
                continue  # Skip if we've already checked this term

            cover[t] = {pt for pt in pts if satisfies(pt, t)}
            print(f"Coverage for term '{t}': {cover[t]}")  # Debug print for coverage values
            checked_terms.add(t)  # Mark term as checked

            # Ensure `t` has unique coverage
            if all(cover[t] != cover[other_t] for other_t in terms):
                print(f"Next distinct term selected: {t} with coverage {cover[t]}")
                return t

        except StopIteration:
            # If no unique term is found, it means we need a new counterexample to distinguish
            print("Exhausted all terms with current coverage; resetting.")
            term_gen = enumerate_terms(GT, pts)  # Reset term generator
            checked_terms.clear()  # Clear checked terms to retry with new counterexamples

def enumerate_terms(GT, pts):
    # GT: Terms in grammar, which are `x`, `y`, `0`, `1`, and combinations
    variables = GT  # ['x', 'y']
    constants = ['0', '1']
    for var in variables + constants:
        if var not in pts:
            print(f"Enumerating term: {var}")
            yield var
    # Additional terms like `x + y` (simple combinations)
    print("Enumerating term: x + y")
    yield "x + y"
    print("Enumerating term: y + x")
    yield "y + x"

def enumerate_predicates(GP, pts):
    # Only generate valid comparisons between x and y
    conditions = ["x > y", "y > x", "x == y"]
    for cond in conditions:
        if cond not in pts:
            print(f"Enumerating predicate: {cond}")
            yield cond

def LearnDT(terms, preds):
    # Updated to use any available predicates to build a decision tree if possible
    if preds:
        # Use first predicate to create a simple decision tree
        pred = next(iter(preds))  # Grab an arbitrary predicate
        print(f"Learning decision tree with predicate '{pred}'")
        return (pred, 'x', 'y')  # Example tree: if pred then x else y
    print("No suitable decision tree learned.")
    return None

def expr(DT):
    # Convert the decision tree to an if-else expression
    if DT:
        condition, true_case, false_case = DT
        expression = f"if {condition}: result = {true_case}\nelse: result = {false_case}"
        print(f"Expression from DT: {expression}")
        return expression
    return ""

def verify(e, Φ):
    # Specification for maximum function: f(x, y) must return the greater of x and y
    test_cases = [(1, 0), (0, 2), (4, 2), (2, 3)]
    for x, y in test_cases:
        expected = max(x, y)
        locals_dict = {"x": x, "y": y}
        try:
            # Execute the expression as code with the given x, y values
            exec(e, {}, locals_dict)
            result = locals_dict.get("result")
            if result != expected:
                print(f"Verification failed for (x={x}, y={y}), expected {expected} but got {result}")
                return (x, y)  # Counterexample found; return it as a tuple
        except Exception as ex:
            print(f"Error executing expression '{e}' for (x={x}, y={y}): {ex}")
            return (x, y)  # Error in execution; return as counterexample
    print("Expression satisfies all test cases.")
    return None  # Satisfies the specification if no counterexamples are found

def satisfies(pt, term):
    # Unpack the point (input values for x and y)
    x, y = pt
    
    # Define the local scope for evaluating the term
    locals_dict = {'x': x, 'y': y}
    
    try:
        # Evaluate the term as a condition or an expression
        if '>' in term or '<' in term or '==' in term:  # It's a condition
            result = eval(term, {}, locals_dict)
            print(f"Evaluated condition '{term}' for (x={x}, y={y}): {result}")
            return result
        else:  # It's an expression we want to evaluate
            result = eval(term, {}, locals_dict)
            # Specification Check: Ensure result is either x or y and >= both
            is_valid_result = (result == x or result == y) and (result >= x and result >= y)
            print(f"Evaluated expression '{term}' for (x={x}, y={y}): {result} | Valid: {is_valid_result}")
            return is_valid_result
    except Exception as e:
        print(f"Error evaluating term '{term}' with point {pt}: {e}")
        return False

# Running the solver
specification = "maximum_function"
max_expr = DCSolve(grammar, specification)
print("Synthesized Expression:", max_expr)
