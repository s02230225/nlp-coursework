from pymorphy3 import MorphAnalyzer

pm3 = MorphAnalyzer()


def has_gram(tag, gram: str) -> bool:
    grams = getattr(tag, "grammemes", set())
    return gram in grams

def animacy_label(animacy):
    match animacy:
        case "anim":
            return "Одушевленное"
        case "inan":
            return "Неодушевленное"
        case _:
            return "N/A"
        
def gender_label(gender):
    match gender:
        case "femn":
            return "Женский"
        case "masc":
            return "Мужской"
        case "neut":
            return "Средний"
        case _:
            return "N/A"

def declination(word_form): 
    parsed_word = pm3.parse(word_form)[0]
    if 'NOUN' not in (parsed_word.tag.POS or ''):
        return 'N/A' 
    
    lemma = parsed_word.normal_form
    parsed_lemma = pm3.parse(lemma)[0]
    
    gen = gender_label(parsed_lemma.tag.gender)
    last_letter = parsed_lemma.word[-1]

    if last_letter in ['а', 'я']:
        return '1-е склонение'
    elif last_letter in ['о', 'е'] or gen == 'Мужской':
        return '2-е склонение'
    elif last_letter == 'ь' and gen == 'Женский':
        return '3-е склонение'
    else:
        return 'N/A'

def case_label(cases):
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
        
def number_label(number):
    match number:
        case "sing":
            return "Единственное"
        case "plur":
            return "Множественное"
        case _:
            return "N/A"

def aspect_label(aspect):
    match aspect:
        case "perf":
            return "Совершенный"
        case "impf":
            return "Несовершенный"
        case _:
            return 'N/A'
        
def returnability(word):
    """
    Возвратность: сперва по граммеме Refl, затем по орфографическому признаку -ся/-сь.
    """
    if has_gram(word.tag, "Refl"):
        return "Возвратный"
    w = getattr(word, "word", "")
    if isinstance(w, str) and (w.endswith("ся") or w.endswith("сь")):
        return "Возвратный"
    return "Невозвратный"

def transit_label(transit):
    match transit:
        case "tran":
            return "Переходный"
        case "intr":
            return "Непереходный"
        case _:
            return 'N/A'

def mood_label(mood):
    match mood:
        case "indc":
            return "Изъявительное"
        case "impr" | "imp2":
            return "Повелительное"
        case _:
            return 'N/A'
        
def tense_label(tense):
    match tense:
        case 'pres':
            return "Настоящее"
        case 'past':
            return "Прошедшее"
        case 'futr':
            return "Будущее"
        case _:
            return 'N/A'

def verb_gender_label(word):
    if has_gram(word.tag, 'femn'):
        return "Женский"
    elif has_gram(word.tag, 'masc'):
        return "Мужской"
    elif has_gram(word.tag, 'neut'):
        return "Средний"
    elif has_gram(word.tag, 'plur'): 
        return "Мн.ч."
    else:
        return "N/A"

def person_label(person):
    match person:
        case '1per':
            return "Первое"
        case '2per':
            return "Второе"
        case '3per':
            return "Третье"
        case _:
            return 'N/A'

def voice_label(voice):
    match voice:
        case 'actv':
            return "Действительный"
        case 'pssv':
            return "Страдательный"
        case _:
            return 'N/A'

# ---------------------------
# Анализаторы по частям речи
# ---------------------------

def analyze_noun(word):
    result = {
        "Часть речи": "Существительное",
        "Начальная форма": word.normal_form,
        "Постоянные признаки": {},
        "Непостоянные признаки": {}
    }
    if word.tag.animacy:
        result["Постоянные признаки"]["Одушевленность"] = animacy_label(word.tag.animacy)
    if word.tag.gender:
        result["Постоянные признаки"]["Род"] = gender_label(word.tag.gender)
    result["Постоянные признаки"]["Склонение"] = declination(word.word)
    if word.tag.case:
        result["Непостоянные признаки"]["Падеж"] = case_label(word.tag.case)
    if word.tag.number:
        result["Непостоянные признаки"]["Число"] = number_label(word.tag.number)
    return result

def analyze_verb(word):
    result = {
        "Часть речи": "Глагол",
        "Начальная форма": word.normal_form,
        "Постоянные признаки": {},
        "Непостоянные признаки": {}
    }
    if word.tag.POS == "INFN":
        result["Непостоянные признаки"]["Форма"] = "Инфинитив"
        if word.tag.aspect:
            result["Постоянные признаки"]["Вид"] = aspect_label(word.tag.aspect)
        result["Постоянные признаки"]["Возвратность"] = returnability(word)
        if word.tag.transitivity:
            result["Постоянные признаки"]["Переходность"] = transit_label(word.tag.transitivity)
        return result
    
    if word.tag.aspect:
        result["Постоянные признаки"]["Вид"] = aspect_label(word.tag.aspect)
    result["Постоянные признаки"]["Возвратность"] = returnability(word)
    if word.tag.transitivity:
        result["Постоянные признаки"]["Переходность"] = transit_label(word.tag.transitivity)
    if word.tag.mood:
        result["Непостоянные признаки"]["Наклонение"] = mood_label(word.tag.mood)
    if word.tag.tense:
        result["Непостоянные признаки"]["Время"] = tense_label(word.tag.tense)
        if result["Непостоянные признаки"]["Время"] == "Прошедшее":
            result["Непостоянные признаки"]["Род"] = verb_gender_label(word)
    if word.tag.number:
        result["Непостоянные признаки"]["Число"] = number_label(word.tag.number)
    if word.tag.person:
        result["Непостоянные признаки"]["Лицо"] = person_label(word.tag.person)
    return result

def analyze_adj(word):
    result = {
        "Часть речи": "Прилагательное",
        "Начальная форма": word.normal_form,
        "Постоянные признаки": {},
        "Непостоянные признаки": {}
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
        result["Непостоянные признаки"]["Число"] = number_label(word.tag.number)
    if word.tag.case:
        result["Непостоянные признаки"]["Падеж"] = case_label(word.tag.case)
    if word.tag.gender:
        result["Непостоянные признаки"]["Род"] = gender_label(word.tag.gender)
    
    # Разряд прилагательного — используем существующие граммемы
    tag = word.tag
    if has_gram(tag, "Qual"):
        result["Постоянные признаки"]['Разряд'] = 'Качественное'
    elif has_gram(tag, "Poss"):
        result["Постоянные признаки"]['Разряд'] = 'Притяжательное'
    elif has_gram(tag, "Apro"):
        # местоименные прилагательные (в некоторых случаях встречается)
        result["Постоянные признаки"]['Разряд'] = 'Местоименное'
    else:
        # если нет явной метки — считаем относительным
        result["Постоянные признаки"]['Разряд'] = 'Относительное'

    return result

def analyze_numeral(word):
    result = {
        "Часть речи": "Числительное",
        "Начальная форма": word.normal_form,
        "Постоянные признаки": {}, 
        "Непостоянные признаки": {}
    }
    # В pymorphy3 обычно применяются Card/Ordn/Coll в граммемах (для NUMR не всегда стабильно),
    # поэтому проверяем безопасно.
    tag = word.tag
    if has_gram(tag, 'Card'):
        result["Постоянные признаки"]["Разряд"] = "Количественное"
    elif has_gram(tag, 'Ordn'):
        result["Постоянные признаки"]["Разряд"] = "Порядковое"
    elif has_gram(tag, 'Coll'):
        result["Постоянные признаки"]["Разряд"] = "Собирательное"
    
    if word.tag.case:
        result["Непостоянные признаки"]["Падеж"] = case_label(word.tag.case)
    if word.tag.number:
        result["Непостоянные признаки"]["Число"] = number_label(word.tag.number)
    if word.tag.gender:
        result["Непостоянные признаки"]["Род"] = gender_label(word.tag.gender)
    return result

def analyze_adverb(word):
    result = {
        "Часть речи": "Наречие",
        "Начальная форма": word.normal_form,
        "Постоянные признаки": {}
    }
    result["Постоянные признаки"]["Неизменяемость"] = "Да"
    
    tag = word.tag
    if has_gram(tag, 'Qual'):
        result["Постоянные признаки"]["Разряд"] = "Качественное"
    elif has_gram(tag, 'Loc'):
        result["Постоянные признаки"]["Разряд"] = "Места"
    elif has_gram(tag, 'Time'):
        result["Постоянные признаки"]["Разряд"] = "Времени"
    elif has_gram(tag, 'Caus'):
        result["Постоянные признаки"]["Разряд"] = "Причины"
    elif has_gram(tag, 'Purp'):
        result["Постоянные признаки"]["Разряд"] = "Цели"
    
    return result

def analyze_pronoun(word):
    result = {
        "Часть речи": "Местоимение",
        "Начальная форма": word.normal_form,
        "Постоянные признаки": {},
        "Непостоянные признаки": {}
    }
    # Лицо (если задано)
    if word.tag.person:
        result["Постоянные признаки"]["Лицо"] = person_label(word.tag.person)

    # Разряд местоимения: pymorphy3 не размечает полноценно все школьные разряды.
    # Чтобы не ошибаться и не падать, укажем метку по возможности:
    # - 'Apro' иногда ставится у местоименных прилагательных.
    if has_gram(word.tag, 'Apro'):
        result["Постоянные признаки"]["Разряд"] = "Местоименное прилагательное"
    else:
        # Если нет явной метки — оставим общий тип без конкретизации
        result["Постоянные признаки"]["Разряд"] = "Местоимение (тип не указан словарём)"

    # Непостоянные признаки
    if word.tag.case:
        result["Непостоянные признаки"]["Падеж"] = case_label(word.tag.case)
    if word.tag.number:
        result["Непостоянные признаки"]["Число"] = number_label(word.tag.number)
    if word.tag.gender:
        result["Непостоянные признаки"]["Род"] = gender_label(word.tag.gender)
    return result

def analyze_participle(word):
    result = {    
        "Часть речи": "Причастие",
        "Начальная форма": word.normal_form,
        "Постоянные признаки": {},
        "Непостоянные признаки": {}
    }
    if word.tag.aspect:
        result["Постоянные признаки"]["Вид"] = aspect_label(word.tag.aspect)
    result["Постоянные признаки"]["Возвратность"] = returnability(word)
    if word.tag.voice:
        result["Постоянные признаки"]["Залог"] = voice_label(word.tag.voice)
    if word.tag.tense:
        result["Постоянные признаки"]["Время"] = tense_label(word.tag.tense)
    if word.tag.transitivity:
        result["Постоянные признаки"]["Переходность"] = transit_label(word.tag.transitivity)
    
    match word.tag.POS:
        case "PRTF":
            result["Непостоянные признаки"]["Форма"] = "Полная"
        case "PRTS":
            result["Непостоянные признаки"]["Форма"] = "Краткая"
    if word.tag.case:
        result["Непостоянные признаки"]["Падеж"] = case_label(word.tag.case)
    if word.tag.number:
        result["Непостоянные признаки"]["Число"] = number_label(word.tag.number)
    if word.tag.gender:
        result["Непостоянные признаки"]["Род"] = gender_label(word.tag.gender)
    return result

def analyze_transgressive(word):
    result = {
        "Часть речи": "Деепричастие",
        "Начальная форма": word.normal_form,
        "Постоянные признаки": {}
    }
    if word.tag.aspect:
        result["Постоянные признаки"]["Вид"] = aspect_label(word.tag.aspect)
    result["Постоянные признаки"]["Возвратность"] = returnability(word)
    result["Постоянные признаки"]["Неизменяемость"] = "Да"
    return result

def analyze_other(word):
    result = {
        "Часть речи": str(word.tag.POS) if word.tag.POS else "Неанализируемая",
        "Начальная форма": word.normal_form
    }
    if word.tag:
        result["Теги"] = str(word.tag)
    return result


def MorphoAnalyz(word):
    res = pm3.parse(word)[0]
    part_of_speech = res.tag.POS
    match part_of_speech:
        case "NOUN":
            return analyze_noun(res)
        case "VERB" | "INFN":
            return analyze_verb(res)
        case "ADJF" | "ADJS" | "COMP":
            return analyze_adj(res)
        case "NUMR":
            return analyze_numeral(res)
        case "ADVB":
            return analyze_adverb(res)
        case "NPRO":
            return analyze_pronoun(res)
        case "PRTF" | "PRTS":
            return analyze_participle(res)
        case "GRND":
            return analyze_transgressive(res)
        case _:
            return analyze_other(res)
