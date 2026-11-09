if __name__ == "__main__":
    # распознавание цифр
    from tensorflow.keras.datasets import mnist
    import numpy as np
    import matplotlib.pyplot as plt
    from tensorflow import keras
    from tensorflow.keras.layers import Dense,  Flatten, Dropout, Conv2D, MaxPooling2D
    (x_train, y_train), (x_test, y_test) = mnist.load_data()  # загрузка выборки

    model = keras.Sequential([
        Conv2D(32, (3,3), padding='same', activation='relu', input_shape=(28, 28, 1)),
        MaxPooling2D((2, 2), strides=2),
        Conv2D(64, (3,3), padding='same', activation='relu'),
        MaxPooling2D((2, 2), strides=2),
        Flatten(),
        Dense(128, activation='relu'),
        Dense(10,  activation='softmax')
    ])
    print(model.summary())     # вывод структуры НС в консоль
    x_train = x_train / 255 # нормализация
    x_test = x_test / 255
    y_train_cat = keras.utils.to_categorical(y_train, 10) # приведение к вектору из 0 и 1 (10 - размерность)
    y_test_cat = keras.utils.to_categorical(y_test, 10)
    #для сверточной НС множества x_tarin и x_test нужно дополнительно подготовить.
    #на входе такой сети ожидается четырехмерный теyзор,
    # нужно  добавить еще одно измерение  для цветовой компоненты
    x_train = np.expand_dims(x_train, axis=3)
    x_test = np.expand_dims(x_test, axis=3)
    print( x_train.shape )
    model.compile(optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy'])
    hit=model.fit(x_train, y_train_cat, batch_size=32, epochs=5, validation_split=0.2,  verbose=False) #обучение
    #print('*******   loss и accuracy  на тестовом наборе   ***********')
    #model.evaluate(x_test, y_test_cat) # Метод evaluate прогоняет все тестовое множество и вычисляет значение критерия качества и метрики
    #print('*********    *****************')
    print ('проверка правильности некоторой цифры')
    n = 5  # изображение - это номер в наборе данных
    x = np.expand_dims(x_test[n], axis=0)
    # выведем рукописную цифру с заданным номером, полученное сетью значение - в виде числа и в виде вектора
    res = model.predict(x)
    print ('печать выходного вектора для', y_test[n])
    print( res  )
    print 
    print( np.argmax(res) , '  - такая цифра должна быть на рисунке. Верно?')
    plt.imshow(x_test[n], cmap=plt.cm.binary)
    plt.show()
    # выделение неверных результатов
    pred = model.predict(x_test)
    pred = np.argmax(pred, axis=1) # массив предсказанных результатов (на тестовом наборе)

    print('вывод некоторых ошибочных некоторых результатов')
    print('смотрим, правильные ли ошибочные картинки, хорошо ли нарисованы')

    er=0
    for i in range(10000): # проверяем тестовой набор
         if pred[i]!=y_test[i]:
             er=er+1 # считаем ошибки
             if er>10 and er<16: # смотрим 5 картинок неверно определенных сетью
                 print("Значение сети: ", y_test[i], ' предсказано   ', pred[i] )
                 plt.imshow(x_test[i], cmap=plt.cm.binary)
                 plt.show()
            
    print ('k-vo  error ', er)

