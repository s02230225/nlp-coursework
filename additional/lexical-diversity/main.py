"""
Анализатор лексикона русскоязычных текстов.

Программа выполняет комплексный лингвистический анализ текстов:
- Морфологический анализ и лемматизация
- Расчет лексических метрик
- Анализ распределения частей речи
- Визуализация результатов
- Сравнительный анализ двух текстов

Автор: Хижко Дмитрий
"""

from lexicon_core import TextLexicon
from comparator import LexiconComparator
import visualizer
import reporter


def print_banner():
    """Вывод приветственного баннера."""
    print("\n" + "=" * 70)
    print("АНАЛИЗАТОР ЛЕКСИКОНА РУССКОЯЗЫЧНЫХ ТЕКСТОВ")
    print("Версия 2.0")
    print("=" * 70 + "\n")

    print("Программа выполняет комплексный анализ лексикона:")
    print("  • Морфологический анализ и лемматизация")
    print("  • Расчет лексических метрик")
    print("  • Анализ распределения частей речи")
    print("  • Визуализация результатов")
    print("  • Сравнение двух текстов\n")


def select_mode():
    """
    Выбор режима работы программы.

    Returns:
        str: '1' для анализа одного текста, '2' для сравнения
    """
    print("Режимы работы:")
    print("  1 - Анализ одного текста")
    print("  2 - Сравнительный анализ двух текстов")

    while True:
        mode = input("\nВыберите режим (1 или 2): ").strip()
        if mode in ['1', '2']:
            return mode
        print("❌ Неверный выбор. Используйте 1 или 2.")


def select_stopwords():
    """
    Выбор использования стоп-слов.

    Returns:
        bool: True для использования стоп-слов, False иначе
    """
    print("\nИспользование стоп-слов:")
    print("  • 'да' - фильтровать служебные слова (рекомендуется)")
    print("  • 'нет' - анализировать все слова")

    use_stop = input("Использовать фильтрацию стоп-слов? (да/нет, по умолчанию 'да'): ").strip().lower()
    return use_stop != 'нет'


def analyze_single_text(file_path, use_stopwords):
    """
    Анализ одного текста.

    Args:
        file_path: путь к файлу
        use_stopwords: использовать ли стоп-слова
    """
    print("\n" + "-" * 70)
    print("РЕЖИМ: АНАЛИЗ ОДНОГО ТЕКСТА")
    print("-" * 70 + "\n")

    try:
        # Этап 1: Загрузка и обработка текста
        print("ЭТАП 1/3: ОБРАБОТКА ТЕКСТА...")
        print("-" * 70 + "\n")
        text = TextLexicon(file_path, use_stopwords)
        print(f"✓ Обработано слов: {len(text.tokens)}")
        print(f"✓ Уникальных лемм: {len(set(text.lemmas))}")

        # Этап 2: Генерация отчета
        print("\n" + "-" * 70)
        print("ЭТАП 2/3: ГЕНЕРАЦИЯ ОТЧЕТА...")
        print("-" * 70 + "\n")
        reporter.generate_single_report(text)

        # Этап 3: Создание визуализаций
        print("\n" + "-" * 70)
        print("ЭТАП 3/3: СОЗДАНИЕ ВИЗУАЛИЗАЦИЙ...")
        print("-" * 70 + "\n")
        visualizer.visualize_single_text(text)

        # Завершение
        print("\n" + "=" * 70)
        print("АНАЛИЗ УСПЕШНО ЗАВЕРШЕН!")
        print("=" * 70)

        from pathlib import Path
        text_name = Path(file_path).stem
        print(f"\nВсе результаты сохранены в 'results/single_text_analysis/':")
        print(f"  📄 {text_name}_report.txt")
        print(f"  📊 {text_name}_pos_distribution.png")
        print(f"  📊 {text_name}_text_analysis.png")

    except FileNotFoundError as e:
        print(f"\n❌ Ошибка: {e}")
        print("Проверьте правильность пути к файлу.")
    except Exception as e:
        print(f"\n❌ Неожиданная ошибка: {e}")
        import traceback
        traceback.print_exc()


def compare_two_texts(file1, file2, use_stopwords):
    """
    Сравнительный анализ двух текстов.

    Args:
        file1: путь к первому файлу
        file2: путь ко второму файлу
        use_stopwords: использовать ли стоп-слова
    """
    print("\n" + "-" * 70)
    print("РЕЖИМ: СРАВНИТЕЛЬНЫЙ АНАЛИЗ ДВУХ ТЕКСТОВ")
    print("-" * 70 + "\n")

    try:
        # Этап 1: Загрузка и обработка текстов
        print("ЭТАП 1/3: ОБРАБОТКА ТЕКСТОВ...")
        print("-" * 70 + "\n")

        print("Обработка текста 1...")
        text1 = TextLexicon(file1, use_stopwords)
        print(f"✓ Обработано слов: {len(text1.tokens)}")

        print("\nОбработка текста 2...")
        text2 = TextLexicon(file2, use_stopwords)
        print(f"✓ Обработано слов: {len(text2.tokens)}")

        # Этап 2: Генерация отчета
        print("\n" + "-" * 70)
        print("ЭТАП 2/3: ГЕНЕРАЦИЯ СРАВНИТЕЛЬНОГО ОТЧЕТА...")
        print("-" * 70 + "\n")

        comparator = LexiconComparator(text1, text2)
        reporter.generate_comparison_report(comparator)

        # Этап 3: Создание визуализаций
        print("\n" + "-" * 70)
        print("ЭТАП 3/3: СОЗДАНИЕ ВИЗУАЛИЗАЦИЙ...")
        print("-" * 70 + "\n")
        visualizer.visualize_comparison(comparator)

        # Завершение
        print("\n" + "=" * 70)
        print("АНАЛИЗ УСПЕШНО ЗАВЕРШЕН!")
        print("=" * 70)

        from pathlib import Path
        text1_name = Path(file1).stem
        text2_name = Path(file2).stem
        base_name = f"{text1_name}_VS_{text2_name}"

        print(f"\nВсе результаты сохранены в 'results/comparison_analysis/':")
        print(f"  📄 {base_name}_report.txt")
        print(f"  📊 {base_name}_pos_comparison.png")
        print(f"  📊 {base_name}_diversity_comparison.png")

    except FileNotFoundError as e:
        print(f"\n❌ Ошибка: {e}")
        print("Проверьте правильность путей к файлам.")
    except Exception as e:
        print(f"\n❌ Неожиданная ошибка: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Главная функция программы."""
    # Приветствие
    print_banner()

    # Выбор режима
    mode = select_mode()

    # Выбор использования стоп-слов
    use_stopwords = select_stopwords()

    # Выполнение анализа
    if mode == '1':
        # Анализ одного текста
        file_path = input("\nВведите путь к текстовому файлу: ").strip()
        analyze_single_text(file_path, use_stopwords)

    else:
        # Сравнение двух текстов
        print("\nВведите пути к файлам для сравнения:")
        file1 = input("  Текст 1: ").strip()
        file2 = input("  Текст 2: ").strip()
        compare_two_texts(file1, file2, use_stopwords)

    # Прощание
    print("\n" + "=" * 70)
    print("Спасибо за использование программы!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
