if __name__ == "__main__":
    from fav_words import analyze_books
    import json


    def determine_style(file):
        analyzed_dict = analyze_books([file])
        style_dicts = {
            'художественный': 'api_cache_fiction.json',
            'научный': 'api_cache_science.json',
            'официально-деловой': 'api_cache_oficial.json',
            'публицистический': 'api_cache_public.json'
        }
        text_lemmas = set()
        for pos in ['NOUN', 'VERB', 'ADJ', 'ADV']:
            for word_data in analyzed_dict[pos]:
                text_lemmas.add(word_data[0])
        intersections = {}
        for style, dict_file in style_dicts.items():
            with open(dict_file, 'r', encoding='utf-8') as f:
                style_dict = json.load(f)
            style_lemmas = set(style_dict.keys())
            common_lemmas = text_lemmas.intersection(style_lemmas)
            intersections[style] = {
                'count': len(common_lemmas),
                'words': common_lemmas
            }

            print(f"пересечение с {style}: {len(common_lemmas)} слов")
        res = max(intersections.items(), key=lambda x: x[1]['count'])
        print(f"наиболее вероятный стиль текста: {res[0]}")
        print(f"общих слов: {res[1]['count']}")
        print(f"общие слова: {', '.join(res[1]['words'])}")

        return

    #determine_style('dogovor_test.txt') # официально-деловой текст
    #determine_style('recenzia_test.txt') # публицистический текст (рецензия на фильм)
    #determine_style('science_text.txt') # научный текст (учебник)
    determine_style('chekhov.txt') # художественный текст (рассказ Чехова)
