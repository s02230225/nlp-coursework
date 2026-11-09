if __name__ == "__main__":
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize 

    # При повторном запуске программы две нижеследующие строчки надо закомментировать.
    # Они нужны чтобы скачать список стоп-слов. После скачивания эти строки можно удалить. 
    import nltk
    nltk.download('stopwords')


    text = "Ах, как он любит ее, ах как сильно! Как он  хочет, чтобы она любила его."
    stop_words = stopwords.words('russian')# заносим стоп-слова в переменную
    set_stop = set(stop_words) # создаем множество
    print('стоп-слова__________________')
    print(stop_words)

    word_tokens = word_tokenize(text) #токенизация
    
    filtered_sentence = [] # сюда будем отбирать слова очищенного текста
  
    for w in word_tokens: 
        if w not in set_stop: 
            filtered_sentence.append(w) 
    print('введенные токены текста___________')
    print(word_tokens)
    print('очищенный текст______________')
    print(filtered_sentence)
    #теперь расширим список стоп-слов и проделаем то же самое
    stop_words.extend(['!', ',', '.', 'ах', 'Ах', 'Как'])
    set_stop = set(stop_words)
    filtered_sentence = [] # сюда будем отбирать слова очищенного текста
  
    for w in word_tokens: 
        if w not in set_stop: 
            filtered_sentence.append(w)
    print('очищенный текст______________')
    print(filtered_sentence)
