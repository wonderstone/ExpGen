from abc import ABC, abstractmethod

class Expression(ABC):
    @abstractmethod
    def validate_expression(self) -> bool:
        """
        Validates the RPN expression.
        """

    @abstractmethod
    def valid_following(self) -> dict:
        """
        Returns a dictionary of valid following tokens for the expression now. 
        """
    
    @abstractmethod
    def to_function(self) -> Callable:
        """
        Converts the RPN expression to a callable function.
        :return: A function that takes arguments (as a dict for variables) and evaluates the expression.
        """

    @abstractmethod
    def evaluate(self, variables: dict) -> float:
        """
        Evaluates the RPN expression.
        :param variables: A dictionary of variable names and their values, e.g., {'x': 2, 'y': 3}.
        :return: The evaluated result of the expression.
        """
    
    @abstractmethod
    def to_string(self) -> str:
        """
        Converts the RPN expression into a readable string.
        :return: A string representing the expression.
        """
    
    @abstractmethod
    def __str__(self) -> str:
        """
        Returns a string representation of the RPN expression.
        """


