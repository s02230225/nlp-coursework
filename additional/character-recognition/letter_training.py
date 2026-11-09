if __name__ == "__main__":
    from PIL import Image
    import numpy as np
    import pandas as pd
    import tensorflow as tf
    import os

    path = os.getcwd()  # получаем расположение файла
    '''
    labels = ['C', 'O', 'Q'] # распознаваемые символы
    labels_for_df = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                     1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                     2, 2, 2, 2, 2, 2, 2, 2, 2, 2] # обозначил как числа для выходов (не распознаются символы)
    column_names = ['pix'+str(i) for i in range(1, 785)] # для датафрейма обозначение

    # здесь создается датафрейм, в котором будут храниться значения пикселей в режиме L
    df1 = pd.DataFrame(columns=column_names)
    for l in labels:
        for i in range(1, 11):
            image = Image.open('my_dataset/' + l + str(i) + '.png') # изображения в датасете раньше переводились в L-формат
            # new_image = image.convert('L')
            # new_image.save('my_dataset/' + l + str(i) + '.png')
            numpydata = np.asarray(image).flatten()
            df1.loc[l+str(i)] = numpydata  # добавляем новую строку в датафрейм

    df1.insert(0, "value", labels_for_df, allow_duplicates=True) # вставляем столбец для нашей буквы

    data = np.array(df1)
    np.random.shuffle(data) # перемешиваем для разделения на обучающие и тестировочные данные
    # действуем в соотношении 80 на 20

    training_data = data[:24].T  # 24, т.к. всего 30 изображений в датасете
    Y_train = training_data[0]  # взяли первую строку - результаты
    X_train = training_data[1:].astype('float32').T  # транспонируем и приводим к float32, чтобы не было ошибки при обучении
    X_train = X_train / 255  # приводим к [0, 1]

    test_data = data[24:].T
    Y_test = test_data[0]
    X_test = test_data[1:].astype('float32').T
    X_test = X_test / 255

    network = tf.keras.models.Sequential()  # создание нейронки с одним слоем
    network.add(tf.keras.layers.Dense(100, activation='relu'))
    network.add(tf.keras.layers.Dense(3, activation='softmax'))  # на выходе три элемента: C, O или Q

    network.compile(loss='categorical_crossentropy', 
                    optimizer='adam', 
                    metrics=['accuracy'])

    Y_train_cat = tf.keras.utils.to_categorical(Y_train, 3)  # приведение к вектору из 0 и 1 (3 - размерность)
    Y_test_cat = tf.keras.utils.to_categorical(Y_test, 3)

    network.fit(X_train, Y_train_cat, epochs=15, verbose=False)

    loss, accuracy = network.evaluate(X_test, Y_test_cat)
    print(loss, accuracy)


    network.save(path + '/checkpoints/check3') # самая лучшая модель
    '''
    network = tf.keras.models.load_model(path + '/checkpoints/check5')

    index = 1
    while os.path.isfile(f"test_letters/test{index}.png"):
        img = Image.open(f"test_letters/test{index}.png")
        new_image = img.convert('L')  # конвертируем в нужный формат
        numpydata = np.asarray(new_image)
        numpydata.shape = (1, 784)  # такой shape из-за транспонирования X_train при обучении
        # ну и для совпадения количества sample'ов у X и Y
        prediction = network.predict(numpydata)
        match np.argmax(prediction):  # выбираем наиболее вероятную версию
            case 0:
                result = 'C'
            case 1:
                result = 'O'
            case 2:
                result = 'Q'
            case _:
                result = "Something's wrong"
        print(f"The letter is probably {result}")
        index += 1

    # идеально при qccqoqoc
