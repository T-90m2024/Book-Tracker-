import json
import os
from tkinter import *
from tkinter import ttk, messagebox

DATA_FILE = "books.json"

class BookTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Book Tracker - Трекер прочитанных книг")
        self.root.geometry("900x600")
        self.root.resizable(True, True)

        self.books = []
        self.load_data()

        # Создание интерфейса
        self.create_input_frame()
        self.create_filter_frame()
        self.create_tree_frame()

        self.refresh_table()

    # ------------------- Ввод данных -------------------
    def create_input_frame(self):
        input_frame = LabelFrame(self.root, text="Добавить новую книгу", padx=10, pady=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        labels = ["Название книги:", "Автор:", "Жанр:", "Количество страниц:"]
        self.entries = {}

        for i, label in enumerate(labels):
            lbl = Label(input_frame, text=label, width=20, anchor="w")
            lbl.grid(row=i, column=0, padx=5, pady=5)
            entry = Entry(input_frame, width=40)
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.entries[label] = entry

        self.add_button = Button(input_frame, text="Добавить книгу", command=self.add_book, bg="green", fg="white")
        self.add_button.grid(row=4, column=0, columnspan=2, pady=10)

    # ------------------- Фильтры -------------------
    def create_filter_frame(self):
        filter_frame = LabelFrame(self.root, text="Фильтрация", padx=10, pady=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        Label(filter_frame, text="Фильтр по жанру:").grid(row=0, column=0, padx=5)
        self.genre_filter = Entry(filter_frame, width=20)
        self.genre_filter.grid(row=0, column=1, padx=5)

        Label(filter_frame, text="Страниц больше:").grid(row=0, column=2, padx=5)
        self.pages_filter = Entry(filter_frame, width=10)
        self.pages_filter.grid(row=0, column=3, padx=5)

        self.filter_button = Button(filter_frame, text="Применить фильтр", command=self.apply_filter)
        self.filter_button.grid(row=0, column=4, padx=10)

        self.reset_button = Button(filter_frame, text="Сбросить фильтр", command=self.reset_filter)
        self.reset_button.grid(row=0, column=5, padx=5)

    # ------------------- Таблица книг -------------------
    def create_tree_frame(self):
        tree_frame = Frame(self.root)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("ID", "Название", "Автор", "Жанр", "Страницы")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)

        scrollbar = Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

        # Кнопка удаления
        self.delete_button = Button(self.root, text="Удалить выбранную книгу", command=self.delete_book, bg="red", fg="white")
        self.delete_button.pack(pady=5)

    # ------------------- Логика -------------------
    def add_book(self):
        title = self.entries["Название книги:"].get().strip()
        author = self.entries["Автор:"].get().strip()
        genre = self.entries["Жанр:"].get().strip()
        pages = self.entries["Количество страниц:"].get().strip()

        # Проверка на пустые поля
        if not title or not author or not genre or not pages:
            messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
            return

        # Проверка, что страницы — число
        if not pages.isdigit():
            messagebox.showerror("Ошибка", "Количество страниц должно быть целым числом!")
            return

        pages = int(pages)

        new_id = max([b["id"] for b in self.books], default=0) + 1
        book = {
            "id": new_id,
            "title": title,
            "author": author,
            "genre": genre,
            "pages": pages
        }
        self.books.append(book)
        self.save_data()
        self.refresh_table()

        # Очистка полей
        for entry in self.entries.values():
            entry.delete(0, END)

        messagebox.showinfo("Успех", f"Книга '{title}' добавлена!")

    def delete_book(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите книгу для удаления!")
            return

        item = self.tree.item(selected[0])
        book_id = item["values"][0]

        for book in self.books:
            if book["id"] == book_id:
                self.books.remove(book)
                break

        self.save_data()
        self.refresh_table()
        messagebox.showinfo("Удалено", "Книга удалена.")

    def apply_filter(self):
        genre_text = self.genre_filter.get().strip().lower()
        pages_text = self.pages_filter.get().strip()

        filtered_books = self.books[:]

        if genre_text:
            filtered_books = [b for b in filtered_books if genre_text in b["genre"].lower()]

        if pages_text:
            if pages_text.isdigit():
                min_pages = int(pages_text)
                filtered_books = [b for b in filtered_books if b["pages"] > min_pages]
            else:
                messagebox.showerror("Ошибка", "Фильтр страниц должен быть числом!")

        self.display_books(filtered_books)

    def reset_filter(self):
        self.genre_filter.delete(0, END)
        self.pages_filter.delete(0, END)
        self.refresh_table()

    def refresh_table(self):
        self.display_books(self.books)

    def display_books(self, books_list):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for book in books_list:
            self.tree.insert("", END, values=(
                book["id"],
                book["title"],
                book["author"],
                book["genre"],
                book["pages"]
            ))

    # ------------------- JSON -------------------
    def save_data(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.books, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Ошибка сохранения", str(e))

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.books = json.load(f)
            except:
                self.books = []
        else:
            self.books = []

# ------------------- Запуск -------------------
if __name__ == "__main__":
    root = Tk()
    app = BookTracker(root)
    root.mainloop()
