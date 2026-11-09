if __name__ == "__main__":
    from numpy import exp, array, random, dot
    import numpy as np
    X_train = array([   [ 0, 0, 0, 0, 0, 0],
                        [ 1, 1, 1, 1, 1, 1],
                        [0, 0, 0, 0, 1, 0],
                        [0, 0, 0, 0, 1, 1],
                        [0, 0, 1, 0, 0, 0],
                        [0, 0, 1, 0, 0, 1],
                        [1, 1, 1, 0, 0, 0],
                        [1, 1, 0, 1, 0, 1],
                        [1, 1, 1, 1, 0, 0],
                        [1, 1, 0, 0, 0, 1],
                        [1, 1, 0, 0, 0, 0],
                    ])
    y_train = array([[0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]]).T
    w_out = np.full((6, 1), 0.5)
    for iteration in range(100000):
        output = 1 / (1 + exp(-(dot(X_train, w_out))))
        w_out += dot(X_train.T, (y_train - output) * output * (1 - output))
        if iteration % 25000 == 0:
            print (w_out, '   ', 1 / (1 + exp(-(dot(array([1, 1, 1, 1, 1, 1]), w_out)))))

    def sigmoid(x):
        return 1 / (1 + exp(-x))

    print('Некоторые тесты для однослойной NN')
    print ( 1 / (1 + exp(-(dot(array([ 0, 0, 0, 0, 1, 0]), w_out)))))
    print ( 1 / (1 + exp(-(dot(array([ 1, 1, 1, 1, 0, 1]), w_out)))))
    print ( 1 / (1 + exp(-(dot(array([ 1, 1, 0, 0, 1, 0]), w_out)))))
    print ( 1 / (1 + exp(-(dot(array([ 1, 1, 0, 0, 1, 1]), w_out)))))
    print ( 1 / (1 + exp(-(dot(array([ 1, 0, 1, 0, 1, 0]), w_out)))))
    print ( 1 / (1 + exp(-(dot(array([ 0, 1, 1, 1, 0, 1]), w_out)))))


    '''
    Тут реализовал двуслойную линейную NN с сигмоидами в качестве функций активации
    '''
    w_h = np.full((6, 11), 0.5) # задаем матрицу весов скрытого уровня размера 6 на 6
    w_out = np.full((11, 1), 0.5)
    for iteration in range(100000):
        # сначала forward propagation (прямое распространение)
        X_1 = dot(X_train, w_h) # первый скрытый слой
        X_2 = sigmoid(X_1) # первая ф-ция активации
        X_3 = dot(X_2, w_out) # выходной слой
        X_4 = sigmoid(X_3) # вторая ф-ция активации
    
        w_out_grad = dot(X_2.T, (y_train - X_4)) # считаем через backprop обновление для весов внешнего слоя
        # для скрытого
        w_h_grad = dot(X_train.T, dot(X_2, (1 - X_2)) * dot((y_train - sigmoid(X_3)), w_out.T))
    
        w_out += w_out_grad
        w_h += w_h_grad


    print ('результат на обучающем наборе для двуслойной NN')
    print (X_4)

    new = [0, 0, 0, 0, 1, 1]
    print ( 'предсказание для  ', new)
    print (sigmoid(dot(sigmoid(dot(new, w_h)), w_out)))
    new = [0, 0, 0, 0, 0, 1]
    print ( 'предсказание для  ', new)
    print (sigmoid(dot(sigmoid(dot(new, w_h)), w_out)))

    '''
    Тут реализовал разбиение на два нейрона (два параллельных полносвязных слоя)
    '''

    w_1 = np.full((3, 1), 0.5)
    w_2 = np.full((3, 1), 0.5)
    for iteration in range(100000):
        # создаем два нейрона размера в 3 элемента
        output1 = 1 / (1 + exp(-(dot(X_train[:, 0:3], w_1))))
        output2 = 1 / (1 + exp(-(dot(X_train[:, 3:], w_2))))
    
        # обновляем веса
        w_1 += dot(X_train[:, 0:3].T, (y_train - output1) * output1 * (1 - output1))
        w_2 += dot(X_train[:, 3:].T, (y_train - output2) * output2 * (1 - output2))
    print('Предсказание на тестовой выборке для двух нейронов')
    print((output1 + output2) / 2) # результат усредняется
