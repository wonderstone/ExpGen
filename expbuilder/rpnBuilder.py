from typing import List, Callable, Optional
from expbuilder.op import OPType
from utils.RPN import RPNBase
from expbuilder.tokens import *

def GetArityDict(ops: dict[str, tuple[Callable, int]]) -> dict[int, set[str]]:
    """
    Get the arity dictionary from the operators dictionary
    """
    arity_dict = dict()
    func_dict = dict()
    for op in ops:
        _, arity = ops[op]
        func_dict[op] = arity
        if arity not in arity_dict:
            arity_dict[arity] = list()
        arity_dict[arity].append(op)
    return arity_dict, func_dict



def GetActionSpace(Constants: Optional[List[float]],
                   Features: Optional[List[str]],
                   DeltaTimes: Optional[List[int]],
                   CSOperators: Optional[List[str]],
                   TSOperators: Optional[List[str]]) -> List[str]: 

    """
    Get the action space for the RPN expression
    """
    action_space = []
    # if Constants is not None, add the constant tokens
    if Constants is not None:
        for c in Constants:
            action_space.append(str(c))
    # if Features is not None, add the feature tokens
    if Features is not None:
        for f in Features:
            action_space.append(f)
    # if DeltaTimes is not None, add the delta time tokens
    if DeltaTimes is not None:
        for d in DeltaTimes:
            action_space.append(str(d))
    # if Operators is not None, add the operator tokens
    if CSOperators is not None:
        for o in CSOperators:
            action_space.append(o)
    if TSOperators is not None:
        for o in TSOperators:
            action_space.append(o)
    # add the SEP token
    action_space.append(SEP_TOKEN.__str__())
    return action_space

def MaskOPSpace(func_arity_dict: dict,
                ValidOPDict: dict,
                Operators: List[str]) -> List[bool]:
    MaxArity = ValidOPDict["Max"]
    if MaxArity is None:
        return [False] * len(Operators)
    
    res = []
    for op in Operators:
        if func_arity_dict[op] <= MaxArity:
            res.append(True)
        else:
            res.append(False)
    return res

def MaskActionSpace(Constants: Optional[List[float]],
                    Features: Optional[List[str]],
                    DeltaTimes: Optional[List[int]],
                    CSOperators: Optional[List[str]],
                    TSOperators: Optional[List[str]],
                    func_arity_dict: dict,
                    ValidDict: dict) -> List[bool]:   
    """
    Get the action space for the RPN expression
    """
    action_space = list()
    # if Constants is not None, add the constant tokens
    if Constants is not None:
        if ValidDict["Constant"]:
            action_space += [True] * len(Constants)
            
        else:
            action_space += [False] * len(Constants)
    else:
        pass
    # if Features is not None, add the feature tokens
    if Features is not None:
        if ValidDict["Feature"]:
            action_space += [True] * len(Features)
        else:
            action_space += [False] * len(Features)
    else:
        pass
    # if DeltaTimes is not None, add the delta time tokens
    if DeltaTimes is not None:
        if ValidDict["DeltaTime"]:
            action_space += [True] * len(DeltaTimes)
        else:
            action_space += [False] * len(DeltaTimes)
    else:
        pass
    # if Operators is not None, add the operator tokens

    if CSOperators is not None:
        if ValidDict["CSOperator"]["Max"] is not None:
            action_space += MaskOPSpace(func_arity_dict, ValidDict["CSOperator"], CSOperators)
        else:
            action_space += [False] * len(CSOperators)
    else:
        pass
    if TSOperators is not None:
        if ValidDict["TSOperator"]["Max"] is not None:
            action_space += MaskOPSpace(func_arity_dict, ValidDict["TSOperator"], TSOperators)
        else:
            action_space += [False] * len(TSOperators)
    # add the SEP token
    if ValidDict["SEP"]:
        action_space.append(True)
    else:
        action_space.append(False)
    return action_space


    







class RPNBuilder(RPNBase):
    def __init__(self, 
                 tokenList: List[Token],
                 default_ops: dict[str, tuple[Callable, int]],
                 max_length:int = 100,
                 custom_ops=None):
        # Convert the list of operators to a list of operator names
        # the iteration should neglect the SequenceIndicatorToken
        strexp = list()
        self.CSops = dict()
        self.TSops = dict()
        self.MaxArity = 0
        for op in tokenList:
            if not isinstance(op, SequenceIndicatorToken):
                strexp.append(str(op))
            if isinstance(op, OperatorToken):
                if op.operator.Optype == OPType.CS:
                    if op.operator.n_args() not in self.CSops:
                        self.CSops[op.operator.n_args()] = set()
                    self.CSops[op.operator.n_args()].add(op.operator.name)
                elif op.operator.Optype == OPType.TS:
                    if op.operator.n_args() not in self.TSops:
                        self.TSops[op.operator.n_args()] = set()
                    self.TSops[op.operator.n_args()].add(op.operator.name)
                if op.operator.n_args() > self.MaxArity:
                    self.MaxArity = op.operator.n_args()
        self.maxLen = max_length
        self.tokenList = tokenList  
        super().__init__(strexp, default_ops, custom_ops)
        # - also has the property of the RPNBase class
        # self.expression, which is the expression string
        # self.ops, which is the copy of default_ops  




    def valid_next_token_formal(self) -> dict:
        """
        Only the formal legality is checked here.
        Returns a dictionary of valid next tokens based on the current token.
        """
        stack = []
        last_token = None
        for token in self.tokenList:
            if isinstance(token,SequenceIndicatorToken):
                pass
            elif isinstance(token, ConstantToken):
                stack.append(0)
                last_token = token
            elif isinstance(token, DeltaTimeToken):
                stack.append(0)
                last_token = token
            elif isinstance(token, FeatureToken):
                stack.append(0)
                last_token = token
            elif isinstance(token, OperatorToken):
                # get operator arity
                _, arity = self.ops[token.operator.name]
                # Pop the necessary number of arguments based on the arity of the operator
                for _ in range(arity):
                    stack.pop()
                stack.append(0)
                last_token = token

        # if the stack has only one element, the expression is valid
        # SEP_TOKEN is ok to choose
        if len(stack) == 1:
            return {"Constant": True, "DeltaTime": True, "Feature": True, 
                    "CSOperator": {"Max": 1, "Min": None},
                    "TSOperator": {"Max": None, "Min": None},
                    "SEP": True}
            
        # in case of the the token list is empty
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

    def valid_next_token_value(self, data:dict) -> dict:
        """
        Returns a dictionary of valid next tokens based on the current token.
        """
        stack = []
        last_token = None
        for token in self.tokenList:
            # if the token is BEGIN_TOKEN or SEP_TOKEN, it is not considered
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


        remaining = self.maxLen - len(self.tokenList)
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
            
        # in case of the the token list is empty
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
                    "TSOperator": {"Max": len(stack)-1, "Min": None}, # for the last token is delta time, the 
                    "SEP": False}
        # if the last token is an operator, the next token can be a constant , a feature,a delta time or a CS operator
        elif isinstance(last_token, OperatorToken):
            return {"Constant": True, "DeltaTime": True, "Feature": True, 
                    "CSOperator": {"Max": len(stack), "Min": None}, 
                    "TSOperator": {"Max": None, "Min": None},
                    "SEP": False}
    
    def add_token_formal(self, token: Token):
        """
        Adds a token to the expression.
        """
        if len(self.tokenList) < self.maxLen:
            # token should be a valid next token
            vnt = self.valid_next_token_formal()
            if isinstance(token, ConstantToken):
                if vnt["Constant"]:
                    self.tokenList.append(token)
                    self.expression.append(str(token))
                else:
                    raise ValueError("ConstantToken is invalid for the expression")
            elif isinstance(token, DeltaTimeToken):
                if vnt["DeltaTime"]:
                    self.tokenList.append(token)
                    self.expression.append(str(token))
                else:
                    raise ValueError("DeltaTimeToken is invalid for the expression")
            elif isinstance(token, FeatureToken):
                if vnt["Feature"]:
                    self.tokenList.append(token)
                    self.expression.append(str(token))
                else:
                    raise ValueError("FeatureToken is invalid for the expression")
            elif isinstance(token, OperatorToken):
                if token.operator.Optype == OPType.CS:
                    if vnt["CSOperator"]["Max"] is None or vnt["CSOperator"]["Max"] < token.operator.n_args():
                        raise ValueError("The Token is invalid for the expression")
                    self.tokenList.append(token)
                    self.expression.append(str(token))

                elif token.operator.Optype == OPType.TS:
                    if vnt["TSOperator"]["Max"] is None and vnt["TSOperator"]["Max"] < token.operator.n_args():
                        raise ValueError("The Token is invalid for the expression")
                    self.tokenList.append(token)
                    self.expression.append(str(token))
            elif isinstance(token, SequenceIndicatorToken):
                if vnt["SEP"]:
                    self.tokenList.append(token)
                else:
                    raise ValueError("SEP Token is invalid for the expression") 
        else:
            raise ValueError("The expression is full")

    def add_token_value(self, data:dict, token: Token):
        """
        Adds a token to the expression.
        """
        if len(self.tokenList) < self.maxLen:
            # token should be a valid next token
            vnt = self.valid_next_token_value(data)
            if isinstance(token, ConstantToken):
                if vnt["Constant"]:
                    self.tokenList.append(token)
                    self.expression.append(str(token))
                else:
                    raise ValueError("The expression is invalid")
            elif isinstance(token, DeltaTimeToken):
                if vnt["DeltaTime"]:
                    self.tokenList.append(token)
                    self.expression.append(str(token))
                else:
                    raise ValueError("The expression is invalid")
            elif isinstance(token, FeatureToken):
                if vnt["Feature"]:
                    self.tokenList.append(token)
                    self.expression.append(str(token))
                else:
                    raise ValueError("The expression is invalid")
            elif isinstance(token, OperatorToken):
                if token.operator.Optype == OPType.CS:
                    if vnt["CSOperator"]["Max"] is None and vnt["CSOperator"]["Max"] < token.operator.n_args():
                        raise ValueError("The Token is invalid for the expression")
                    self.tokenList.append(token)
                    self.expression.append(str(token))

                elif token.operator.Optype == OPType.TS:
                    if vnt["TSOperator"]["Max"] is None and vnt["TSOperator"]["Max"] < token.operator.n_args():
                        raise ValueError("The Token is invalid for the expression")
                    self.tokenList.append(token)
                    self.expression.append(str(token))
            elif isinstance(token, SequenceIndicatorToken):
                if vnt["SEP"]:
                    self.tokenList.append(token)
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

    r = ref(1)


    default_ops = {
            '+': (lambda x, y: x + y, 2),
            '-': (lambda x, y: x - y, 2),
            '*': (lambda x, y: x * y, 2),
            '/': (lambda x, y: x / y, 2),
        }

    # try the ref class
    r = ref(1)
    print(r.calc(1,1))
    print(r.calc(2,1))
    print(r.calc(3,1))



    op_add = Operator(name="add", Optype=OPType.CS, callable=add, argTypeList=[float, int])
    op_ref = Operator(name="ref", Optype=OPType.TS ,callable=r.calc, argTypeList=[float,int])
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
    rpn.add_token_value(data=tmpdata, token=ConstantToken(3))
    pass
