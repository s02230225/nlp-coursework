import os
import re
import math
from collections import Counter
from dataclasses import dataclass

import pandas as pd
from pymorphy3 import MorphAnalyzer
from razdel import tokenize

from config import *


morph = MorphAnalyzer()
pos_names = {
    'NOUN': 'SUBSTANTIVES',
    'ADJF': 'ADJECTIVES', 
    'VERB': 'VERBS',
    'ADVB': 'ADVERBS'
}


@dataclass
class TokenInfo:
    orig: str
    lemma: str
    pos: str
    gram: object


def load_ext_freq_dict(filename):
    df = pd.read_csv(filename, sep=';', encoding='utf-8')
    ext_freq_dict, rank_dict = {}, {}
    for _, row in df.iterrows():
        lemma = str(row.iloc[0]).strip().lower()
        ext_freq_dict[lemma] = float(row.iloc[1])
        rank_dict[lemma] = int(row.iloc[2])
    return ext_freq_dict, rank_dict


def merge_ext_dicts(folder_path):
    freq_dict, rank_dict = {}, {}
    for filename in os.listdir(folder_path):
        if filename.endswith('.csv'):
            filepath = os.path.join(folder_path, filename)
            curr_freq, curr_rank = load_ext_freq_dict(filepath)
            freq_dict.update(curr_freq)
            rank_dict.update(curr_rank)
    return freq_dict, rank_dict


def texts_load(folder_path):
    texts = {}
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            filepath = os.path.join(folder_path, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                texts[filename] = f.read()
    return texts


def text_clean(text):
    text = re.sub(r'Глава\s+[XIVLC\dА-Яа-я]+', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'Часть\s+[XIVLC\dА-Яа-я]+', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'\[\d+\]', ' ', text)
    text = re.sub(r'[^А-Яа-яЁё\s\-.,!?;:]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def text_lemmatize(text):
    infos = []
    for token in tokenize(text):
        word = token.text
        parsed = morph.parse(word)[0]
        infos.append(TokenInfo(
            orig=word, 
            lemma=parsed.normal_form,
            pos=parsed.tag.POS, 
            gram=parsed.tag
        ))
    return infos


def filter_significant(token_infos):
    result = []
    for t_i in token_infos:
        # skipping foreign languages
        if not t_i.pos:
            continue
        if t_i.pos in SIGNIFICANT and not any(tag in t_i.gram for tag in SPECIAL):
            lemma = t_i.lemma.lower()
            if lemma in STOP_WORDS:
                continue
            if t_i.pos == "ADJF" and any(tag in t_i.gram for tag in ["Anph", "Apro"]):
                continue
            result.append((t_i.lemma, t_i.pos))
    return result


def freq_dict(lemmas):
    words = [l for l, _ in lemmas]
    total = len(words)
    if total == 0:
        return {}, 0
    counts = Counter(words)
    freq = {word: count / total for word, count in counts.items()}
    return freq, total


def filter_1_in_1000(freq_dict):
    threshold = THRESHOLD_PER_1K / 1000
    return {lemma: freq for lemma, freq in freq_dict.items() 
            if freq >= threshold}


def filter_popular(freq_dict, external_freq_dict):
    return {
        lemma: freq for lemma, freq in freq_dict.items()
        if external_freq_dict.get(lemma, 0) >= IPM_THRESHOLD
    }


def process_single_text(text, external_dict, do_filter=True):
    text = text_clean(text)
    lemmas = text_lemmatize(text)
    lemmas = filter_significant(lemmas)
    freq, total = freq_dict(lemmas)
    print(f"- Words after filtering: {total} total, {len(freq)} unique lemmas\n")

    freq = filter_1_in_1000(freq)
    if do_filter:
        freq = filter_popular(freq, external_dict)

    pos_freq_dicts = {pos: [] for pos in SIGNIFICANT}
    for pos in SIGNIFICANT:
        pos_lemmas = [(l, p) for l, p in lemmas if p == pos]
        pos_freq, _ = freq_dict(pos_lemmas)
        pos_freq = filter_1_in_1000(pos_freq)
        if do_filter:
            pos_freq = filter_popular(pos_freq, external_dict)
        pos_freq_dicts[pos] = pos_freq
    
    return freq, pos_freq_dicts


def filter_author(freq_dicts, min_fraction=MIN_FRACTION):
    n_texts = len(freq_dicts)
    if n_texts == 0:
        return {}
    
    occurrences = Counter()
    for d in freq_dicts:
        occurrences.update(d.keys())
        
    threshold = max(1, math.ceil(n_texts * min_fraction))
    common_words = {w for w, count in occurrences.items() if count >= threshold}
    avg_freqs = {}

    for word in common_words:
        total_freq = 0
        count_texts_with_word = 0
        for d in freq_dicts:
            if word in d:
                total_freq += d[word]
                count_texts_with_word += 1
        avg_freqs[word] = total_freq / count_texts_with_word
    
    return avg_freqs
    

def analyze_author(folder_path, external_dict, do_filter=True):
    texts = texts_load(folder_path)
    if not texts:
        print("No texts found for analysis")
        return {}, {}
    
    freq_dicts = []
    pos_freq_dicts = {pos: [] for pos in SIGNIFICANT}
    
    for i, (filename, text) in enumerate(texts.items(), 1):
        print(f'Currently processing text number {i}: {filename}')
        freq, pos_freqs = process_single_text(text, external_dict, do_filter)
        freq_dicts.append(freq)
        for pos in SIGNIFICANT:
            pos_freq_dicts[pos].append(pos_freqs[pos])
    
    favourite_words = filter_author(freq_dicts, MIN_FRACTION)
    favourite_by_pos = {
        pos: filter_author(pos_freq_dicts[pos], MIN_FRACTION)
        for pos in SIGNIFICANT
    }

    return favourite_words, favourite_by_pos


def print_favourite_words(favourite_words):
    if not favourite_words:
        print(" No words found matching the criteria\n")
        return
    print(f"\nFavourite words found: {len(favourite_words)}")
    sorted_words = sorted(favourite_words.items(), key=lambda x: x[1], reverse=True)
    for i, (word, freq) in enumerate(sorted_words[:10], 1):
        print(f"{i:2d}. {word:15s} — {freq:.5f}")


def print_favourite_by_pos(favourite_by_pos):
    for pos in SIGNIFICANT:
        pos_name = pos_names.get(pos, pos)
        print(f"\n{pos_name}:")
        print_favourite_words(favourite_by_pos.get(pos, {}))
