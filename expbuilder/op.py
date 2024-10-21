from enum import IntEnum
from typing import Callable, List, Type

class Optype(IntEnum):
    CS = 1
    TS = 2

class Operator:
    ops_available = dict()

    def __init__(self, 
                 name: str,
                 Optype: Optype,
                 callable: Callable, 
                 argTypeList: List[Type]):
        self.name = name
        self.Optype = Optype
        self.callable = callable
        self.argTypeList = argTypeList
        Operator.add(self)

    @classmethod
    def add(cls, op: 'Operator'):
        cls.ops_available[op.name] = op.callable

    def n_args(self) -> int:
        return len(self.argTypeList)

    def eval(self, *args):
        return self.callable(*args)

    def __repr__(self):
        return f"Operator(name={self.name}, callable={self.callable}, argTypeList={self.argTypeList})"


