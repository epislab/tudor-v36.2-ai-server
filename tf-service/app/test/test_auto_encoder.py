import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt

# MNIST 데이터 로드
(x_train, _), (x_test, _) = tf.keras.datasets.mnist.load_data()
x_train = x_train.astype(np.float32) / 255.
x_test = x_test.astype(np.float32) / 255.
x_train = x_train.reshape(-1, 28 * 28)
x_test = x_test.reshape(-1, 28 * 28)

learning_rate = 0.01
training_epoch = 20
batch_size = 100
n_hidden = 256
n_input = 28 * 28

# 오토인코더 모델 정의
class AutoEncoder(tf.keras.Model):
    def __init__(self, n_hidden, n_input):
        super().__init__()
        self.encoder = tf.keras.layers.Dense(n_hidden, activation='sigmoid')
        self.decoder = tf.keras.layers.Dense(n_input, activation='sigmoid')
    def call(self, x):
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return decoded

model = AutoEncoder(n_hidden, n_input)
optimizer = tf.keras.optimizers.RMSprop(learning_rate)

# 학습 루프
train_dataset = tf.data.Dataset.from_tensor_slices(x_train).shuffle(10000).batch(batch_size)
for epoch in range(training_epoch):
    total_cost = 0
    batch_count = 0
    for batch_xs in train_dataset:
        with tf.GradientTape() as tape:
            decoded = model(batch_xs)
            loss = tf.reduce_mean(tf.square(batch_xs - decoded))
        grads = tape.gradient(loss, model.trainable_variables)
        optimizer.apply_gradients(zip(grads, model.trainable_variables))
        total_cost += float(loss)
        batch_count += 1
    print('Epoch:', '%04d' % (epoch + 1), 'Avg Cost:', '{:.4f}'.format(total_cost / batch_count))

print('-----최적화 완료------')

# 신경망 모델 테스트(검정)
sample_size = 10
samples = model(x_test[:sample_size]).numpy()

fig, ax = plt.subplots(2, sample_size, figsize=(sample_size, 2))
for i in range(sample_size):
    ax[0][i].set_axis_off()
    ax[1][i].set_axis_off()
    ax[0][i].imshow(np.reshape(x_test[i], (28, 28)), cmap='gray')
    ax[1][i].imshow(np.reshape(samples[i], (28, 28)), cmap='gray')
plt.show()