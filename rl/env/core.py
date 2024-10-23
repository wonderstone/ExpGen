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


MAX_EXPR_LENGTH = 20
MAX_EPISODE_LENGTH = 256


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
        self._builder.tokenexp = [BEG_TOKEN]


    
    def step(self, action: Token, data:dict):
        if (isinstance(action, SequenceIndicatorType) and action == SequenceIndicatorType.SEP):
            reward = self._evaluate()
            done = True
        elif len(self._builder.tokenexp) < MAX_EXPR_LENGTH:
            self._builder.add_token(data,action)
            reward = 0
            done = False
        else:
            done = True
            reward = self._evaluate() if self._builder.validate_expression() else -1
        if math.isnan(reward):
            reward = -1

        return self._builder.tokenexp, reward, done, self._builder.valid_next_token({'x': self.x, 'y': self.y})
    
    
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

    default_ops = {
        '+': (lambda x, y: x + y, 2),
        '-': (lambda x, y: x - y, 2),
        '*': (lambda x, y: x * y, 2),
        '/': (lambda x, y: x / y, 2),
        'sin': (torch.sin, 1),
        'cos': (torch.cos, 1),
        'exp': (torch.exp, 1),
    }

    env = RegressionEnv(default_ops=default_ops, expression=[BEG_TOKEN], n_samples=100, noise=0.1)
    print(env.reset(seed = 666))

    data = {'x': env.x, 'y': env.y}
    res =  env._builder.valid_next_token(data)
    print(res)
    env._builder.add_token(data,ConstantToken(2))
    env._builder.add_token(data,FeatureToken('x'))

    print(env._builder.expression)

    print(env.step(SEP_TOKEN,data))

