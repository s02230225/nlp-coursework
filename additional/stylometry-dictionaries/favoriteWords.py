'''
    Данная программа анализирует текст и ищет наиболее часто встречаемые леммы
    знаменательной части речи (любимые слова автора)

    Для токенизации текста используется Natasha
'''

from collections import Counter
from natasha import (
    Segmenter,
    MorphVocab,
    NewsEmbedding,
    NewsMorphTagger,
    Doc
)

# список стоп слов - слов, которые не участвуют в конкурсе на "любимые слова"
stopWords = []
# частотные словари
freq = {}

# подгрузка необходимых файлов (словарей, списка стоп слов)
def init(stopWordsFile: str, freqFile: str):
    global stopWords
    global freq
    try:
        with open(stopWordsFile, 'r', encoding='utf-8') as file:
            text = file.read()
        stopWords = [value.lower() for value in text.split('\n')
                     if value and value[0] != '#']
    except FileNotFoundError:
        print('Error: The data files (' + stopWordsFile + ') were not found. Check the files path.')
        exit()

    try:
        with open(freqFile, 'r', encoding='utf-8') as file:
            text = file.read()
        freq = {value.split()[0].lower(): value.split()[2] for value in text.split('\n')
                if value and value[0] != '#'}
    except FileNotFoundError:
        print('Error: The data files (' + freqFile + ') were not found. Check the files path.')
        exit()

# выделение списка лемм знаменательной части речи
def getImpntWords(text: str):
    segmenter = Segmenter()
    morph_vocab = MorphVocab()

    emb = NewsEmbedding()
    morph_tagger = NewsMorphTagger(emb)

    results = []

    nTokens = 0
    textList = text.split('\n')
    for text in textList:
        doc = Doc(text)
        doc.segment(segmenter)
        doc.tag_morph(morph_tagger)

        for token in doc.tokens:
            token.lemmatize(morph_vocab)

            ''' Далее фильтруем токены, оставляя только слова "знаменательной" части речи
                (также отсекаются имена собственные, они имеют тег 'PROPN'), 
                а также подсчитываем общее число словоупотреблений.
            '''
            if token.pos not in {'X', 'SYM', 'PUNCT'}:
                nTokens += 1
            if (token.pos not in {'NOUN', 'VERB', 'ADJ', 'ADV'}) or (token.lemma in stopWords):
                continue

            results.append({
                'lemma': token.lemma,
                'pos': token.pos
            })
    return results, nTokens

# эта функция возвращает частотность леммы на миллион слов
def getIPM(lemma : str, pos: str):
    if lemma in freq:
        return freq[lemma]
    else:
        return None

# сортировка по словоупотреблению, подсчет необходимой статистики
def calculatingStatistics(lemmaListList , nTokens: int):
    lemmaList = []
    for elem in lemmaListList:
        lemmaList.extend(elem)

    # нужно для проверки условия: слово содержится хотя бы в половине текстов автора
    lemmasOfText = [set([elem['lemma'] for elem in sublist]) for sublist in lemmaListList]
    def isLemmaInHalfTexts(lemma: str):
        count = 0
        for text in lemmasOfText:
            if lemma in text:
                count += 1
        return count >= len(lemmasOfText) // 2 + len(lemmasOfText) % 2

    dic = dict(Counter(tuple(item.items()) for item in lemmaList))
    dic = [
            {'lemma': dict(key)['lemma'],
             'pos': dict(key)['pos'],
             'count': value
             } for key, value in dic.items()]

    dic = sorted(dic, key=lambda item: item['count'], reverse=True)

    result = [
        {'lemma': item['lemma'],
         'pos': item['pos'],
         'wpt': item['count'] / nTokens * 1000,
         'ipm': getIPM(item['lemma'], item['pos']),
         'count': item['count'],
         'halfTexts': isLemmaInHalfTexts(item['lemma'])
         } for item in dic]

    return result

# вывод топа
def printStatistic(statistic, pos: str, count: int, wrt: bool):
    filtered = [
        item for item in statistic
        if item['wpt'] >= 1 and item['ipm'] is not None
           and float(item['ipm']) >= 1 and item['halfTexts']

    ]
    discarded = [
        item for item in statistic
        if not(item['wpt'] >= 1 and item['ipm'] is not None
               and float(item['ipm']) >= 1 and item['halfTexts'])
    ]

    if pos != 'ALL':
        filtered = [
            item for item in filtered
            if item['pos'] == pos
        ]
        discarded = [
            item for item in discarded
            if item['pos'] == pos
        ]

    if count == 0:
        count = len(filtered)
    countm = min(count, len(filtered))

    def printItem(item, n: int):
        print(f'{n + 1}) ' + item['lemma']
              + f'\tis contained in half of the author\'s texts: {item["halfTexts"]};'
              + f'\tcount of word form: {item["count"]};'
              + f'\twords per thousand: {item["wpt"]};'
              + f'\tipm: {item["ipm"]}')

    def writeItem(item, n: int, mode):
        with open('out.txt', mode, encoding='utf-8') as file:
            file.write(f'{n + 1}) ' + item['lemma']
              + f'\tis contained in half of the author\'s texts: {item["halfTexts"]};'
              + f'\tcount of word form: {item["count"]};'
              + f'\twords per thousand: {item["wpt"]};'
              + f'\tipm: {item["ipm"]}\n')

    if countm != 0:
        print('\nFavorite words:')
    else:
        print('\nThere are no words that meet the criterion!')
        if wrt:
            with open('out.txt', 'w', encoding='utf-8') as file:
                file.write("\n")
    for i in range(countm):
        printItem(filtered[i], i)
        if wrt:
            if i==0:
                writeItem(filtered[i], i, "w")
            else:
                writeItem(filtered[i], i, "a")
    if countm != 0 and countm < count:
        print('\nOther words don\'t meet the criteria!')

    if len(discarded) > 0 and countm < count:
        print('\nThe following words do not meet the criteria, but they are quite frequent:')
        i = 0
        while(len(discarded) > i and i + countm < count):
            printItem(discarded[i], i)
            if wrt:
                writeItem(discarded[i], i, "a")
            i += 1

# вывод данных по запросу пользователя
def loop(statistic):
    while (True):
        key = input('Write statistics to a file out.txt?? [y/n]').upper()
        wrt = False
        if key == 'Y' or key == 'YES':
            wrt = True
        while (True):
            count = input('Enter the number of favorite words (0 if must show all words):')
            if count.isdigit():
                count = int(count)
                break

        while (True):
            pos = input('Enter the name of the part of speech (\'NOUN\', \'VERB\', \'ADJ\', \'ADV\', \'ALL\'):').upper()
            if pos in ['NOUN', 'VERB', 'ADJ', 'ADV', 'ALL']:
                printStatistic(statistic, pos, count, wrt)
                break
            print('Uncorrect value! Enter the name of the part of speech (\'NOUN\', \'VERB\', \'ADJ\', \'ADV\', \'ALL\'):')

        key = input('Continue? [y/n]').upper()
        if key == 'N' or key == 'NO':
            break

#парсинг имен файлов
def parseFilenames(string : str):
    filenames = []
    name = ""
    quote = False
    quotechar = None

    i = 0
    while i < len(string):
        char = string[i]
        if char in ("'", '"'):
            if not quote:
                quote = True
                quotechar = char
            elif char == quotechar:
                quote = False
                quotechar = None
                if name:
                    filenames.append(name)
                    name = ""
            else:
                name += char
        elif char == ' ' and not quote:
            if name:
                filenames.append(name)
                name = ""
        else:
            name += char
        i += 1
    if name:
        filenames.append(name)

    return filenames

if __name__ == '__main__':
    init('stopWords.txt', "freqrnc2011.txt")

    string = input('Enter file names (separated by a space):')
    filenames = parseFilenames(string)

    texts = []
    for filename in filenames:
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                texts. append(file.read())
        except FileNotFoundError:
            print('Error: The file (' + filename + ') was not found. Check the file path.')
            exit()
        except Exception:
            print('Error reading the file')
            exit()

    # получение статистики
    wordlists = []
    ns = []
    for text in texts:
        wordlist, n = getImpntWords(text)
        wordlists.append(wordlist)
        ns.append(n)

    statistic = calculatingStatistics(wordlists, sum(ns))

    # вывод:
    loop(statistic)
