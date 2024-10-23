# try a tensor with math.sin
import math
from torch import Tensor


x = Tensor([1, 2, 3])
y = Tensor([4, 5, 6])

print(f"Tensor x: {x}")
print(f"Tensor y: {y}")

# z = math.sin(x) + y
z = x.sin() + y
print(f"Result: {z}")

# use np.sin instead of math.sin
import numpy as np

zz = np.sin(x) + y
print(f"Result: {zz}")

