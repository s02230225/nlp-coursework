SIGNIFICANT = ['NOUN', 'ADJF', 'VERB', 'ADVB']
SPECIAL = ['Name', 'Surn', 'Patr', 'Geox', 'Orgn']

DICT_PATH = "freq_dicts"
AUTHORS_PATH = "authors_for_analysis"
RESULTS_PATH = "analyze_results"

STOP_WORDS = {
    "это", "всё", "ещё", "такой", "весь", "один", "самый", "свой", "только",
    "который", "наш", "ваш", "твой", "тот", "этот", "мочь", "надо", "можно",
    "должный", "быть", "в", "на", "по", "и", "а", "но", "что", "же", "не",
    "нет", "да", "ли", "то", "же", "как", "когда", "где", "ну"
}

MIN_FRACTION = 0.5
# >= 50% of texts
IPM_THRESHOLD = 1
# 1 in 1000000 in corpus
THRESHOLD_PER_1K = 1
# 1 in 1000 in author's texts
