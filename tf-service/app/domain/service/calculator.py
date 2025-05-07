import tensorflow as tf
from app.domain.model.calc_schema import CalcSchema
class Calculator:

    @tf.function
    def plus(self, num1, num2): return tf.add(num1, num2)
    
    @tf.function
    def minus(self, num1, num2): return tf.subtract(num1, num2)
    
    @tf.function
    def multiple(self, num1, num2): return tf.multiply(num1, num2)
    
    @tf.function
    def div(self, num1, num2): return tf.divide(num1, num2)





    def sample(self):
        print("👩🏻😎👩🏻‍🦰 1. 여기 까지 실행 되나요?")
        mnist = tf.keras.datasets.mnist
        print("👩🏻😎👩🏻‍🦰 2. 여기 까지 실행 되나요?")
        (x_train, y_train),(x_test, y_test) = mnist.load_data()
        print("👩🏻😎👩🏻‍🦰 3. 여기 까지 실행 되나요?")
        x_train, x_test = x_train / 255.0, x_test / 255.0
        print("👩🏻😎👩🏻‍🦰 4. 여기 까지 실행 되나요?")
        model = tf.keras.models.Sequential([
        tf.keras.layers.Flatten(input_shape=(28, 28)),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(10, activation='softmax')
        ])
        print("👩🏻😎👩🏻‍🦰 5. 여기 까지 실행 되나요?")
        model.compile(optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy'])
        print("👩🏻😎👩🏻‍🦰 6. 여기 까지 실행 되나요?")
        model.fit(x_train, y_train, epochs=5)
        print("👩🏻😎👩🏻‍🦰 7. 여기 까지 실행 되나요?")
        model.evaluate(x_test, y_test)
        print("👩🏻😎👩🏻‍🦰 8. 실행 끝끝")

    
    
