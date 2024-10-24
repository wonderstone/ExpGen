import math
import os
import random
from typing import Callable, List, Optional
import numpy as np
from expbuilder.rpnBuilder import RPNBuilder
from expbuilder.tokens import *
import torch
from torch.backends import cudnn

# use RL framework to solve a regression problem
# the final output would be a RPN expression
# the environment have a fixed dataset y = 2 * x + 1 + noise

default_ops = {
        '+': (lambda x, y: x + y, 2),
        '-': (lambda x, y: x - y, 2),
        '*': (lambda x, y: x * y, 2),
        '/': (lambda x, y: x / y, 2),
        'sin': (torch.sin, 1),
        'cos': (torch.cos, 1),
        'exp': (torch.exp, 1),
    }

default_ops_list = list(default_ops.keys())

default_features = ["x" ]
# DELTA_TIMES = [1, 2, 3, 4, 5]

CONSTANTS = [-1., -0.5, -0.01, 0.01, 0.5, 1., 2.]

REWARD_PER_STEP = 0.

MAX_EXPR_LENGTH = 20
MAX_EPISODE_LENGTH = 256


SIZE_NULL = 1 # cause the first token is always a BEG_TOKEN
SIZE_OP = len(default_ops_list)
SIZE_FEATURE = len(default_features)
# SIZE_DELTA_TIME = len(DELTA_TIMES)
SIZE_CONSTANT = len(CONSTANTS)
SIZE_SEP = 1

# SIZE_ALL = SIZE_NULL + SIZE_OP + SIZE_FEATURE + SIZE_DELTA_TIME + SIZE_CONSTANT + SIZE_SEP
SIZE_ALL = SIZE_NULL + SIZE_OP + SIZE_FEATURE + SIZE_CONSTANT + SIZE_SEP



SIZE_ACTION = SIZE_ALL - SIZE_NULL

OFFSET_OP = SIZE_NULL
OFFSET_FEATURE = OFFSET_OP + SIZE_OP

OFFSET_CONSTANT = OFFSET_FEATURE + SIZE_FEATURE
# OFFSET_DELTA_TIME = OFFSET_FEATURE + SIZE_FEATURE
# OFFSET_CONSTANT = OFFSET_DELTA_TIME + SIZE_DELTA_TIME
OFFSET_SEP = OFFSET_CONSTANT + SIZE_CONSTANT


def action_to_token(action_raw: int) -> Token:
    action = action_raw + SIZE_NULL
    if action < OFFSET_OP:
        raise ValueError(f"Invalid action {action_raw}")
    elif action < OFFSET_FEATURE:
        return OperatorToken(default_ops_list[action - OFFSET_OP])
    elif action < OFFSET_CONSTANT:
        return FeatureToken(default_features[action - OFFSET_FEATURE])
    elif action < OFFSET_SEP:
        return ConstantToken(CONSTANTS[action - OFFSET_CONSTANT])
    elif action == OFFSET_SEP:
        return SEP_TOKEN
    else:
        raise ValueError(f"Invalid action {action_raw}")







class RegressionEnv():

    def __init__(self, expression: List[Token], default_ops: dict[str, tuple[Callable, int]],
                 n_samples=100, noise=0.1):
        self.n_samples = n_samples
        self.noise = noise
        self._builder = RPNBuilder(expression, default_ops, max_length=MAX_EXPR_LENGTH)
        self.x = torch.tensor(np.random.uniform(-10, 10, n_samples), dtype=torch.float32)
        self.y = 2 * self.x + 1 + torch.tensor(np.random.normal(0, noise, n_samples), dtype=torch.float32)

    
    def reset(self, seed: Optional[int] = None):
        reseed_everything(seed)
        self._builder.tokenList = [BEG_TOKEN]


    
    def step(self, action: Token, data:dict):
        if (isinstance(action, SequenceIndicatorType) and action == SequenceIndicatorType.SEP):
            reward = self._evaluate()
            done = True
        elif len(self._builder.tokenList) < MAX_EXPR_LENGTH:
            self._builder.add_token_value(data,action)
            reward = 0
            done = False
        else:
            done = True
            reward = self._evaluate() if self._builder.validate_expression() else -1
        if math.isnan(reward):
            reward = -1

        return self._builder.tokenList, reward, done, self._builder.valid_next_token_value({'x': self.x, 'y': self.y})
    
    
    def _evaluate(self):
        try:
            return self._builder.evaluate({'x': self.x, 'y': self.y})
        except Exception as e:
            return -1
    
    def render(self):
        pass

    def close(self):
        pass    







def reseed_everything(seed: Optional[int]):
    if seed is None:
        return

    random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    cudnn.deterministic = True
    cudnn.benchmark = True



if __name__ == "__main__":

    
    env = RegressionEnv(default_ops=default_ops, expression=[BEG_TOKEN], n_samples=100, noise=0.1)
    print(env.reset(seed = 666))

    data = {'x': env.x, 'y': env.y}
    res =  env._builder.valid_next_token_value(data)
    print(res)
    env._builder.add_token_value(data,ConstantToken(2))
    env._builder.add_token_value(data,FeatureToken('x'))

    print(env._builder.expression)

    print(env.step(SEP_TOKEN,data))

