"""
Модуль для генерации текстовых отчетов.
Содержит функции для создания отчетов в формате TXT.
"""

from pathlib import Path


def get_filename_without_extension(filepath):
    """Извлечение имени файла без расширения."""
    return Path(filepath).stem


def generate_single_report(text, output_dir='results/single_text_analysis'):
    """
    Генерация отчета для одного текста.

    Args:
        text: объект TextLexicon
        output_dir: директория для сохранения отчета
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    text_name = get_filename_without_extension(text.text_path)
    output_file = f'{output_dir}/{text_name}_report.txt'

    with open(output_file, 'w', encoding='utf-8') as f:
        _write_header(f, "АНАЛИЗ ЛЕКСИКОНА ТЕКСТА")

        f.write(f"Файл: {text.text_path}\n")
        f.write(f"Использованы стоп-слова: {'Да' if text.use_stopwords else 'Нет'}\n\n")

        # Раздел 1: Базовые характеристики
        _write_basic_stats(f, text)

        # Раздел 2: Лексические метрики
        _write_metrics(f, text)

        # Раздел 3: Распределение частей речи
        _write_pos_distribution(f, text)

        # Раздел 4: Топ слов
        _write_top_lemmas(f, text)

        # Раздел 5: Топ слов по частям речи
        _write_top_by_pos(f, text)

        f.write("\n" + "=" * 70 + "\n")

    print(f"✓ Отчет сохранен: {output_file}")


def generate_comparison_report(comparator, output_dir='results/comparison_analysis'):
    """
    Генерация сравнительного отчета для двух текстов.

    Args:
        comparator: объект LexiconComparator
        output_dir: директория для сохранения отчета
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    text1_name = get_filename_without_extension(comparator.text1.text_path)
    text2_name = get_filename_without_extension(comparator.text2.text_path)
    output_file = f'{output_dir}/{text1_name}_VS_{text2_name}_report.txt'

    with open(output_file, 'w', encoding='utf-8') as f:
        _write_header(f, "СРАВНИТЕЛЬНЫЙ АНАЛИЗ ЛЕКСИКОНА ТЕКСТОВ")

        f.write(f"Текст 1: {comparator.text1.text_path}\n")
        f.write(f"Текст 2: {comparator.text2.text_path}\n\n")

        # Раздел 1: Базовые характеристики
        _write_comparison_basic_stats(f, comparator)

        # Раздел 2: Лексические метрики
        _write_comparison_metrics(f, comparator)

        # Раздел 3: Распределение частей речи
        _write_comparison_pos(f, comparator)

        # Раздел 4: Топ слов
        _write_comparison_top_lemmas(f, comparator)

        # Раздел 5: Топ слов по частям речи
        _write_comparison_top_by_pos(f, comparator)

        f.write("\n" + "=" * 70 + "\n")

    print(f"✓ Отчет сохранен: {output_file}")


def _write_header(f, title):
    """Запись заголовка отчета."""
    f.write("=" * 70 + "\n")
    f.write(f"{title}\n")
    f.write("=" * 70 + "\n\n")


def _write_section_header(f, title):
    """Запись заголовка раздела."""
    f.write(f"\n\n{title}\n")
    f.write("-" * 70 + "\n")


def _write_basic_stats(f, text):
    """Запись базовых статистик для одного текста."""
    _write_section_header(f, "1. БАЗОВЫЕ ХАРАКТЕРИСТИКИ")

    stats = text.get_basic_stats()

    f.write(f"Всего слов (токенов): {stats['total_tokens']}\n")
    f.write(f"Уникальных лемм: {stats['unique_lemmas']}\n")
    f.write(f"Уникальных словоформ: {stats['unique_wordforms']}\n")
    f.write(f"Средняя длина леммы: {stats['avg_lemma_length']:.2f} символов\n")
    f.write(f"Средняя длина словоформы: {stats['avg_token_length']:.2f} символов\n")


def _write_metrics(f, text):
    """Запись лексических метрик для одного текста."""
    _write_section_header(f, "2. ЛЕКСИЧЕСКИЕ МЕТРИКИ")

    metrics = text.get_all_metrics()
    interpretations = text.get_metrics_interpretation()

    # Таблица метрик
    f.write(f"{'Метрика':<35} {'Значение':>15} {'Интерпретация'}\n")
    f.write("-" * 70 + "\n")

    # TTR метрики
    f.write(f"{'TTR (Type-Token Ratio)':<35} {metrics['ttr']:>15.4f} {interpretations['ttr']}\n")
    f.write(f"{'Guiraud-index (RTTR)':<35} {metrics['rttr']:>15.4f}\n")
    f.write(f"{'Corrected TTR':<35} {metrics['cttr']:>15.4f}\n")
    f.write(f"{'mean segment type-token ratio':<35} {metrics['msttr']:>15.4f}\n")

    # Другие метрики разнообразия
    f.write(f"{'Индекс Хердана (C)':<35} {metrics['herdan_c']:>15.4f} {interpretations['herdan_c']}\n")
    f.write(f"{'Убер-индекс':<35} {metrics['uber_index']:>15.4f}\n")


    # Hapax legomena
    f.write(f"{'Hapax legomena ratio':<35} {metrics['hapax_ratio']:>15.4f} {interpretations['hapax_ratio']}\n")
    f.write(f"{'Средняя частота слова':<35} {metrics['avg_word_freq']:>15.2f}\n")

    # Морфологические коэффициенты
    f.write(f"{'Прилаг./Сущ. ratio':<35} {metrics['adj_noun_ratio']:>15.4f} {interpretations['adj_noun_ratio']}\n")
    f.write(f"{'Глаг./Сущ. ratio':<35} {metrics['verb_noun_ratio']:>15.4f} {interpretations['verb_noun_ratio']}\n")
    f.write(f"{'Нареч./Глаг. ratio':<35} {metrics['adv_verb_ratio']:>15.4f}\n")

def _write_pos_distribution(f, text):
    """Запись распределения частей речи для одного текста."""
    _write_section_header(f, "3. РАСПРЕДЕЛЕНИЕ ЧАСТЕЙ РЕЧИ")

    pos_dist = text.get_pos_distribution()
    total_pos = sum(pos_dist.values())

    f.write(f"{'Часть речи':<25} {'Количество':>15} {'Процент':>15}\n")
    f.write("-" * 70 + "\n")

    for pos, count in sorted(pos_dist.items(), key=lambda x: x[1], reverse=True):
        percent = (count / total_pos) * 100
        f.write(f"{pos:<25} {count:>15} {percent:>14.1f}%\n")


def _write_top_lemmas(f, text):
    """Запись топ лемм для одного текста."""
    _write_section_header(f, "4. ТОП-20 САМЫХ ЧАСТОТНЫХ ЛЕММ")

    top_lemmas = text.get_top_lemmas(20)
    stats = text.get_basic_stats()
    total_words = stats['total_tokens']

    f.write(f"{'№':>3} {'Лемма':<20} {'Частота':>12} {'Процент':>12}\n")
    f.write("-" * 70 + "\n")

    for i, (lemma, count) in enumerate(top_lemmas, 1):
        percent = (count / total_words) * 100
        f.write(f"{i:>3}. {lemma:<20} {count:>10} {percent:>11.2f}%\n")


def _write_top_by_pos(f, text):
    """Запись топ слов по частям речи для одного текста."""
    _write_section_header(f, "5. ТОП-7 СЛОВ ПО ОСНОВНЫМ ЧАСТЯМ РЕЧИ")

    # Единый набор частей речи для всех отчетов
    for pos_name in ['существительные', 'глаголы', 'прилагательные', 'наречия']:
        top_pos = text.get_top_by_pos(pos_name, 7)
        if top_pos:
            f.write(f"\n{pos_name.upper()}:\n")
            for i, (word, count) in enumerate(top_pos, 1):
                f.write(f"  {i}. {word} ({count})\n")


def _write_comparison_basic_stats(f, comparator):
    """Запись сравнения базовых статистик."""
    _write_section_header(f, "1. БАЗОВЫЕ ХАРАКТЕРИСТИКИ")

    stats_comp = comparator.compare_statistics()

    f.write(f"{'Характеристика':<30} {'Текст 1':>15} {'Текст 2':>15} {'Разница':>15}\n")
    f.write("-" * 70 + "\n")

    labels = {
        'total_tokens': 'Всего слов',
        'unique_lemmas': 'Уникальных лемм',
        'unique_wordforms': 'Уникальных словоформ',
        'avg_lemma_length': 'Средняя длина леммы',
        'avg_token_length': 'Средняя длина словоформы',
    }

    for key, label in labels.items():
        data = stats_comp[key]
        if 'avg' in key:
            f.write(f"{label:<30} {data['text1']:>15.2f} {data['text2']:>15.2f} {data['difference']:>15.2f}\n")
        else:
            f.write(f"{label:<30} {data['text1']:>15} {data['text2']:>15} {data['difference']:>15}\n")


def _write_comparison_metrics(f, comparator):
    """Запись сравнения лексических метрик."""
    _write_section_header(f, "2. ЛЕКСИЧЕСКИЕ МЕТРИКИ")

    metrics_comp = comparator.compare_metrics()

    # Размеры текстов (важная информация!)
    stats1 = comparator.text1.get_basic_stats()
    stats2 = comparator.text2.get_basic_stats()
    f.write(f"Размер текстов: Текст 1 = {stats1['total_tokens']} слов, ")
    f.write(f"Текст 2 = {stats2['total_tokens']} слов\n\n")

    f.write(f"{'Метрика':<35} {'Текст 1':>15} {'Текст 2':>15} {'Разница':>15}\n")
    f.write("-" * 70 + "\n")

    # Все метрики с разницей
    metrics_labels = {
        'ttr': 'TTR',
        'rttr': 'RTTR',
        'cttr': 'Corrected TTR',
        'msttr': 'mean segment type-token ratio',
        'herdan_c': 'Коэфф. Хердана (C)',
        'hapax_ratio': 'Hapax legomena ratio',
        'avg_word_freq': 'Средняя частота слова',
        'adj_noun_ratio': 'Прилаг./Сущ. ratio',
        'verb_noun_ratio': 'Глаг./Сущ. ratio',
        'adv_verb_ratio': 'Нареч./Глаг. ratio',
    }

    for key, label in metrics_labels.items():
        data = metrics_comp[key]
        f.write(f"{label:<35} {data['text1']:>15.4f} {data['text2']:>15.4f} {data['difference']:>15.4f}\n")

    # Интерпретации
    f.write("\nИнтерпретация метрик:\n")
    interp1 = comparator.text1.get_metrics_interpretation()
    interp2 = comparator.text2.get_metrics_interpretation()

    f.write(f"\nТекст 1:\n")
    f.write(f"  TTR: {interp1['ttr']}\n")
    f.write(f"  Коэфф. Хердана: {interp1['herdan_c']}\n")

    f.write(f"\nТекст 2:\n")
    f.write(f"  TTR: {interp2['ttr']}\n")
    f.write(f"  Коэфф. Хердана: {interp2['herdan_c']}\n")

def _write_comparison_pos(f, comparator):
    """Запись сравнения распределения частей речи."""
    _write_section_header(f, "3. РАСПРЕДЕЛЕНИЕ ЧАСТЕЙ РЕЧИ (ОТНОСИТЕЛЬНОЕ)")

    pos_comp = comparator.compare_pos_distribution()

    f.write(f"{'Часть речи':<25} {'Текст 1':>15} {'Текст 2':>15} {'Разница':>10}\n")
    f.write("-" * 70 + "\n")

    for pos, data in sorted(pos_comp.items(), key=lambda x: x[1]['text1_percent'], reverse=True):
        f.write(
            f"{pos:<25} {data['text1_percent']:>14.2f}% {data['text2_percent']:>14.2f}% {data['difference']:>9.2f}%\n")

def _write_comparison_top_lemmas(f, comparator):
    """Запись топ лемм обоих текстов."""
    _write_section_header(f, "4. ТОП-15 САМЫХ ЧАСТОТНЫХ ЛЕММ")

    f.write("\nТекст 1:\n")
    for i, (lemma, count) in enumerate(comparator.text1.get_top_lemmas(15), 1):
        f.write(f"  {i:2}. {lemma:<20} {count:>5}\n")

    f.write("\nТекст 2:\n")
    for i, (lemma, count) in enumerate(comparator.text2.get_top_lemmas(15), 1):
        f.write(f"  {i:2}. {lemma:<20} {count:>5}\n")


def _write_comparison_top_by_pos(f, comparator):
    """Запись топ слов по частям речи для обоих текстов."""
    _write_section_header(f, "5. ТОП-5 СЛОВ ПО ОСНОВНЫМ ЧАСТЯМ РЕЧИ")

    # Единый набор частей речи
    for pos_name in ['существительные', 'глаголы', 'прилагательные', 'наречия']:
        f.write(f"\n{pos_name.upper()}:\n")

        f.write("Текст 1: ")
        top1 = comparator.text1.get_top_by_pos(pos_name, 5)
        if top1:
            f.write(", ".join([f"{w} ({c})" for w, c in top1]) + "\n")
        else:
            f.write("нет данных\n")

        f.write("Текст 2: ")
        top2 = comparator.text2.get_top_by_pos(pos_name, 5)
        if top2:
            f.write(", ".join([f"{w} ({c})" for w, c in top2]) + "\n")
        else:
            f.write("нет данных\n")
