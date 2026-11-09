# Пример работы стеммера Snowball и лемматизатора WordNet

"""
Для разбиения на слова используется функция word_tokenize,
которая разбивает текст на слова с использованием регулярных
выражений (инженерный подход).

Для стемминга используется стеммер Snowball.
Этот стеммер использует бессловарный подход. 
Слово разбивается на 3 области:
RV — область слова после первой гласной
R1 — область слова после первого сочетания "гласная-согласная"
R2 — область R1 после первого сочетания "гласная-согласная"
Алгоритм состоит из 4-ех шагов в проверке и отбрасывании
предустановленных окончаний на области RV.
Омонимия не снимается, обработка новых слов происходит
согласно алгоритму. Пример работы:
кенгуру-кенгур, бегавшая-бега

Для лемматизация используется WordNetLemmatizer.
Используется словарный подход.
Алгоритм таков: если слово находится в словаре исключений, оно сразу обрабатывается.
Если нет, то алгоритм примеряет на входное слово все известные для данной
части речи (она задана) замены окончаний, и ищет совпадения в словаре.
Форма с минимальной длиной выдается в качестве результата лемматизации.
Омонимия не снимается, нужно явно указать часть речи. Неизвестные слова остаются "как есть".
corpora-corpus, churches-church
"""
import sys
import nltk
from nltk.stem import SnowballStemmer, WordNetLemmatizer
from nltk.tokenize import word_tokenize
nltk.download('wordnet')
def get_stems(text):
    if not text:
        return []
    
    stemmer = SnowballStemmer("russian")
    words = word_tokenize(text)
    stems = [stemmer.stem(w) for w in words]
    return stems

def get_lemmas(text):
    if not text:
        return []

    lemmatizer = WordNetLemmatizer()
    words = word_tokenize(text)
    lemmas = [lemmatizer.lemmatize(w) for w in words]
    return lemmas

def main():
    stems = get_stems(input("Enter text in Russian:"))
    # lemmas = get_lemmas(input("Enter text in English:"))
    
    print("Stems:", stems)
    # print("Lemmas:", lemmas)


if __name__ == "__main__":
    main()
