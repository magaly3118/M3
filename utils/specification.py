from typing import Callable

class Specification:
    def __init__(self, condition:Callable):
        """
        Initiates an object of type specification with the given condition

        Parameters:
            condition (Callable): The condition used to check if a synthesized function satisfies the specification. It has syntax spec(output, *inputs) where output refers to the output of the synthesized function when it's passed the given inputs
        """
        self.condition = condition

    def holds(self, synthesized_func:Callable, inputs:tuple):
        """
        Checks if the given function satisfies the specification on the given inputs

        Parameters:
            func (Callable): A synthesized funtion
            inputs (tuple): The inputs to check the function with

        Returns:
            bool: True if the spefication's condition is met, False otherwise
        """
        try:
            output = synthesized_func(*inputs)
            return self.condition(output, *inputs)
        
        except Exception as e:
            print(f"Error evaluating program: {e}")
            return False

# Example usage
if __name__ == "__main__":
    def spec_condition(output, x, y):
        return output <= y and output < x

    def synthesized_func(x, y):
        if x < 0:
            return x - 1 
        else:
            return y

    spec = Specification(spec_condition)
    for test_input in [(0, 1), (-1, 3)]:
        print(spec.holds(synthesized_func, test_input))