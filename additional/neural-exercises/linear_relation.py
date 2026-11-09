if __name__ == "__main__":
    import numpy as np
    import matplotlib.pyplot as plt
    from tensorflow import keras
    from tensorflow.keras.layers import Dense
    print ('Какое-то время оно думает - надо подождать. Потом построится график - его надо посмотреть и закрыть')

    # обучающее множество - список входов и соответствующих выходов
    c = np.array([-3, -1, 0, 2,  4, 5, 6])   # вход
    # c = np.array([-3, -1, 0])   # вход
    f = np.array([11, 7, 5, 1, -3, -5,  -7]) # выход   y=-2x+5
    f = np.array([-30000, -10000, 0, 20000, 40000, 50000,  60000]) # выход   y=-2x+5
    # f = np.array([11, 7, 5]) # выход   y=-2x+5

    model = keras.Sequential()  # слои вид сети - последовательные, друг за другом 
    model.add(Dense(units=1, input_shape=(1,), activation='linear'))

    # Dense - конструктор, формирование полносвязного слоя
    # add - добавление слоя с заданынми параметрами
    # units - количество нейронов
    # input_shape=(1,) - один вход
    # activation - функция активации
    # Конструктор Dense формирует полносвязный слой
    #    (все входы будут связаны со всеми нейронами данного слоя.
    # Связи - веса и дополнительно для каждого нейрона добавляется смещение – bias. 
    print ('модель построена')
    model.summary()
    model.compile(loss='mean_squared_error', optimizer=keras.optimizers.Adam(0.1))
    # выбираем минимум среднего квадрата ошибки и оптимизацию по Adam
    log = model.fit(c, f, epochs=200, verbose=False)
    # fit - метод для обучения (выход, выход, к-во эпох, печатать ли текущую информацию

    plt.plot(log.history['loss'])
    plt.grid(True)
    plt.show()
    # график  показывает, как меняется loss - изменить количество эпох


    print('f(2)=',model.predict(np.array([2])))  # печать предсказания модели для 2
    print('f(-10)=',model.predict(np.array([-10])))
    print('f(10)=',model.predict(np.array([10])))
    print('веса  ', model.get_weights())  # при хорошей модели веса равны коэффициентам

    # print('f(10000)=',model.predict(np.array([10000])))
    # print('f(10000)=',model.predict(np.array([-10000])))
    # print('f(0.0001)=',model.predict(np.array([0.0001])))
    # print('f(0.0001)=',model.predict(np.array([-0.0001])))
