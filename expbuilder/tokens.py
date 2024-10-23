from typing import Type
from expbuilder.op import Operator
from enum import IntEnum

class Token:
    def __repr__(self):
        return str(self)

class SequenceIndicatorType(IntEnum):
    BEG = 0
    SEP = 1

class ConstantToken(Token):
    def __init__(self, constant: float) -> None:
        self.constant = constant

    def __str__(self): return str(self.constant)

    def Val(self):
        return self.constant

class DeltaTimeToken(Token):
    def __init__(self, delta_time: int) -> None:
        self.delta_time = delta_time

    def __str__(self): return str(self.delta_time)

    def Val(self):
        return self.delta_time

class FeatureToken(Token):
    def __init__(self, feature: str) -> None:
        self.feature = feature

    def __str__(self): return '$' + self.feature.lower()

    def Val(self, kwargs: dict):
        return kwargs[str(self.feature)]

class OperatorToken(Token):
    def __init__(self, operator: Type[Operator]) -> None:
        self.operator = operator

    def __str__(self): return self.operator.name

class SequenceIndicatorToken(Token):
    def __init__(self, indicator: SequenceIndicatorType) -> None:
        self.indicator = indicator

    def __str__(self): return self.indicator.name


BEG_TOKEN = SequenceIndicatorToken(SequenceIndicatorType.BEG)
SEP_TOKEN = SequenceIndicatorToken(SequenceIndicatorType.SEP)

if __name__ == "__main__":
    # Example usage
    token = FeatureToken("FeatureName")
    kwargs = {"$featurename": 42}
    result = token.Val(kwargs)
    print(result)  # Output: 42