if __name__ == "__main__":
    import text_job as tj # импорт файла text_job
    from nltk.tokenize import word_tokenize
    import morph # импорт файла morph.py
    import sys
    import re
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    from tqdm import tqdm

    # Флаги анализатора
    sw_flg = False  # флаг использования стопслов
    lm_flg = False  # флаг работы с леммами
    wf_flg = False  # флаг работы с словоформами
    lm_rf_flg = False  # флаг подсчета статистики лемм
    wf_rf_flg = False  # флаг подсчета статистики словоформ
    morph_flg = False  # флаг морфологического разбора
    heaps_lm_flg = False # флаг Хипса для лемм
    heaps_wf_flg = False # флаг Хипса для словоформ

    print("-" * 40)
    print("Тема 9. Законы текста. copyrighted by Nikita Zhigalov")
    print("Работа анализатора:")
    print("Использовать ли при обработке список стоп-слов? (y/n)")
    match input().strip().lower():
        case "y":
            tj.form_stop_words()  # формируем список стоп-слов
            sw_flg = True  # поднимаем флаг, указывающий на обработку стоп-слов
        case "n":
            pass
        case _:
            sys.exit("Неверный ввод.")

    print()
    print('-' * 60)
    print()
    try:  # пробуем открыть входной файл
        file_path = input(
            "Введите полный путь обрабатываемого файла (того, откуда берем текст): \n"
            + "Также возможно выбрать один из следующих вариантов готовых текстов (просто скопируйте и вставте путь): \n"
            + '1. Л.Н.Толстой "Война и мир" - texts/war_and_peace.txt\n'
            + '2. Ф.М.Достоевский "Преступление и наказание" (фрагмент) - texts/crime_and_punishment.txt\n'
            + '3. Конституция РФ - texts/constitution.txt\n'
            + '4. Статья на Хабре - "Как фармить Kaggle" - texts/habr_kaggle_farm.txt\n'
            + '5. Доклад "Институциональная школа экономики" - texts/institutionalism.txt\n'
            + '6. Конспект лекций по курсу "Операционные системы", ВМК 2006г. - texts/os_mash.txt\n'
            + '7. Описание этого задания - texts/description_big_task.txt\n'
            + '8. Практическое применение: проверка текста на копипасту ("Преступление и наказание" + снова первая половина "Преступления и наказания" + первые пять глав "Война и мир") - texts/copypaste_proof.txt\n'
        )
        f = open(file_path, mode="r", encoding="utf-8")
        text = f.read()
        f.close()
        words = word_tokenize(
            tj.filter_punct(text.lower())
        )  # разбиваем весь текст на отдельные токены + убираем букву ё и всю пунктуацию
        if sw_flg:  # убираем стоп-слова, если есть соотв. флаг
            words = [w for w in words if w not in tj.stop_words]
        words_num = len(words)  # общее число слов в тексте
    except OSError:
        sys.exit("Некорректное имя/путь файла.")

    print()
    print('-' * 60)
    print()

    output_path = "results/" + input(
        "Введите название файла (.txt), в который выводится вся информация: "
    )
    if not re.search(r"[.]txt$", output_path):
        sys.exit("Неверный формат файла (необходим .txt)")
    print("Выходной файл " + output_path + " принят и будет создан в папке /results")

    print()
    print('-' * 60)
    print()

    print("Выполнить ли подсчет лемм (нормальных форм) слов из файла? (y/n)")
    match input().lower().strip():
        case "y":
            lm_count, lm_ranged = tj.ranged_lemmas(
                words
            )  # получаем общее число лемм в тексте (с повторами) + отсортированный список лемм по числу вхождений
            lm_flg = True  # поднимаем флаг, что статистика была собрана
        case "n":
            pass
        case _:
            sys.exit("Неверный ввод.")

    if lm_flg:
        lemmas_freq = dict()  # относительне частоты по леммам
        rank = dict()  # хотим получить ранг для каждой леммы
        print("Выполнить подсчет относительных частот и ранга лемм в файл? (y/n)")
        match input().lower().strip():
            case "y":
                lemmas_freq = tj.relative_freq(lm_ranged)  # подсчитываем отн. частоты
                r = {
                    key: rank
                    for rank, key in enumerate(sorted(set(lemmas_freq.values()), reverse=True), 1)
                }
                rank_lm = {k: r[v] for k, v in lemmas_freq.items()}
                f = open(
                    output_path, mode="a", encoding="utf-8"
                )  # записываем собранную информацию в файл
                f.write("Относительные частоты и ранг лемм.\n")
                for word in lemmas_freq:
                    f.write(
                        word.upper()
                        + " | ранг: %d |" % rank_lm[word]
                        + " отн. частота (Fr): %.4f |" % lemmas_freq[word]
                        + " абс. частота (Fa): %d\n" % lm_ranged[word]
                    )
                f.write("\n" + "-" * 50 + "\n")
                f.close()
                lm_rf_flg = True  # поднимаем флаг, что статистика по частотам лемм была собрана
            case "n":
                pass
            case _:
                sys.exit("Неверный ввод.")
    
        print()
        print('-' * 60)
        print()
    
        print("Вывести среднюю длину лемм? (y/n)")
        match input().lower().strip():
            case "y":
                lm_sum = sum(map(len, lm_ranged.keys()))  # считаем суммарную длину всех лемм в тексте
                print("Средняя длина лемм в тексте: %.4f" % (lm_sum / len(lm_ranged)))
            case "n":
                pass
            case _:
                sys.exit("Неверный ввод.")
        if lm_rf_flg:  # если частоты подсчитаны, то предлагаем вывести на экран
        
            print()
            print('-' * 60)
            print()
        
            print("Вывести самые частые леммы на экран (не более 20)? (y/n)")
            match input().lower().strip():
                case "y":
                    line = input("Введите число от 1 до 20: ")
                    if line.isdigit():  # проверка на число
                        num = int(line)
                        if 1 <= num <= 20:  # проверка на диапозон
                            i = 0
                            for word in lemmas_freq:
                                i += 1
                                print(
                                    word.upper()
                                    + " | ранг: %d |" % rank_lm[word]
                                    + " отн. частота (Fr): %.4f |" % lemmas_freq[word]
                                    + " абс. частота (Fa): %d |" % lm_ranged[word]
                                )
                                if i >= num:
                                    break
                        else:
                            print("Число неверное, пропустим этот этап :(")
                    else:
                        print("Это не число 0_o")
                case "n":
                    pass
                case _:
                    sys.exit("Неверный ввод.")

    print()
    print('-' * 60)
    print()

    print("Выполнить ли подсчет различных словоформ из файла? (y/n)")
    match input().lower().strip():
        case "y":
            wf_count, wf_ranged = tj.ranged_wordforms(words)  # получаем общее число словоформ в тексте (с повторами) + отсортированный список словоформ по числу вхождений
            wf_flg = True  # поднимаем флаг, что статистика была собрана
        case "n":
            pass
        case _:
            sys.exit("Неверный ввод.")

    if wf_flg:
        wordform_freq = dict()  # относительные частоты по словоформам
        rank = dict()  # ранги словоформ в тексте
    
        print()
        print('-' * 60)
        print()
    
        print("Выполнить подсчет относительных частот словоформ в файл? (y/n)")
        match input().lower().strip():
            case "y":
                wordform_freq = tj.relative_freq(wf_ranged)  # подсчет отн. частоты словоформ
                r = {
                    key: rank
                    for rank, key in enumerate(sorted(set(wordform_freq.values()), reverse=True), 1)
                }
                rank_wf = {k: r[v] for k, v in wordform_freq.items()}
                f = open(output_path, mode="a", encoding="utf-8")
                f.write("Относительные частоты и ранг словоформ." + "\n")
                for word in wordform_freq:
                    f.write(
                        word.upper()
                        + " | ранг: %d" % rank_wf[word]
                        + " отн. частота: %.4f" % wordform_freq[word]
                        + " абс. частота (Fa): %d\n" % wf_ranged[word]
                    )
                f.write("\n" + "-" * 50 + "\n")
                f.close()
                wf_rf_flag = True  # поднимаем флаг, что частоты подсчитаны
            case "n":
                pass
            case _:
                sys.exit("Неверный ввод.")
            
        print()
        print('-' * 60)
        print()
    
        print("Вывести среднюю длину словоформ? (y/n)")
        match input().lower().strip():
            case "y":
                wf_sum = sum(map(len, wf_ranged.keys()))
                print("Средняя длина словоформ в тексте: %.4f" % (wf_sum / len(wf_ranged)))
            case "n":
                pass
            case _:
                sys.exit("Неверный ввод.")
    
        print()
        print('-' * 60)
        print()
    
        print("Вывести самые частые словоформы (не более 20)? (y/n)")
        if wf_rf_flag:  # если частоты подсчитаны, то предлагаем вывести на экран
            match input().lower().strip():
                case "y":
                    line = input("Введите число от 1 до 20: ")
                    if line.isdigit():
                        num = int(line)
                        if 1 <= num <= 20:
                            i = 0
                            for word in wordform_freq:
                                i += 1
                                print(
                                    word.upper()
                                    + " | ранг: %d |" % rank_wf[word]
                                    + " отн. частота (Fr): %.4f |" % wordform_freq[word]
                                    + " абс. частота (Fa): %d" % wf_ranged[word]
                                )
                                if i >= num:
                                    break
                        else:
                            print("Число неверное, пропустим этот этап :(")
                    else:
                        print("Это не число 0_o")
                case "n":
                    pass
                case _:
                    sys.exit("Неверный ввод.")
                
    print()
    print('-' * 60)
    print()


    print("Провести полный морфологический анализ слов в тексте? (y/n)")
    match input().lower().strip():
        case "y":
            outxlsx = "results/" + input(
                "Введите название файла, в который выводится морфологический разбор (формат .xlsx): "
            )
            if not re.search(r"[.]xlsx$", outxlsx):
                sys.exit("Неверный формат файла (необходим .xlsx)")
            print("Файл " + outxlsx + " успешно сформирован и сохранен в папке /results")
            w_info = []
            for word in tqdm(words):
                w_info += [
                    morph.morphological_analysis(word)
                ]  # для каждого слова запускаем морфологический анализ
            words_data = pd.DataFrame(
                data=w_info, index=words
            )  # формируем таблицу данных для дальнейшего вывода
            print("Части речи отсортированы по частоте встречи")
            print(words_data["Часть речи"].value_counts())
            words_data[~words_data.index.duplicated(keep='first')].to_excel(outxlsx) # убираем повторяющиеся слова и конвертируем в таблицу
            plt.figure(figsize=(12, 6))
            tj.graph_morph(words_data["Часть речи"].value_counts())
            plt.show()
        
            summary_plot_info_morph = words_data["Часть речи"].value_counts() # сохраняем данные для подведения итогов
            morph_flg = True # морфологический анализ выполнен успешно
        case "n":
            pass
        case _:
            sys.exit("Неверный ввод.")

    print()
    print('-' * 60)
    print()

    print("Анализировать текст на выполнение закона Хипса для лемм? (y/n)")
    match input().lower().strip():
        case "y":
            print("Введите размер разбиения текста (на сколько частей):")
            num = input()
            if num.isdigit():
                N = int(num)
            else:
                N = 100
            summary_plot_info_lemm = tj.get_heaps_lm(words, N)
            if summary_plot_info_lemm:
                heaps_lm_flg = True # Хипс для лемм построен
        case "n":
            pass
        case _:
            sys.exit("Неверный ввод.")

    print()
    print('-' * 60)
    print()

    print("Анализировать текст на выполнение закона Хипса для словоформ? (y/n)")
    match input().lower().strip():
        case "y":
            print("Введите размер разбиения текста (на сколько частей):")
            num = input()
            if num.isdigit():
                N = int(num)
            else:
                N = 100
            summary_plot_info_wf = tj.get_heaps_wf(words, N)
            if summary_plot_info_wf:
                heaps_wf_flg = True
        case "n":
            pass
        case _:
            sys.exit("Неверный ввод.")

    print()
    print('-' * 60)
    print()

    print('Итог по работе анализатора.')
    print('Использование списка стоп-слов: ' + str(sw_flg))
    if lm_flg:
        print()
        print("Информация по леммам")
        lm_sum = sum(map(len, lm_ranged.keys()))
        print("Средняя длина лемм в тексте: %.4f" % (lm_sum / len(lm_ranged)))
        if lm_rf_flg:
            print("Самые частые 5 лемм: ")
            i = 0
            for word in lemmas_freq:
                i += 1
                print(
                    word.upper()
                    + " | ранг: %d |" % rank_lm[word]
                    + " отн. частота (Fr): %.4f |" % lemmas_freq[word]
                    + " абс. частота (Fa): %d |" % lm_ranged[word]
                )
                if i > 4:
                    break

    if wf_flg: 
        print()
        print("Информация по словоформам")
        wf_sum = sum(map(len, wf_ranged.keys()))
        print("Средняя длина словоформ в тексте: %.4f" % (wf_sum / len(wf_ranged)))
        if wf_rf_flag:
            print("Самые частые 5 словоформ: ")
            i = 0
            for word in wordform_freq:
                i += 1
                print(
                    word.upper()
                    + " | ранг: %d |" % rank_wf[word]
                    + " отн. частота (Fr): %.4f |" % wordform_freq[word]
                    + " абс. частота (Fa): %d" % wf_ranged[word]
                )
                if i > 4:
                    break
        
    print()
    print('-' * 60)
    print()
        

    if any([heaps_lm_flg, heaps_wf_flg, morph_flg]): plt.figure(figsize=(20, 11)) # если был задан хотя бы один график, то начинаем создавать сводный
    if morph_flg:
        print("Статистика по числу различных частей речи")
        print(words_data["Часть речи"].value_counts())
    
        if (not heaps_lm_flg) and (not heaps_wf_flg):
            tj.graph_morph(summary_plot_info_morph)
        else:
            plt.suptitle("Итоги в графиках по тексту: " + file_path, fontsize=20)
            plt.subplot(121)
            tj.graph_morph(summary_plot_info_morph)
            if heaps_lm_flg and heaps_wf_flg:
                plt.subplot(222)
                tj.plot_heaps_lm(*summary_plot_info_lemm)
                plt.legend()
                plt.subplot(224)
                tj.plot_heaps_wf(*summary_plot_info_wf)
                plt.legend()
            elif heaps_lm_flg:
                plt.subplot(122)
                tj.plot_heaps_lm(*summary_plot_info_lemm)
                plt.legend()
            elif heaps_wf_flg:
                plt.subplot(122)
                tj.plot_heaps_lm(*summary_plot_info_wf)
                plt.legend()
    elif heaps_lm_flg and heaps_wf_flg:
        plt.subplot(121)
        tj.plot_heaps_lm(*summary_plot_info_lemm)
        plt.legend()
        plt.subplot(122)
        tj.plot_heaps_wf(*summary_plot_info_wf)
        plt.legend()
    elif heaps_lm_flg:
        tj.plot_heaps_lm(*summary_plot_info_lemm)
        plt.legend()
    elif heaps_wf_flg:
        tj.plot_heaps_lm(*summary_plot_info_wf)
        plt.legend()

    if any([heaps_lm_flg, heaps_wf_flg, morph_flg]):
        plot_adr = 'graphs/summary_' + str(np.random.randint(10000, 99999)) + '.png'
        print('-'*60)
        print('Итоговый график сохранен в ' + plot_adr)
        print('-'*60)
        plt.savefig(plot_adr)

    print("БОНУС. Провести анализ выполнения закона Хипса для словоформ для всех 8 тестовых текстов? (y/n)")
    match input().strip().lower():
        case "y":
            plt.figure(figsize=(16,10))
            files = ['texts/war_and_peace.txt', 'texts/crime_and_punishment.txt', 'texts/constitution.txt', 'texts/habr_kaggle_farm.txt', 'texts/institutionalism.txt', 'texts/os_mash.txt', 'texts/description_big_task.txt', 'texts/copypaste_proof.txt']
            for file_path in tqdm(files):
                f = open(file_path, mode="r", encoding="utf-8")
                text = f.read()
                f.close()
                words = word_tokenize(
                    tj.filter_punct(text.lower())
                )  # разбиваем весь текст на отдельные токены + убираем букву ё и всю пунктуацию
                if sw_flg:  # убираем стоп-слова, если есть соотв. флаг
                    words = [w for w in words if w not in tj.stop_words]
                words_num = len(words)  # общее число слов в тексте
                unique = set()
                unique_num = []
                step = len(words) // 100
                for i in range(step, (step * 99) + 1, step):
                    unique_num += [len(unique)]
                    unique |= set(words[i - step : i])
                unique_num += [len(list(set(words)))]
                tj.plot_heaps_wf(unique_num, step, label=file_path[6:-4], plot_heaps=False)
            plt.legend()
            plt.show()
        case "n":
            pass
        case _:
            sys.exit("Неверный ввод.")
