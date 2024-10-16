import math
from typing import List, Union, Callable



def negate(a):
    return -a
def ternary_op(a, b, c):
    return a if a > b else c
# Define default operators for Karva expression, with their arity
DEFAULT_OPS = {
    '+': (lambda a, b: a + b, 2),
    '-': (lambda a, b: a - b, 2),
    '*': (lambda a, b: a * b, 2),
    '/': (lambda a, b: a / b if b != 0 else float('inf'), 2),  # Division with zero handling
    'sin': (lambda a: math.sin(a), 1),
    'cos': (lambda a: math.cos(a), 1),
    'log': (lambda a: math.log(a), 1),
    'neg': (negate, 1),   # Unary negation
    '?': (ternary_op, 3)  # Ternary operator example
}


class TreeNode:
    """
    Represents a node in the expression tree.
    Each node stores a value (which could be an operator or a terminal) and references to child nodes.
    """
    def __init__(self, value):
        self.value = value
        self.children = []

    def add_child(self, child_node):
        self.children.append(child_node)

class InvalidKarvaExpressionError(Exception):
    pass

class KarvaExpression:
    def __init__(self, expression: List[Union[str, float, int]], head_length: int, custom_ops=None):
        """
        Initializes the KarvaExpression with a list of tokens and optional custom operators.
        :param expression: List of tokens representing the Karva expression.
        :param head_length: Length of the head of the Karva expression.
        :param custom_ops: Dictionary of custom operators/functions {symbol: (function, arity)}.
        """
        self.expression = expression
        self.head_length = head_length
        self.ops = DEFAULT_OPS.copy()  # Start with default ops
        if custom_ops:
            self.ops.update(custom_ops)  # Add/override with custom operators
        self.validate_expression()

    def validate_expression(self):
        """
        Validates the Karva expression by checking operator arity and ensuring that the tail
        contains only terminals (no operators).
        """
        if len(self.expression) <= self.head_length:
            raise InvalidKarvaExpressionError("Expression length must be greater than the head length.")

        # Get the largest arity of the operators
        max_arity = max(arity for _, (func, arity) in self.ops.items())

        # give tail length
        tail_length = self.head_length*(max_arity-1) + 1

        if len(self.expression) < self.head_length + tail_length:
            raise InvalidKarvaExpressionError("Expression length must be greater or equal to the head + tail length.")
                
        # Ensure the tail contains only terminals
        for token in self.expression[self.head_length:]:
            if token in self.ops:
                raise InvalidKarvaExpressionError("Tail of Karva expression should contain only terminals.")

    def build_tree(self) -> TreeNode:
        """
        Builds the expression tree from the Karva expression.
        :return: The root of the expression tree.
        """
        idx = 0
        def build_subtree():
            nonlocal idx
            token = self.expression[idx]
            idx += 1

            node = TreeNode(token)

            if token in self.ops:
                func, arity = self.ops[token]
                # Add children nodes recursively based on operator arity
                for _ in range(arity):
                    child_node = build_subtree()
                    node.add_child(child_node)
            elif isinstance(token, (int, float)) or token.isdigit():
                child_node = TreeNode(token)
            elif isinstance(token, str):
                child_node = TreeNode(token)
            else:
                raise InvalidKarvaExpressionError(f"Unsupported token: {token}")
            
            return node
        
        return build_subtree()

    def evaluate_tree(self, node: TreeNode, variables: dict = None) -> float:
        """
        Evaluates the expression tree rooted at the given node.
        :param node: The root node of the tree.
        :param variables: A dictionary of variable names and their values, e.g., {'x': 2, 'y': 3}.
        :return: The evaluated result of the tree.
        """
        if isinstance(node.value, (int, float)):  # If the node is a number
            return node.value
        elif isinstance(node.value, str) and node.value in variables:  # If it's a variable
            return variables[node.value]
        elif node.value in self.ops:  # If it's an operator
            func, _ = self.ops[node.value]
            # Recursively evaluate the child nodes and apply the operator
            args = [self.evaluate_tree(child, variables) for child in node.children]
            return func(*args)
        else:
            raise InvalidKarvaExpressionError(f"Unsupported token or undefined variable: {node.value}")

    def evaluate(self, variables: dict = None) -> float:
        """
        Evaluates the Karva expression with the provided variable values.
        :param variables: A dictionary of variable names and their values.
        :return: The result of the evaluation.
        """
        tree = self.build_tree()  # Build the expression tree from the Karva expression
        return self.evaluate_tree(tree, variables)

    def to_string(self) -> str:
        """
        Converts the Karva expression into a readable string (infix notation), respecting operator precedence.
        :return: A string representing the expression.
        """
        def tree_to_string(node: TreeNode) -> str:
            if isinstance(node.value, (int, float)):  # If the node is a number
                return str(node.value)
            
            elif node.value in self.ops:  # If it's an operator
                func, arity = self.ops[node.value]
                children_strings = [tree_to_string(child) for child in node.children]
                if arity == 1:
                    return f"{node.value}({children_strings[0]})"
                elif arity == 2 and node.value in ['+', '-', '*', '/']:
                    return f"({children_strings[0]} {node.value} {children_strings[1]})"
                else:
                    return f"{node.value}({', '.join(children_strings)})"
            
            elif isinstance(node.value, str):  # If it's a variable
                return node.value
            else:
                raise InvalidKarvaExpressionError(f"Unsupported token: {node.value}")
        
        tree = self.build_tree()  # Build the expression tree
        return tree_to_string(tree)




if __name__ == "__main__":
    # Example usage:

    # Define a Karva expression: head = [+, neg], tail = [x, 2]
    karva_expr = KarvaExpression(['+', 'neg', 'x', 2,3,4,5], head_length=2)

    # Evaluate the expression (x = 3)
    result = karva_expr.evaluate({'x': 3})  # This evaluates neg(3) + 2
    print(f"Evaluation result: {result}")  # Output: -1.0

    # Define a Karva expression with a ternary operator: head = [?, x, y, z]
    karva_ternary_expr = KarvaExpression(['?', 'x', 'y', 'z', 2,3,4,5, 2,3,4,5], head_length=3)

    # Evaluate the ternary expression (x = 5, y = 3, z = 10)
    ternary_result = karva_ternary_expr.evaluate({'x': 5, 'y': 3, 'z': 10})
    print(f"Evaluation result: {ternary_result}")  # Output: 5.0

    # Convert to a readable string
    infix_str = karva_expr.to_string()
    print(f"Infix expression: {infix_str}")  # Output: (neg x + 2)

    infix_ternary_str = karva_ternary_expr.to_string()
    print(f"Infix ternary expression: {infix_ternary_str}")  # Output: x ? y : z

