from pymorphy2 import MorphAnalyzer
from nltk.stem.snowball import SnowballStemmer
import subprocess
import os

pymorph = MorphAnalyzer()
stemmer = SnowballStemmer("russian")

test_words = [
    # Омонимы - слова которые могут быть разными частями речи
    "стекло", "печь", "мой", "замок",

    # Сложные случаи
    "искупалась", "самый", "пятью",

    # Незнакомые слова (из стихотворения)
    "хливкие", "шорьки", "воркались", "бромбокяшки"
]

print(", ".join(test_words))
print()
print("1. PYMPORHY2")

for word in test_words:
    parsed = pymorph.parse(word)[0]
    print(f"'{word}' -> лемма: '{parsed.normal_form}', часть речи: {parsed.tag.POS}")

print()
print("2. SNOWBALL (NLTK):")

for word in test_words:
    stem = stemmer.stem(word)
    print(f"'{word}' -> основа: '{stem}'")

print()
print("3. MYSTEM:")

for word in test_words:
    try:
        result = subprocess.run(
            ['mystem.exe', '-c', '-l', '-d'],
            input=word + '\n',
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        output = result.stdout.strip()
        print(f"'{word}' -> {output}")

    except Exception as e:
        print(f"'{word}' -> ошибка: {e}")
