import torch
from rl.env.core import RegressionEnv
from expbuilder.tokens import Token,BEG_TOKEN,SEP_TOKEN

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