"""
Модуль для расчета различных лексических метрик текста.

Содержит функции для вычисления:
- Коэффициентов лексического разнообразия (TTR и его модификации)
- Статистических характеристик распределения слов
- Морфологических коэффициентов
"""

import math
from collections import Counter


def calculate_ttr_metric(lemmas):
    """
    Расчет коэффициента Type-Token Ratio

    Args:
        lemmas: список лемм текста

    """
    unique = len(set(lemmas))
    total = len(lemmas)

    if total == 0:
        return 0

    return unique / total

def calculate_rttr_metric(lemmas):
    """
    Расчет индекса Жиро  (англ. Guiraud-index, RTTR)

    Args:
        lemmas: список лемм текста

    """
    unique = len(set(lemmas))
    total = len(lemmas)

    if total == 0:
        return 0

    return unique / total ** 0.5

def calculate_сttr_metric(lemmas):
    """
    Скорректированное TTR

    Args:
        lemmas: список лемм текста

    """
    unique = len(set(lemmas))
    total = len(lemmas)

    if total == 0:
        return 0

    return unique / (2*total) ** 0.5


def calculate_msttr_metric(lemmas, segment_size=100):
    """
    TTR сегмента (англ. mean segment type-token ratio, MSTTR)

    Рассчитывается путем разделения текста на сегменты фиксированного размера
    и вычисления среднего TTR по всем полным сегментам.

    Args:
        lemmas: список лемм текста
        segment_size: размер сегмента в словах (по умолчанию 100)

    Returns:
        float: средний TTR по сегментам

    """
    if len(lemmas) == 0:
        return 0

    if len(lemmas) <= segment_size:
        return len(set(lemmas)) / len(lemmas)

    segment_ttrs = []

    # Разбиваем на сегменты и вычисляем TTR для каждого
    for i in range(0, len(lemmas), segment_size):
        if i + segment_size < len(lemmas):
            segment = lemmas[i:i + segment_size]
        else:
            segment = lemmas[i:len(lemmas)]

        if segment:
            unique_words = len(set(segment))
            segment_ttr = unique_words / len(segment)  # TTR для фактического размера сегмента
            segment_ttrs.append(segment_ttr)

    if not segment_ttrs:
        return 0

    # Среднее значение TTR по всем сегментам
    return sum(segment_ttrs) / len(segment_ttrs)


def calculate_herdan_c(lemmas):
    """
    Индекс Хердана (Herdan's C).

    C = log(V) / log(N)

    Где:
    V - количество уникальных слов (types)
    N - общее количество слов (tokens)

    Интерпретация:
    - Близко к 1: высокое разнообразие
    - Близко к 0: низкое разнообразие
    - Менее зависит от длины текста, чем TTR
    """
    unique = len(set(lemmas))
    total = len(lemmas)

    if total <= 1 or unique <= 1:
        return 0

    return math.log(unique) / math.log(total)


def calculate_uber_index(lemmas):
    """
    Убер-Индекс  (Uber-Index).

    Показывает среднее количество словоформ, использованных для каждой уникальной лексической единицы в тексте.
    """
    unique = len(set(lemmas))
    total = len(lemmas)

    if total <= 1 or unique <= 1 or total == unique:
        return 0

    return math.log(total)**2 / (math.log(total) - math.log(unique))

def calculate_hapax_legomena_ratio(lemmas):
    """
    Доля hapax legomena (слов, встречающихся только 1 раз).

    Hapax ratio = V1 / V

    Где:
    V1 - количество слов с частотой 1
    V - количество уникальных слов

    Интерпретация:
    - Высокая доля (>0.5): много редких слов, богатый словарь
    - Низкая доля (<0.3): мало редких слов, повторяющаяся лексика

    Используется: для оценки наличия редких/специфичных слов
    """
    if not lemmas:
        return 0

    freq_dist = Counter(lemmas)
    hapax_count = sum(1 for freq in freq_dist.values() if freq == 1)
    unique_count = len(freq_dist)

    return hapax_count / unique_count if unique_count > 0 else 0

def calculate_average_word_frequency(lemmas):
    """
    Средняя частота слова.

    Avg freq = N / V

    Интерпретация:
    - Низкая (<2): каждое слово встречается редко, высокое разнообразие
    - Высокая (>5): слова повторяются часто, низкое разнообразие
    """
    unique = len(set(lemmas))
    total = len(lemmas)

    return total / unique if unique > 0 else 0


def calculate_pos_ratios(lemmas, pos_tags):
    """
    Морфологические коэффициенты (отношения частей речи).

    Рассчитываются:
    1. Отношение прилагательных к существительным (Adj/Noun)

    2. Отношение глаголов к существительным (Verb/Noun)

    3. Отношение наречий к глаголам (Adv/Verb)

    Returns:
        dict с коэффициентами
    """
    pos_counter = Counter(pos_tags)

    # Группируем части речи
    noun_count = pos_counter.get('NOUN', 0)
    adj_count = pos_counter.get('ADJF', 0) + pos_counter.get('ADJS', 0)
    verb_count = pos_counter.get('VERB', 0) + pos_counter.get('INFN', 0)
    adv_count = pos_counter.get('ADVB', 0)

    return {
        'adj_noun_ratio': adj_count / noun_count if noun_count > 0 else 0,
        'verb_noun_ratio': verb_count / noun_count if noun_count > 0 else 0,
        'adv_verb_ratio': adv_count / verb_count if verb_count > 0 else 0
    }


def calculate_all_metrics(lemmas, pos_tags):
    """
    Расчет всех доступных метрик текста.

    Args:
        lemmas: список лемм
        pos_tags: список частей речи

    Returns:
        dict со всеми метриками
    """
    metrics = {}

    # 1. TTR
    metrics['ttr'] = calculate_ttr_metric(lemmas)

    # 2. Guiraud-index (RTTR)
    metrics['rttr'] = calculate_rttr_metric(lemmas)

    # 3. СTTR
    metrics['cttr'] = calculate_сttr_metric(lemmas)

    # 4. MSTTR
    metrics['msttr'] = calculate_msttr_metric(lemmas)

    # 5. Индекс Хердана
    metrics['herdan_c'] = calculate_herdan_c(lemmas)

    # 6. Убер-индекс
    metrics['uber_index'] = calculate_uber_index(lemmas)

    # 7. Доля hapax legomena
    metrics['hapax_ratio'] = calculate_hapax_legomena_ratio(lemmas)

    # 8. Средняя частота слова
    metrics['avg_word_freq'] = calculate_average_word_frequency(lemmas)

    # 9-11. Морфологические коэффициенты
    metrics.update(calculate_pos_ratios(lemmas, pos_tags))

    return metrics


def interpret_metrics(metrics):
    """
    Интерпретация рассчитанных метрик.

    Returns:
        dict с текстовыми интерпретациями
    """
    interpretations = {}

    # TTR
    ttr = metrics['ttr']
    if ttr > 0.75:
        interpretations['ttr'] = "Высокое разнообразие: богатый, разнообразный лексикон"
    elif ttr > 0.55:
        interpretations['ttr'] = "Среднее разнообразие: нормальный словарный состав"
    else:
        interpretations['ttr'] = "Низкое разнообразие: повторяющаяся лексика"

    # Коэффициент Хердана
    herdan = metrics['herdan_c']
    if herdan > 0.94:
        interpretations['herdan_c'] = "Очень высокое лексическое богатство"
    elif herdan > 0.89:
        interpretations['herdan_c'] = "Высокое лексическое богатство"
    else:
        interpretations['herdan_c'] = "Умеренное лексическое богатство"

    # Hapax legomena
    hapax = metrics['hapax_ratio']
    if hapax > 0.8:
        interpretations['hapax_ratio'] = "Много редких слов, богатый словарь"
    elif hapax > 0.5:
        interpretations['hapax_ratio'] = "Умеренное количество редких слов"
    else:
        interpretations['hapax_ratio'] = "Мало редких слов"

    # Морфологические коэффициенты
    adj_noun = metrics['adj_noun_ratio']
    if adj_noun > 0.4:
        interpretations['adj_noun_ratio'] = "Описательный, художественный стиль"
    else:
        interpretations['adj_noun_ratio'] = "Лаконичный, деловой стиль"

    verb_noun = metrics['verb_noun_ratio']
    if verb_noun > 0.5:
        interpretations['verb_noun_ratio'] = "Динамичный стиль, много действий"
    else:
        interpretations['verb_noun_ratio'] = "Статичный стиль, описания"

    return interpretations
