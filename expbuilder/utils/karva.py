# Karva expression class
# Used to compile and evaluate Karva expressions.
# Karva expressions are a form of genetic programming that represents mathematical expressions as head-tail list.
# The head contains operators and operands.
# the tail contains only terminals (variables or constants).

from typing import List, Union, Callable
import math

from common import Expression


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

class KEBase(Expression):
    def __init__(self, 
                 expression: List[Union[str, float, int]],
                 default_ops: dict[str, tuple[Callable, int]], 
                 head_length: int, 
                 custom_ops=None):
        """
        Initializes the KarvaExpression with a list of tokens and optional custom operators.
        :param expression: List of tokens representing the Karva expression.
        :param head_length: Length of the head of the Karva expression.
        :param custom_ops: Dictionary of custom operators/functions {symbol: (function, arity)}.
        """
        self.expression = expression
        self.head_length = head_length
        self.ops = default_ops.copy()  # Start with default ops
        if custom_ops:
            self.ops.update(custom_ops)  # Add/override with custom operators

    def validate_expression(self):
        """
        Validates the Karva expression Formal Legalitiy
        by checking operator arity and ensuring that the tail
        contains only terminals (no operators).
        """
        if len(self.expression) <= self.head_length:
            # raise InvalidKarvaExpressionError("Expression length must be greater than the head length.")
            # print("Expression length must be greater than the head length.")
            return False
        # Get the largest arity of the operators
        max_arity = max(arity for _, (_, arity) in self.ops.items())

        # give tail length
        tail_length = self.head_length*(max_arity-1) + 1

        if len(self.expression) < self.head_length + tail_length:
            # raise InvalidKarvaExpressionError("Expression length must be greater or equal to the head + tail length.")
            # print("Expression length must be greater or equal to the head + tail length.")
            return False
        
        # Ensure the tail contains only terminals
        for token in self.expression[self.head_length:]:
            if token in self.ops:
                # raise InvalidKarvaExpressionError("Tail of Karva expression should contain only terminals.")
                # print("Tail of Karva expression should contain only terminals.")
                return False
            
        return True
    

    def build_tree(self) -> TreeNode:
        """
        Builds the expression tree from the Karva expression.
        the process is recursive, whenever encount a operator, 
        it will call itself to build the subtree and add it to the current node.
        so "+ - * a b c d e f" would be built as: (a * b) - c + d
                 +
                / \
               -   d
              / \
             *   c
            / \
           a   b

        This process is different from the original Karva expression.
        The original Karva expression will build the subtree from the head to the tail sequentially.
        so "+ - * a b c d e f" would be built as: (a - b) + c * d
                 +
                / \
               -   *
              / \ / \
             a  b c  d
        
        :return: The root of the expression tree.
        """
        idx = 0
        def build_subtree():
            nonlocal idx
            token = self.expression[idx]
            idx += 1

            node = TreeNode(token)

            if token in self.ops:
                _, arity = self.ops[token]
                # Add children nodes recursively based on operator arity
                for _ in range(arity):
                    child_node = build_subtree()
                    node.add_child(child_node)
            elif isinstance(token, (int, float)) or token.isdigit() or isinstance(token, str):
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

   
    
    
    
    
    
    def to_function(self) -> Callable:
        """
        Converts the Karva expression to a callable function.
        :return: A function that takes arguments (as a dict for variables) and evaluates the expression.
        """  
        return self.evaluate


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
                children_strings = [tree_to_string(child) for child in node.children]
                return f"{node.value}({', '.join(children_strings)})"
            elif isinstance(node.value, str):  # If it's a variable
                return node.value
            else:
                raise InvalidKarvaExpressionError(f"Unsupported token: {node.value}")
        
        tree = self.build_tree()  # Build the expression tree
        return tree_to_string(tree)
    
    
    def __str__(self):
        return self.to_string()


if __name__ == "__main__":
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


    # Example usage:

    # + Define a Karva expression: head = [+, neg], tail = [x, 2.2, 3.1, 4.8, 5.2]
    # - Acutally, tail only needs headsize * (max_arity - 1) + 1 = 2 * (2 - 1) + 1 = 3 elements
    karva_expr = KEBase(['+', 'neg', 'x', 2.2, 3.1, 4.8, 5.2],
                        default_ops=DEFAULT_OPS,
                        head_length=2)
    
    # = Convert to a readable string: +(neg(x), 2.2)
    infix_str = karva_expr.to_string()
    print(f"Infix expression: {infix_str}")  

    infix_str_original = karva_expr.to_string_original()
    print(f"Infix expression original: {infix_str_original}") 


    # Evaluate the expression (x = 3)
    result = karva_expr.evaluate({'x': 3})  # This evaluates neg(3) + 2
    print(f"Evaluation result: {result}")  # Output: -0.7999999999999998

    # # Define a Karva expression with a ternary operator: head = [?, x, y, z]
    # karva_ternary_expr = KEBase(['?', 'x', 'y', 'z', 2,3,4,5, 2,3,4,5], head_length=3)

    # # Evaluate the ternary expression (x = 5, y = 3, z = 10)
    # ternary_result = karva_ternary_expr.evaluate({'x': 5, 'y': 3, 'z': 10})
    # print(f"Evaluation result: {ternary_result}")  # Output: 5.0

    
    # infix_ternary_str = karva_ternary_expr.to_string()
    # print(f"Infix ternary expression: {infix_ternary_str}")  # Output: x ? y : z

