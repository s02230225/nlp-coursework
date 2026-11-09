from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from nltk.probability import FreqDist
from pymorphy3 import MorphAnalyzer
import matplotlib.pyplot as plt
import os

# Проверяем и создаем директорию 'results', если ее нет
if not os.path.exists('results'):
    os.makedirs('results')

punctuation = ',.!?…;:-()[]"`}{*%—«»–”“/&\№'
pm3 = MorphAnalyzer()
stop_words = [] # Инициализируем глобальный список стоп-слов

def no_punctuation_yo(text):
    for el in punctuation:
        text = text.replace(el, '')
    text = text.replace('ё', 'е')
    text = ''.join([i for i in text if not i.isdigit()])
    return text

def form_stop_words(additional_stopwords_file):
    global stop_words
    stop_words = stopwords.words("russian")

    try:
        _ensure_file(additional_stopwords_file)
        with open(additional_stopwords_file, 'r', encoding='utf-8') as f:
            additional = [line.strip().lower() for line in f if line.strip()]
            stop_words.extend(additional)
    except FileNotFoundError:
        print(f"Файл '{additional_stopwords_file}' не найден. Будут использованы только стандартные стоп-слова NLTK.")
    
    stop_words.extend(["''", "n"])
    # Уберём дубли и приведём к списку
    stop_set = {w for w in stop_words if w}
    stop_words = sorted(stop_set)


def _ensure_file(path: str):
    """Гарантирует, что файл существует (создаёт пустой при отсутствии)."""
    os.makedirs(os.path.dirname(path), exist_ok=True) if os.path.dirname(path) else None
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            pass

def _normalize_tokens(raw: str) -> list[str]:
    """Нормализует строку токенов: разделяет по запятым/пробелам, чистит, ловерит."""
    # Разрешим и запятые, и пробелы как разделители
    tokens = [t.strip().lower() for t in raw.replace(",", " ").split()]
    return [t for t in tokens if t]

def add_user_stopwords_interactive(file_path: str = "additional_stopwords.txt"):
    """
    Интерактивно добавляет стоп-слова, дописывая их в файл.
    Пустая строка — завершение ввода.
    Дубликаты игнорируются.
    """
    _ensure_file(file_path)

    # читаем текущее содержимое, чтобы не плодить дубли
    with open(file_path, "r", encoding="utf-8") as f:
        existing = {line.strip().lower() for line in f if line.strip()}
        print(existing)

    print("Введите стоп-слова (через запятую или пробелы). Пустая строка — завершить.")
    added_total = 0
    while True:
        try:
            line = input("> ").strip()
        except EOFError:
            break
        if not line:
            break
        new_tokens = _normalize_tokens(line)
        # оставляем только те, которых ещё нет
        to_append = [w for w in new_tokens if w not in existing]
        if to_append:
            with open(file_path, "a", encoding="utf-8") as f:
                for w in to_append:
                    f.write(w + "\n")
                    existing.add(w)
            added_total += len(to_append)
            print(f"Добавлено: {', '.join(to_append)}")
        else:
            print("Все введённые слова уже есть в файле.")

    print(f"Готово. Всего новых слов: {added_total}")

def add_user_stopwords(words: list[str], file_path: str = "additional_stopwords.txt"):
    """
    Неинтерактивная версия: дописывает переданный список слов.
    Дубликаты игнорируются.
    """
    _ensure_file(file_path)

    with open(file_path, "r", encoding="utf-8") as f:
        existing = {line.strip().lower() for line in f if line.strip()}

    # нормализуем вход
    clean = []
    for w in words:
        clean.extend(_normalize_tokens(w))

    to_append = [w for w in clean if w not in existing]
    if to_append:
        with open(file_path, "a", encoding="utf-8") as f:
            for w in to_append:
                f.write(w + "\n")
    return len(to_append)

def count_lemmas(text):
    lemmas = {}
    for word in text:
        p = pm3.parse(word)[0]
        if p.normal_form in lemmas:
            lemmas[p.normal_form] += 1
        else:
            lemmas[p.normal_form] = 1
    total_words = sum(lemmas.values())
    sortedlemmas = dict(sorted(lemmas.items(), key=lambda x: x[1], reverse=True))
    return sortedlemmas, total_words

def count_wordforms(text):
    wordforms = {}
    for word in text:
        if word in wordforms:
            wordforms[word] += 1
        else:
            wordforms[word] = 1
    total_wordforms = sum(wordforms.values())
    sorted_wf = dict(sorted(wordforms.items(), key=lambda x: x[1], reverse=True))
    return sorted_wf, total_wordforms

def Rel_Freq(dic):
    total = sum(dic.values())
    if total == 0:
        return {}
    freq_dic = {word: round(count / total, 2) for word, count in dic.items()}
    sorted_fd = dict(sorted(freq_dic.items(), key=lambda x: x[1], reverse=True))
    return sorted_fd

def length_wordforms(dic):
    total_occurrences = sum(dic.values())
    if total_occurrences == 0:
        return {}, 0.0
    lengths = {word: len(word) * count for word, count in dic.items()}
    average_len = round(sum(lengths.values()) / total_occurrences, 2)
    sorted_lengths = dict(sorted(lengths.items(), key=lambda x: x[1], reverse=True))
    return sorted_lengths, average_len

def Stem_Freq(text, outfile):
    stemmer = SnowballStemmer("russian")
    stemmed_words = [stemmer.stem(word) for word in text]

    freq = FreqDist(stemmed_words)
    
    # Записываем в файл полную информацию
    with open(outfile, 'a', encoding='utf-8') as f:
        f.write('--- Список основ и их количество (с помощью FreqDist) ---\n')
        for i, (word, count) in enumerate(freq.most_common()):
            f.write(f'{word}\t{count}\n')
        f.write('\n' + '_' * 60 + '\n\n')

    # Выводим на экран топ-5
    print("\nТоп-5 основ слов:")
    for i, (word, count) in enumerate(freq.most_common(5)):
        print(f"{word}: {count}")

def how_rich_is_lexic(dic):
    total_occurrences = sum(dic.values())
    if total_occurrences == 0:
        return 0.0
    res = len(dic) / total_occurrences
    return round(res, 2)

def letters_with_graph(text, file_name, save_dir='results', show=False):
    os.makedirs(save_dir, exist_ok=True)

    alphabet = "абвгдежзийклмнопрстуфхцчшщъыьэюя"
    new_text = text.lower().replace(' ', '')
    d = {el: new_text.count(el) for el in alphabet if new_text.count(el) > 0}

    base = os.path.splitext(os.path.basename(file_name))[0]
    outpath = os.path.join(save_dir, f"letter_frequency_{base}.png")

    plt.figure(figsize=(10, 6))
    plt.title(f"Частота встречания букв в тексте: {os.path.basename(file_name)}")
    plt.xlabel("Буквы")
    plt.ylabel("Частота")
    plt.bar(list(d.keys()), list(d.values()))
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(outpath)
    if show:
        plt.show()
    plt.close()
    return d, outpath


def POS_graph(ser, file_name, save_dir='results', show=False):
    os.makedirs(save_dir, exist_ok=True)

    bd = dict(ser)
    x_axis = list(bd.keys())
    y_axis = list(bd.values())

    base = os.path.splitext(os.path.basename(file_name))[0]
    outpath = os.path.join(save_dir, f"pos_frequency_{base}.png")

    plt.figure(figsize=(12, 6))
    plt.title(f"Частота частей речи в тексте: {os.path.basename(file_name)}")
    plt.xlabel("Части речи")
    plt.ylabel("Частота")
    plt.xticks(rotation=45, ha='right')
    plt.bar(x_axis, y_axis)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(outpath)
    if show:
        plt.show()
    plt.close()
    return outpath


def POS_pie_chart(ser, file_name, save_dir='results', show=False):
    os.makedirs(save_dir, exist_ok=True)

    bd = dict(ser)
    labels = list(bd.keys())
    sizes = list(bd.values())

    base = os.path.splitext(os.path.basename(file_name))[0]
    outpath = os.path.join(save_dir, f"pos_pie_chart_{base}.png")

    plt.figure(figsize=(10, 10))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.title(f"Процентное соотношение частей речи в тексте: {os.path.basename(file_name)}")
    plt.axis('equal')
    plt.tight_layout()
    plt.savefig(outpath)
    if show:
        plt.show()
    plt.close()
    return outpath
