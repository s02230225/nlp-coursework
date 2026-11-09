if __name__ == "__main__":
    import numpy as np
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score
    import matplotlib.pyplot as plt

    # Чтение слов из файла words_small.txt
    with open("words_small.txt", "r", encoding="utf-8") as f:
        words = f.read().split()[1:]  # Пропускаем первый пустой элемент

    # Получение эмбеддингов
    embeddings = []
    valid_words = []
    for word in words:
        if word in wv_embeddings:
            embeddings.append(wv_embeddings[word])
            valid_words.append(word)

    embeddings = np.array(embeddings)
    # Нормализация
    embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)

    # Анализ оптимального количества кластеров
    inertias = []
    silhouette_scores = []
    k_range = range(2, 11)

    for k in k_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(embeddings)
        inertias.append(kmeans.inertia_)
        
        if len(set(labels)) > 1:
            silhouette_scores.append(silhouette_score(embeddings, labels))
        else:
            silhouette_scores.append(0)

    # Визуализация
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

    # График инерции
    ax1.plot(k_range, inertias, 'bo-')
    ax1.set_xlabel('Количество кластеров')
    ax1.set_ylabel('Инерция')
    ax1.set_title('Метод локтя')
    ax1.grid(True)

    # График силуэтного коэффициента
    ax2.plot(k_range, silhouette_scores, 'ro-')
    ax2.set_xlabel('Количество кластеров')
    ax2.set_ylabel('Силуэтный коэффициент')
    ax2.set_title('Силуэтный анализ')
    ax2.grid(True)

    plt.tight_layout()
    plt.show()
