if __name__ == "__main__":
    import nltk

    def isrussian(word):
        return all((('а' <= s <= 'я') or (s == '.' or s == '/' or s == '-')) for s in word) # проверяем что только выделенные символы содержатся в слове

    def parse_sentences(text):
        i = 1
        sent_lens = []
        all_sentences = nltk.sent_tokenize(text, language="russian")
        for sentence in all_sentences:
            tokens = sentence.lower().strip()
            token_count = len(tokens.split())
            # all_w = tokens.split()
            # all_w = [tok.replace('ё', 'е').replace(' . ', ' ').replace(' - ', ' ').replace(' / ', ' ') for tok in all_w]
            tokens = tokens.replace('ё', 'е')
            tokens = tokens.replace(' . ', ' ')
            tokens = tokens.replace(' - ', ' ')
            tokens = tokens.replace(' / ', ' ')
            new = ''
            for s in tokens:
                if (not s.isspace()) and (not s.isalnum()) and (s not in ('.', '-', '/')):
                   new += ' '
                else:
                    new += s
            if new[-1] == '.':
                new = new[:-1]
            rwords_lens = []
            for s in new.split():
                if isrussian(s):
                    rwords_lens += [len(s)]
            print('Предложение %d.' % i, "  ", sentence, 'Токенов: %d,' % token_count, 'русских слов: %d' % len(rwords_lens), '(' + str(rwords_lens)[1:-1] + ' букв' + ')')
            i += 1
            sent_lens += [token_count]
        print('Средняя длина предложения: %.4f' % (sum(sent_lens) / len(all_sentences)))
        print('Средняя длина слова из русских букв: %.4f' % (sum(rwords_lens) / len(rwords_lens)))

    punctuation_marks = """\
    		На записке был текст: "Привет. Буду утром." \
      		"Привет. Как дела?" - сказал он. \
    		«Не могу дождаться летних каникул», — воскликнул Петя.
    		"""
    
    # parse_sentences(punctuation_marks)
    f = open('test')
    parse_sentences(f.read())
