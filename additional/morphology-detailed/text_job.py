from nltk.corpus import stopwords
from pymorphy3 import MorphAnalyzer
import matplotlib.pyplot as plt
from tqdm import tqdm
import numpy as np

punctuation = ',.!?…;:-()[]"`}{*%—«»–”“/\\&№=+*'
pm = MorphAnalyzer()

def filter_punct(text): # Удаляем все знаки пунктуации и цифры, заменяем ё на е
    for sym in punctuation:
        text = text.replace(sym, '')
    text = text.replace('ё', 'е') # все токены будут в нижнем регистре, поэтому достаточно заменить лишь 'ё'
    text = ''.join([i for i in text if not i.isdigit()]) # удаляем слова содержащие числа и собственно числа
    return text

def form_stop_words(): # формируем список стоп-слов
    global stop_words
    stop_words = stopwords.words("russian") # пополняем список стоп-слов, потому что он недостаточно полный
    stop_words.extend(["''", "г", 'м', 'ф', 'ю', 'т', 'е', "из", "к", "с", "мной", "мною", "тебе", "тобой", "тобою", "нему", \
                    "ею", "нею", "ими", "ним", "весьма", "как-то", "как-либо", "как-нибудь",\
                    "какое", "какие", "какого", "каких", "какому", "каким", "какою", "какими", "каком",\
                    "такое", "такая", "такие", "такого", "таких", "таким", "такому", "такую", "такими",\
                    "где-нибудь", "где-либо", "где-то", "кое-как", "кое-где", "кое-кто", \
                    "кое-что", "кое-куда", "куда-нибудь", "куда-либо", "куда-то", "кто", "вы", "вам", "вами",\
                    "вас", "этот", "это", "эти", "эта", "эту", "ту", "та", "тот", "те", \
                    "около", "ибо", "среди", "обо", "напротив", "зато", "хотя", "ко", "со"]) # стоит учитывать, что сюда входят и большинство местоимений

def ranged_wordforms(words): # формирует словарь с числом вхождений словоформ (по сути словарь абс. частот)
    wordform = dict()
    for word in tqdm(words):
        if wordform.get(word, -1) == -1:
            wordform[word] = 1
        else:
            wordform[word] += 1 # если слово есть увеличиваем счетчик на 1
    wordforms_number = sum(wordform.values()) # число всех словоформ
    ranged = dict(sorted(wordform.items(), key=lambda x: x[1], reverse=True))
    return wordforms_number, ranged

def ranged_lemmas(words): # формирует словарь с числом вхождений лемм (по сути словарь абс. частот)
    lemmas = dict()
    for word in tqdm(words):
        lemm = pm.parse(word)[0].normal_form # берем наиболее близкий вариант леммы
        if lemmas.get(lemm, -1) == -1:
            lemmas[lemm] = 1
        else:
            lemmas[lemm] += 1 # если слово есть увеличиваем счетчик на 1
    lemmas_number = sum(lemmas.values()) # число всех лемм
    ranged = dict(sorted(lemmas.items(), key=lambda x: x[1], reverse=True)) # делаем отсортированный список по числу словоформ
    return lemmas_number, ranged

def relative_freq(dictionary): # По словарю вычисляет относительную частоту его эл-ов плюс сортирует по ней
    total = sum(dictionary.values()) # Всего слов
    freq_dict = dict()
    for word in dictionary.keys():
        freq_dict[word] = dictionary[word] / total # Относительная частота
    sorted_fd = dict(sorted(freq_dict.items(), key=lambda x: x[1], reverse=True))
    return sorted_fd

def graph_morph(word_counts): # Диаграмма числа слов по частям речи
    words = dict(word_counts)
    plt.title("Диаграмма частот частей речи", fontsize=18)
    plt.xlabel("Часть речи", fontsize=16)
    plt.ylabel("Частота", fontsize=16)
    plt.xticks(rotation=20) # Поворачиваем слова на оси для лучшей читаемости
    plt.bar(list(words.keys()), list(words.values()))

def plot_heaps_lm(unique_num, step, label="unique_lemms", plot_heaps=True, a=45, b=0.48): # график закона Хипса для лемм
    plt.title(
        "Закон Хипса и график появления новых лемм в тексте",
        fontsize=18,
    )
    plt.xlabel("Размер исходного текста в долях", fontsize=16)
    plt.ylabel("Число уникальных лемм", fontsize=16)
    plt.plot(np.linspace(0, 1, 100), unique_num, label=label)
    if plot_heaps:
        plt.plot(
            np.linspace(0, 1, 100), a * ((step * np.arange(100)) ** b), label="Heaps"
        )
    

def plot_heaps_wf(unique_num, step, label="unique_wordforms", plot_heaps=True, a=35, b=0.58): # график закона Хипса для словоформ
    plt.title(
        "Закон Хипса и график появления новых словоформ в тексте",
        fontsize=18,
    )
    plt.xlabel("Размер исходного текста в долях", fontsize=16)
    plt.ylabel("Число уникальных словоформ", fontsize=16)
    plt.plot(np.linspace(0, 1, 100), unique_num, label=label)
    if plot_heaps:
        plt.plot(
            np.linspace(0, 1, 100), a * ((step * np.arange(100)) ** b), label="Heaps"
        )
        
def get_heaps_lm(words, N = 100): # построение графика закона Хипса для лемм
    lemms = [pm.parse(word)[0].normal_form for word in tqdm(words)]
    if len(lemms) < N:
        print("Анализ невозможен: текст слишком мал!")
        return False
    else:
        print(
            "Закон Хипса: Число уникальных слов = a * N^b, где a,b - константы, N - всего число слов в фрагменте"
        )
        print('Были подобраны следующие константы (под леммы) (если настраивать по "Война и мир"): a = 45 и b = 0.48')
        unique = set()
        unique_num = []
        step = len(lemms) // N
        for i in range(step, (step * (N-1)) + 1, step):
            unique_num += [len(unique)]
            unique |= set(lemms[i - step : i])
        unique_num += [len(list(set(lemms)))]
        plt.figure(figsize=(12,8))
        plot_heaps_lm(unique_num, step)
        plt.legend()
        plt.show()
        return (unique_num, step)
    
def get_heaps_wf(words, N=100): # построение графика закона Хипса для словоформ
    if len(words) < N:
        print("Анализ невозможен: текст слишком мал!")
        return False
    else:
        print(
            "Закон Хипса: Число уникальных слов = a * N^b, где a,b - константы, N - всего число слов в фрагменте"
        )
        print('Были подобраны следующие константы (под словоформы) (если настраивать по "Война и мир"): a = 35 и b = 0.58')
        unique = set()
        unique_num = []
        step = len(words) // N
        for i in range(step, (step * (N-1)) + 1, step):
            unique_num += [len(unique)]
            unique |= set(words[i - step : i])
        unique_num += [len(list(set(words)))]
        plt.figure(figsize=(12,8))
        plot_heaps_wf(unique_num, step, a=35, b=0.58)
        plt.legend()
        plt.show()
        return (unique_num, step)
