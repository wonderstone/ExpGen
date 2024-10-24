from enum import IntEnum
from typing import Callable, List, Type

class OPType(IntEnum):
    CS = 1
    TS = 2

class Operator:
    ops_available = dict()

    def __init__(self, 
                 name: str,
                 Optype: OPType,
                 callable: Callable, 
                 argTypeList: List[Type]):
        self.name = name
        self.Optype = Optype
        self.callable = callable
        self.argTypeList = argTypeList
        Operator.add_dict(self)

    @classmethod
    def add_dict(cls, op: 'Operator'):
        cls.ops_available[op.name] = op.callable

    def n_args(self) -> int:
        return len(self.argTypeList)

    def eval(self, *args):
        return self.callable(*args)

    def __repr__(self):
        return f"Operator(name={self.name}, callable={self.callable}, argTypeList={self.argTypeList})"


if __name__ == "__main__":
    # Example usage
    # + add operator
    def add(a, b):
        return a + b
    
    # + ref operator
    # - ref operator is a class that has a method calc that takes two arguments
    import queue
    class ref:
        def __init__(self, n:int):
            # init a queue of length n
            self.q = queue.Queue(n+1)
            # Fill the queue with None values to start with
            for _ in range(n):
                self.q.put(None)
        
        def calc(self, v,n):
            # add n to the queue
            self.q.put(v)
            # return the sum of the queue
            return self.q.get()



    # try the ref class
    r = ref(1)
    print(r.calc(1,1))
    print(r.calc(2,1))

    # try the Operator class
    op_add = Operator(name="add", Optype=OPType.CS, callable=add, argTypeList=[float, int])
    op_ref = Operator(name="ref", Optype=OPType.TS ,callable=r.calc, argTypeList=[float,int])
    print(op_add)
    print(f"Number of arguments: {op_add.n_args()}")
    print(f"Available operators: {Operator.ops_available}")
    # do the function call
    result = op_add.eval(3, 4)
    print(result)
    result = op_ref.eval(3, 1)
    print(result)