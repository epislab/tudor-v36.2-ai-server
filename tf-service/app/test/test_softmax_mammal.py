import tensorflow as tf
import numpy as np

# [털, 날개]
x_data = np.array(
    [[0, 0],[1, 0],[1, 1],[0, 0],[0, 0], [0, 1]], dtype=np.float32
)

# 기타, 포유류, 조류 (원핫 인코딩)
y_data = np.array([
    [1, 0, 0], # 기타
    [0, 1, 0], # 포유류
    [0, 0, 1], # 조류
    [1, 0, 0], # 기타
    [0, 1, 0], # 포유류
    [0, 0, 1]  # 조류
], dtype=np.float32)

# 신경망 모델 정의 (Keras 사용)
class SimpleNN(tf.keras.Model):
    def __init__(self):
        super().__init__()
        self.dense1 = tf.keras.layers.Dense(3, activation='relu')
        self.softmax = tf.keras.layers.Softmax()
    def call(self, x):
        x = self.dense1(x)
        return self.softmax(x)

model = SimpleNN()
optimizer = tf.keras.optimizers.SGD(learning_rate=0.01)

# 학습 루프
for step in range(100):
    with tf.GradientTape() as tape:
        logits = model(x_data)
        loss = tf.reduce_mean(tf.keras.losses.categorical_crossentropy(y_data, logits))
    grads = tape.gradient(loss, model.trainable_variables)
    optimizer.apply_gradients(zip(grads, model.trainable_variables))
    if (step + 1) % 10 == 0:
        print(step + 1, float(loss))

# 결과 확인
pred = tf.argmax(model(x_data), axis=1).numpy()
target = tf.argmax(y_data, axis=1)
print('예측값', pred)
print('실제값', target.numpy())
accuracy = np.mean(pred == target.numpy())
print('정확도: %.2f' % (accuracy * 100))