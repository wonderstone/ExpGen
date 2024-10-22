from abc import ABC, abstractmethod
from typing import Callable, Any
class Expression(ABC):
    @abstractmethod
    def validate_expression(self) -> bool:
        """
        Validates the RPN/Karva expression.
        """

    @abstractmethod
    def to_function(self) -> Callable:
        """
        Converts the RPN/Karva expression to a callable function.
        :return: A function that takes arguments (as a dict for variables) and evaluates the expression.
        """

    @abstractmethod
    def evaluate(self, variables: dict) -> Any:
        """
        Evaluates the RPN/Karva expression.
        :param variables: A dictionary of variable names and their values, e.g., {'x': 2, 'y': 3}.
        :return: The evaluated result of the expression(float/Tensor).
        """
    
    @abstractmethod
    def to_string(self) -> str:
        """
        Converts the RPN/Karva expression into a readable string.
        :return: A string representing the expression.
        """
    
    @abstractmethod
    def __str__(self) -> str:
        """
        Returns a string representation of the RPN/Karva expression.
        """


