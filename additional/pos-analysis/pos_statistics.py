import pymorphy3
import nltk
from nltk.corpus import stopwords
from collections import Counter
import re
import sys

# Инициализация морфологического анализатора
morph = pymorphy3.MorphAnalyzer()

# Проверка, есть ли в слове хотя бы один кириллический символ
def is_russian_word(word):
    return bool(re.search(r'[а-яА-ЯёЁ]', word))

# Удаление знаков пунктуации и цифр
def no_punctuation_and_digit(text, punctuation):
    for symb in punctuation:
        text = text.replace(symb, ' ')
    text = ''.join([i for i in text if not i.isdigit()])
    return text

# Загрузка стоп-слов из файла
def load_stopwords_from_file(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            stopwords_list = [line.strip() for line in f if line.strip()]
        return set(stopwords_list)
    except Exception as e:
        print(f"Ошибка при загрузке стоп-слов из файла: {e}")
        return set()

# Подсчёт числа лемм
def lemmas_counter(text):
    lemmas = []
    for w in text:
        try:
            lemma = morph.parse(w)[0].normal_form
            lemmas.append(lemma)
        except:
            continue
    return Counter(lemmas)

# Анализ распределения по частям речи
def analyze_parts_of_speech(text):
    pos_counter = Counter()
    for word in text:
        try:
            p = morph.parse(word)[0]
            pos = p.tag.POS
            
            # Объединяем части речи
            if pos in ['ADJF', 'ADJS', 'COMP']:
                pos = 'ADJ'  # прилагательные
            elif pos in ['VERB', 'INFN']:
                pos = 'VERB'  # глаголы
            elif pos in ['PRTF', 'PRTS']:
                pos = 'PRT'  # причастия
            
            pos_counter[pos] += 1
        except:
            continue
    return pos_counter

# Вычисление коэффициента лексического богатства
def calculate_lexical_richness(unique_lemmas, total_words):
    return unique_lemmas / total_words if total_words > 0 else 0

# Анализ длины слов
def analyze_word_length(text):
    if not text:
        return {'min': 0, 'max': 0, 'avg': 0}
    
    lengths = [len(word) for word in text]
    return {
        'min': min(lengths),
        'max': max(lengths),
        'avg': sum(lengths) / len(lengths)
    }

# Получение самых частотных ЛЕММ по частям речи
def get_most_frequent_by_pos(text, pos_list, top_n=5):
    pos_lemmas = {}
    for pos in pos_list:
        lemmas = []
        for word in text:
            try:
                p = morph.parse(word)[0]
                current_pos = p.tag.POS
                
                if current_pos in ['ADJF', 'ADJS', 'COMP'] and pos == 'ADJ':
                    lemma = p.normal_form
                    lemmas.append(lemma)
                elif current_pos in ['VERB', 'INFN'] and pos == 'VERB':
                    lemma = p.normal_form
                    lemmas.append(lemma)
                elif current_pos in ['PRTF', 'PRTS'] and pos == 'PRT':
                    lemma = p.normal_form
                    lemmas.append(lemma)
                elif current_pos == pos:
                    lemma = p.normal_form
                    lemmas.append(lemma)
            except:
                continue
        if lemmas:
            pos_lemmas[pos] = Counter(lemmas).most_common(top_n)
    return pos_lemmas

# Подсчет уникальных лемм по частям речи
def count_unique_lemmas_by_pos(text):
    unique_lemmas_by_pos = {}
    for word in text:
        try:
            p = morph.parse(word)[0]
            pos = p.tag.POS
            
            # Объединяем части речи
            if pos in ['ADJF', 'ADJS', 'COMP']:
                pos = 'ADJ'  # прилагательные
            elif pos in ['VERB', 'INFN']:
                pos = 'VERB'  # глаголы
            elif pos in ['PRTF', 'PRTS']:
                pos = 'PRT'  # причастия
            
            lemma = p.normal_form
            if pos not in unique_lemmas_by_pos:
                unique_lemmas_by_pos[pos] = set()
            unique_lemmas_by_pos[pos].add(lemma)
        except:
            continue
    return unique_lemmas_by_pos

# Название частей речи на русском
def ru_name_of_part_of_speech(eng_name):
    pos_names = {
        'NOUN': 'существительные',
        'ADJ': 'прилагательные',  # объединенные ADJF, ADJS, COMP
        'VERB': 'глаголы',  # объединенные VERB, INFN
        'PRT': 'причастия',  # объединенные PRTF, PRTS
        'GRND': 'деепричастия',
        'NUMR': 'числительные',
        'ADVB': 'наречия',
        'NPRO': 'местоимения',
        'PRED': 'предикативы',
        'PREP': 'предлоги',
        'CONJ': 'союзы',
        'PRCL': 'частицы',
        'INTJ': 'междометия'
    }
    return pos_names.get(eng_name, 'неопределенная часть речи')

def analyze_text_statistics(text):
    # Общестатистические характеристики
    total_words = len(text)
    lemmas_count = lemmas_counter(text)
    unique_lemmas = len(lemmas_count)
    length_stats = analyze_word_length(text)
    
    # Особенности лексикона
    pos_counter = analyze_parts_of_speech(text)
    lexical_richness = calculate_lexical_richness(unique_lemmas, total_words)
    
    # Анализ по частям речи
    main_pos = ['NOUN', 'ADJ', 'VERB', 'ADVB', 'NPRO', 'NUMR', 'PRT']
    frequent_by_pos = get_most_frequent_by_pos(text, main_pos, 5)
    unique_lemmas_by_pos = count_unique_lemmas_by_pos(text)
    
    return {
        'total_words': total_words,
        'lemmas_count': lemmas_count,
        'unique_lemmas': unique_lemmas,
        'length_stats': length_stats,
        'pos_counter': pos_counter,
        'lexical_richness': lexical_richness,
        'frequent_by_pos': frequent_by_pos,
        'unique_lemmas_by_pos': unique_lemmas_by_pos
    }

# Вывод статистики на экран и в файл
def print_statistics(results, output_file=None):
    
    def write_output(text):
        print(text)
        if output_file:
            output_file.write(text + '\n')
    
    # РАЗДЕЛ 1: ОБЩЕСТАТИСТИЧЕСКИЕ ХАРАКТЕРИСТИКИ
    write_output("=" * 70)
    write_output("ОБЩЕСТАТИСТИЧЕСКИЕ ХАРАКТЕРИСТИКИ ТЕКСТА")
    write_output("=" * 70)
    
    write_output(f"1. Общее число словоупотреблений: {results['total_words']}")
    write_output(f"2. Общее число уникальных лемм: {results['unique_lemmas']}")
    write_output("\n3. Самые частотные слова (топ-15):")

    # Форматированная таблица частотных слов
    write_output(f"{'№':<2}  {'Слово':<20} {'Частота':<8} {'%':<6}")
    write_output("-" * 45)
    for i, (word, count) in enumerate(results['lemmas_count'].most_common(15), 1):
        frequency = (count / results['total_words']) * 100
        write_output(f"{i:<2}  {word:<20} {count:<8} {frequency:<5.2f}%")
    
    write_output("\n4. Характеристики длины словоформ:")
    write_output(f"{'Параметр':<15} {'Значение':<10}")
    write_output("-" * 25)
    write_output(f"{'Средняя':<15} {results['length_stats']['avg']:<10.2f}")
    write_output(f"{'Минимальная':<15} {results['length_stats']['min']:<10}")
    write_output(f"{'Максимальная':<15} {results['length_stats']['max']:<10}")
    
    # Распределение по длинам слов
    length_distribution = Counter(len(word) for word in text_processed)
    write_output("\n5. Распределение слов по длине (топ-5):")
    write_output(f"{'Длина':<6} {'Кол-во':<8} {'%':<6}")
    write_output("-" * 25)
    for length, count in length_distribution.most_common(5):
        percentage = (count / results['total_words']) * 100
        write_output(f"{length:<6} {count:<8} {percentage:<5.1f}%")
    
    # РАЗДЕЛ 2: ОСОБЕННОСТИ ЛЕКСИКОНА
    write_output("\n" + "=" * 70)
    write_output("ОСОБЕННОСТИ ЛЕКСИКОНА")
    write_output("=" * 70)
    
    # Характеристика 1: Коэффициент лексического богатства
    write_output(f"1. Коэффициент лексического богатства: {results['lexical_richness']:.4f}\n")
    write_output("   (отношение числа уникальных лемм к общему числу словоупотреблений)")
    
    # Характеристика 2: Распределение по частям речи
    write_output("\n2. Распределение слов по частям речи:\n")
    total_pos_words = sum(results['pos_counter'].values())
    
    write_output(f"{'Часть речи':<25} {'Кол-во':<8} {'%':<6}")
    write_output("-" * 45)
    
    # Сортируем части речи по частоте
    sorted_pos = results['pos_counter'].most_common()
    
    for pos, count in sorted_pos:
        percentage = (count / total_pos_words) * 100
        write_output(f"{ru_name_of_part_of_speech(pos):<25} {count:<8} {percentage:<5.1f}%")
    
    # Характеристика 3: Количество уникальных лемм по частям речи
    write_output("\n3. Количество уникальных лемм по частям речи:\n")
    
    # Сортируем по количеству уникальных лемм
    unique_counts = {}
    for pos in results['unique_lemmas_by_pos']:
        unique_counts[pos] = len(results['unique_lemmas_by_pos'][pos])
    
    sorted_unique = sorted(unique_counts.items(), key=lambda x: x[1], reverse=True)
    
    write_output(f"{'Часть речи':<25} {'Леммы':<8}")
    write_output("-" * 35)
    for pos, count in sorted_unique:
        write_output(f"{ru_name_of_part_of_speech(pos):<25} {count:<8}")
    
    # Характеристика 4: Соотношение основных частей речи
    write_output("\n4. Соотношение основных частей речи:\n")
    noun_count = results['pos_counter'].get('NOUN', 0)
    adj_count = results['pos_counter'].get('ADJ', 0)  # объединенные прилагательные
    verb_count = results['pos_counter'].get('VERB', 0)  # объединенные глаголы
    prt_count = results['pos_counter'].get('PRT', 0)  # объединенные причастия
    total_main = noun_count + adj_count + verb_count + prt_count
    
    if total_main > 0:
        write_output(f"{'Часть речи':<15} {'Кол-во':<8} {'%':<6}")
        write_output("-" * 30)
        write_output(f"{'Существительные':<15} {noun_count:<8} {noun_count/total_main*100:<5.1f}%")
        write_output(f"{'Прилагательные':<15} {adj_count:<8} {adj_count/total_main*100:<5.1f}%")
        write_output(f"{'Глаголы':<15} {verb_count:<8} {verb_count/total_main*100:<5.1f}%")
        write_output(f"{'Причастия':<15} {prt_count:<8} {prt_count/total_main*100:<5.1f}%")
    
    # Характеристика 5: Самые частотные ЛЕММЫ существительных
    write_output("\n5. Самые частотные существительные (леммы):\n")
    if 'NOUN' in results['frequent_by_pos']:
        write_output(f"{'Лемма':<15} {'Частота':<8} {'%':<6}")
        write_output("-" * 30)
        for lemma, count in results['frequent_by_pos']['NOUN']:
            frequency = (count / results['total_words']) * 100
            write_output(f"{lemma:<15} {count:<8} {frequency:<5.2f}%")
    
    # Характеристика 6: Самые частотные ЛЕММЫ прилагательных
    write_output("\n6. Самые частотные прилагательные (леммы):\n")
    if 'ADJ' in results['frequent_by_pos']:
        write_output(f"{'Лемма':<15} {'Частота':<8} {'%':<6}")
        write_output("-" * 30)
        for lemma, count in results['frequent_by_pos']['ADJ']:
            frequency = (count / results['total_words']) * 100
            write_output(f"{lemma:<15} {count:<8} {frequency:<5.2f}%")
    
    # Характеристика 7: Самые частотные ЛЕММЫ глаголов
    write_output("\n7. Самые частотные глаголы (леммы):\n")
    if 'VERB' in results['frequent_by_pos']:
        write_output(f"{'Лемма':<15} {'Частота':<8} {'%':<6}")
        write_output("-" * 30)
        for lemma, count in results['frequent_by_pos']['VERB']:
            frequency = (count / results['total_words']) * 100
            write_output(f"{lemma:<15} {count:<8} {frequency:<5.2f}%")
    
    # Характеристика 8: Самые частотные ЛЕММЫ причастий
    write_output("\n8. Самые частотные причастия (леммы):\n")
    if 'PRT' in results['frequent_by_pos']:
        write_output(f"{'Лемма':<15} {'Частота':<8} {'%':<6}")
        write_output("-" * 30)
        for lemma, count in results['frequent_by_pos']['PRT']:
            frequency = (count / results['total_words']) * 100
            write_output(f"{lemma:<15} {count:<8} {frequency:<5.2f}%")
    
    # Характеристика 9: Самые частотные ЛЕММЫ наречий
    write_output("\n9. Самые частотные наречия (леммы):\n")
    if 'ADVB' in results['frequent_by_pos']:
        write_output(f"{'Лемма':<15} {'Частота':<8} {'%':<6}")
        write_output("-" * 30)
        for lemma, count in results['frequent_by_pos']['ADVB']:
            frequency = (count / results['total_words']) * 100
            write_output(f"{lemma:<15} {count:<8} {frequency:<5.2f}%")
    
    # Характеристика 10: Разнообразие лексики по частям речи
    write_output("\n10. Лексическое разнообразие по частям речи:\n")
    if unique_counts:
        most_diverse_pos = max(unique_counts, key=unique_counts.get)
        write_output(f"{'Параметр':<30} {'Значение':<15}")
        write_output("-" * 45)
        write_output(f"{'Наиболее разнообразная часть речи':<30} {ru_name_of_part_of_speech(most_diverse_pos):<15}")
        write_output(f"{'Количество лемм':<30} {unique_counts[most_diverse_pos]:<15}")
    
    # Характеристика 11: Соотношение знаменательных и служебных частей речи в виде таблицы
    significant_pos = ['NOUN', 'ADJ', 'VERB', 'PRT', 'ADVB', 'NUMR']  # обновленный список
    functional_pos = ['PREP', 'CONJ', 'PRCL']
    
    significant_count = sum(results['pos_counter'].get(pos, 0) for pos in significant_pos)
    functional_count = sum(results['pos_counter'].get(pos, 0) for pos in functional_pos)
    total_classified = significant_count + functional_count
    
    if total_classified > 0:
        write_output(f"\n11. Соотношение знаменательных и служебных частей речи:\n")
        write_output(f"{'Тип':<20} {'Кол-во':<8} {'%':<6}")
        write_output("-" * 35)
        write_output(f"{'Знаменательные':<20} {significant_count:<8} {significant_count/total_classified*100:<5.1f}%")
        write_output(f"{'Служебные':<20} {functional_count:<8} {functional_count/total_classified*100:<5.1f}%")
    
    write_output("\n" + "=" * 70)
    write_output("АНАЛИЗ ЗАВЕРШЕН")
    write_output("=" * 70)

# Основная программа
if __name__ == "__main__":
    print("ПРОГРАММА АНАЛИЗА ЛЕКСИКОНА РУССКОГО ТЕКСТА")
    print("=" * 50)
    
    # Выбор стоп-слов
    print('\nВыбор списка стоп-слов:')
    print('0 - без стоп-слов')
    print('1 - стандартный список nltk')
    print('2 - загрузить из файла')
    
    answer = input('Ваш выбор: ').strip()
    
    punctuation = '.,!?:;()[]«»-_@#%$"`}{—*–”“/\'&№'
    
    if answer == '0':
        set_stop = set()
    elif answer == '1':
        set_stop = set(stopwords.words('russian'))
    elif answer == '2':
        stopwords_file = input("Введите путь к файлу со стоп-словами: ").strip()
        set_stop = load_stopwords_from_file(stopwords_file)
        if not set_stop:
            print("Используется стандартный список стоп-слов")
            set_stop = set(stopwords.words('russian'))
    else:
        print("Неверный выбор, используется стандартный список стоп-слов")
        set_stop = set(stopwords.words('russian'))
    
    # Чтение файла
    try:
        file_name = input("\nВведите путь к файлу c текстом для проверки: ").strip()
        with open(file_name, 'r', encoding='utf-8') as f:
            text_content = f.read()
        print(f"Файл '{file_name}' успешно загружен")
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        sys.exit(1)
    
    # Обработка текста
    cleaned_text = no_punctuation_and_digit(text_content.lower().replace('ё', 'е'), punctuation)
    word_tokens = nltk.word_tokenize(cleaned_text, language='russian')
    text_processed = [w for w in word_tokens if w not in set_stop and is_russian_word(w)]
    
    # Анализ текста
    results = analyze_text_statistics(text_processed)
    
    # Вывод результатов
    output_filename = input("\nВведите имя файла для сохранения результатов(можно просто нажать enter, данные созранятся в файл lexical_analysis_results.txt): ").strip()
    if not output_filename:
        output_filename = "lexical_analysis_results.txt"
    
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            print("\n" + "=" * 70)
            print("РЕЗУЛЬТАТЫ АНАЛИЗА ЛЕКСИКОНА")
            print("=" * 70)
            
            # Вывод на экран и в файл
            print_statistics(results, f)
            
        print(f"\nПолные результаты сохранены в файл: {output_filename}")
        
    except Exception as e:
        print(f"Ошибка при сохранении файла: {e}")
        print("Вывод результатов только на экран:")
        print_statistics(results)
