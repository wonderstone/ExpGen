from typing import List, Callable
from op import Optype
from utils.RPN import RPNExpression
from tokens import *



class RPNBuilder(RPNExpression):
    def __init__(self, 
                 expression: List[Token],
                 default_ops: dict[str, tuple[Callable, int]],
                 max_length:int = 100,
                 custom_ops=None):
        # Convert the list of operators to a list of operator names
        # the iteration should neglect the SequenceIndicatorToken
        strexp = list()
        self.CSops = dict()
        self.TSops = dict()
        self.MaxArity = 0
        self.maxLen = max_length    
        for op in expression:
            if not isinstance(op, SequenceIndicatorToken):
                strexp.append(str(op))
            if isinstance(op, OperatorToken):
                if op.operator.Optype == Optype.CS:
                    if op.operator.n_args() not in self.CSops:
                        self.CSops[op.operator.n_args()] = set()
                    self.CSops[op.operator.n_args()].add(op.operator.name)
                elif op.operator.Optype == Optype.TS:
                    if op.operator.n_args() not in self.TSops:
                        self.TSops[op.operator.n_args()] = set()
                    self.TSops[op.operator.n_args()].add(op.operator.name)
                if op.operator.n_args() > self.MaxArity:
                    self.MaxArity = op.operator.n_args()
        self.tokenexp = expression

        super().__init__(strexp, default_ops, custom_ops)





    


    def valid_next_token(self, data:dict) -> dict:
        """
        Returns a dictionary of valid next tokens based on the current token.
        """
        stack = []
        last_token = None
        for token in self.tokenexp:
            if isinstance(token,SequenceIndicatorToken):
                pass
            elif isinstance(token, ConstantToken):
                stack.append(token.Val())
                last_token = token
            elif isinstance(token, DeltaTimeToken):
                stack.append(token.Val())
                last_token = token
            elif isinstance(token, FeatureToken):
                stack.append(token.Val(data))
                last_token = token
            elif isinstance(token, OperatorToken):
                # get operator arity
                func, arity = self.ops[token.operator.name]
                # Pop the necessary number of arguments based on the arity of the operator
                args_to_pass = [ stack.pop() for _ in range(arity)][::-1]
                result = func(*args_to_pass)
                stack.append(result)
                last_token = token


        remaining = self.maxLen - len(self.tokenexp)
        # if all the remaining tokens are operators with the maximum arity, the expression is valid
        # how long the stack should be to be valid
        MinArity4Choose = (len(stack)-1)/remaining + 1
        # if the stack has only one element, the expression is valid
        # SEP_TOKEN is ok to choose
        if len(stack) == 1:
            return {"Constant": True, "DeltaTime": True, "Feature": True, 
                    "CSOperator": {"Max": 1, "Min": None},
                    "TSOperator": {"Max": None, "Min": None},
                    "SEP": True}
            
    
        if last_token is None:
            return {"Constant": True, "DeltaTime": False, "Feature": True, 
                    "CSOperator": {"Max": None, "Min": None}, 
                    "TSOperator": {"Max": None, "Min": None},
                    "SEP": False}
        # if the last token is a constant or a feature, the next token can be all types
        elif isinstance(last_token, ConstantToken) or isinstance(last_token, FeatureToken):
            return {"Constant": True, "DeltaTime": True, "Feature": True, 
                    "CSOperator": {"Max": len(stack), "Min": None}, 
                    "TSOperator": {"Max": None, "Min": None},
                    "SEP": False}
        # if the last token is a delta time, the next token can only be a TS operator
        elif isinstance(last_token, DeltaTimeToken):
            return {"Constant": False, "DeltaTime": False, "Feature": False, 
                    "CSOperator": {"Max": None, "Min": None}, 
                    "TSOperator": {"Max": len(stack), "Min": None},
                    "SEP": False}
        # if the last token is an operator, the next token can be a constant , a feature,a delta time or a CS operator
        elif isinstance(last_token, OperatorToken):
            return {"Constant": True, "DeltaTime": True, "Feature": True, 
                    "CSOperator": {"Max": len(stack), "Min": None}, 
                    "TSOperator": {"Max": None, "Min": None},
                    "SEP": False}

    def add_token(self, data:dict, token: Token):
        """
        Adds a token to the expression.
        """
        if len(self.tokenexp) < self.maxLen:
            # token should be a valid next token
            vnt = self.valid_next_token(data)
            if isinstance(token, ConstantToken):
                if vnt["Constant"]:
                    self.tokenexp.append(token)
                    self.expression.append(str(token))
                else:
                    raise ValueError("The expression is invalid")
            elif isinstance(token, DeltaTimeToken):
                if vnt["DeltaTime"]:
                    self.tokenexp.append(token)
                    self.expression.append(str(token))
                else:
                    raise ValueError("The expression is invalid")
            elif isinstance(token, FeatureToken):
                if vnt["Feature"]:
                    self.tokenexp.append(token)
                    self.expression.append(str(token))
                else:
                    raise ValueError("The expression is invalid")
            elif isinstance(token, OperatorToken):
                if token.operator.Optype == Optype.CS:
                    if vnt["CSOperator"]["Max"] is not None and vnt["CSOperator"]["Max"] < token.operator.n_args():
                        raise ValueError("The Token is invalid for the expression")
                    self.tokenexp.append(token)
                    self.expression.append(str(token))

                elif token.operator.Optype == Optype.TS:
                    if vnt["TSOperator"]["Max"] is not None and vnt["TSOperator"]["Max"] < token.operator.n_args():
                        raise ValueError("The Token is invalid for the expression")
                    self.tokenexp.append(token)
                    self.expression.append(str(token))
            elif isinstance(token, SequenceIndicatorToken):
                if vnt["SEP"]:
                    self.tokenexp.append(token)
                else:
                    raise ValueError("The expression is invalid for the SEP token") 
        else:
            raise ValueError("The expression is full")
# Example usage
if __name__ == "__main__":
    def add(a, b):
        return a + b
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
    print(r.calc(3,1))



    op_add = Operator(name="add", Optype=Optype.CS, callable=add, argTypeList=[float, int])
    op_ref = Operator(name="ref", Optype=Optype.TS ,callable=r.calc, argTypeList=[float,int])
    print(op_add)
    print(f"Number of arguments: {op_add.n_args()}")
    print(f"Available operators: {Operator.ops_available}")
    # do the function call
    result = op_add.eval(3, 4)
    print(f"Result: {result}")


    # build the RPN expression
    tokens = [BEG_TOKEN,
              ConstantToken(3), 
              FeatureToken("close"), 
              OperatorToken(op_add),
              DeltaTimeToken(1), 
              OperatorToken(op_ref)]
    rpn = RPNBuilder(tokens, default_ops={"add": (add, 2), "ref": (r.calc, 2)}, max_length=9)
    print(f"RPN expression: {rpn.expression}")
    print(rpn.to_string())
    result = rpn.evaluate({'$close': 4})
    print(f"Result: {result}")
    result = rpn.evaluate({'$close': 5})
    print(f"Result: {result}")
    
    # test add_token
    tmpdata = {'$close': 6}
    rpn.add_token(data=tmpdata, token=ConstantToken(3))
    pass
