import os, json, numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter
from analyze_author import process_single_text, merge_ext_dicts
from config import *


def load_profiles(path):
    return {
        f.replace(".json", ""): json.load(open(os.path.join(path, f), encoding="utf-8"))
        for f in os.listdir(path) if f.endswith(".json")
    }


def top_words(freq, n=50): 
    return dict(sorted(freq.items(), key=lambda x: x[1], reverse=True)[:n])


def sim_cos(d1, d2, n=100):
    all_w = list(set(top_words(d1, n)) | set(top_words(d2, n)))
    if len(all_w) < 20: 
        return 0
    v1 = np.array([d1.get(w, 0) for w in all_w])
    v2 = np.array([d2.get(w, 0) for w in all_w])
    return float(cosine_similarity([v1], [v2])[0][0])


def sim_top_words(author_profile, text_freq, n=50):
    author_top = set(top_words(author_profile["overall"], n))
    text_top = set(top_words(text_freq, n))
    return len(author_top & text_top) / n


def sim_charact_words(author_name, author_profile, all_profiles, text_freq):
    author_words = set(author_profile["overall"].keys())
    other_freq = Counter()

    for name, profile in all_profiles.items():
        if name != author_name:
            for w, f in profile["overall"].items():
                if w in author_words:
                    other_freq[w] += f

    scores = {}
    for w in author_words:
        author_f = author_profile["overall"][w]
        avg_other = other_freq[w] / 5 if other_freq[w] > 0 else 1e-6
        scores[w] = author_f / avg_other

    top_unique = {w for w, _ in sorted(scores.items(), key=lambda x: x[1], reverse=True)[:25]}
    text_top = set(top_words(text_freq, 50))
    return len(top_unique & text_top) / 25


def sim_pos(author_profile, text_pos):
    sim = []

    for pos in SIGNIFICANT:
        a_pos = author_profile["by_pos"].get(pos, {})
        t_pos = text_pos.get(pos, {})
        if not a_pos or not t_pos:
            continue

        a_top = set(top_words(a_pos, 15))
        t_top = set(top_words(t_pos, 15))
        overlap = len(a_top & t_top) / 15
        sim.append(overlap)

    return np.mean(sim) if sim else 0.0


def cmp_author(name, profile, freq, pos, all_profiles):
    metrics = {
        "top": sim_top_words(profile, freq),
        "char": sim_charact_words(name, profile, all_profiles, freq),
        "freq": sim_cos(profile["overall"], freq),
        "pos": sim_pos(profile, pos),
    }
    score = (
        metrics["top"] * 0.2 +
        metrics["char"] * 0.5 +
        metrics["freq"] * 0.2 +
        metrics["pos"] * 0.1
    )

    return score, metrics


def identify_author(text_path, profiles, ext_dict):
    with open(text_path, "r", encoding="utf-8") as f:
        text = f.read()

    print(f"\nAnalyzing: {os.path.basename(text_path)}")
    text_freq, text_pos = process_single_text(text, ext_dict, do_filter=True)
    results = {}

    for author, profile in profiles.items():
        score, comps = cmp_author(author, profile, text_freq, text_pos, profiles)
        results[author] = (score, comps)

    sorted_results = sorted(results.items(), key=lambda x: x[1][0], reverse=True)

    print('Similarities:')
    for author, (score, comps) in sorted_results:
        print(f" {author:12s}: {score:.4f}")

    best_author = sorted_results[0][0]
    print(f"\nPresumed author: {best_author}")

    return sorted_results


def main():
    ext_dict, _ = merge_ext_dicts(DICT_PATH)
    author_profiles = load_profiles(RESULTS_PATH)
    print(f"Loaded author profiles: {', '.join(author_profiles.keys())}")

    test_files = [
        os.path.join("texts_for_testing", f)
        for f in os.listdir("texts_for_testing")
        if f.endswith(".txt")
    ]

    for test_file in test_files:
        identify_author(test_file, author_profiles, ext_dict)


if __name__ == "__main__":
    main()
