if __name__ == "__main__":
    from numpy import exp, array, random, dot

    def sigmoid(x):
        return 1 / (1 + exp(-x))

    def mean_squared_error(tru, pred): # функция потерь
        return ((tru - pred) ** 2).mean()

    training_set_inputs = array([[0, 0, 0],
                                 [0, 0, 1], 
                                 [0, 1, 0], 
                                 [0, 1, 1],
                                 [1, 0, 0],
                                 [1, 0, 1],
                                 [1, 1, 1]]) # входные данные

    # напомним, что наша функция - not(x3), отсюда выходные данные
    training_set_outputs = array([[1, 0, 1, 0, 1, 0, 0]]).T

    # задаем веса случайным образом
    weights = 2 * random.random((3, 1)) - 1

    max_iter = 100000 # вводим количество итераций
    limit = 1e-8 # порог по точности (разность между текущей ошибкой и предыдущей)
    previous = 10000 # предыдущая ошибка, установим большое значение для первой итерации
    how_often = int(input("Введите как часто по итерациям выводить значения: "))

    for i in range(max_iter + 1):
        output = sigmoid(dot(training_set_inputs, weights)) # наш результат
        error = training_set_outputs - output # величина ошибки
        gradient = output * (1 - output) # градиент сигмоиды
        weights += dot(training_set_inputs.T, error * gradient) # обновленные веса

        current = mean_squared_error(training_set_outputs, output) # вычисление средне квадратичного отклонения
        if abs(current - previous) < limit:
            print(f"Достигнут предел на {i} итерации")
            break
    
        if i % how_often == 0:
            print(f"Итерация: {i}")
            print(f"Ошибка: {current}")
            print(f"Предсказание: {sigmoid(dot(array([1, 1, 0]), weights))}")

        previous = current

    print("Предсказание для тестового набора с достигнутой точностью")
    print(sigmoid(dot(array([1, 1, 0]), weights)))

    '''
    Очевидно, надо анализировать разность между ожидаемым результатом и предсказанием.
    Для работы будем использовать метрику среднеквадратичной ошибки по которой будем определять,
    как сходимся к результату.
    Также анализируем разности между предыдущей и текущей ошибкой. Если модуль разности 
    будет меньше некой задаваемой константы limit, то тогда производим остановку. 
    Если что-то идет не так, то завершаем при достижении max_iter числа итераций.

    В решении используются MeanSquaredError (функция потерь), а также происходит 
    корректировка весов благодаря вычислению ошибки и производной функции активации (Gradient)
    Если уменьшать порядок limit, то увеличим точность предсказания (но для этого надо увеличивать
    max_iter еще, если порядок слишком велик)
    '''
