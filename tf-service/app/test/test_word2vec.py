import tensorflow as tf
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager, rc
rc('font', family=font_manager.FontProperties(fname='C:/Windows/Fonts/나눔고딕코딩.TTF').get_name())

# tensorflow 연산에서 matplot 사용할 때 한글 처리

# 단어 벡터를 분석해 볼 임의의 문장들
sentences = [
    "나 고양이 좋다",
    "나 강아지 좋다",
    "나 동물 좋다",
    "강아지 고양이 동물",
    "여자친구 고양이 강아지 좋다",
    "고양이 생선 우유 좋다",
    "강아지 생선 싫다 우유 좋다",
    "강아지 고양이 눈 좋다",
    "나 여자친구 좋다",
    "여자친구 나 싫다",
    "여자친구 나 영화 책 음악 좋다",
    "나 게임 만화 애니 좋다",
    "고양이 강아지 싫다",
    "강아지 고양이 좋다"
]
# 문장을 전부 합친 후 공백으로 단어들을 나누고 고유한 단어들로 리스트 생성
word_sequnce = " ".join(sentences).split()
word_list = list(set(word_sequnce))
# 텐서플로 데이터타입 3가지
# tuple () , dict {}, list []
# 단 텐서 요소의 데이터 타입과 혼동 주의 !!
# 문자열로 분석하는 것 보다, 숫자로 분석하는 것이 훨씬 용이하므로
# 리스트에서 문자들을 인덱스로 뽑아서 사용하기 위해
# 이를 표현하기 위한 연관배열과
# 단어 리스트에서 단어를 참조할 수 있는 인덱스 배열을 만듭니다.

word_dict = {W: i for i, W in enumerate(word_list)}

skip_grams = []
for i in range(1, len(word_sequnce) - 1):
    target = word_dict[word_sequnce[i]]
    context = [word_dict[word_sequnce[i - 1]], word_dict[word_sequnce[i + 1]]]
    for W in context:
        skip_grams.append([target, W])
    # (target, context[0]), (target, context[1]), ...(target, context[n])
    
def random_batch(data, size):
    random_inputs = []
    random_labels = []
    random_index = np.random.choice(range(len(data)), size, replace=False)
    for i in random_index:
        random_inputs.append(data[i][0])
        random_labels.append(data[i][1])
    return np.array(random_inputs), np.array(random_labels)

# *******
# 옵션 설정
# *******
# 학습을 반복할 횟수
training_epoch = 300
# 학습률
learning_rate = 0.1
# 한번에 학습할 데이터의 크기
batch_size = 20
# 단어 벡터를 구성할 임베딩 차원의 크기
embedding_size = 2
# x, y 그래프로 표현하기 쉽게 2개의 값만 출력
num_sampled = 15
# word2vec 모델을 학습시키기 위한 nce_loss 함수에서 사용하기 위한 샘플링 크기
# batch_size 보다는 작아야 함
voc_size = len(word_list)
# 총 단어의 갯수

# *****
# 신경망 모델 구성
# *****
# 모델 정의
class Word2Vec(tf.keras.Model):
    def __init__(self, vocab_size, embedding_dim):
        super().__init__()
        self.embeddings = tf.keras.layers.Embedding(vocab_size, embedding_dim)
        self.nce_weights = self.add_weight(
            shape=(vocab_size, embedding_dim), initializer='random_uniform', name='nce_weights')
        self.nce_biases = self.add_weight(
            shape=(vocab_size,), initializer='zeros', name='nce_biases')

    def call(self, inputs):
        return self.embeddings(inputs)

model = Word2Vec(voc_size, embedding_size)
optimizer = tf.keras.optimizers.Adam(learning_rate)

@tf.function
def train_step(inputs, labels):
    with tf.GradientTape() as tape:
        embed = model(inputs)
        loss = tf.reduce_mean(
            tf.nn.nce_loss(
                weights=model.nce_weights,
                biases=model.nce_biases,
                labels=tf.expand_dims(labels, 1),
                inputs=embed,
                num_sampled=num_sampled,
                num_classes=voc_size
            )
        )
    grads = tape.gradient(loss, model.trainable_variables)
    optimizer.apply_gradients(zip(grads, model.trainable_variables))
    return loss

# *****
# 신경망 모델 학습
# ****
# 학습 루프
for step in range(1, training_epoch + 1):
    batch_inputs, batch_labels = random_batch(skip_grams, batch_size)
    loss_val = train_step(batch_inputs, batch_labels)
    if step % 10 == 0:
        print(f"loss at step {step}: {loss_val.numpy()}")
    
    trained_embeddings = model.embeddings.get_weights()[0]
    # with 구문 안에서는 sess.run 대신에 간단히 eval() 함수를 사용할 수 있음

# ******
# 임베딩된 word2vec 결과 확인
# ******

for i, label in enumerate(word_list):
    x, y = trained_embeddings[i]
    plt.scatter(x, y)
    plt.annotate(label, xy=(x, y), xytext=(5, 2),
                 textcoords = 'offset points', ha = 'right', va = 'bottom')

plt.show()