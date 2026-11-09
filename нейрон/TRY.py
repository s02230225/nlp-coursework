if __name__ == "__main__":
    from numpy import exp, array, random, dot

    # Простой XOR для проверки
    X_simple = array([[0, 0], [0, 1], [1, 0], [1, 1]])
    y_simple = array([[0, 1, 1, 0]]).T

    random.seed(42)
    w1 = 2 * random.random((2, 2)) - 1
    w2 = 2 * random.random((2, 1)) - 1

    learning_rate = 1.0  # Оригинальная скорость

    for i in range(10000):
        l1 = 1 / (1 + exp(-(dot(X_simple, w1))))
        l2 = 1 / (1 + exp(-(dot(l1, w2))))
        
        l2_error = y_simple - l2
        l2_delta = l2_error * l2 * (1 - l2)
        l1_delta = l2_delta.dot(w2.T) * l1 * (1 - l1)
        
        w2 += learning_rate * l1.T.dot(l2_delta)
        w1 += learning_rate * X_simple.T.dot(l1_delta)

    print("Проверка простого XOR:")
    for i in range(4):
        l1 = 1 / (1 + exp(-(dot(X_simple[i], w1))))
        l2 = 1 / (1 + exp(-(dot(l1, w2))))
        print(f"{X_simple[i]} → {l2[0]:.3f} (ожидается: {y_simple[i][0]})")
