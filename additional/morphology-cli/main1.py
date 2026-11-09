if __name__ == "__main__":
    import TextInfo1 as ti
    import MyProg1
    import pandas as pd
    import sys
    import re
    import os



    def write_to_file(filename, title, data_dict, total_count=None, top_n=5, mode='a', display_message=None):
        """
        В файл записывает ПОЛНЫЙ список в табличном виде, а на экран выводит только ТОП-N.
        Все числа с плавающей точкой округляются до двух знаков после запятой.
        """
        def fmt(value):
            """Округляем float до 2 знаков, остальное — без изменений"""
            if isinstance(value, float):
                return f"{value:.2f}"
            elif isinstance(value, int):
                return f"{value:d}"
            else:
                return str(value)

        # Определяем ширину колонки под слова (по максимальной длине ключей)
        max_word_len = max((len(str(k)) for k in data_dict.keys()), default=10)
        word_col = max(10, min(max_word_len + 2, 30))  # ограничим ширину до 30 символов
        num_col = 12  # ширина колонки под число

        with open(filename, mode=mode, encoding='utf-8') as f:
            f.write(f"--- {title} ---\n")
            if total_count is not None:
                f.write(f"Всего различных: {fmt(total_count)}\n\n")

            f.write("Полный список, отсортированный по частоте:\n")
            f.write(f"{'Слово':{word_col}}{'Частота':>{num_col}}\n")
            f.write('-' * (word_col + num_col) + '\n')

            for word, count in data_dict.items():
                f.write(f"{word:{word_col}}{fmt(count):>{num_col}}\n")

            f.write('\n' + '_' * 60 + '\n\n')

        # На экран — только топ-N в таком же табличном виде
        if display_message:
            print(f"\n{display_message}")
        if top_n:
            print(f"Топ-{top_n}:")
            print(f"{'Слово':{word_col}}{'Частота':>{num_col}}")
            print('-' * (word_col + num_col))
            for i, (word, count) in enumerate(data_dict.items()):
                if i >= top_n:
                    break
                print(f"{word:{word_col}}{fmt(count):>{num_col}}")



    def write_morpho_analysis_to_txt(filename, analyzed_data, original_words, text_file_name):
        with open(filename, mode='a', encoding='utf-8') as f:
            f.write(f"--- Подробный морфологический анализ текста из файла: {os.path.basename(text_file_name)} ---\n\n")
            for i, (word, analysis) in enumerate(zip(original_words, analyzed_data)):
                f.write(f"Словоформа: {word}\n")
                f.write(f"  Часть речи: {analysis.get('Часть речи', 'N/A')}\n")
                f.write(f"  Начальная форма: {analysis.get('Начальная форма', 'N/A')}\n")

                if "Постоянные признаки" in analysis and analysis["Постоянные признаки"]:
                    f.write("  Постоянные признаки:\n")
                    for key, value in analysis["Постоянные признаки"].items():
                        f.write(f"    - {key}: {value}\n")
            
                if "Непостоянные признаки" in analysis and analysis["Непостоянные признаки"]:
                    f.write("  Непостоянные признаки:\n")
                    for key, value in analysis["Непостоянные признаки"].items():
                        f.write(f"    - {key}: {value}\n")
            
                if "Теги" in analysis: # Для "Неанализируемых" частей речи
                    f.write(f"  Теги: {analysis['Теги']}\n")

                f.write('\n' + '-' * 30 + '\n\n') # Разделитель между словами
            f.write('\n' + '_' * 60 + '\n\n')


    def get_user_input(prompt, validation_func=None, error_message="Неверный ввод, попробуйте еще раз."):
        while True:
            user_input = input(prompt).lower().strip()
            if validation_func is None or validation_func(user_input):
                return user_input
            else:
                print(error_message)

    def validate_yes_no(input_str):
        return input_str in ["да", "нет"]

    def validate_txt_filename(input_str):
        return re.search(r'[.]txt$', input_str)

    # Проверяем и создаем директорию 'results', если ее нет
    if not os.path.exists('results'):
        os.makedirs('results')

    print("Показывать ли графики после завершения всех расчётов? (да/нет)")
    SHOW_PLOTS_AFTER = (get_user_input("", validate_yes_no) == "да")

    sw_flag = False
    lemma_flag = False
    wordf_flag = False

    print("Выполнить ли предобработку, расширив список стоп-слов? (да/нет)")
    if get_user_input("", validate_yes_no) == "да":
        # сначала предложим пользователю дописать свои слова в файл
        print("Хотите добавить свои стоп-слова в файл перед обработкой? (да/нет)")
        if get_user_input("", validate_yes_no) == "да":
            # интерактивный ввод; файл по умолчанию 'additional_stopwords.txt' в текущей папке
            ti.add_user_stopwords_interactive('additional_stopwords.txt')

        # теперь формируем общий список стоп-слов (NLTK + пользовательские из файла)
        ti.form_stop_words('additional_stopwords.txt')
        sw_flag = True



    while True:
        file = input("Введите полный путь обрабатываемого файла: ")
        try:
            with open(file, mode='r', encoding='utf-8') as f:
                text_content = f.read() # Читаем весь контент для передачи в write_morpho_analysis_to_txt
                # --- Создаём отдельную папку для результатов именно этого файла ---
                base_filename = os.path.splitext(os.path.basename(file))[0]  # имя без расширения
                result_dir = os.path.join('results', base_filename)
                print(result_dir)
                os.makedirs(result_dir, exist_ok=True)  # создаём, если нет

                # Подменим базовую папку вывода для всех результатов
                print(f"Все результаты будут сохранены в папку: {result_dir}")

                text = ti.word_tokenize(ti.no_punctuation_yo(text_content.lower()))
                total_words = len(text)
                if sw_flag:
                    words = [w for w in text if w not in ti.stop_words]
                else:
                    words = [w for w in text]
            break
        except OSError:
            print("Я не знаю такого файла. Пожалуйста, проверьте путь и имя файла и попробуйте еще раз.")

    outfile = get_user_input("Введите название файла (.txt), в который выводится вся информация: ",
                             validate_txt_filename, "Неверный формат файла (необходим .txt)")
    outfile = os.path.join(result_dir, outfile)

    # Очищаем файл перед записью, если он существует
    with open(outfile, 'w', encoding='utf-8') as f:
        f.write(f"Анализ текста из файла: {file}\n\n")

    print("Выполнить ли подсчет лемм/основ слов из нашего файла? (да/нет)")
    if get_user_input("", validate_yes_no) == "да":
        d1, res1 = ti.count_lemmas(words)
        write_to_file(outfile, "Самые частые леммы", d1, res1, top_n=5, display_message="Топ-5 самых частых лемм:")
        lemma_flag = True

    print("Выполнить ли подсчет словоформ из нашего файла? (да/нет)")
    if get_user_input("", validate_yes_no) == "да":
        d2, res2 = ti.count_wordforms(words)
        write_to_file(outfile, "Самые частые словоформы", d2, res2, top_n=5, display_message="Топ-5 самых частых словоформ:")
        wordf_flag = True

    if lemma_flag or wordf_flag:
        print("Выполнить ли вывод относительных частот в файл? (да/нет)")
        if get_user_input("", validate_yes_no) == "да":
            print("Для лемм или для словоформ выполняем вывод?")
            choice = get_user_input("1. Леммы; 2. Словоформы\n", lambda x: x in ['1', '2'])
            if choice == '1' and lemma_flag:
                write_to_file(outfile, "Относительные частоты лемм", ti.Rel_Freq(d1), top_n=5, display_message="Топ-5 относительных частот лемм:")
            elif choice == '2' and wordf_flag:
                write_to_file(outfile, "Относительные частоты словоформ", ti.Rel_Freq(d2), top_n=5, display_message="Топ-5 относительных частот словоформ:")
            else:
                print("Сделаем вид, будто ничего не было или выбранная опция недоступна.")

        print("Выполнить ли подсчет средней длины всех лемм/словоформ? (да/нет)")
        if get_user_input("", validate_yes_no) == "да":
            print("Для лемм или для словоформ выполняем вывод?")
            choice = get_user_input("1. Леммы; 2. Словоформы; 3. Оба\n", lambda x: x in ['1', '2', '3'])
            if choice == '1' and lemma_flag:
                tup_lemm = ti.length_wordforms(d1)
                write_to_file(outfile, 'Длины всех лемм', tup_lemm[0], top_n=5, display_message="Топ-5 длин лемм:")
                print("Средняя длина всех лемм в тексте составила:", tup_lemm[1])
            elif choice == '2' and wordf_flag:
                tup_wf = ti.length_wordforms(d2)
                write_to_file(outfile, 'Длины всех словоформ', tup_wf[0], top_n=5, display_message="Топ-5 длин словоформ:")
                print("Средняя длина всех словоформ в тексте составила:", tup_wf[1])
            elif choice == '3' and lemma_flag and wordf_flag:
                tup_lemm = ti.length_wordforms(d1)
                write_to_file(outfile, 'Длины всех лемм', tup_lemm[0], top_n=5, display_message="Топ-5 длин лемм:")
                print("Средняя длина всех лемм в тексте составила:", tup_lemm[1])
                tup_wf = ti.length_wordforms(d2)
                write_to_file(outfile, 'Длины всех словоформ', tup_wf[0], top_n=5, display_message="Топ-5 длин словоформ:")
                print("Средняя длина всех словоформ в тексте составила:", tup_wf[1])
            else:
                print("Сделаем вид, будто ничего не было или выбранная опция недоступна.")
        
        print("Вывести ли коэффициент лексического разнообразия обрабатываемого текста? (да/нет)")
        if get_user_input("", validate_yes_no) == "да" and lemma_flag:
            lex = ti.how_rich_is_lexic(d1)
            print(f'Коэффициент лексического разнообразия файла {file} равен: {lex}')
            with open(outfile, 'a', encoding='utf-8') as f:
                f.write(f"Коэффициент лексического разнообразия: {lex}\n\n")

    print("Выполнить ли вывод основ, благодаря SnowballStemmer? (да/нет)")
    if get_user_input("", validate_yes_no) == "да":
        ti.Stem_Freq(words, outfile)

    print("Провести ли подробный морфологический анализ словоформ в тексте? (да/нет)")
    if get_user_input("", validate_yes_no) == "да":
        morpho_analysis_outfile = os.path.join(result_dir, input("Введите название файла (.txt), в который выводится подробный морфологический разбор: "))
        if not validate_txt_filename(morpho_analysis_outfile):
            sys.exit("Неверный формат файла (необходим .txt)")

        analyzed_data = []
        for w in words:
            analyzed_data.append(MyProg1.MorphoAnalyz(w))
    
        # Теперь вызываем новую функцию для записи в TXT
        write_morpho_analysis_to_txt(morpho_analysis_outfile, analyzed_data, words, file)

        # Для графиков и статистики частей речи все равно нужен DataFrame
        data_words = pd.DataFrame(data=analyzed_data, index=words)
        pos_counts = data_words["Часть речи"].value_counts()
        print("Части речи, отсортированы по частоте встречи:")
        print(pos_counts)
    
        with open(outfile, 'a', encoding='utf-8') as f:
            f.write("--- Частота частей речи ---\n")
            f.write(pos_counts.to_string())
            f.write('\n' + '_' * 60 + '\n\n')

        p1 = ti.POS_graph(pos_counts, file, save_dir=result_dir, show=SHOW_PLOTS_AFTER)
        p2 = ti.POS_pie_chart(pos_counts, file, save_dir=result_dir, show=SHOW_PLOTS_AFTER)
     # Добавлен круговой график частей речи

    print("А статистика по буквам нужна? (да/нет)")
    if get_user_input("", validate_yes_no) == "да":
        ws = ' '.join(words)
        letter_freq, _ = ti.letters_with_graph(ws, file, save_dir=result_dir, show=SHOW_PLOTS_AFTER)
        write_to_file(outfile, "Частота встречаемости букв", letter_freq)

    print("Анализ завершен.")
