if __name__ == "__main__":
    from sys import argv
    from analyser import Analyser
    from visualise import get_num_stats, get_pos_info, get_lemma_table, plot_pos_dists, plot_top_lemmas


    with open(argv[1], 'r', encoding='utf-8') as file:
        text, language, pipeline = [line.strip() for line in file.readlines()]
    a = Analyser(text, language, pipeline)
    print(a.sent_cnt)
    print(a.avg_sent_len)
    print(a.avg_word_len())
    print(a.lemma_cnt())
    print(a.word_form_cnt())
    print(a.lex_diversity(), end='\n\n')
    print(a.top_lemmas(1, {'NOUN'}), end='\n\n')
    print(a.get_pos(), end='\n\n')
    print(a.pos_dist(), end='\n\n')
    print(get_num_stats(a), end='\n\n')
    print(get_pos_info(a, pos={'NOUN'}), end='\n\n')
    print(get_lemma_table(3, a, pos={'NOUN'}))
    plot_pos_dists('pos_dist.jpg', 'tab20b', a)
    plot_top_lemmas('nouns.jpg', 'viridis', 4, a, pos={'NOUN'})
