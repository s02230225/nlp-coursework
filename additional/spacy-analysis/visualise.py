import matplotlib.pyplot as plt  # для построения графиков
from pandas import DataFrame  # для таблицы с численной статистикой

from analyser import Analyser


# функции для визуализации полученной статистики
def get_num_stats(*analysers):
    stats = DataFrame(
        {
            a.language: [
                a.avg_sent_len,
                a.avg_word_len(),
                a.lemma_cnt(),
                a.word_form_cnt(),
                a.lex_diversity(),
            ]
            for a in analysers
        },
        index=[
            'Средняя длина предложения',
            'Средняя длина слова',
            'Число уникальных лемм',
            'Общее число словоформ',
            'Коэффициент лексического богатства',
        ],
    )
    return stats.to_markdown()


def get_pos_info(*analysers, pos=Analyser.WORD_POS):
    pos_list = sorted(list(pos))
    pos_info = DataFrame(
        [
            [Analyser.POS_INFO[name]] + [
                a.word_form_cnt(pos={name}) for a in analysers
            ]
            for name in pos_list
        ],
        index=pos_list,
        columns=['Значение'] + [a.language for a in analysers],
    )
    return pos_info.to_markdown()


def get_lemma_table(num, *analysers, pos=Analyser.WORD_POS):
    table = {}
    for a in analysers:
        lemmas = a.top_lemmas(num, pos)
        table[a.language] = lemmas.index
        table[f'№ ({a.language})'] = lemmas.values
    lemma_table = DataFrame(table, index=range(1, num + 1))
    return lemma_table.to_markdown(colalign=['left'] * (2 * len(analysers) + 1))


def plot_pos_dists(file, colormap, *analysers, pos=Analyser.WORD_POS):
    cmap = {
        name: color
        for name, color in zip(sorted(pos), plt.colormaps[colormap].colors)
    }
    plt.figure(figsize=(18 * len(analysers), 18))
    for idx, a in enumerate(analysers, 1):
        dist = a.pos_dist(pos).sort_index()
        plt.subplot(1, len(analysers), idx)
        plt.title(a.language, fontsize=48)
        plt.pie(
            x=dist.values,
            labels=dist.index,
            labeldistance=1.2,
            textprops={'fontsize': 24},
            colors=[cmap[name] for name in dist.index],
        )
    plt.savefig(file)


def plot_top_lemmas(file, colormap, num, *analysers, pos=Analyser.WORD_POS):
    plt.figure(figsize=(3 * num * len(analysers), 14))
    for idx, a in enumerate(analysers, 1):
        lemmas = a.top_lemmas(num, pos)
        cmap = plt.colormaps[colormap]
        mx, mn = lemmas.max(), lemmas.min()
        color = [cmap((val - mn) / (mx - mn)) for val in lemmas]
        plt.subplot(1, len(analysers), idx)
        plt.title(a.language, fontsize=48)
        plt.xticks(fontsize=34, rotation=18)
        plt.yticks(fontsize=34)
        plt.bar(
            x=lemmas.index,
            height=lemmas.values,
            color=color,
        )
    plt.savefig(file)
