if __name__ == "__main__":
    from collections import defaultdict
    import csv
    import os


    def extract_simple_texts(csv_file, categories, output_dir="text_categories_simple", max_texts=100):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        category_texts = defaultdict(list)
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                category = row['class'].strip().lower()
                text = row['text'].strip()
                if category in categories and text:
                    if len(category_texts[category]) < max_texts:
                        category_texts[category].append(text)
        for category, texts in category_texts.items():
            filename = f"{category}.txt"
            filepath = os.path.join(output_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                for text in texts:
                    f.write(text + "\n\n")
            print(f"Создан файл: {filename} с {len(texts)} текстами")
        print(f"\nВсего обработано категорий: {len(category_texts)}")

    categories = ['world', 'politics', 'religion', 'society', 'science', 'culture', 'economy']
    csv_file = "text_series_full.csv"
    if not os.path.isfile(csv_file):
        print("Файл не найден!")
    else:
        extract_simple_texts(csv_file, categories)
        print("Файлы созданы!")
