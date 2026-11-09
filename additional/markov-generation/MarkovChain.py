from nltk.tokenize import sent_tokenize, word_tokenize
import re
import random

def sentence_split(text, del_delimiters):
    sents = sent_tokenize(text)
    sent_words = []
    for sent in sents:
        if del_delimiters:
            sent = re.sub(r'[^\w\s]', '', sent)
        words = word_tokenize(sent)
        sent_words += [["*START*"] + words + ["*END*"]]
    sent_words[-1] += ["NONE"]
    return sent_words


def create_dict(sents, ws):
    d = {}  # counts words
    dict_b = {}
    prev = []
    for sent in sents:
        for word in sent:
            word = re.sub(r'\s', '', word)
            if word in d:
                d[word] += 1
            else:
                d[word] = 1
            if prev:
                if len(prev) == ws:
                    window = tuple(prev)
                    if window in dict_b:
                        if not (word in dict_b[window]):
                            dict_b[window] += [word]
                    else:
                        dict_b[window] = [word]
                    prev = prev[1:] + [word]
                else:
                    prev += [word]
            else:
                prev += [word]
    return combine_dicts(d, dict_b)


def combine_dicts(d, dict_b):
    final_dict = {}
    for el in dict_b:
        l = []
        for word in dict_b[el]:
            l += [dict.fromkeys([word], d[word])]
        final_dict[el] = l
    return final_dict


def generate_sentence(dict_base, del_delimiters, random_start=False, count_words=False, len_words=0, weight=False,
                      count_sent=False, len_sent=5):
    str = ""
    flag = True
    new_first_word = False
    len_sentences = len_sent
    first_word = find_first_word(dict_base, random_start)
    str += make_sub_string(first_word, del_delimiters)
    word = first_word
    while flag:
        next_word = find_next_word(word, dict_base, count_words, len_words, weight)
        f = True
        while f:
            if count_sent & (len_sentences > 0) & (next_word[0] == "NONE"):
                if len(dict_base[word]) == 1:
                    if count_sent & (len_sentences > 1):
                        next_word = find_first_word(dict_base, random_start)
                        new_first_word = True
                    else:
                        f = False
                else:
                    next_word = find_next_word(word, dict_base, count_words, len_words, weight)
            else:
                f = False
        if next_word[0] == "NONE":
            flag = False
        elif count_sent & (len_sentences <= 0):
            flag = False
        elif count_sent & (next_word[0] == "*START*"):
            len_sentences -= 1
            if not new_first_word:
                word = make_next_tuple(word, next_word)
            else:
                word = next_word
        else:
            if not new_first_word:
                word = make_next_tuple(word, next_word)
            else:
                word = next_word
        if flag:
            str += make_sub_string(tuple(list(next_word)), del_delimiters)
        new_first_word = False
    return str


def find_first_word(dict_base, random_start):
    if random_start:
        return random.choice(list(dict_base.keys()))
    else:
        l = []
        for el in dict_base:
            if el[0] == "*START*":
                l += [el]
        return random.choice(l)


def find_next_word(curr_word, dict_base, count_left_len, left_len_word, weight):
    list_of_possible = dict_base[curr_word]
    if not weight:
        if not count_left_len:
            l = []
            for el in list_of_possible:
                l += [list(el.keys())]
            return random.choice(l)
        else:
            list_from = []
            list_probability = []
            for el in list_of_possible:
                list_from += list(el.keys())
                if list(el.keys())[0] == "*END*":
                    if left_len_word <= 0:
                        list_probability += [1 + abs(left_len_word) + 1]
                    else:
                        list_probability += [1]
                else:
                    list_probability += [1]
            return random.choices(list_from, weights=list_probability)
    else:
        list_from = []
        list_probability = []
        most_met = 0
        for e in list_probability:
            if list(e.values)[0] > most_met:
                most_met = list(e.values)[0]
        for el in list_of_possible:
            list_from += list(el.keys())
            if list(el.keys())[0] == "*END*":
                if count_left_len:
                    if left_len_word <= 0:
                        list_probability += [el[list(el.keys())[0]] * most_met * (abs(left_len_word) + 1)]
                    else:
                        list_probability += [el[list(el.keys())[0]]]
                else:
                    list_probability += [el[list(el.keys())[0]]]
            else:
                list_probability += [el[list(el.keys())[0]]]
        return random.choices(list_from, weights=list_probability)


def make_sub_string(tuple_word, del_delimiters):
    str = ""
    for el in tuple_word:
        if el != "*START*":
            if el == "*END*":
                if del_delimiters:
                    str = str[:-1] + ". "
            elif el == "NONE":
                str += ".\n"
            else:
                str += el + " "
    return str


def make_next_tuple(prev_tuple, next_word):
    l = []
    for el in prev_tuple:
        l += [el]
    l += next_word
    l = l[1:]
    return tuple(l)


def go(same, corpus, dict_base, window_size, del_delimiters, random_start,
       count_words, len_words, weight, count_sentences, len_sentences):
    if (not same) | (not dict_base):
        sentences = sentence_split(corpus, del_delimiters)
        dict_base = create_dict(sentences, window_size)
    res = generate_sentence(dict_base, del_delimiters, random_start,
                            count_words, len_words, weight, count_sentences, len_sentences)
    return res, dict_base
