statistic = {}

artisticFreq = {}
businessFreq = {}
conversationalFreq = {}
journalisticFreq = {}
scientificFreq = {}


# подгрузка необходимых файлов (словарей, списка стоп слов)
def init(artisticFile: str,
         businessFile: str,
         conversationalFile: str,
         journalisticFile: str,
         scientificFile: str):
    global artisticFreq
    global businessFreq
    global conversationalFreq
    global journalisticFreq
    global scientificFreq
    try:
        with open(artisticFile, 'r', encoding='utf-8') as file:
            text = file.read()
        artisticFreq = {value.split()[0].lower(): float(value.split()[1]) / 1000 for value in text.split('\n')
                        if value and value[0] != '#'}
    except FileNotFoundError:
        print('Error: The data files (' + artisticFile + ') were not found. Check the files path.')
        exit()

    try:
        with open(businessFile, 'r', encoding='utf-8') as file:
            text = file.read()
        businessFreq = {value.split()[0].lower(): float(value.split()[1]) / 1000 for value in text.split('\n')
                        if value and value[0] != '#'}
    except FileNotFoundError:
        print('Error: The data files (' + businessFile + ') were not found. Check the files path.')
        exit()

    try:
        with open(conversationalFile, 'r', encoding='utf-8') as file:
            text = file.read()
        conversationalFreq = {value.split()[0].lower(): float(value.split()[1]) / 1000 for value in text.split('\n')
                              if value and value[0] != '#'}
    except FileNotFoundError:
        print('Error: The data files (' + conversationalFile + ') were not found. Check the files path.')
        exit()

    try:
        with open(journalisticFile, 'r', encoding='utf-8') as file:
            text = file.read()
        journalisticFreq = {value.split()[0].lower(): float(value.split()[1]) / 1000 for value in text.split('\n')
                            if value and value[0] != '#'}
    except FileNotFoundError:
        print('Error: The data files (' + journalisticFile + ') were not found. Check the files path.')
        exit()

    try:
        with open(scientificFile, 'r', encoding='utf-8') as file:
            text = file.read()
        scientificFreq = {value.split()[0].lower(): float(value.split()[1]) / 1000 for value in text.split('\n')
                          if value and value[0] != '#'}
    except FileNotFoundError:
        print('Error: The data files (' + scientificFile + ') were not found. Check the files path.')
        exit()


# Вычисление оценки принадлежности к стилю"
def calculateStyleScore(statistic):
    listFreq = [
        (artisticFreq, 0.0, "artistic style"),
        (businessFreq, 0.0, "business style"),
        (conversationalFreq, 0.0, "conversational style"),
        (journalisticFreq, 0.0, "journalistic style"),
        (scientificFreq, 0.0, "scientific style")
    ]

    for i, style in enumerate(listFreq):
        style_dict, score, style_name = style
        matched_words = 0
        total_weight = 0.0

        for word, freq in statistic.items():
            if word in style_dict:
                # Вес = частота в тексте * частота в стиле
                weight = freq * style_dict[word]
                total_weight += weight
                matched_words += 1

        # Нормализация по количеству совпадений
        if matched_words > 0:
            listFreq[i] = (style_dict, total_weight / matched_words, style_name)
        else:
            listFreq[i] = (style_dict, 0.0, style_name)

    return [
        ("artistic style", listFreq[0][1]),
        ("business style", listFreq[1][1]),
        ("conversational style", listFreq[2][1]),
        ("journalistic style", listFreq[3][1]),
        ("scientific style", listFreq[4][1])
    ]


if __name__ == '__main__':
    init("artistic.txt", "business.txt", "conversational.txt", "journalistic.txt", "scientific.txt")
    try:
        filename = input('Enter file name:')
        with open(filename, 'r', encoding='utf-8') as file:
            text = file.read()
        statistic = {value.split()[1].lower(): float(value.split()[19][:-1]) for value in text.split('\n')
                     if value and value[0] != '#'}
    except FileNotFoundError:
        print('Error: The data files (' + filename + ') were not found. Check the files path.')
        exit()
    except Exception:
        print('Error reading the file')
        exit()

    styleScores = calculateStyleScore(statistic)
    print("Resulting weights:")

    for elem in styleScores:
        print(elem[0] + ":  " + f"{elem[1]}")
    styleScores = sorted(styleScores, key=lambda x: x[1], reverse=True)
    print("Еhe expected style:" + styleScores[0][0])
