"""
Вариант 12. "Засоренность речи"
Задача программы:
Анализ русскоязнычных текстов и оценка из "засоренности" - доли сленговых/жаргонных/бранных/англицизмов и т.д. среди знаменательных слов.
Программа:
    1) лемматизирует текст (Pymorphy3), токенизирует (razdel), считает части речи
    2) отфильтровывает токены: оставляет только слова, только из кириллицы
    3) считает знаменательные POS (части речи)
    4) определяет засоряющие слова по словарю лемм (slang_lemmas.csv: lemma,category,pos), берет для них POS из словаря
        - дополнительно подгоняет неточные (после лемматизации) формы слов к тем, что находятся в словаре, с помощью простых преобразований
    5) считает и выводит:
        - базовую статистику (числа токенов, слов, уникальных лемм, коэффициент лексического разнообразия текста)
        - распределение слов по POS
        - засоренность: долю мусора среди всех слов и среди только знаменательных
        - разбивку по категориям засоряющих слов
        - распределение засоряющих слов по POS
        - полный список засоряющих лемм с их количеством
    6) сохраняет неразобранные морфологическим анализатором слова, которых нет в словаре в файл <имя>_unknowns.csv в папку out при наличии таковых
    7) строит график долей засоряющих лемм внутри каждой знаменательной POS в папку out в файл <имя>_by_pos.png
    8) решает практическую задачу: определение соответствия текста, принадлежащей к определенному текстовому жанру, условной норме засоренности для данного жанра

Необходимые файлы:
  - slang_lemmas_copy.csv с колонками lemma,category,pos в папке data.
  - текстовый файл (.txt) для анализа (UTF-8) в папке corpus.

Требуемые библиотеки:
  pip install razdel pymorphy3 nltk matplotlib
"""

if __name__ == "__main__":
    import re                       # регулярные выражения: фильтрация «словных» токенов, поиск латиницы
    import csv                      # работа с csv файлами
    from pathlib import Path        # работа с путями/файлами
    import matplotlib.pyplot as plt # для графика

    from razdel import tokenize     # русская токенизация
    import pymorphy3                # лемматизация, части речи
    from nltk import FreqDist       # частоты


    #знаменательные части речи----------------------------------------------------
    contentPos = {"NOUN", "ADJF", "ADJS", "VERB", "ADVB", "NUMR", "NPRO", "PRTF", "PRTS", "GRND", "COMP"}
    # для расшифровки
    dictPos = {"NOUN": "сущ.", "ADJF": "прил.(полн)", "ADJS": "прил.(кратк)", "VERB": "глаг.", "ADVB": "нареч.", "NUMR": "числ.", "NPRO": "мест.", "PRTF": "прич.(полн)", "PRTS": "прич.(кратк)", "GRND": "деепр.", "COMP": "прил.(ср.степ.)"}

    #вспомогательные функции------------------------------------------------------

    # 1) перевод в нижний регистр, замена ё на е
    def normalizeText(s):
        return s.lower().replace("ё", "е")

    # 2) перевод инфинитива к глаголу
    def normPos(pos):
        if not pos:
            return None
        if pos == "INFN":
            return "VERB"
        return pos

    # 3) проверка, что токен — слово
    def isWordToken(t):
        if re.fullmatch(r"[A-Za-zА-Яа-яЁё]+", t):
            return True
        return False

    # 4) проверка наличия латиницы
    def hasLatin(s):
        if re.search(r"[A-Za-z]", s):
            return True
        return False

    # 5) чтение словаря сленга из CSV, возвращает словарь
    def readSlangCsv(pathStr):
        slangMap = {}
        p = Path(pathStr)
        with p.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f, delimiter=",")
            for row in reader:
                lemma = normalizeText((row["lemma"] or "").strip())
                category = (row["category"] or "").strip()
                pos = row.get("pos","").strip()
                if not lemma or not category:
                    continue
                slangMap[lemma] = {"cat":category, "pos": pos}
        return slangMap

    # 6) создание поясняющего отчёта, возвращает массив строк
    def makeReport(fileName, result):
        lines = []
        lines.append(f"Файл: {fileName}")

        lines.append("\nОбщая статистика:")
        lines.append(f"  Всего токенов:                  {result.get('totalTokens', 0)}")
        lines.append(f"  Словных токенов:                {result.get('wordTokensTotal', 0)}")
        lines.append(f"  Уникальных лемм:                {result.get('uniqueLemmas', 0)}")
        lines.append(f"  Коэфф. лексич. разнообразия:   {result.get('ttr', 0.0)}")

        # распределение cлов по частям речи
        posCounts = result.get("posCounts")
        if posCounts and getattr(posCounts, "most_common", None):
            lines.append("\nРаспределение по частям речи:")
            for pos, cnt in posCounts.most_common():
                frac = posCounts.freq(pos)
                lines.append(f"  - {pos}: {cnt} ({frac*100:.1f}%)")
   
        # засорённость
        lines.append("\nПодсчёт «засорённости» (только знаменательные POS):")
        lines.append(f"  Знаменательных слов:            {result['contentWords']}")
        lines.append(f"  «Засоряющих» по словарю:        {result['slangTotal']}")
        lines.append(f"  Степень засорённости:           {result['clogPercent']:.3f}%")
        if 'slangShareAmongAll' in result:
            lines.append(f"  Доля «мусорных» среди всех слов: {result['slangShareAmongAll']:.3f}%")

        # распределение засоряющих слов по категориям
        perCategory = result.get("perCategory")
        if perCategory and getattr(perCategory, "most_common", None):
            lines.append("\nПо категориям:")
            for cat, cnt in perCategory.most_common():
                frac = perCategory.freq(cat)
                lines.append(f"  - {cat}: {cnt} ({frac*100:.1f}%)")
    
        # засоряющие по частям речи, доля внутри каждой POS, доля от всех знаменательных
        slangPos = result.get("slangPosCounts")
        posCounts = result.get("posCounts", {})
        totalContent = result.get("contentWords", 0)

        def percentage(n, d):
            return (n / d * 100 ) if d else 0.0

        if slangPos and getattr(slangPos, "most_common", None):
            lines.append("\n«Засоряющие» по частям речи:")
            lines.append(" POS : кол-во | доля в своём POS | доля от всех знаменательных (только для знаменательных)")
            for pos, cnt in slangPos.most_common():
                samePosTotal = posCounts.get(pos, 0)
                base = result.get("posCounts", {}).get(pos, 0)
                shareInPos = percentage(cnt, samePosTotal)
                shareInAll_str = (f"{percentage(cnt, totalContent):.4f}%" if pos in contentPos else "--") # рассчитываем долю среди всех знаменательных слов только для знаменательных частей речи!!
                lines.append(f"  - {pos}: {cnt:>3} | {shareInPos:>15.4f}% | {shareInAll_str:>26}")

        # полный список засоряющих лемм
        if result.get("allLemmas"):
            pairs = [f"{lemma}:{cnt}" for lemma, cnt in result["allLemmas"]]
            lines.append("\nВсе «засоряющие» леммы (lemma:count):")
            lines.append(", ".join(pairs))
        else:
            lines.append("\nЗасоряющих лемм не найдено.")

        # про unknowns
        unknowns = result.get("unknowns")
        unkTotal = unknowns.N() if hasattr(unknowns, "N") else 0
        if unkTotal:
            lines.append(f"\nНеизвестные слова для морфоанализатора/словаря: {unkTotal}")
        else:
            lines.append("\nНеизвестных для морфоанализатора (если при этом нет в словаре) слов не найдено.")

        return "\n".join(lines)

    # 6.1) сохранение отчета в виде файла, возвращает путь к файлу
    def saveTextReport(fileName, textReport, outDir = Path("out")):
        outDir = Path(outDir)
        outDir.mkdir(parents = True, exist_ok = True)
        path = outDir / f"{fileName}_report.txt"
        path.write_text(textReport, encoding = "utf-8")
        print(f"\nТекстовый отчет сохранен: {path}")
        return path

    # 7) функция построения графика по долям засоряющих слов по значимым частям речи, возвращает путь к файлу
    def plotSlangByContentPOS(result, out_dir: Path, stem: str):

        posCounts = result.get("posCounts")
        slangPosCounts = result.get("slangPosCounts")
        if not posCounts or not slangPosCounts:
            print("График: нет данных posCounts/slangPosCounts (пропускаем)")
            return None

        bars = []

        for pos in contentPos:
            total = posCounts.get(pos, 0)
            if total <= 0:
                continue
            slang = slangPosCounts.get(pos, 0)
            share = (slang / total * 100.0) if total else 0.0
            bars.append((dictPos[pos], share, slang, total))

        if not bars:
            print("График: среди значимых POS нет данных (пропускаем)")
            return None

        bars.sort(key=lambda x: x[1], reverse=True)
        labels = [b[0] for b in bars]
        shares = [b[1] for b in bars]

        plt.figure(figsize=(9, 5))
        plt.bar(labels, shares)
        plt.title("Доля «мусорных» внутри каждой значимой части речи (%)")
        plt.ylabel("% (внутри POS)")
        plt.xlabel("POS")
        plt.tight_layout()

        for i, (pos, share, slang, total) in enumerate(bars):
            plt.text(i, share, f"{share:.1f}%\n{slang}/{total}", ha="center", va="bottom")

        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{stem}_slang_by_content_pos.png"
        plt.savefig(out_path, dpi=150)
        plt.close()
        print(f"График сохранён: {out_path}")
        return out_path


    # 8)сохранение неизвестных слов в файл CSV (слово, количество), возвращает путь к файлу
    def saveUnknownsCsv(originalPath, unknownFd, outDir = Path("out")):
        if not unknownFd:
            return None
        outDir = Path(outDir)
        outDir.mkdir(parents=True, exist_ok=True)

        stem = Path(originalPath).stem
        outPath = outDir / f"{stem}_unknowns.csv"
        with outPath.open("w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["token", "count"])
            for tok, cnt in unknownFd.most_common():
                w.writerow([tok, cnt])
        print(f"Файл неизвестных слов сохранён: {outPath}")
        return outPath

    # 9)ищем самый близкий ключ для сленгового слова в словаре
    def selectSlangKey(tok: str, lemma: str, slang: dict):
        """
        В ходе работы было замечено, что pymorphy иногда выдает неправильные леммы, например, "фейлом" -> "фейлом", "долбанутой" -> "долбанута"
        1) пробуем лемму от pymorphy3
        2) если не нашли в словаре - пробуем исходный токен
        3) если все ещё не нашли - пробуем применить упрощения:
        возвращает None или подходящий словарный ключ (лемму)
         """
        if lemma in slang:
            return lemma
        if tok in slang:
            return tok

        candidates = []

        def noun_variants(s: str): # базовая обрезка типичных окончаний существительных
            res = []
            suffixes = ["ов","ев","ами","ями","ам","ям","ах","ях","ом","ем","ой","ей","ою","ею","у","ю","а","я","ы","и","е", "о"]
            for suf in suffixes:
                if s.endswith(suf) and len(s) > len(suf) + 1:
                    res.append(s[:-len(suf)])
            return res

        def adj_variants(s: str): #приводим к "ый", "ий", как для прилагательных
            res = []
            for suf in ("ая", "яя", "ой", "ей", "ою", "ею", "ую", "юю", "ое", "ее", "ого", "его", 
                        "ому", "ему", "ым", "им", "ом", "ем", "ые", "ие", "ых", "их", "ыми", "ими"):
                if s.endswith(suf) and len(s) > 2:
                    res.append(s[:-2] + "ый")
                    res.append(s[:-2] + "ий")
                    break
            return res

        def verb_variants(s: str): # варианты для глаголов
            res: list[str] = []
            bases: set[str] = set()
            exact: set[str] = set()

            if not s or len(s) < 2:
                return res
        
            if s.endswith(("ся", "сь")) and len(s) > 2:
                forms={s[:-2]}
            else:
                forms={s}

            def add_base(b: str):
                if b:
                    bases.add(b)

            for w in list(forms):
                # прошедшее время
                for suf, cut in (("ила", 3), ("ило", 3), ("или", 3), ("ил", 2),("ала", 3), ("ало", 3), ("али", 3), ("ал", 2),
                    ("ела", 3), ("ело", 3), ("ели", 3), ("ел", 2),("яла", 3), ("яло", 3), ("яли", 3), ("ял", 2)):
                    if w.endswith(suf) and len(w) > cut + 1:
                        add_base(w[:-cut])

                #настоящее, будущее время
                for suf, cut in (("ешь", 3), ("ишь", 3), ("ете", 3), ("ите", 3),("ем", 2), ("им", 2),
                    ("ют", 2), ("ут", 2), ("ят", 2), ("ат", 2),("ую", 2),("ю", 1), ("у", 1)):
                    if w.endswith(suf) and len(w) > cut + 1:
                        add_base(w[:-cut])

                # деепричастия
                for suf, cut, tail in (("вшись", 5, "ться"),("шись",  4, "ться"),("вши",   3, "ть"),("ши",    2, "ть"),
                                       ("ая",    2, None),("яя",    2, None),("в",     1, "ть")):
                    if w.endswith(suf) and len(w) > cut + 1:
                        base = w[:-cut]
                        add_base(base)
                        if tail:
                            exact.add(base + tail)

                # причастия
                for suf in ("вший", "вшая", "вшее", "вшие","вшего", "вшую", "вших","вшему","вшей","вшим","вшими","вшем"):
                    if w.endswith(suf) and len(w) > len(suf) + 1:
                        base = w[:-len(suf)]
                        exact.add(base + "ть")
                for suf in ("нный", "нная", "нное", "нные","нного","нную","нных","нной","нному","нным","нными","нном"):
                    if w.endswith(suf) and len(w) > len(suf) + 1:
                        base = w[:-len(suf)]
                        exact.add(base + "ть")

            for b in bases:
                for inf in ("ить", "ать", "ять", "еть"):
                    res.append(b + inf)

            res.extend(exact)

            seen = set()
            out = []
            for x in res: #удаление дубликатов, сохраняя порядок
                if x not in seen:
                    seen.add(x)
                    out.append(x)
            return out

        candidates = []
        candidates += noun_variants(tok) + noun_variants(lemma)
        candidates += adj_variants(tok) + adj_variants(lemma)
        candidates += verb_variants(tok) + verb_variants(lemma)

        # проверяем по словарю (первое совпадение — и выходим)
        seen = set()
        for c in candidates:
            if c in seen:
                continue
            seen.add(c)
            if c in slang:
                return c
        return None

    # 10) основная функция анализа текста --------------------------------------------
    def analyzeText(text, slangLemmas):
        morph = pymorphy3.MorphAnalyzer()

        tokens = [t.text for t in tokenize(normalizeText(text))]
        wordTokens = [t for t in tokens if isWordToken(t)]

        totalTokens = len(tokens)
        wordTokensCount = len(wordTokens)

        posCounts = FreqDist()          # частоты частей речи для всех токенов-слов, для сленга POS берем из словаря, иначе - из pymorphy3
        lemmaSeen = set()               # для коэффициента лексического разнообразия (отношение кол-ва уникальных лемм к кол-ву всех слов)
        contentPosCounts = FreqDist()   # частоты частей речи только среди знаменательных
        perCategory = FreqDist()        # частоты засоряющих слов по категориям
        slangLemmaFd = FreqDist()       # частоты конкретных засоряющих слов по отдельности
        slangPosCounts = FreqDist()     # частоты засоряющих по частям речи (POS) (распределение мусора по POS, расчет долея по каждой части речии)
        unknownFd = FreqDist()          # частоты токенов, которые не распознал морфоанализатор, и которых нет в словаре сленга

        for tok in wordTokens:

            parses = morph.parse(tok) # работа морф. анализатора над токеном
            if parses:
                p = parses[0]
                morphPos = normPos(p.tag.POS) # сюда положим POS от морфоанализатора
                lemma = normalizeText(p.normal_form or tok)
            else:
                morphPos = None
                lemma = tok #оставляем как есть, если анализатор не смог определить POS

            if hasLatin(tok): # пропускаем латиницу
                lemmaSeen.add(lemma)
                continue

            key = selectSlangKey(tok, lemma, slangLemmas) # получаем соответствующий ключ. Получили None -- слова нет в словаре сленга,оно не засоряющее, иначе - получаем лемму из словаря, соответствующую засоряющему слову
            dictPos = None # POS из словаря (актуально для засоряющих слов)                          

            if key is not None:
                temp = slangLemmas[key]
                dictPos = (temp.get("pos") or "").upper() or "UNKNOWN"
                lemmaSeen.add(key)
            else:
                lemmaSeen.add(lemma)
        
            effectivePos = dictPos if dictPos else morphPos # "действующей" леммой для засоряющего слова будет его лемма в словаре, для остальных - то, что дал морфоанализатор

            if effectivePos:
                posCounts.update([effectivePos]) # считаем POS у всех слов
                if effectivePos in contentPos:
                    contentPosCounts.update([effectivePos]) # считаем POS среди знаменательных


            if key is not None: # для засоряющих слов
                cat = temp["cat"]
                perCategory.update([cat])
                slangLemmaFd.update([key])
                slangPosCounts.update([(dictPos or "UNKNOWN")])

            elif morphPos is None and not parses:
                unknownFd.update([tok])

        # доли
        contentCnt = contentPosCounts.N()
        slangTotal = slangPosCounts.N()

        ttr = round(len(lemmaSeen) / wordTokensCount, 3) if wordTokensCount else 0.0 # коэфф лексического разнообразия
        slangShareAmongAll = (slangTotal / wordTokensCount * 100) if wordTokensCount else 0.0 # доля засоряющих относительно всех слов

        result = {
            # общая статистика
            "totalTokens": totalTokens,
            "wordTokensTotal": wordTokensCount,
            "posCounts": posCounts,
            "contentPosCounts": contentPosCounts,
            "uniqueLemmas": len(lemmaSeen),
            "ttr": ttr,

            # засорённость
            "contentWords": contentCnt,
            "slangTotal": slangTotal,
            "clogPercent": round((slangTotal / contentCnt * 100) if contentCnt else 0.0, 3),
            "slangShareAmongAll": round(slangShareAmongAll, 3),

            # распределение мусора
            "perCategory": perCategory,
            "allLemmas": slangLemmaFd.most_common(),
            "slangPosCounts": slangPosCounts,

            "unknowns": unknownFd,
        }

        return result

    # РЕАЛИЗАЦИЯ ПРАКТИЧЕСКОЙ ЗАДАЧИ: оценка чистоты текста в соответствии с его жанром
    # профили жанров: пороги допустимой засоримости-------------------------------
    CATEGORY_PROFILES = {
        "научная_литература":         {"okMax": 1.3,  "desc": "научная/академическая публикация"},
        "официальный_документ":   {"okMax": 0.5,  "desc": "официально-деловой стиль"},
        "публицистика":           {"okMax": 0.8,  "desc": "новости/публицистическая статья"},
        "блог":                   {"okMax": 9.5, "desc": "личный блог"},
        "соцсети_форум":      {"okMax": 22.9, "desc": "неформальный текст/форумы"},
    }

    # выбор пользователем категории, к которой текст принадлежит
    def pickCategoryInteractive():
        print("\nВыберите категорию текста:")
        keys = list(CATEGORY_PROFILES.keys())
        for i, k in enumerate(keys, 1):
            print(f"  {i}. {k} — {CATEGORY_PROFILES[k]['desc']}")
        while True:
            raw = input("Номер категории: ").strip()
            if raw.isdigit() and 1 <= int(raw) <= len(keys):
                return keys[int(raw) - 1]
            print("Ошибка. Введите номер из списка.")

    # возвращает isOk, verdict, note, где:
    # isOk: bool — проходит ли порог, verdict: строка-вердикт, note: краткий комментарий по порогу.
    def isOkForCategory(clogPercent, catKey):
        prof = CATEGORY_PROFILES.get(catKey)
        if not prof:
            return None, "Неизвестная категория.", ""
        okMax = prof["okMax"]
        isOk = clogPercent <= okMax 
        verdict = "Допустимо для жанра" if isOk else "Слишком 'засорено' для жанра"
        note = f"Порог для «{catKey}»: ≤ {okMax:.1f}%. У текста: {clogPercent:.3f}%."
        return isOk, verdict, note

    # делает короткий совет: какие категории сленга и по каким POS чаще всего встретились.
    def buildAdvice(result):
        lines = []
        perCat = result.get("perCategory")
        totalSlang = 0
        if perCat and hasattr(perCat, "most_common"):
            totalSlang = perCat.N()
            if totalSlang:
                lines.append("Категории сленга (топ):")
                for cat, cnt in perCat.most_common():
                    share = cnt / totalSlang * 100
                    lines.append(f"  - {cat}: {cnt} ({share:.1f}%)")
        slangPos = result.get("slangPosCounts")
        posCounts = result.get("posCounts", {})
        if slangPos and hasattr(slangPos, "most_common"):
            lines.append("Где концентрируется «мусор» (по POS):")
            for pos, cnt in slangPos.most_common():
                base = posCounts.get(pos, 0) or 1
                share_in_pos = cnt / base * 100
                lines.append(f"  - {pos}: {cnt} (доля внутри своего POS: {share_in_pos:.1f}%)")

        if not lines:
            return "Подсказки: сленг не обнаружен по словарю."
        return "\n".join(lines)



    # код вне функций--------------------------------------------------------------

    CORPUS_DIR = Path("corpus")
    files = [p.name for p in CORPUS_DIR.iterdir() if p.is_file()]
    print("Доступные файлы в corpus/:")
    for name in sorted(files):
        print("  -", name)

    while True:
        userName = input("\nКакой текст вы хотите проверить? (имя файла из corpus/ с расширением, q - выход): ").strip()
        if userName.lower() == "q":
            print("Выход.")
            raise SystemExit(0)
        filePath = CORPUS_DIR / userName
        if filePath.exists() and filePath.is_file():
            break
        else:
            print(f"Файл не найден в corpus/: {userName}. Проверьте имя и попробуйте ещё раз.")
    category_key = pickCategoryInteractive()

    # читаем текст и словарь
    text = filePath.read_text(encoding="utf-8", errors="ignore")
    if input("Показать текст файла на экране? (1 - да, 0 - нет)").strip() == "1":
        print("\n\n--------------------------------------------------")
        print(text)
    slangPath = Path("data/slang_lemmas_copy.csv")
    slangLemmas = readSlangCsv(slangPath)

    # анализируем текст и печатаем отчёт
    result = analyzeText(text, slangLemmas)

    print("\n--------------------------------------------------")
    isOk, verdict, note = isOkForCategory(result["clogPercent"], category_key)
    print("\nОценка соответствия жанру:")
    print(f"{verdict}")
    print(note)

    print("\nНа что обратить внимание:")
    print(buildAdvice(result))

    print("\n--------------------------------------------------\n")

    reportText = makeReport(filePath.stem, result)
    if input("Показать отчет на экране? (1 - да, 0 - нет): ").strip() =="1":
        print("\n" + reportText)

    outDir = Path("out")
    reportPath = saveTextReport(filePath.stem, reportText, outDir)
    unkPath = saveUnknownsCsv(filePath, result["unknowns"], outDir)
    plotSlangByContentPOS(result, outDir, filePath.stem)
