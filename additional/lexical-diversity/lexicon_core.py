"""
Модуль для анализа лексикона одного текста.
Содержит класс TextLexicon для обработки и анализа русскоязычных текстов.
"""

import pymorphy3
import nltk
from nltk.corpus import stopwords
from collections import Counter
from pathlib import Path
import metrics

# Инициализация морфологического анализатора (один на всю программу)
morph_analyzer = pymorphy3.MorphAnalyzer()


def load_custom_stopwords():
    """
    Загрузка дополнительных стоп-слов из файла config/stopwords_custom.txt.

    Файл содержит дополнительные стоп-слова, которых нет в стандартном
    списке NLTK, с пояснениями по категориям.

    Returns:
        list: список дополнительных стоп-слов
    """
    custom_words = []
    try:
        with open('config/stopwords_custom.txt', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Пропускаем комментарии и пустые строки
                if line and not line.startswith('#'):
                    custom_words.append(line)
        print(f"✓ Загружено {len(custom_words)} дополнительных стоп-слов")
    except FileNotFoundError:
        print("⚠️ Файл config/stopwords_custom.txt не найден")
        print("   Используются только базовые стоп-слова NLTK")
    return custom_words


class TextLexicon:
    """
    Класс для анализа лексикона одного текста.

    Выполняет:
    - Загрузку и очистку текста
    - Токенизацию и лемматизацию
    - Морфологический анализ
    - Расчет статистических характеристик
    - Расчет лексических метрик

    Attributes:
        text_path (str): путь к файлу с текстом
        use_stopwords (bool): использовать ли фильтрацию стоп-слов
        raw_text (str): исходный текст
        tokens (list): список токенов (слов)
        lemmas (list): список лемм (начальных форм)
        pos_tags (list): список частей речи
    """

    def __init__(self, text_path, use_stopwords=True):
        """
        Инициализация анализатора текста.

        Args:
            text_path (str): путь к файлу с текстом
            use_stopwords (bool): использовать ли фильтрацию стоп-слов
        """
        self.text_path = text_path
        self.use_stopwords = use_stopwords
        self.raw_text = ""
        self.tokens = []
        self.lemmas = []
        self.pos_tags = []

        # Загружаем стоп-слова
        if use_stopwords:
            # Базовые стоп-слова из NLTK
            self.stopwords = set(stopwords.words('russian'))
            # Дополнительные стоп-слова из файла
            custom_stopwords = load_custom_stopwords()
            self.stopwords.update(custom_stopwords)
        else:
            self.stopwords = set()

        # Знаки препинания для удаления
        self.punctuation = '.,;:!?…()[]{}«»"\'—–-/@#$%^&*+=_~`|\\<>'

        # Загружаем и обрабатываем текст
        self._load_and_process()

    def _load_and_process(self):
        """Загрузка файла и первичная обработка текста."""
        try:
            with open(self.text_path, 'r', encoding='utf-8') as file:
                self.raw_text = file.read()
            print(f"✓ Файл {Path(self.text_path).name} успешно загружен")
        except FileNotFoundError:
            raise FileNotFoundError(f"Файл {self.text_path} не найден")
        except Exception as e:
            raise Exception(f"Ошибка при чтении файла: {e}")

        # Последовательная обработка
        self._tokenize()
        self._lemmatize()

    def _clean_text(self, text):
        """
        Очистка текста от пунктуации и цифр.

        Args:
            text (str): исходный текст

        Returns:
            str: очищенный текст в нижнем регистре
        """
        # Удаляем знаки препинания
        for char in self.punctuation:
            text = text.replace(char, ' ')

        # Удаляем цифры
        text = ''.join(c if not c.isdigit() else ' ' for c in text)

        # Убираем множественные пробелы
        text = ' '.join(text.split())

        # Нижний регистр, замена ё на е для унификации
        return text.lower().replace('ё', 'е')

    def _tokenize(self):
        """
        Токенизация текста.

        Разбивает текст на отдельные слова (токены),
        фильтрует только русские слова и удаляет стоп-слова.
        """
        cleaned = self._clean_text(self.raw_text)
        words = nltk.word_tokenize(cleaned, language='russian')

        # Фильтруем: только русские слова без стоп-слов
        self.tokens = [
            word for word in words
            if word and any('а' <= c <= 'я' for c in word)
               and (not self.use_stopwords or word not in self.stopwords)
        ]

    def _lemmatize(self):
        """
        Лемматизация и определение частей речи.

        Для каждого токена определяет начальную форму (лемму)
        и часть речи с помощью морфологического анализатора.
        """
        for token in self.tokens:
            parsed = morph_analyzer.parse(token)[0]
            self.lemmas.append(parsed.normal_form)
            self.pos_tags.append(parsed.tag.POS)

    def get_basic_stats(self):
        """
        Базовые статистические характеристики текста.

        Returns:
            dict: словарь с базовыми метриками
        """
        lemma_counts = Counter(self.lemmas)
        token_counts = Counter(self.tokens)

        return {
            'total_tokens': len(self.tokens),
            'unique_lemmas': len(lemma_counts),
            'unique_wordforms': len(token_counts),
            'avg_lemma_length': sum(len(l) for l in self.lemmas) / len(self.lemmas) if self.lemmas else 0,
            'avg_token_length': sum(len(t) for t in self.tokens) / len(self.tokens) if self.tokens else 0,
        }

    def get_all_metrics(self):
        """
        Расчет всех лексических метрик из модуля metrics.py.

        Включает:
        - TTR и его модификации
        - Коэффициенты Хердана
        - Hapax legomena
        - Морфологические коэффициенты

        Returns:
            dict: все рассчитанные метрики
        """
        return metrics.calculate_all_metrics(self.lemmas, self.pos_tags)

    def get_metrics_interpretation(self):
        """
        Интерпретация рассчитанных метрик.

        Returns:
            dict: текстовые интерпретации для каждой метрики
        """
        all_metrics = self.get_all_metrics()
        return metrics.interpret_metrics(all_metrics)

    def get_pos_distribution(self):
        """
        Распределение слов по частям речи.

        Группирует слова по частям речи с преобразованием
        английских обозначений в русские названия.

        Returns:
            dict: количество слов каждой части речи
        """
        pos_map = {
            'NOUN': 'Существительные',
            'VERB': 'Глаголы',
            'INFN': 'Глаголы',
            'ADJF': 'Прилагательные',
            'ADJS': 'Прилагательные',
            'ADVB': 'Наречия',
            'NPRO': 'Местоимения',
            'PREP': 'Предлоги',
            'CONJ': 'Союзы',
            'PRCL': 'Частицы',
            'NUMR': 'Числительные',
            'PRTF': 'Причастия',
            'PRTS': 'Причастия',
            'GRND': 'Деепричастия',
        }

        pos_counter = Counter()
        for lemma, pos in zip(self.lemmas, self.pos_tags):
            pos_name = pos_map.get(pos, 'Прочие')
            pos_counter[pos_name] += 1

        return dict(pos_counter)

    def get_top_lemmas(self, n=20):
        """
        Получение самых частотных лемм.

        Args:
            n (int): количество лемм для возврата

        Returns:
            list: список кортежей (лемма, частота)
        """
        lemma_counts = Counter(self.lemmas)
        return lemma_counts.most_common(n)

    def get_top_by_pos(self, pos_name, n=10):
        """
        Получение самых частотных слов определенной части речи.

        Args:
            pos_name (str): название части речи (существительные, глаголы и т.д.)
            n (int): количество слов для возврата

        Returns:
            list: список кортежей (слово, частота)
        """
        pos_codes = {
            'существительные': ['NOUN'],
            'глаголы': ['VERB', 'INFN'],
            'прилагательные': ['ADJF', 'ADJS'],
            'наречия': ['ADVB'],
        }

        codes = pos_codes.get(pos_name.lower(), [])
        filtered_lemmas = [
            lemma for lemma, pos in zip(self.lemmas, self.pos_tags)
            if pos in codes
        ]

        return Counter(filtered_lemmas).most_common(n)
