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
    def __init__(self, expression: list, ops: dict):
        self.expression = expression
        self.ops = ops
        self.idx = 0  # Current index in the expression list

    def build_tree(self) -> TreeNode:
        """
        Builds the expression tree from the Karva expression following the sequential parsing rules.
        :return: The root of the expression tree.
        """
        if self.idx >= len(self.expression):
            raise InvalidKarvaExpressionError("Ran out of tokens while building the tree.")
        
        # Get the current token
        token = self.expression[self.idx]
        self.idx += 1  # Move to the next token

        # Create a tree node for this token
        node = TreeNode(token)

        if token in self.ops:
            # If the token is an operator, get its arity and add children accordingly
            _, arity, _ = self.ops[token]
            
            # Recursively build subtrees for each of the operator's operands in a strictly sequential order
            for _ in range(arity):
                child_node = self.build_tree()
                node.add_child(child_node)

        # If the token is an operand (number, variable, etc.), it is a leaf node.
        return node


# Example usage:
DEFAULT_OPS = {
    '+': (lambda a, b: a + b, 2, 1),  # (operator, arity, precedence)
    '-': (lambda a, b: a - b, 2, 1),
    '*': (lambda a, b: a * b, 2, 2),
    '/': (lambda a, b: a / b if b != 0 else float('inf'), 2, 2),
    'neg': (lambda a: -a, 1, 3)
}

# Karva expression: ['+', '-', '*', 'a', 'b', 'c', 'd']
karva_expr = KarvaExpression(['+', '-', '*', 'a', 'b', 'c', 'd'], DEFAULT_OPS)
root = karva_expr.build_tree()

# Simple tree traversal to print the tree
def print_tree(node, depth=0):
    print("  " * depth + str(node.value))
    for child in node.children:
        print_tree(child, depth + 1)

# Print the tree structure
print_tree(root)