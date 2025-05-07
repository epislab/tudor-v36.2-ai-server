import tensorflow as tf
import matplotlib.pyplot as plt
import numpy as np

np.random.seed(777)

X = np.array([1, 2, 3], dtype=np.float32)
Y = np.array([1, 2, 3], dtype=np.float32)

W_history = []
cost_history = []

for i in range(-30, 50):
    curr_W = i * 0.1
    hypothesis = X * curr_W
    cost = np.mean((hypothesis - Y) ** 2)
    W_history.append(curr_W)
    cost_history.append(cost)

# 차트로 확인
plt.plot(W_history, cost_history)
plt.xlabel('W')
plt.ylabel('Cost')
plt.title('Cost vs W')
plt.show()