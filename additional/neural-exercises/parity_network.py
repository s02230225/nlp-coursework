if __name__ == "__main__":
    import numpy as np
    import random

    # Создаем обучающую выборку
    X_train = np.array([list(format(random.randint(0, 63), '06b')) for i in range(10)], dtype=int)
    y_train = (X_train[:, -1])^1  # Четность определяется последним битом числа

    # Создаем нейронную сеть
    class Parity:
        def __init__(self):
            self.weights = np.random.randn(6)  # Инициализируем случайными весами

        def sigmoid(self, x):
            return 1 / (1 + np.exp(-x))

        def forward(self, x):
            return self.sigmoid(np.dot(x, self.weights))

        def train(self, X, y, steps=1000, learning_rate=0.1, tolerance=1e-3):
            prev_loss = np.inf
            for step in range(steps):
                prediction = self.forward(X)
                self.weights -= np.dot(learning_rate * (prediction - y) * prediction * (1 - prediction), X)

                loss = np.mean((y - [self.forward(x) for x in X]) ** 2)

                # Проверяем условие сходимости
                if abs(prev_loss - loss) < tolerance:
                    print(">>> Обучение завершено на итерации", step)
                    break

                prev_loss = loss



    # Создаем и обучаем модель
    model = Parity()
    model.train(X_train, y_train, steps=10000, learning_rate=0.1)

    # Тестируем модель
    test_data = np.array([list(format(random.randint(0, 63), '06b')) for i in range(5)], dtype=int)


    for x in test_data:
        x = np.array(x, dtype=int)  # Преобразуем вектор в нужный формат
        prediction = model.forward(x)
        #print(model.weights)
        print(f"Input: {x}, Prediction: {prediction:.2f}, Even: {prediction >= 0.5}")
