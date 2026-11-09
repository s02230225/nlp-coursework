if __name__ == "__main__":
    def letter_stat(text):
        d = dict()
        for s in text.lower():
            if s == 'ё': s = 'е'
            if s.isalpha():
                if d.get(s, 0) == 0:
                    d[s] = 1
                else:
                    d[s] += 1
        return d

    f = open('test', encoding='utf-8')
    text = f.read()
    d = letter_stat(text)
    letter_count = sum(d.values())
    ind = 0
    for key, val in sorted(d.items(), key= lambda x: x[1], reverse=True):
        ind += 1
        if 'а' <= key <= 'я':
            print(str(ind) + '.' + ' ' + str(key) + ' - ' + str(val) + ' | ' + '%.5f' % (val / letter_count) + ' | ' + 'русская')
        elif 'a' <= key <= 'z':
            print(str(ind) + '.' + ' ' + str(key) + ' - ' + str(val) + ' | ' + '%.5f' % (val / letter_count) + ' | ' + 'latin')


    import matplotlib.pyplot as plt
    d = dict(sorted(d.items(), key= lambda x: x[0]))

    plt.figure(figsize=(14, 14))
    plt.title('Кол-во букв в тексте', fontsize=18)
    plt.pie(x = d.values(), labels = d.keys(), explode = [i/letter_count for i in d.values()])
    plt.show()
