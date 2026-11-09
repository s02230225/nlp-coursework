import os
import json
from config import *
from analyze_author import analyze_author, merge_ext_dicts


def round_freqs(freqs, digits=5):
    return {k: round(v, digits) for k, v in freqs.items()}


def sort_by_freq(freq_dict):
    return dict(sorted(freq_dict.items(), key=lambda x: x[1], reverse=True))


def save_res(folder_name, overall_res, by_pos_res):
    filepath = os.path.join(RESULTS_PATH, f"{folder_name}.json")
    data = {
        "overall": sort_by_freq(round_freqs(overall_res)), 
        "by_pos": {pos: sort_by_freq(round_freqs(pos_dict)) for pos, pos_dict in by_pos_res.items()}
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Results for {folder_name} saved to {filepath}")


def main():
    ans = input('Filter words by external dictionaries? (1 - yes, 0 - no): ').strip()
    do_filter = ans != "0"
    # rank - additional, isn't used for this task
    ext_dict, rank = merge_ext_dicts(DICT_PATH) if do_filter else ({}, {})

    authors = [a for a in os.listdir(AUTHORS_PATH)
               if os.path.isdir(os.path.join(AUTHORS_PATH, a))]

    for author in authors:
        print(f"\nAnalyzing {author}\n")
        folder_path = os.path.join(AUTHORS_PATH, author)
        fav_words, fav_by_pos = analyze_author(folder_path, ext_dict, do_filter)
        save_res(author, fav_words, fav_by_pos)

    print("\nAll results successfully saved.")


if __name__ == "__main__":
    main()
