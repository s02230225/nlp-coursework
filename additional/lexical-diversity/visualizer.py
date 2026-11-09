"""
Модуль для визуализации результатов анализа.
Содержит функции для создания графиков и диаграмм.
"""

import matplotlib.pyplot as plt
from pathlib import Path


def get_filename_without_extension(filepath):
    """
    Извлечение имени файла без расширения.

    Args:
        filepath (str): полный путь к файлу

    Returns:
        str: имя файла без расширения
    """
    return Path(filepath).stem


def visualize_single_text(text, output_dir='results/single_text_analysis'):
    """
    Создание визуализаций для одного текста.

    Создает два графика:
    1. Столбчатая диаграмма распределения частей речи
    2. Две круговые диаграммы (разнообразие + топ-5 частей речи)

    Args:
        text: объект TextLexicon
        output_dir: директория для сохранения графиков
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    text_name = get_filename_without_extension(text.text_path)

    # График 1: Распределение частей речи
    _plot_pos_distribution(text, text_name, output_dir)

    # График 2: Лексическое разнообразие
    _plot_text_analysis(text, text_name, output_dir)


def visualize_comparison(comparator, output_dir='results/comparison_analysis'):
    """
    Создание визуализаций для сравнения двух текстов.

    Создает два графика:
    1. Сравнение распределения частей речи (в процентах)
    2. Сравнение лексического разнообразия

    Args:
        comparator: объект LexiconComparator
        output_dir: директория для сохранения графиков
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    text1_name = get_filename_without_extension(comparator.text1.text_path)
    text2_name = get_filename_without_extension(comparator.text2.text_path)
    base_name = f"{text1_name}_VS_{text2_name}"

    # График 1: Сравнение частей речи
    _plot_pos_comparison(comparator, base_name, output_dir)

    # График 2: Сравнение лексического разнообразия
    _plot_diversity_comparison(comparator, base_name, output_dir)


def _plot_pos_distribution(text, text_name, output_dir):
    """Столбчатая диаграмма распределения частей речи для одного текста."""
    pos_dist = text.get_pos_distribution()

    fig, ax = plt.subplots(figsize=(12, 6))
    pos_names = list(pos_dist.keys())
    pos_values = list(pos_dist.values())

    colors = plt.cm.Set3(range(len(pos_names)))
    bars = ax.bar(pos_names, pos_values, color=colors, alpha=0.8, edgecolor='black')

    ax.set_xlabel('Части речи', fontsize=12)
    ax.set_ylabel('Количество слов', fontsize=12)
    ax.set_title('Распределение слов по частям речи', fontsize=14, fontweight='bold')
    ax.set_xticks(range(len(pos_names)))
    ax.set_xticklabels(pos_names, rotation=45, ha='right')
    ax.grid(axis='y', alpha=0.3)

    # Добавляем значения над столбцами
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontsize=9)

    plt.tight_layout()
    plt.savefig(f'{output_dir}/{text_name}_pos_distribution.png', dpi=150)
    print(f"✓ График сохранен: {output_dir}/{text_name}_pos_distribution.png")
    plt.close()


def _plot_text_analysis(text, text_name, output_dir):
    """Две круговые диаграммы: разнообразие и топ-5 частей речи."""
    stats = text.get_basic_stats()
    metrics = text.get_all_metrics()
    pos_dist = text.get_pos_distribution()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Диаграмма 1: Уникальные vs повторяющиеся
    unique = stats['unique_lemmas']
    repeated = stats['total_tokens'] - unique
    sizes = [unique, repeated]
    colors = ['#ff9999', '#66b3ff']
    explode = (0.05, 0)

    wedges1, texts1 = ax1.pie(sizes, explode=explode, colors=colors, startangle=90)

    # Легенда с процентами
    total = sum(sizes)
    labels1 = [f'Уникальные леммы ({sizes[0] / total * 100:.1f}%)',
               f'Повторяющиеся ({sizes[1] / total * 100:.1f}%)']
    ax1.legend(wedges1, labels1, loc="best", fontsize=10)
    ax1.set_title(f'Лексическое разнообразие\n(TTR: {metrics["ttr"]:.3f})',
                  fontsize=12, fontweight='bold')

    # Диаграмма 2: Топ-5 частей речи
    top_pos = sorted(pos_dist.items(), key=lambda x: x[1], reverse=True)[:5]
    labels_pos = [p[0] for p in top_pos]
    values = [p[1] for p in top_pos]
    colors2 = plt.cm.Pastel1(range(len(labels_pos)))

    wedges2, texts2 = ax2.pie(values, colors=colors2, startangle=90)

    # Легенда с процентами
    total2 = sum(values)
    labels2 = [f'{labels_pos[i]} ({values[i] / total2 * 100:.1f}%)' for i in range(len(labels_pos))]
    ax2.legend(wedges2, labels2, loc="best", fontsize=10)
    ax2.set_title('Топ-5 частей речи', fontsize=12, fontweight='bold')

    plt.tight_layout()
    plt.savefig(f'{output_dir}/{text_name}_text_analysis.png', dpi=150)
    print(f"✓ График сохранен: {output_dir}/{text_name}_text_analysis.png")
    plt.close()


def _plot_pos_comparison(comparator, base_name, output_dir):
    """Сравнение распределения частей речи (в процентах)."""
    pos_comp = comparator.compare_pos_distribution()
    pos_names = list(pos_comp.keys())
    text1_values = [pos_comp[p]['text1_percent'] for p in pos_names]
    text2_values = [pos_comp[p]['text2_percent'] for p in pos_names]

    fig, ax = plt.subplots(figsize=(14, 7))
    x = range(len(pos_names))
    width = 0.35

    bars1 = ax.bar([i - width / 2 for i in x], text1_values, width,
                   label='Текст 1', alpha=0.85, color='#3498db')
    bars2 = ax.bar([i + width / 2 for i in x], text2_values, width,
                   label='Текст 2', alpha=0.85, color='#e74c3c')

    ax.set_xlabel('Части речи', fontsize=12, fontweight='bold')
    ax.set_ylabel('Процент от общего числа слов', fontsize=12, fontweight='bold')
    ax.set_title('Сравнение распределения частей речи (относительное)',
                 fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(pos_names, rotation=45, ha='right')
    ax.legend(fontsize=11)
    ax.grid(axis='y', alpha=0.3, linestyle='--')

    # Добавляем значения над столбцами (только если > 1%)
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            if height > 1:
                ax.text(bar.get_x() + bar.get_width() / 2., height,
                        f'{height:.1f}%',
                        ha='center', va='bottom', fontsize=8)

    plt.tight_layout()
    plt.savefig(f'{output_dir}/{base_name}_pos_comparison.png', dpi=150)
    print(f"✓ График сохранен: {output_dir}/{base_name}_pos_comparison.png")
    plt.close()


def _plot_diversity_comparison(comparator, base_name, output_dir):
    """Сравнение лексического разнообразия двух текстов."""
    metrics1 = comparator.text1.get_all_metrics()
    metrics2 = comparator.text2.get_all_metrics()
    stats1 = comparator.text1.get_basic_stats()
    stats2 = comparator.text2.get_basic_stats()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Текст 1
    sizes1 = [stats1['unique_lemmas'], stats1['total_tokens'] - stats1['unique_lemmas']]
    colors1 = ['#ff9999', '#66b3ff']

    wedges1, texts1 = ax1.pie(sizes1, colors=colors1, startangle=90)
    total1 = sum(sizes1)
    labels1 = [f'Уникальные ({sizes1[0] / total1 * 100:.1f}%)',
               f'Повторяющиеся ({sizes1[1] / total1 * 100:.1f}%)']
    ax1.legend(wedges1, labels1, loc="best", fontsize=10)
    ax1.set_title(f"Текст 1 (TTR: {metrics1['ttr']:.3f})",
                  fontsize=12, fontweight='bold')

    # Текст 2
    sizes2 = [stats2['unique_lemmas'], stats2['total_tokens'] - stats2['unique_lemmas']]
    colors2 = ['#ffcc99', '#99ccff']

    wedges2, texts2 = ax2.pie(sizes2, colors=colors2, startangle=90)
    total2 = sum(sizes2)
    labels2 = [f'Уникальные ({sizes2[0] / total2 * 100:.1f}%)',
               f'Повторяющиеся ({sizes2[1] / total2 * 100:.1f}%)']
    ax2.legend(wedges2, labels2, loc="best", fontsize=10)
    ax2.set_title(f"Текст 2 (TTR: {metrics2['ttr']:.3f})",
                  fontsize=12, fontweight='bold')

    plt.suptitle('Лексическое разнообразие текстов', fontsize=14,
                 fontweight='bold', y=0.98)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/{base_name}_diversity_comparison.png', dpi=150)
    print(f"✓ График сохранен: {output_dir}/{base_name}_diversity_comparison.png")
    plt.close()
