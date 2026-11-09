if __name__ == "__main__":
    import pymorphy3 as pm # для морфологического анализа
    import nltk # для токенизации
    from nltk.corpus import stopwords # стандартный список стоп-слов
    from nltk.stem import SnowballStemmer # для получения основ слов
    from collections import Counter # для удобного подсчёта числа лемм и словоформ
    import matplotlib.pyplot as plt # для построения графиков
    import sys # для корректного завершения программы
    import re # для регулярных выражений

    morph = pm.MorphAnalyzer()
        
    # определение рода
    def gender_tag(gender):
        match gender:
            case 'femn':
                return 'женский'
            case 'masc':
                return 'мужской'
            case 'neut':
                return 'средний'
            case _:
                return 'N/A'

    # определение падежа
    def case_tag(case): 
        match case:
            case 'nomn':
                return 'именительный'
            case 'gent':
                return 'родительный'
            case 'datv':
                return 'дательный'
            case 'accs':
                return 'винительный'
            case 'ablt':
                return 'творительный'
            case 'loct':
                return 'предложный'    
            case _:
                return 'N/A'

    # определение числа
    def number_tag(number):
        match number:
            case 'sing':
                return 'единственное'
            case 'plur':
                return 'множественное'
            case _:
                return 'N/A'

    # анализатор для существительных
    def noun_analyzer(word):
        begin = 'часть речи: cуществительное'
        permanent_tags = ''
        non_permanent_tags = ''
        if word.tag.animacy:
            match word.tag.animacy:
                case 'anim':
                    permanent_tags += 'одушевленное'
                case 'inan':
                    permanent_tags += 'неодушевленное'
                case _:
                    permanent_tags += 'N/A (одушевлённость)'
            permanent_tags += ', '
        if word.tag.gender:
            permanent_tags += gender_tag(word.tag.gender)
            permanent_tags += ' род'
        if word.tag.case:
            non_permanent_tags += case_tag(word.tag.case)
            non_permanent_tags += ' падеж, '
        if word.tag.number:
            non_permanent_tags += number_tag(word.tag.number)
            non_permanent_tags += ' число'
        return f'{begin}, \nначальная форма: {word.normal_form}, \nпостоянные признаки: {permanent_tags}, \nнепостоянные признаки: {non_permanent_tags}'

    # анализатор для прилагательных (для полных, кратких, сравнительных форм)
    def adj_analyzer(word): 
        begin = 'часть речи: прилагательное'
        non_permanent_tags = ''
        match word.tag.POS:
            case 'ADJF':
                non_permanent_tags += 'полная'
            case 'ADJS':
                non_permanent_tags += 'краткая'
            case 'COMP':
                non_permanent_tags += 'сравнительная'
        non_permanent_tags += ' форма, '
        if word.tag.number:
            non_permanent_tags += number_tag(word.tag.number)
            non_permanent_tags += ' число, '
        if word.tag.case:
            non_permanent_tags += case_tag(word.tag.case)
            non_permanent_tags += ' падеж, '
        if word.tag.gender:
            non_permanent_tags += gender_tag(word.tag.gender)
            non_permanent_tags += ' род'
        return f'{begin}, \nначальная форма: {word.normal_form}, \nнепостоянные признаки: {non_permanent_tags}'

    # анализатор для глаголов
    def verb_analyzer(word):
        begin = 'часть речи: глагол'
        permanent_tags = ''
        non_permanent_tags = ''
        if word.tag.POS == "INFN": 
            non_permanent_tags += 'инфинитив'
            return f'{begin}, непостоянные признаки: {non_permanent_tags}'
        if word.tag.aspect:
            match word.tag.aspect:
                case 'perf':
                    permanent_tags +='совершенный'
                case 'impf':
                    permanent_tags += 'несовершенный'
                case _:
                    permanent_tags += 'N/A'
            permanent_tags += ' вид, '
        if word.tag.transitivity:
            match word.tag.transitivity:
                case "tran":
                    permanent_tags += 'переходный'
                case "intr":
                    permanent_tags += 'непереходный'
                case _: 
                    permanent_tags += 'N/A (переходность)'
        if word.tag.mood:
            match word.tag.mood:
                case 'indc':
                    non_permanent_tags += 'изъявительное наклонение, '
                case 'impr': 
                    non_permanent_tags += 'повелительное наклонение, '
                case _:
                    non_permanent_tags += 'N/A (наклонение), '
        if word.tag.tense:
            match word.tag.tense:
                case 'pres':
                    non_permanent_tags += 'настоящее время, '
                case 'past':
                    non_permanent_tags += 'прошедшее время, '
                case 'futr':
                    non_permanent_tags += 'будущее время, '
                case _:
                    non_permanent_tags += 'N/A (время), '
        if word.tag.number:
            non_permanent_tags += number_tag(word.tag.number)
            non_permanent_tags += ' число, '
        if word.tag.person:
            match word.tag.person:
                case '1per':
                    non_permanent_tags += '1'
                case '2per':
                    non_permanent_tags += '2'
                case '3per':
                    non_permanent_tags += '3'
                case _:
                    non_permanent_tags += 'N/A'
            non_permanent_tags += ' лицо'
        return f'{begin}, \nпостоянные признаки: {permanent_tags}, \nнепостоянные признаки: {non_permanent_tags}'


    # морфологический анализатор
    def morph_analyzer(word):
        p = morph.parse(word)[0]
        if p.tag.POS == 'VERB' or p.tag.POS == 'INFN': # для глаголов и инфинитивов
            return verb_analyzer(p)
        if p.tag.POS == 'NOUN': # для существительных
            return noun_analyzer(p)
        if p.tag.POS == 'ADJF' or p.tag.POS == 'ADJS' or p.tag.POS == 'COMP': # для полных, кратких, сравнительных форм
            return adj_analyzer(p)
        return 'неанализируемая часть речи'

    # подсчёт числа лемм
    def lemmas_counter(text):    
        lemmas = [morph.parse(w)[0].normal_form for w in text]
        return Counter(lemmas)

    # удаление знаков пунктуации и цифр
    def no_punctuation_and_digit(text): 
        for symb in punctuation:
            text = text.replace(symb, '')
        text = ''.join([i for i in text if not i.isdigit()])
        return text

    # название частей речи на русском
    def ru_name_of_part_of_speech(eng_name):
        if eng_name == 'NOUN':
            return 'существительные'
        elif eng_name == 'ADJF' or eng_name == 'ADJS' or eng_name == 'COMP':
            return 'прилагательные'
        elif eng_name == 'VERB' or eng_name == 'INFN':
            return 'глаголы'
        elif eng_name == 'PRTF' or eng_name == 'PRTS':
            return 'причастия'
        elif eng_name == 'GRND':
            return 'деепричастия'
        elif eng_name == 'NUMR':
            return 'числительные'
        elif eng_name == 'ADVB':
            return 'наречия'    
        elif eng_name == 'NPRO':
            return 'местоимения'
        elif eng_name == 'PRED':
            return 'предикативы'
        elif eng_name == 'PREP':
            return 'предлоги'
        elif eng_name == 'CONJ':
            return 'союзы'
        elif eng_name == 'PRCL':
            return 'частицы'
        elif eng_name == 'INTJ':
            return 'междометия'
        else:
            return 'часть речи не определена'

    # проверка, есть ли в слове хотя бы один кириллический символ  
    def is_russian_word(word):
        return bool(re.search(r'[а-яА-ЯёЁ]', word))

    # подсчет количества гласных в слове
    def count_vowels(word):
        vowels = 'аеёиоуыэюяАЕЁИОУЫЭЮЯ'
        return sum(1 for letter in word if letter in vowels)

    print('0. Определение списка стоп-слов')
    print('0 - обработка текста без списка стоп-слов')
    print('1 - обработка текста со списком стоп-слов nltk')
    print('2 - обработка текста с расширенным списком стоп-слов nltk (по умолчанию)')
    answer = input('Ваш выбор: ')
    match answer:
        case '0':
            set_stop = set()
        case '1':
            stop_words = stopwords.words('russian') # заносение стоп-слов в переменную
            set_stop = set(stop_words)
        case _:
            stop_words = stopwords.words("russian") # пополняем список стоп-слов, потому что он недостаточно полный
            stop_words.extend(["''", "в", "г", "по", "г", "из", "к", "с", "от", "мной", "мною", "тебе", "тобой", "тобою", "нему", \
                        "ею", "нею", "ими", "ним", "весьма", "как-то", "как-либо", "как-нибудь",\
                        "какое", "какие", "какого", "каких", "какому", "каким", "какою", "какими", "каком",\
                        "такое", "такая", "такие", "такого", "таких", "таким", "такому", "такую", "такими",\
                        "где-нибудь", "где-либо", "где-то", "кое-как", "кое-где", "кое-кто", \
                        "кое-что", "кое-куда", "куда-нибудь", "куда-либо", "куда-то", "кто", "вы", "вам", "вами",\
                        "вас", "этот", "это", "эти", "эта", "эту", "ту", "та", "тот", "те", \
                        "около", "ибо", "среди", "обо", "напротив", "зато", "хотя", "ко", "со"])
            set_stop = set(stop_words)

    punctuation = '.,!?:;(\\)[]«»-_@#%$"`}{—*–”“/\'&№' # знаки пунктуации

    try:
        file_name = input("Введите полный путь обрабатываемого файла: ") # открываем файл и работаем с ним
        with open(file_name, mode='r', encoding='utf-8') as f:
            print(f'Файл {file_name} успешно найден')
            all_text = f.read()
            word_tokens = nltk.word_tokenize(no_punctuation_and_digit(all_text.lower().replace('ё', 'е')), language='russian') 
            text = [w for w in word_tokens if w not in set_stop and is_russian_word(w)] # удаление стоп-слов и иностранных слов
    except OSError: # на случай если произошла ошибка 
        sys.exit("Файл не найден.")

    outfile_name = input("Введите название файла, в который выводится вся информация: ")
    outfile = 'results/' + outfile_name + '.txt'
    try:
        with open(outfile, mode='a', encoding='utf-8') as f:
            print(f'Файл {outfile_name}.txt успешно сформирован/открыт в директории results/')
    except OSError: # на случай если произошла ошибка
        sys.exit("Ошибка при создании/открытии файла.")


    lemmas_count = None
    wordform_count = None

    print('Отвечайте на последующие вопросы: "y"/"n" маленькими буквами без лишних пробелов (по умолчанию ответ "n" - no)\n')

    s = ''
    s += '----------------------------------\n'
    lemmas_count = lemmas_counter(text)
    s += f'Всего слов: {lemmas_count.total()}\n'
    s += f'Уникальных лемм: {len(lemmas_count)}\n'
    freq_lemmas_list = list(lemmas_count)
    middle_lemmas_length = sum(len(w) for w in freq_lemmas_list) / len(freq_lemmas_list)
    s += f'Средняя длина лемм: {round(middle_lemmas_length, 4)}\n'
    s += '----------------------------------\n'
    print(s)
    with open(outfile, mode='a', encoding='utf-8') as f:
        f.write(s)

    answer_1 = input('\n1. Вывести самые частотные леммы? Если да - введите необходимое число, иначе введите 0\nВаш ответ: ')
    if answer_1 != '0' and answer_1.isdigit():
        s = ''
        s += '----------------------------------\n'
        s += 'Самые частотные леммы:\n'
        answer_2 = input('\nВывести дополнительно основы самых частотных слов? (y/n)\nВаш ответ: ')
        if answer_2 == 'y':
            stemmer = SnowballStemmer('russian')
            ind = 1
            for w in lemmas_count.most_common(int(answer_1)):
                s += f'    {ind}. {w[0]} - {w[1]} - {stemmer.stem(w[0])}\n'
                ind += 1
        else:
            ind = 1
            for w in lemmas_count.most_common(int(answer_1)):
                s += f'    {ind}. {w[0]} - {w[1]}\n'
                ind += 1
        s += '----------------------------------\n'
        print(s)
        with open(outfile, mode='a', encoding='utf-8') as f:
            f.write(s)


    answer = input('\n2. Посчитать общее число словоформ в тексте, вывести наиболее частотные и найти среднюю длину всех словоформ? (y/n)\nВаш ответ: ')
    if answer == 'y':
        s = ''
        s += '----------------------------------\n'
        wordform_count = Counter(text)
        s += f'Всего словоформ: {wordform_count.total()}\n'
        freq_wordform_list = list(wordform_count)
        middle_wordform_length = sum(len(w) for w in freq_wordform_list) / len(freq_wordform_list)
        s += f'Средняя длина словоформ: {round(middle_wordform_length, 4)}\n'
        answer_1 = input('\nВывести самые частотные словоформы? Если да - введите необходимое число, иначе введите 0\nВаш ответ: ')
        if answer_1 != '0' and answer_1.isdigit():
            s += f'Самые частотные словоформы:\n'
            ind = 1
            for w in wordform_count.most_common(int(answer_1)):
                s += f'    {ind}. {w[0]} - {w[1]}\n'
                ind += 1
        s += '----------------------------------\n'
        print(s)
        with open(outfile, mode='a', encoding='utf-8') as f:
            f.write(s)


    answer = input('\n3. Вывести относительные частоты самых частотных слов (лемм)? Если да - введите необходимое число, иначе введите 0\nВаш ответ: ')
    if answer != '0' and answer.isdigit():
        s = ''
        s += '----------------------------------\n'
        if not lemmas_count:
            lemmas_count = lemmas_counter(text)
        all_words_count = sum(lemmas_count.values())
        s += f'Относительные частоты самых частотных слов:\n'
        ind = 1
        for w in lemmas_count.most_common(int(answer)):
            s += f'    {ind}. {w[0]} - {round(w[1] / all_words_count, 4)}\n'
            ind += 1
        s += '----------------------------------\n'
        print(s)
        with open(outfile, mode='a', encoding='utf-8') as f:
            f.write(s)


    answer = input('\n4. Посчитать коэффициент лексического богатства текста? (y/n)\nВаш ответ: ')
    if answer == 'y':
        s = '' 
        s += '----------------------------------\n'
        if not lemmas_count:
            lemmas_count = lemmas_counter(text)
        s += f'{round(len(lemmas_count) / sum(lemmas_count.values()), 4)} - коэффициент лексического богатства текста\n'
        s += '----------------------------------\n'
        print(s)
        with open(outfile, mode='a', encoding='utf-8') as f:
            f.write(s)


    answer = input('\n5. Получить количество уникальных лемм для разных частей речи и построить соответствующую диаграмму? (y/n)\nВаш ответ: ')
    if answer == 'y':
        s = ''
        s += '----------------------------------\n'
        s += 'Количество уникальных лемм для разных частей речи:\n'
        if not lemmas_count:
            lemmas_count = lemmas_counter(text)
        total = len(lemmas_count)
        print(total)
        lemmas_turple = lemmas_count.items()
        parts_of_speach_count = dict(Counter([ru_name_of_part_of_speech(morph.parse(w[0])[0].tag.POS) for w in lemmas_turple]))
        for key, value in parts_of_speach_count.items():
            s += '  {0}: {1}\n'.format(key,value)
        s += '----------------------------------\n'
        print(s)
        with open(outfile, mode='a', encoding='utf-8') as f:
            f.write(s)

        fig, ax = plt.subplots() # визуализация распределения лемм по частям речи
        ax.pie(parts_of_speach_count.values())
        plt.legend(labels=[f"{key} ({(value/total):.1%})" for key, value in parts_of_speach_count.items()])
        path = 'results/diagram_' + outfile_name +'1.png'
        plt.savefig(path)
        plt.show()
 

    answer = input('\n6. Вывести самые частотные слова для разных частей речи? (y/n)\nВаш ответ: ')
    if answer == 'y':
        s = ''
        if not lemmas_count:
            lemmas_count = lemmas_counter(text)
        lemmas_turple = lemmas_count.items()
        parts_of_speach_count = []
        for w in lemmas_turple:
            parts_of_speach_count.append((ru_name_of_part_of_speech(morph.parse(w[0])[0].tag.POS), w[0], w[1]))
        sorted_parts_of_speach_count = sorted(parts_of_speach_count, key=lambda point: (str(point[0]), -point[2]))
        answer_1 = input('\nПо сколько слов выводить?\nВаш ответ (число): ')
        s += '----------------------------------\n'
        s += f'Самые частотные слова для разных частей речи: \n'
        part_of_speach_flag = True
        last_part_of_speach = ''
        count = 0
        for part_of_speach in sorted_parts_of_speach_count:
            if part_of_speach_flag:
                if last_part_of_speach == '':
                    s += f'{part_of_speach[0]}:\n'
                    last_part_of_speach = str(part_of_speach[0])
                if last_part_of_speach != str(part_of_speach[0]):
                    last_part_of_speach = str(part_of_speach[0])
                    count = 0
                    s += f'{part_of_speach[0]}:\n'
                s += f'    {count + 1}. {part_of_speach[1]} - {part_of_speach[2]}\n'
                count += 1
                if count == int(answer_1):
                    last_part_of_speach = str(part_of_speach[0])
                    part_of_speach_flag = False
                    count = 0
            elif str(part_of_speach[0]) != last_part_of_speach and count == 0:
                s += f'{part_of_speach[0]}:\n'
                s += f'    {count + 1}. {part_of_speach[1]} - {part_of_speach[2]}\n'
                count += 1
                part_of_speach_flag = True
        s += '----------------------------------\n'
        print(s)
        with open(outfile, mode='a', encoding='utf-8') as f:
            f.write(s)

    answer = input('\n7. Провести морфологический анализ имеющихся слов? (Только для сущ., глаг. и прил.) (y/n)\nВаш ответ: ')
    if answer == 'y':
        s = ''
        s += '----------------------------------\n'
        s += 'Морфологический анализ имеющихся слов:\n\n'
        if not wordform_count:
            wordform_count = Counter(text)
        ind = 1
        for w in wordform_count.most_common():
            s += f'{ind}. {w[0]} \n{morph_analyzer(w[0])}\n\n'
            ind += 1
        s += '----------------------------------\n'
        with open(outfile, mode='a', encoding='utf-8') as f:
            f.write(s)
        print(f'Морфологический разбор слов отправлен в {outfile}')

    answer = input('\n8. Вывести количество различных словоформ для наиболее частотных слов и построить соответствующую диаграмму? (y/n)\nВаш ответ: ')
    if answer == 'y':
        answer_1 = input('\nДля какого количества лемм\nВаш ответ (число): ')
        s = ''
        s +='----------------------------------\n'
        s += 'Количество различных словоформ для наиболее частотных слов:\n'
        if not lemmas_count:
            lemmas_count = lemmas_counter(text)
        lemma_base = [w[0] for w in lemmas_count.most_common(int(answer_1))]
        if not wordform_count:
            wordform_count = Counter(text)
        wordform_turple = wordform_count.items()
        res = Counter([(morph.parse(w[0])[0].normal_form, w[0]) for w in wordform_turple if morph.parse(w[0])[0].normal_form in lemma_base]).items()
        mas = dict()
        for w in res:
            if w[0][0] in mas:
                mas[w[0][0]] += w[1]
            else:
                mas[w[0][0]] = w[1]    
        sorted_mas = sorted(mas.items(), key=lambda item: item[1], reverse=True)
        mas_for_graph = dict(mas)
        for i in sorted_mas:
            s += '{0}: {1}\n'.format(i[0], i[1])
        s += '----------------------------------'
        print(s)
        with open(outfile, mode='a', encoding='utf-8') as f:
            f.write(s)
        plt.bar(mas_for_graph.keys(), mas_for_graph.values()) # визуализация словоформ по частотным леммам
        plt.xticks(rotation=30)
        path = 'results/diagram_' + outfile_name +'2.png'
        plt.savefig(path)
        plt.show()

    answer = input('\n9. Посчитать индекс удобочитаемости Флеша (адаптированный для русского языка)? (y/n)\nВаш ответ: ')
    if answer == 'y':
        sentences = nltk.sent_tokenize(all_text, language='russian')
        word_tokens_new = nltk.word_tokenize(no_punctuation_and_digit(all_text.lower().replace('ё', 'е')), language='russian') 
        text_new = [w for w in word_tokens_new if is_russian_word(w)] # удаление иностранных слов
        lemmas_count_new = lemmas_counter(text_new)
        total_words = lemmas_count_new.total()
        num_sentences = len(sentences)
        total_syllables = 0
        for word in text_new:
            total_syllables += count_vowels(word)  # Считаем количество слогов в каждом слове
        if total_words == 0 or num_sentences == 0:
            print('Некорректные данные')
        else:
            fre = 206.835 - 1.3 * (total_words / num_sentences) - 60.1 * (total_syllables / total_words)
            s = '' 
            s += '----------------------------------\n'
            s += f'{round(fre, 4)} - индекс удобочитаемости Флеша\n'
            s += '----------------------------------\n'
            print(s)
            with open(outfile, mode='a', encoding='utf-8') as f:
                f.write(s)

    answer = input('\n10. Посчитать коэффициент прилагательных и причастий? (y/n)\nВаш ответ: ') # отношение прилагательных к существительным
    if answer == 'y':
        if not wordform_count:
            wordform_count = Counter(text)
        wordform_turple = wordform_count.items()
        parts_of_speach_count = dict(Counter([ru_name_of_part_of_speech(morph.parse(w[0])[0].tag.POS) for w in wordform_turple]))
        if 'существительные' not in parts_of_speach_count or ('прилагательные' not in parts_of_speach_count and 'причастия' not in parts_of_speach_count):
            print('Невозможно посчитать коэффициент прилагательных и причастий')
        else:
            s = ''
            s += '----------------------------------\n'
            key1 = 'прилагательные'
            key2 = 'причастия'
            key3 = 'существительные'
            if 'прилагательные' in parts_of_speach_count:
                if 'причастия' in parts_of_speach_count:
                    s += f"{round((parts_of_speach_count[key1] + parts_of_speach_count[key2])/ parts_of_speach_count[key3], 4)} - коэффициент прилагательных и причастий\n"
                else:
                    s += f"{round(parts_of_speach_count[key1]/ parts_of_speach_count[key3], 4)} - коэффициент прилагательных и причастий\n"
            else:
                s += f"{round(parts_of_speach_count[key2]/ parts_of_speach_count[key3], 4)} - коэффициент прилагательных и причастий\n"
            s += '----------------------------------\n'
            print(s)
            with open(outfile, mode='a', encoding='utf-8') as f:
                f.write(s)
