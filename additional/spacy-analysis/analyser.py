from pandas import DataFrame  # для работы с таблицей характеристик словоформ
from spacy import load  # для загрузки нужной модели spaCy


# класс для морфологического анализа текста и подсчёта статистики
class Analyser:
    NOISE_POS = {'PUNCT', 'SPACE', 'SYM', 'X'}
    AUX_POS = {'ADP', 'AUX', 'CCONJ', 'DET', 'INTJ', 'NUM', 'PART', 'PRON', 'SCONJ'}
    MAIN_POS = {'ADJ', 'ADV', 'NOUN', 'PROPN', 'VERB'}
    WORD_POS = AUX_POS | MAIN_POS
    POS_INFO = {
        'ADJ': 'прилагательные',
        'ADP': 'адлоги',
        'ADV': 'наречия',
        'AUX': 'вспомогательные глаголы',
        'CCONJ': 'сочинительные союзы',
        'DET': 'детерминативы',
        'INTJ': 'междометия',
        'NOUN': 'существительные',
        'NUM': 'числительные',
        'PART': 'частицы',
        'PRON': 'местоимения',
        'PROPN': 'имена собственные',
        'PUNCT': 'пунктуация',
        'SCONJ': 'подчинительные союзы',
        'SPACE': 'пробельные символы',
        'SYM': 'специальные символы',
        'VERB': 'глаголы',
        'X': 'другие токены',
    }

    def __init__(self, text, language, pipeline):
        text = text.replace('-', ' ').replace('Потом', 'потом')
        doc = load(pipeline)(text)
        words = [token for token in doc if token.pos_ not in self.NOISE_POS]
        self.words = DataFrame(
            [[word.text, word.lemma_, word.pos_] for word in words],
            columns=['text', 'lemma', 'pos'],
        )
        self.sent_cnt = len([sent for sent in doc.sents])
        self.avg_sent_len = len(words) / self.sent_cnt
        self.language = language

    def get_pos(self, pos=WORD_POS):
        return self.words[self.words.pos.isin(pos)]

    def avg_word_len(self, pos=WORD_POS):
        return self.get_pos(pos).text.apply(len).mean()

    def lemma_cnt(self, pos=WORD_POS):
        return self.get_pos(pos).lemma.nunique()

    def word_form_cnt(self, pos=WORD_POS):
        return len(self.get_pos(pos))

    def lex_diversity(self, pos=WORD_POS):
        return self.lemma_cnt(pos) / self.word_form_cnt(pos)

    def pos_dist(self, pos=WORD_POS):
        return self.get_pos(pos).pos.value_counts()

    def top_lemmas(self, num, pos=WORD_POS):
        return self.get_pos(pos).lemma.value_counts().head(num)
