"""
Модуль для сравнения двух текстов.
Содержит класс LexiconComparator для сопоставления характеристик текстов.
"""

from lexicon_core import TextLexicon


class LexiconComparator:
    """
    Класс для сравнительного анализа двух текстов.

    Выполняет:
    - Сравнение базовых статистик
    - Сравнение лексических метрик
    - Сравнение распределения частей речи (в процентах!)
    - Расчет различий между текстами

    Attributes:
        text1 (TextLexicon): первый текст для сравнения
        text2 (TextLexicon): второй текст для сравнения
    """

    def __init__(self, text1: TextLexicon, text2: TextLexicon):
        """
        Инициализация компаратора.

        Args:
            text1: объект TextLexicon первого текста
            text2: объект TextLexicon второго текста
        """
        self.text1 = text1
        self.text2 = text2

    def compare_statistics(self):
        """
        Сравнение базовых статистических характеристик.

        Returns:
            dict: сравнение для каждой характеристики с разницей
        """
        stats1 = self.text1.get_basic_stats()
        stats2 = self.text2.get_basic_stats()

        comparison = {}
        for key in stats1.keys():
            comparison[key] = {
                'text1': stats1[key],
                'text2': stats2[key],
                'difference': stats1[key] - stats2[key]
            }

        return comparison

    def compare_metrics(self):
        """
        Сравнение всех лексических метрик.

        Returns:
            dict: сравнение метрик с разницей
        """
        metrics1 = self.text1.get_all_metrics()
        metrics2 = self.text2.get_all_metrics()

        comparison = {}
        for key in metrics1.keys():
            comparison[key] = {
                'text1': metrics1[key],
                'text2': metrics2[key],
                'difference': metrics1[key] - metrics2[key]
            }

        return comparison

    def compare_pos_distribution(self):
        """
        Сравнение распределения частей речи (ОТНОСИТЕЛЬНОЕ!).

        ВАЖНО: Используются проценты, а не абсолютные значения,
        что позволяет корректно сравнивать тексты разного размера.

        Returns:
            dict: для каждой части речи:
                - text1_count: абсолютное количество в тексте 1
                - text2_count: абсолютное количество в тексте 2
                - text1_percent: процент в тексте 1
                - text2_percent: процент в тексте 2
                - difference: разница в процентных пунктах
        """
        pos1 = self.text1.get_pos_distribution()
        pos2 = self.text2.get_pos_distribution()

        # Вычисляем общее количество слов для расчета процентов
        total1 = sum(pos1.values())
        total2 = sum(pos2.values())

        # Объединяем все части речи из обоих текстов
        all_pos = set(pos1.keys()) | set(pos2.keys())

        comparison = {}
        for pos in all_pos:
            count1 = pos1.get(pos, 0)
            count2 = pos2.get(pos, 0)

            # КЛЮЧЕВОЙ МОМЕНТ: рассчитываем проценты для корректного сравнения
            percent1 = (count1 / total1 * 100) if total1 > 0 else 0
            percent2 = (count2 / total2 * 100) if total2 > 0 else 0

            comparison[pos] = {
                'text1_count': count1,
                'text2_count': count2,
                'text1_percent': percent1,
                'text2_percent': percent2,
                'difference': percent1 - percent2
            }

        return comparison

    def compare_top_words(self, n=10):
        """
        Сравнение самых частотных слов обоих текстов.

        Args:
            n (int): количество слов для сравнения

        Returns:
            dict: топ слов каждого текста
        """
        return {
            'text1': self.text1.get_top_lemmas(n),
            'text2': self.text2.get_top_lemmas(n)
        }

    def find_unique_words(self, min_freq=2):
        """
        Поиск уникальных слов в каждом тексте.

        Слова, которые встречаются в одном тексте, но не встречаются в другом.

        Args:
            min_freq (int): минимальная частота слова для учета

        Returns:
            dict: списки уникальных слов для каждого текста
        """
        from collections import Counter

        lemmas1_freq = Counter(self.text1.lemmas)
        lemmas2_freq = Counter(self.text2.lemmas)

        # Слова с частотой >= min_freq
        words1 = {word for word, freq in lemmas1_freq.items() if freq >= min_freq}
        words2 = {word for word, freq in lemmas2_freq.items() if freq >= min_freq}

        return {
            'unique_to_text1': sorted(words1 - words2),
            'unique_to_text2': sorted(words2 - words1),
            'common': sorted(words1 & words2)
        }
