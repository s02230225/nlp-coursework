if __name__ == "__main__":
    from numpy import exp, array, random, dot, ones

    # Обучающая
    X_train = array([[0, 1, 0, 1], [1, 0, 1, 0], [0, 0, 1, 1], [1, 1, 0, 0],
                     [0, 1, 1, 0], [1, 0, 0, 1], [0, 0, 0, 0], [1, 1, 1, 1]])

    # Тестовая
    X_test = array([[0, 0, 0, 1], [0, 0, 1, 0], [0, 1, 0, 0], [0, 1, 1, 1],
                    [1, 0, 0, 0], [1, 0, 1, 1], [1, 1, 0, 1], [1, 1, 1, 0]])

    # XOR 2-го и 4-го элементов
    y_train = array([[X_train[i][1] ^ X_train[i][3] for i in range(8)]]).T
    y_test = array([[X_test[i][1] ^ X_test[i][3] for i in range(8)]]).T

    random.seed(1)

    def main(L):
        # Добавляем смещение
        X_train_bias = ones((8, 5))
        X_train_bias[:, :4] = X_train
        
        w1 = 2 * random.random((5, 4)) - 1
        w2 = 2 * random.random((5, 1)) - 1
        
        print("Обучение, итераций:", L)
        for i in range(L):
            l1 = 1 / (1 + exp(-(dot(X_train_bias, w1))))
            
            l1_bias = ones((8, 5))
            l1_bias[:, :4] = l1
            
            l2 = 1 / (1 + exp(-(dot(l1_bias, w2))))
            
            l2_error = y_train - l2
            l2_delta = l2_error * l2 * (1 - l2)
            l1_error = l2_delta.dot(w2.T)
            l1_delta = l1_error[:, :4] * l1 * (1 - l1)
            
            w2 += l1_bias.T.dot(l2_delta)
            w1 += X_train_bias.T.dot(l1_delta)
        
        print("Тест:")
        total_error = 0
        for i in range(8):
            test_input = ones(5)
            test_input[:4] = X_test[i]
            
            l1 = 1 / (1 + exp(-(dot(test_input, w1))))
            
            l1_bias = ones(5)
            l1_bias[:4] = l1
            
            l2 = 1 / (1 + exp(-(dot(l1_bias, w2))))
            
            predicted = l2[0]
            expected = y_test[i][0]
            error = abs(predicted - expected)
            total_error += error
            print("Цель, ответ, ошибка")
            print(f"{expected}, {predicted:.5f}, {error:.5f}")

    # Тестим
    main(250)
    main(1000)
    main(4000)
    main(16000)
    main(64000)
