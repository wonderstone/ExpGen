#  Reverse Polish Notation (RPN) class
#  Used to compile the RPN expressions into a Python function
#  RPN is a mathematical notation in which every operator follows 
#  all of its operands, for example, 3 + 4 is written as 3 4 +.

from typing import List, Union, Callable
import math

from common import Expression

class InvalidExpressionError(Exception):
    pass

class RPNBase(Expression):
    def __init__(self, 
                 expression: List[Union[str, float, int]], 
                 default_ops: dict[str, tuple[Callable, int]],
                 custom_ops=None):
        """
        Initializes the RPNExpression with a list of tokens and optional custom operators.
        :param expression: List of tokens (e.g., [2, 3, '+', 5, '*'] for (2 + 3) * 5, or ['x', 2, '+'] for variables).
        :param custom_ops: Dictionary of custom operators/functions {symbol: (function, arity)}.
        """
        self.expression = expression
        self.ops = default_ops.copy()  # Start with default ops
        if custom_ops:
            self.ops.update(custom_ops)  # Add/override with custom operators


    def validate_expression(self):
        """
        Validates the RPN expression by Formal Legality.

        """
        stack = []
        for token in self.expression:
            if isinstance(token, (int, float)) or token.isdigit() or isinstance(token, str):  # Support variables
                stack.append(token)
            elif token in self.ops:
                _, arity = self.ops[token]  # Get the arity of the operator
                if len(stack) < arity:
                    # raise InvalidExpressionError(f"Invalid RPN expression: insufficient values for operator '{token}'")
                    # print(f"Invalid RPN expression: insufficient values for operator '{token}'")
                    return False
                for _ in range(arity):
                    stack.pop()
                stack.append(0)  # Push dummy value to simulate the result of the operation
            else:
                # raise InvalidExpressionError(f"Unsupported token: {token}")
                # print(f"Unsupported token: {token}")
                return False
        # Check the stack size: must be 1 
        if len(stack) == 1 :
            return True
        else:
            # raise InvalidExpressionError("Invalid RPN expression: insufficient values.")
            # print("Invalid RPN expression: insufficient values.")
            return False
        

    def to_function(self) -> Callable:
        """
        Converts the RPN expression to a callable function.
        :return: A function that takes arguments (as a dict for variables) and evaluates the expression.
        """
        def evaluate(variables: dict = None):
            """
            Evaluates the RPN expression using the given variable values.
            :param variables: A dictionary of variable names and their values, e.g., {'x': 2, 'y': 3}.
            :return: The evaluated result.
            """
            stack = []
            variables = variables or {}

            for token in self.expression:
                if isinstance(token, (int, float)):  # Direct number
                    stack.append(token)
                elif token.isdigit():  # If it's a string digit, convert to int
                    stack.append(float(token))
                elif isinstance(token, str) and token in variables:  # If it's a variable
                    stack.append(variables[token])
                elif token in self.ops:  # Operator
                    func, arity = self.ops[token]
                    # Pop the necessary number of arguments based on the arity of the operator
                    args_to_pass = [stack.pop() for _ in range(arity)][::-1]
                    result = func(*args_to_pass)
                    stack.append(result)
                else:
                    raise InvalidExpressionError(f"Unsupported token or undefined variable: {token}")
            return stack[0]

        return evaluate

    def to_string(self) -> str:
        """
        Converts the RPN expression to a readable string.
        :return: A string representing the expression in which every operator has its operands enclosed in parentheses.
        """
        stack = []
        for token in self.expression:
            if isinstance(token, (int, float)):
                # If it's a number, convert to string and push to stack
                stack.append(str(token))
            elif token.isdigit():
                # If it's a string digit, push to stack
                stack.append(token)
            elif token in self.ops:
                # If it's an operator, get its arity
                _, arity = self.ops[token]
                expression = f"{token}({', '.join([stack.pop() for _ in range(arity)][::-1])})"
                stack.append(expression)
                # ~ the following code is for "+, -, *, /" myth(迷思) only
                # if arity == 1:
                #     a = stack.pop()
                #     expression = f"{token}({a})"
                #     stack.append(expression)
                # elif arity == 2 and token in ['+', '-', '*', '/']:
                #     # only binary operator and in +, -, *, / set would be considered
                #     b = stack.pop()
                #     a = stack.pop()
                #     expression = f"({a} {token} {b})"
                #     stack.append(expression)
                # else:
                #     # output = f"{token}({', '.join([stack.pop() for _ in range(arity)][::-1])})"
                #     expression = f"{token}({', '.join([stack.pop() for _ in range(arity)][::-1])})"
                #     stack.append(expression)
            elif isinstance(token, str):
                # If it's a variable, push to stack
                stack.append(token)
            else:
                raise InvalidExpressionError(f"Unsupported token: {token}")
        return stack[0]
    
    def __str__(self):
        return self.to_string()
    
    def evaluate(self, variables: dict = None) -> float:
        """
        Evaluates the RPN expression with the provided variable values.
        :param variables: A dictionary of variable names and their values.
        :return: The result of the evaluation.
        """
        func = self.to_function()
        return func(variables)


if __name__ == "__main__":
    # Define normal functions
    def add(a, b):
        return a + b

    def subtract(a, b):
        return a - b

    def multiply(a, b):
        return a * b

    def divide(a, b):
        return a / b if b != 0 else float('inf')  # Handle division by zero

    def power(a, b):
        return a ** b

    def negate(a):
        return -a

    def ternary_op(a, b, c):
        return a if a > b else c

    # Define default supported operators with regular functions and their arity

    DEFAULT_OPS = {
        # '+': (lambda a, b: a + b, 2),
        # '-': (lambda a, b: a - b, 2),
        'Add': (add, 2),        # (function, arity)
        'Sub': (subtract, 2),
        'Mul': (multiply, 2),
        'Div': (divide, 2),
        'Pow': (lambda a, b: a ** b,2),  # Power operator
        # 'pow': power,  # or use math.pow
        'Sin': (math.sin, 1),  # Sine function
        'Cos': (math.cos, 1),  # Cosine function
        'Log': (math.log, 1),  # Logarithm function
        'Neg': (negate, 1),   # Unary negation
        '?': (ternary_op, 3)  # Ternary operator example
    }

    # Example usage:

    # + Define an RPN expression with variables -, x, +, 2 -> RPN: ['x', 'Neg', 2, 'Add']
    # - Exp: Add(Neg(x), 2)
    rpn_expr = RPNBase(['x', 'Neg', 2, 'Add'], DEFAULT_OPS )
    infix_str = rpn_expr.to_string()
    print(f"Expression: {infix_str}")  # Output: Add(Neg(x), 2)
    # = Evaluate the expression with x = 3
    result = rpn_expr.evaluate({'x': 3})
    print(f"Evaluation result with x=3: {result}")  # Output: -1.0

    # + Define an RPN expression with ternary operator: if x > y then x else z -> RPN: ['x', 'y', 'z', '?']
    # - Exp: ?(x, y, z)
    rpn_ternary_expr = RPNBase(['x', 'y', 'z', '?'], DEFAULT_OPS)
    infix_ternary_str = rpn_ternary_expr.to_string()
    print(f"Ternary expression: {infix_ternary_str}")  # Output: ?(x, y, z)
    # = Evaluate the ternary expression with x = 5, y = 3, z = 10
    ternary_result = rpn_ternary_expr.evaluate({'x': 5, 'y': 3, 'z': 10})
    print(f"Evaluation result of ternary with x=5, y=3, z=10: {ternary_result}")  # Output: 5.0

    # + Define an RPN expression with variables: (-x + 2)** 3 -> RPN: ['x', 'Neg', 2, 'Add', 3, 'Pow']
    # - Exp: Pow(Add(Neg(x), 2), 3)
    rpn_power_expr = RPNBase(['x', 'Neg', 2, 'Add', 3, 'Pow'], DEFAULT_OPS)
    infix_power_str = rpn_power_expr.to_string()
    print(f"Power expression: {infix_power_str}")  # Output: pow((neg(x) + 2),3)
    # = Evaluate the expression with x = 4
    result = rpn_power_expr.evaluate({'x': 4})
    print(f"Evaluation result with x=4: {result}")  # Output: -8.0


    # + Define an RPN expression with variables: 2, 3, *, 4, +, 6 -> RPN: [2, 3, 'Add', 4, 6, 'Mul', 'Add']
    # - Exp: Add(Add(2, 3), Mul(4, 6))
    tmp_expr = RPNBase([2, 3, 'Add', 4, 6, 'Mul', 'Add'], DEFAULT_OPS)
    tmp_result = tmp_expr.evaluate()
    print(f"{tmp_expr.to_string()}: {tmp_result}")

