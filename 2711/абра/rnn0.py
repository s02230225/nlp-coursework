if __name__ == "__main__":
    # рекурентная сеть
    # предсказание следующей буквы по трем предыдущим
    import os
    os.environ['TF_CPP_MIN_LOG_LEVEL']='2'

    import numpy as np
    import re
    from tensorflow.keras.layers import Dense, SimpleRNN, Input
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.optimizers import Adam
    from tensorflow.keras.preprocessing.text import Tokenizer

    with open ('sl3.txt', 'r', encoding='utf-8') as f: # файл
               text=f.read()
               text=text.replace('\ufeff', ' ')# убираем первый невидимый символ

    # парсим текст как последовательность символов
    num_characters = 6 # 4 бувы и пробел, перевод строки
    tokenizer = Tokenizer(num_words=num_characters, char_level=True)
    tokenizer.fit_on_texts(text)
    print(tokenizer.word_index) # сформирован словарь

    inp_chars = 3 # количество символов для формирования предсказания
    data = tokenizer.texts_to_matrix(text)
    n = data.shape[0]-inp_chars
    X = np.array([data[i:i+inp_chars, :] for i in range(n)])
    Y = data[inp_chars:] #предсказание следующего символа

    model = Sequential()
    model.add(Input((inp_chars, num_characters))) 
    model.add(SimpleRNN(100, activation='tanh')) # количество нейронов
    model.add(Dense(num_characters, activation='softmax'))
    model.summary()

    model.compile(loss='categorical_crossentropy', metrics=['accuracy'], optimizer='adam')
    history = model.fit(X, Y, batch_size=16, epochs=2,  verbose=False )

    def buildPhrase(inp_str, str_len = 20):
    # прогноз очередного символа и добавления его в конец начальной строки (длина str_len)  
      for i in range(str_len):
        x = []
        for j in range(i, i+inp_chars):
          x.append(tokenizer.texts_to_matrix(inp_str[j])) # преобразуем символы в One-Hot-encoding (OHE)
     
        x = np.array(x)
        inp = x.reshape(1, inp_chars, num_characters)
     
        pred = model.predict( inp, verbose=False ) # предсказываем OHE четвертого символа
        d = tokenizer.index_word[pred.argmax(axis=1)[0]] # получаем ответ в символьном представлении
     
        inp_str += d # дописываем строку
     
      return inp_str
    print ('************   ********  **')
    for mm in ("ма ", " но", "ном", "ман", "ама", " a ", " м "," ма", "а м"):
        res = buildPhrase(mm)
        print(res)

