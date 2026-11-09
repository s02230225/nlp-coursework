if __name__ == "__main__":
    from os import chdir, getcwd  # для управления рабочей директорией
    from sys import argv  # для получения аргументов с командной строки
    from tempfile import TemporaryDirectory  # для получения временной директории

    from markdown_pdf import MarkdownPdf, Section  # для генерации pdf из Markdown

    from analyser import Analyser
    from visualise import get_num_stats, get_pos_info, get_lemma_table, plot_pos_dists, plot_top_lemmas


    # генерация pdf-файла со статистикой по русскому и английскому тексту
    # использование: python main.py rus.txt eng.txt stats.pdf

    title = input('Название текста: ').strip()
    incl_aux_pos = int(input('Включать вспомогательные части речи в график частотных лемм? (0/1): '))
    top_lemma_num = int(input('Число отображаемых на графике частотных лемм: '))
    main_pos_num = int(input('Число отображаемых на графике лемм основных частей речи: '))

    rus_path, eng_path, out_path = argv[1:]
    print(f'Анализ русского текста из {rus_path}...')
    with open(rus_path, 'r', encoding='utf-8') as rus_file:
        rus = Analyser(rus_file.read(), 'Русский', 'ru_core_news_sm')
    print(f'Анализ английского текста из {eng_path}...')
    with open(eng_path, 'r', encoding='utf-8') as eng_file:
        eng = Analyser(eng_file.read(), 'Английский', 'en_core_web_sm')

    parent = getcwd()
    tmpdir = TemporaryDirectory()
    chdir(tmpdir.name)
    stats = MarkdownPdf()

    print('Генерация общей статистики по текстам...')
    plot_pos_dists('pos_dists.jpg', 'tab20b', rus, eng)
    general_stats = f'''
    ## {title}: cтатистика

    ### Численная статистика

    {get_num_stats(rus, eng)}

    ### Распределение частей речи

    {get_pos_info(rus, eng)}

    ![](pos_dists.jpg)
    '''
    stats.add_section(Section(general_stats, borders=(24, 24, -24, -24), toc=False))

    print('Генерация статистики по часто используемым словам...')
    incl_pos = Analyser.WORD_POS if incl_aux_pos else Analyser.MAIN_POS
    plot_top_lemmas('common_rus.jpg', 'viridis', top_lemma_num, rus, pos=incl_pos)
    plot_top_lemmas('common_eng.jpg', 'viridis', top_lemma_num, eng, pos=incl_pos)
    top_lemmas = f'''
    ### Самые часто используемые слова

    {get_lemma_table(top_lemma_num, rus, eng, pos=incl_pos)}

    ![](common_rus.jpg)

    ![](common_eng.jpg)
    '''
    stats.add_section(Section(top_lemmas, borders=(24, 24, -24, -24), toc=False))

    print('Генерация статистики по существительным и прилагательным...')
    plot_top_lemmas('nouns.jpg', 'cividis', main_pos_num, rus, eng, pos={'NOUN'})
    plot_top_lemmas('adjectives.jpg', 'plasma', main_pos_num, rus, eng, pos={'ADJ'})
    main_pos_p1 = f'''
    ### Существительные

    {get_lemma_table(main_pos_num, rus, eng, pos={'NOUN'})}

    ![](nouns.jpg)

    ### Прилагательные

    {get_lemma_table(main_pos_num, rus, eng, pos={'ADJ'})}

    ![](adjectives.jpg)
    '''
    stats.add_section(Section(main_pos_p1, borders=(24, 24, -24, -24), toc=False))

    print('Генерация статистики по глаголам и наречиям...')
    plot_top_lemmas('verbs.jpg', 'inferno', main_pos_num, rus, eng, pos={'VERB'})
    plot_top_lemmas('adverbs.jpg', 'magma', main_pos_num, rus, eng, pos={'ADV'})
    main_pos_p2 = f'''
    ### Глаголы

    {get_lemma_table(main_pos_num, rus, eng, pos={'VERB'})}

    ![](verbs.jpg)

    ### Наречия

    {get_lemma_table(main_pos_num, rus, eng, pos={'ADV'})}

    ![](adverbs.jpg)
    '''
    stats.add_section(Section(main_pos_p2, borders=(24, 24, -24, -24), toc=False))

    print(f'Сохранение полученной статистики в {out_path}...')
    chdir(parent)
    stats.save(out_path)
    tmpdir.cleanup()
