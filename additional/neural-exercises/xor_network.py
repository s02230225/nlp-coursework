if __name__ == "__main__":
    import numpy as np

    X = np.array([[0, 0],
                  [0, 1],
                  [1, 0],
                  [1, 1]])

    y = np.array([[0], [1], [1], [0]])

    # Фиксируем рандом, чтобы были одинаковые результаты для удобства проверки
    #np.random.seed(0)

    class XOR:
        def __init__(self):
            self.input_weights = np.random.rand(X.shape[1], X.shape[0])
            self.hidden_weights = np.random.rand(X.shape[0], y.shape[1])
            self.input_bias = np.random.rand(1, X.shape[0])
            self.output_bias = np.random.rand(1, y.shape[1])


        def sigmoid(self, x):
            return 1 / (1 + np.exp(-x))


        def sigmoid_derivative(self, x):
            return x * (1 - x)

        def forward(self, x):
            hidden_input = np.dot(X, self.input_weights) + self.input_bias
            hidden_output = self.sigmoid(hidden_input)

            output = np.dot(hidden_output, self.hidden_weights) + self.output_bias
            predicted_output = self.sigmoid(output)

            return predicted_output, hidden_output

        def train(self, X, y, steps = 10000, learning_rate = 0.1):

            for step in range(steps):
                # Feed-Forward
                predicted_output, hidden_output = self.forward(X)

                # Используем градиентный спуск для обратного прохода, вычисляем градиенты для двух слоев
                error = y - predicted_output
                d_output = error * self.sigmoid_derivative(predicted_output)
                error_hidden = np.dot(d_output, self.hidden_weights.T)
                d_hidden = error_hidden * self.sigmoid_derivative(hidden_output)

                # Корректируем веса и смещения в соответствии с формулой градиентного спуска
                self.hidden_weights += learning_rate * np.dot(hidden_output.T, d_output)
                self.input_weights += learning_rate * np.dot(X.T, d_hidden)
                self.output_bias += learning_rate * np.sum(d_output, axis=0)
                self.input_bias += learning_rate * np.sum(d_hidden, axis=0)


    # Создаем объект класса
    model = XOR()
    # Обучаем модель
    model.train(X, y, steps = 10000, learning_rate = 0.1)

    predicted_output = (model.forward(X)[0])

    # Вывод результатов
    for i, out in enumerate(predicted_output):
        print(f"XOR for {X[i]} is {1 if predicted_output[i] > 0.5 else 0}")
