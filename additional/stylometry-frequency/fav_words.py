import os
from natasha import Segmenter, MorphVocab, NewsEmbedding, NewsMorphTagger, Doc
from collections import Counter
import requests
import json
import time

api_cache = {}
# здесь устанавливаем словарь
word_freq_file = "api_cache.json"


def load_cache():
    global api_cache
    try:
        with open(word_freq_file, 'r', encoding='utf-8') as f:
            api_cache = json.load(f)
        print(f"Загружен кэш с частотами")
    except Exception as e:
        print(f"Ошибка загрузки кэша: {e}")
        api_cache = {}


def save_cache():
    try:
        with open(word_freq_file, 'w', encoding='utf-8') as f:
            json.dump(api_cache, f, ensure_ascii=False, indent=2)
        print(f"Кэш сохранен")
    except Exception as e:
        print(f"Ошибка сохранения кэша: {e}")



def define_word_freq(word, pos, max_tries=10):
    api_cache_key = word
    if api_cache_key in api_cache:
        return api_cache[api_cache_key]

    url = "https://ruscorpora.ru/api/v1/word-portrait/"
    trans_pos = {
        'NOUN': 'S',
        'VERB': 'V',
        'ADJ': 'A',
        'ADV': 'ADV'
    }
    pos_api = trans_pos.get(pos, 'S')
    query = {
        'lemma': word,
        'pos': pos_api,
        'corpus': {
            'type': 'MAIN'
            },
        'resultType': ['PORTRAIT_FREQUENCY'],
        'seed': 8918596
    }

    token = os.environ.get("RUSCORPORA_API_TOKEN")
    if not token:
        raise RuntimeError("Задайте RUSCORPORA_API_TOKEN перед обращением к частотному API")
    headers = {"Authorization": f"Bearer {token}"}
    params = {"query": json.dumps(query, ensure_ascii=False)}
    for i in range(max_tries):
        try:
            time.sleep(1)
            response = requests.get(url, params=params, headers=headers, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if 'frequencyData' in data and 'ipm' in data['frequencyData']:
                    ipm = data['frequencyData']['ipm']
                    api_cache[api_cache_key] = ipm
                    save_cache()
                    print(word, ipm)
                    return ipm
                print(f'нет данных об ipm для слова {word}')
                break
            elif response.status_code == 429:
                print(f'Превышен лимит запросов для {word}')
                time.sleep(26)
                continue
            else:
                print(f'ошибка запроса, статус {response.status_code}, попытка {i + 1}')
                if i < max_tries - 1:
                    time.sleep(3)
                    continue
        except requests.exceptions.Timeout:
            print(f'превышено время запроса для {word}, попытка {i + 1}')
            if i < max_tries - 1:
                continue
        except requests.exceptions.ConnectionError:
            print(f"ошибка соединения для '{word}', попытка {i + 1}")
            if i < max_tries - 1:
                time.sleep(5)
                continue

        except Exception as e:
            print(f"ошибка для '{word}': {e}, попытка {i+ 1}")
            if i < max_tries - 1:
                time.sleep(3)
                continue
    error_value = 0.000001
    api_cache[api_cache_key] = error_value
    save_cache()
    print(f"Не удалось получить ipm для слова {word}, {max_tries} попыток")
    return error_value


def process_text(text):
    segmenter = Segmenter()
    morph_vocab = MorphVocab()
    emb = NewsEmbedding()
    morph_tagger = NewsMorphTagger(emb)
    doc = Doc(text)
    doc.segment(segmenter)
    doc.tag_morph(morph_tagger)

    lemmas = []
    count = 0 # сколько всего слов

    for token in doc.tokens:
        token.lemmatize(morph_vocab)

        if token.pos not in ['PUNCT', 'SYM']:
            count += 1

        if token.pos in {'NOUN', 'ADJ', 'VERB', 'ADV'} and token.pos != 'PROPN':
            lemmas.append((token.lemma, token.pos))

    return lemmas, count


def find_fav_words(all_lemmas, word_in_diff_books, min_freq, min_k):
    fav_words_parts = {
        'NOUN': [],
        'VERB': [],
        'ADJ': [],
        'ADV': []
    }
    for part in ['NOUN', 'VERB', 'ADJ', 'ADV']:
        part_lemmas = [lemma for lemma, pos_val in all_lemmas if pos_val == part]
        unique_count = Counter(part_lemmas)
        print(unique_count.most_common(10))
        k = 0
        checked_words = 0
        max_checks = 80
        for word, count in unique_count.most_common():
            if k >= 20:
                break
            checked_words += 1

            k_books = word_in_diff_books.get(word, 0)
            if k_books >= min_k and count >= min_freq:
                nkrya_ipm = define_word_freq(word, part)
                if nkrya_ipm >= 1:
                    fav_words_parts[part].append((word, count, nkrya_ipm, k_books))
                    k += 1

    print(fav_words_parts)
    return fav_words_parts


def analyze_books(books):
    all_lemmas = [] # тут будут собираться слова из всех произведений
    count = 0
    book_data = []
    print('Запускаем обработку произведений')
    for book in books:
        print('Обрабатываем книгу: ', book)
        with open(book, 'r') as f:
            text = f.read()
            lemmas, book_count = process_text(text)
            all_lemmas.extend(lemmas)
            count += book_count
            book_data.append({
                'name': book,
                'lemmas': lemmas,
                'book_count': book_count,
                'unique_words': set(lemma for lemma, pos in lemmas)
            })
            print(f'В книге {book}: {book_count} слов')
    print('Статистика: ')
    print(f'Всего произведений: {len(books)}')
    print(f'Всего слов: {count}')
    print(f'Знаменательных слов (нарицательных): {len(all_lemmas)}')
    # сатистика по произведениям
    word_in_diff_books = {}
    lemma_abs_freq = Counter(lemma for lemma, pos in all_lemmas) # формирует список кортежей (уникальная лемма - частота)
    for word in lemma_abs_freq:
        k = 0
        for book in book_data:
            if word in book['unique_words']:
                k += 1
        word_in_diff_books[word] = k
    min_freq = count / 10000
    min_k = len(books) // 2 + 1
    dict_fav_words = find_fav_words(all_lemmas, word_in_diff_books, min_freq, min_k)
    return dict_fav_words


books_tolstoy = [
        'karenina.txt',
        'voskresenie.txt',
        'voyna_i_mir.txt',
        'kreicerova-sonata.txt',
        'kavkazskiy_plennik.txt'
    ]
#book_test = ['test1.txt', 'test2.txt', 'test3.txt']
books_fiction = ['karenina.txt',
        'voskresenie.txt',
        'voyna_i_mir.txt',
        'kreicerova-sonata.txt',
        'kavkazskiy_plennik.txt',
                 'belaya_gvardiya.txt',
                 'idiot.txt',
                 'sobachie_serdce.txt',
                 'master_i_margarita.txt']
#analyze_books(books_fiction)
books_sceince = ['astronomiya.txt',
                 'biologiya.txt',
                 'chemistry.txt',
                 'economy.txt',
                 'geography.txt',
                 'history.txt']
#analyze_books(books_sceince)
books_oficial = ['rf_laws.txt',
                 'trudovoy_kodeks.txt',
                 'semeynyi_kodeks.txt']

#analyze_books(books_oficial)
books_public = ['statii_publicistic.txt', 'belinskiy-statii.txt', 'public_text.txt',
                'recenzia.txt', 'reportazh1.txt']


#analyze_books(books_public)

books_dost = ['CrimeAndPunishment.txt', 'TheDemons.txt', 'TheIdiot.txt']
if __name__ == "__main__":
    load_cache()
    analyze_books(books_dost)
# раскомментировать для проверки на текстах Толстого
#analyze_books(books_tolstoy)
