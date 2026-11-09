from pymorphy3 import MorphAnalyzer

pm = MorphAnalyzer() # создаем один заранее и будем использовать только его, т.к. его экземпляр весит > 15мб

def animacy_val(animacy): # функция, определяющая одушевленность
    match animacy:
        case "anim":
            return "Одушевленное"
        case "inan":
            return "Неодушевленное"
        case _:
            return "N/A"
        
def gender_val(gender): # функция, определяющая род
    match gender:
        case "femn":
            return "Женский"
        case "masc":
            return "Мужской"
        case "neut":
            return "Средний"
        case _:
            return "N/A"

def declination_val(word): # функция, определяющая склонение
    lemma = word.normal_form # привели существительное к нормальной форме
    parsed_lemma = pm.parse(lemma)[0]
    gen = gender_val(parsed_lemma.tag.gender)
    last_letter = parsed_lemma.word[-1]
    if last_letter in ['а', 'я']:
        return '1-е склонение'
    elif last_letter in ['о', 'е'] or gen == 'Мужской':
        return '2-е склонение'
    elif last_letter in ['ь'] and gen == 'Женский':
        return '3-е склонение'
    else:
        return 'N/A'

def case_val(cases): # Падеж, считаем, что их 6
    match cases:
        case "nomn":
            return "Именительный"
        case "gent":
            return "Родительный"
        case "datv":
            return "Дательный"
        case "accs":
            return "Винительный"
        case "ablt":
            return "Творительный"
        case "loct":
            return "Предложный"     
        case _:
            return "N/A"
        
def number_val(number): # Число
    match number:
        case "sing":
            return "Единственное"
        case "plur":
            return "Множественное"
        case _:
            return "N/A"

def aspect_val(aspect): # Вид у глагола
    match aspect:
        case "perf":
            return "Совершенный"
        case "impf":
            return "Несовершенный"
        case _:
            return 'N/A'

def is_returnable(word): # Возвратный ли глагол
    if word.word.endswith('ся') or word.word.endswith('сь'):
        return "Возвратный"
    return "Невозвратный"

def is_transitive(transit): # Переходность
    match transit:
        case "tran":
            return "Переходный"
        case "intr":
            return "Непереходный"
        case _:
            return 'N/A'

def mood_val(mood): # Наклонение
    match mood:
        case "indc":
            return "Изъявительное"
        case "impr":
            return "Повелительное"
        case _:
            return 'N/A'
        
def tense_val(tense): # Время
    match tense:
        case 'pres':
            return "Настоящее"
        case 'past':
            return "Прошедшее"
        case 'futr':
            return "Будущее"
        case _:
            return 'N/A'

def verb_gender_label(word): # Род глагола
    last = word.word[-1]
    if word.word.endswith('ся') or word.word.endswith('сь'): # проверка на возвратность
        last = word.word[-3] # слово будет корректным глаголом, поэтому RE не будет
    if last == 'а':
        return "Женский"
    elif last == 'о':
        return "Средний"
    elif last == 'и':
        return "Мн.ч."
    else:
        return "Мужской"

def person_val(person): # Лицо
    match person:
        case '1per':
            return "Первое"
        case '2per':
            return "Второе"
        case '3per':
            return "Третье"
        case _:
            return 'N/A'

def voice_val(voice): # Залог
    match voice:
        case 'actv':
            return "Действительный"
        case 'pssv':
            return "Страдательный"
        case _:
            return 'N/A'
        
def analyze_noun(word): # анализатор существительного
    result = {
        "Часть речи": "Существительное",
        "Начальная форма": word.normal_form,
        "Постоянные признаки": {}, # одушевленность, род и склонение
        "Непостоянные признаки": {} # падеж и число
    }
    if word.tag.animacy:
        result["Постоянные признаки"]["Одушевленность"] = animacy_val(word.tag.animacy)
    if word.tag.gender:
        result["Постоянные признаки"]["Род"] = gender_val(word.tag.gender)
    result["Постоянные признаки"]["Склонение"] = declination_val(word)
    if word.tag.case:
        result["Непостоянные признаки"]["Падеж"] = case_val(word.tag.case)
    if word.tag.number:
        result["Непостоянные признаки"]["Число"] = number_val(word.tag.number)
    return result


def analyze_verb(word): # анализатор глагола
    result = {
        "Часть речи": "Глагол",
        "Начальная форма": word.normal_form,
        "Постоянные признаки": {}, # вид, возвратность, переходность
        "Непостоянные признаки": {} # наклонение, время, число, род и лицо
    }
    if word.tag.POS == "INFN": 
        result["Непостоянные признаки"]["Форма"] = "Инфинитив"
        return result # нам нет смысла обрабатывать начальную форму
    
    if word.tag.aspect:
        result["Постоянные признаки"]["Вид"] = aspect_val(word.tag.aspect)
    result["Постоянные признаки"]["Возвратность"] = is_returnable(word)
    if word.tag.transitivity:
        result["Постоянные признаки"]["Переходность"] = is_transitive(word.tag.transitivity)
    if word.tag.mood:
        result["Непостоянные признаки"]["Наклонение"] = mood_val(word.tag.mood)
    if word.tag.tense:
        result["Непостоянные признаки"]["Время"] = tense_val(word.tag.tense)
        if result["Непостоянные признаки"]["Время"] == "Прошедшее":
            result["Непостоянные признаки"]["Род"] = verb_gender_label(word)
    if word.tag.number:
        result["Непостоянные признаки"]["Число"] = number_val(word.tag.number)
    if word.tag.person:
        result["Непостоянные признаки"]["Лицо"] = person_val(word.tag.person)
    return result

def analyze_adjective(word): # анализатор прилагательного
    result = {
        "Часть речи": "Прилагательное",
        "Начальная форма": word.normal_form,
        "Непостоянные признаки": {} # форма, число, падеж, род
    }
    match word.tag.POS:
        case "ADJF":
            result["Непостоянные признаки"]["Форма"] = "Полная"
        case "ADJS":
            result["Непостоянные признаки"]["Форма"] = "Краткая"
        case "COMP":
            result["Непостоянные признаки"]["Форма"] = "Сравнительная"
            return result
    if word.tag.number:
        result["Непостоянные признаки"]["Число"] = number_val(word.tag.number)
    if word.tag.case:
        result["Непостоянные признаки"]["Падеж"] = case_val(word.tag.case)
    if word.tag.gender:
        result["Непостоянные признаки"]["Род"] = gender_val(word.tag.gender)
    return result

def analyze_numeral(word): # анализатор числительного
    result = {
        "Часть речи": "Числительное",
        "Начальная форма": word.normal_form,
        "Непостоянные признаки": {} # падеж, число и род
    }
    if word.tag.case:
        result["Непостоянные признаки"]["Падеж"] = case_val(word.tag.case)
    if word.tag.number:
        result["Непостоянные признаки"]["Число"] = number_val(word.tag.number)
    if word.tag.gender:
        result["Непостоянные признаки"]["Род"] = gender_val(word.tag.gender)
    return result

def analyze_adverb(word): # анализатор наречия
    result = {
        "Часть речи": "Наречие",
        "Начальная форма": word.normal_form,
        "Постоянные признаки": {} # неизменяемость
    }
    result["Постоянные признаки"]["Неизменяемость"] = "Да"
    return result

def analyze_pronoun(word): # анализатор местоимения
    result = {
        "Часть речи": "Местоимение",
        "Начальная форма": word.normal_form,
        "Постоянные признаки": {}, # лицо
        "Непостоянные признаки": {} # падеж, число и род
    }
    if word.tag.person:
        result["Постоянные признаки"]["Лицо"] = person_val(word.tag.person)
    if word.tag.case:
        result["Непостоянные признаки"]["Падеж"] = case_val(word.tag.case)
    if word.tag.number:
        result["Непостоянные признаки"]["Число"] = number_val(word.tag.number)
    if word.tag.gender:
        result["Непостоянные признаки"]["Род"] = gender_val(word.tag.gender)
    return result

def analyze_participle(word): # анализатор причастия
    result = {    
        "Часть речи": "Причастие",
        "Начальная форма": word.normal_form,
        "Постоянные признаки": {}, # вид, возвратность, залог, время и переходность
        "Непостоянные признаки": {} # форма, падеж, число, род
    }
    if word.tag.aspect:
        result["Постоянные признаки"]["Вид"] = aspect_val(word.tag.aspect)
    result["Постоянные признаки"]["ВозвратносАть"] = is_returnable(word)
    if word.tag.voice:
        result["Постоянные признаки"]["Залог"] = voice_val(word.tag.voice)
    if word.tag.tense:
        result["Постоянные признаки"]["Время"] = tense_val(word.tag.tense)
    if word.tag.transitivity:
        result["Постоянные признаки"]["Переходность"] = is_transitive(word.tag.transitivity)
    match word.tag.POS:
        case "PRTF":
            result["Непостоянные признаки"]["Форма"] = "Полная"
        case "PRTS":
            result["Непостоянные признаки"]["Форма"] = "Краткая"
    if word.tag.case:
        result["Непостоянные признаки"]["Падеж"] = case_val(word.tag.case)
    if word.tag.number:
        result["Непостоянные признаки"]["Число"] = number_val(word.tag.number)
    if word.tag.gender:
        result["Непостоянные признаки"]["Род"] = gender_val(word.tag.gender)
    return result

def analyze_transgressive(word): # анализатор деепричастия
    result = {
        "Часть речи": "Деепричастие",
        "Начальная форма": word.normal_form,
        "Постоянные признаки": {} # вид, возвратность и неизменяемость
    }
    if word.tag.aspect:
        result["Постоянные признаки"]["Вид"] = aspect_val(word.tag.aspect)
    result["Постоянные признаки"]["Возвратность"] = is_returnable(word)
    result["Постоянные признаки"]["Неизменяемость"] = "Да"
    return result

def analyze_other(word): # анализатор других частей речи
    result = {
        "Часть речи": "Неанализируемая",
        "Начальная форма": word.normal_form
    }
    return result

def morphological_analysis(word): # основной морфологический анализатор
    res = pm.parse(word)[0] # рассматриваем наиболее правдоподобный вариант
    part_of_speech = res.tag.POS # выделяем часть речи
    match part_of_speech:
        case "NOUN": # Существительное
            return analyze_noun(res)
        case "VERB" | "INFN": # Глагол или инфинитив
            return analyze_verb(res)
        case "ADJF" | "ADJS" | "COMP": # Полные/краткие прилагательные и компаративы
            return analyze_adjective(res)
        case "NUMR": # Числительное
            return analyze_numeral(res)
        case "ADVB": # Наречие
            return analyze_adverb(res)
        case "NPRO": # Местоимение
            return analyze_pronoun(res)
        case "PRTF" | "PRTS": # Причастие
            return analyze_participle(res)
        case "GRND": # Деепричастие
            return analyze_transgressive(res)
        case _: # Другие части речи (например, служебные и междометия)
            return analyze_other(res)
