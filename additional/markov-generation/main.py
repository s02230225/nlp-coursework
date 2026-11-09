if __name__ == "__main__":
    from tkinter import *
    from tkinter.filedialog import askopenfilename

    from MarkovChain import go


    class Application(Frame):
        def __init__(self, master):
            super(Application, self).__init__(master)
            self.window_size = 1
            self.grid()
            self.load_corpus = StringVar()
            self.load_corpus.set(None)
            self.del_delimiters = BooleanVar()
            self.del_delimiters.set(True)
            self.was_delimiters = True
            self.random_start = BooleanVar()
            self.count_words = BooleanVar()
            self.count_sentences = BooleanVar()
            self.len_sentences = 5
            self.len_words = 0
            self.weight = BooleanVar()
            self.corpus_txt = ""
            self.file_to_load = ""
            self.same_file = True
            self.dict_base = {}
            self.create_widgets()


        def create_widgets(self):
            Label(self, text="Загрузите корпус:").grid(row=0, column=0, sticky=W, padx=5, pady=5)
            Radiobutton(self, text="Текст из файла", variable=self.load_corpus,
                        value="0", command=lambda: self.open_file_load()).grid(row=1, column=0, sticky=W)
            Radiobutton(self, text="Свой текст", variable=self.load_corpus,
                        value="1").grid(row=2, column=0, sticky=W)
            self.text_field = Text(self, width=40, height=10, wrap=WORD)
            self.text_field.grid(row=3, column=0, columnspan=3, padx=5, pady=5)

            Checkbutton(self, text="Удалить знаки препинания", variable=self.del_delimiters).grid(row=4, column=0, sticky=W)
            Checkbutton(self, text="Случайное начало", variable=self.random_start).grid(row=5, column=0, sticky=W)
            Checkbutton(self, text="Учитывать встречаемость", variable=self.weight).grid(row=7, column=0, sticky=W)

            Checkbutton(self, text="Количество предложений =", variable=self.count_sentences).grid(row=8, column=0, sticky=W)
            self.len_sentences_field = Entry(self, width=5)
            self.len_sentences_field.insert(0, str(self.len_sentences))
            self.len_sentences_field.grid(row=8, column=1, sticky=W)

            Label(self, text="Размер окна").grid(row=9, column=0, sticky=W, padx=5, pady=5)
            self.window_size_entry = Entry(self, width=5)
            self.window_size_entry.insert(0, str(self.window_size))
            self.window_size_entry.grid(row=9, column=0, sticky=E)

            self.frm_res = Frame(relief=GROOVE, borderwidth=5)
            self.result_txt = Text(master=self.frm_res, width=50, height=30, wrap=WORD)
            self.result_txt.pack(fill=BOTH, side=RIGHT, expand=True)
            self.scroll = Scrollbar(command=self.result_txt.yview)
            self.scroll.pack(side=RIGHT, fill=Y)
            self.result_txt.config(yscrollcommand=self.scroll.set)
            self.frm_res.pack(fill=BOTH, side=RIGHT, expand=True)

            self.bttn2 = Button(self, text="Сгенерировать", command=lambda: self.generate())
            self.bttn2.grid(row=9, column=2, sticky=E, padx=5, pady=5)

        def open_file_load(self):
            filepath = askopenfilename(
                filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
            )
            if not filepath:
                return
            self.same_file = False
            with open(filepath, "r", encoding='utf-8') as input_file:
                self.corpus_txt = input_file.read()

        def generate(self):
            self.result_txt.delete(0.0, END)
            if self.load_corpus.get() == "1":
                self.corpus_txt = self.text_field.get(0.0, END)
            window_size_1 = self.window_size_entry.get()
            if int(window_size_1) != self.window_size:
                self.window_size = int(window_size_1)
            if self.was_delimiters != self.del_delimiters.get():
                self.was_delimiters = self.del_delimiters.get()
                self.same_file = False
            res = go(self.same_file, self.corpus_txt, self.dict_base, self.window_size, self.del_delimiters.get(), self.random_start.get(),
                     self.count_words.get(), 0, self.weight.get(), #int(self.len_words_field.get())
                     self.count_sentences.get(), int(self.len_sentences_field.get()))
            self.result_txt.insert(1.0, res[0])
            self.dict_base = res[1]
            self.same_file = True


    # создание базового окна
    root = Tk()
    root.title("Генерация текста на основе цепей Маркова")
    frame = Frame(relief=GROOVE, borderwidth=5)

    #
    app = Application(frame)
    app.grid()

    frame.pack()
    root.mainloop()
