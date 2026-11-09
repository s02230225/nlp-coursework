if __name__ == "__main__":
    import nltk

    def parse_sentences(text):
        i = 1
        for sentence in nltk.sent_tokenize(text):
            print(i, "  ", sentence)
            i += 1


    punctuation_marks = """\
    Yeah? Wow! Well, it just can't be?! You'll tell me later... \
    The pale gray sky brightened, turned cold, turned blue; \
    the stars blinked with a weak light, then disappeared; \
    the earth was damp, the leaves were misted up, in some places living sounds and voices began to be heard. \
    'I'll be there tomorrow,' he said.
    """
     
    print('-' * 40)
    print('1. Знаки препинания')
    parse_sentences(punctuation_marks) # проверка различных знаков препинания
    print('-' * 40)

    shortening = """\
    'Keys and 15 rub; James gave it to me this morning', I said. \
    Federal State Budgetary Educational Institution of Higher Education \
    "M.V.Lomonosov Moscow State University". \
    The I.I.Ivanov Technical College is located at this address.
    """

    print('-' * 40)
    print('2. Сокращения')
    parse_sentences(shortening) # проверка сокращений
    print('-' * 40)

    direct_speech = """\
    The note had the text: "Hello. I'll be there in the morning." \
    "Hello. How are you?" - He said. \
    "I can't wait for the summer holidays," Petya exclaimed.
    """

    print('-' * 40)
    print('3. Прямая речь')
    parse_sentences(direct_speech) # прямая речь
    print('-' * 40)

    alpha_num = """\
    This model has the name 1BDCS23 in the catalog. \
    R2-D2 is one of my favorite Star Wars characters! \
    My father had an old VAZ21001, which is still gathering dust in the garage.
    """

    print('-' * 40)
    print('4. Цифро-буквенные комбинации')
    parse_sentences(alpha_num) # цифро-буквенные комбинации
    print('-' * 40)

    dates = """\
    My grandparents were born on 02/29/1946 and 12/31/1950. \
    The date was at the bottom of the note: 04.22.2004. \
    04.03.2010 everyone needs to come to the organizational meeting!
    """

    print('-' * 40)
    print('5. Даты')
    parse_sentences(dates) # Даты
    print('-' * 40)

    floating_point = """\
    I bought this apple in Pyaterochka for 20.50 rubles. \
    The number of pi is 3.14159265...
    """

    print('-' * 40)
    print('6. Числа с плавающей запятой')
    parse_sentences(floating_point) # Числа с плавающей запятой
    print('-' * 40)

    mixed = """\
    This st. corp. named after I.I.Ivanov, produces GPT-122U models from 12/14/1977. \
    'Will you go to the cinema with me on 07/10/2010, Vitya?' - I asked him.
    """

    print('-' * 40)
    print('7. Комбинации всего вышеперчисленного')
    parse_sentences(mixed) # Комбинации
    print('-' * 40)
