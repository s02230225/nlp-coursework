if __name__ == "__main__":
    from numpy import exp, array, random, dot

    def sigmoid(x):
        return 1 / (1 + exp(-x))

    training_set_inputs = array([[0, 0, 1],
                                 [0, 1, 0],
                                 [0, 1, 1],
                                 [1, 0, 0],
                                 [0, 0, 0]])

    training_set_outputs = array([[0, 1, 0, 1, 1]]).T

    weights = 2 * random.random((4, 1)) - 1 # 4 из-за добавленного смещения

    bias = 1
    # ниже массив, где каждый элемент - список из 4 элементов. 4й из-за смещений
    biased_training_set_inputs = array([[bias, *inp] for inp in training_set_inputs])

    for i in range(100000):
        output = sigmoid(dot(biased_training_set_inputs, weights))
        error = training_set_outputs - output
        gradient = output * (1 - output)
        weights += dot(biased_training_set_inputs.T, error * gradient)
        if i % 25000==0:
            print(weights, '   ', sigmoid(dot(array([bias, 0 ,1, 1]), weights)))

    print("Предсказание")
    print(sigmoid(dot(array([bias, 1, 1, 1]), weights)))
    print(sigmoid(dot(array([bias, 1, 0, 1]), weights)))
    print(sigmoid(dot(array([bias, 1, 1, 0]), weights)))

    '''
    Благодаря смещению, мы получили точные варианты для двух "некорректных векторов"
    [0,0,0] выдает [0.99583628] на 100000 итерациях
    [1,1,1] выдает [0.01069002] на 100000 итерациях
    У остальных данных результаты чуть просели (сравнивал с тем файлом AAAAA, 
    который я прикреплял в работе в классе)
    [1,0,1] выдает [0.0088829]
    [1,1,0] выдает [0.99944447]
    '''
