import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import urllib.request
import urllib.error
from datetime import datetime


class GitHubUserFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub User Finder")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        # Файл для избранного
        self.favorites_file = "favorites.json"
        self.favorites = self.load_favorites()

        # Создание интерфейса
        self.create_widgets()

        # Загрузка избранных при старте
        self.display_favorites()

    def create_widgets(self):
        # Верхняя панель поиска
        search_frame = ttk.LabelFrame(self.root, text="Поиск пользователя", padding=10)
        search_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(search_frame, text="Введите username:").pack(side="left", padx=5)
        self.search_entry = ttk.Entry(search_frame, width=40)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<Return>", lambda e: self.search_user())

        self.search_button = ttk.Button(search_frame, text="Найти", command=self.search_user)
        self.search_button.pack(side="left", padx=5)

        # Кнопка очистки
        self.clear_button = ttk.Button(search_frame, text="Очистить", command=self.clear_search)
        self.clear_button.pack(side="left", padx=5)

        # Основная область с вкладками
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=5)

        # Вкладка результатов поиска
        self.search_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.search_tab, text="Результаты поиска")

        # Вкладка избранного
        self.favorites_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.favorites_tab, text="Избранное")

        # Создание таблиц
        self.create_search_results()
        self.create_favorites_list()

    def create_search_results(self):
        # Таблица для результатов поиска
        columns = ("ID", "Логин", "Имя", "Тип", "Репозитории", "Действия")
        self.search_tree = ttk.Treeview(self.search_tab, columns=columns, show="headings", height=15)

        self.search_tree.heading("ID", text="ID")
        self.search_tree.heading("Логин", text="Логин")
        self.search_tree.heading("Имя", text="Имя")
        self.search_tree.heading("Тип", text="Тип")
        self.search_tree.heading("Репозитории", text="Репозитории")
        self.search_tree.heading("Действия", text="Действия")

        self.search_tree.column("ID", width=80)
        self.search_tree.column("Логин", width=150)
        self.search_tree.column("Имя", width=150)
        self.search_tree.column("Тип", width=100)
        self.search_tree.column("Репозитории", width=100)
        self.search_tree.column("Действия", width=120)

        # Скроллбар
        scrollbar = ttk.Scrollbar(self.search_tab, orient="vertical", command=self.search_tree.yview)
        self.search_tree.configure(yscrollcommand=scrollbar.set)

        self.search_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Двойной клик для добавления в избранное
        self.search_tree.bind("<Double-1>", self.add_to_favorites_from_search)

    def create_favorites_list(self):
        # Таблица для избранных
        columns = ("ID", "Логин", "Имя", "Тип", "Репозитории", "Дата добавления", "Действия")
        self.fav_tree = ttk.Treeview(self.favorites_tab, columns=columns, show="headings", height=15)

        self.fav_tree.heading("ID", text="ID")
        self.fav_tree.heading("Логин", text="Логин")
        self.fav_tree.heading("Имя", text="Имя")
        self.fav_tree.heading("Тип", text="Тип")
        self.fav_tree.heading("Репозитории", text="Репозитории")
        self.fav_tree.heading("Дата добавления", text="Дата добавления")
        self.fav_tree.heading("Действия", text="Действия")

        self.fav_tree.column("ID", width=80)
        self.fav_tree.column("Логин", width=150)
        self.fav_tree.column("Имя", width=150)
        self.fav_tree.column("Тип", width=100)
        self.fav_tree.column("Репозитории", width=100)
        self.fav_tree.column("Дата добавления", width=150)
        self.fav_tree.column("Действия", width=100)

        scrollbar = ttk.Scrollbar(self.favorites_tab, orient="vertical", command=self.fav_tree.yview)
        self.fav_tree.configure(yscrollcommand=scrollbar.set)

        self.fav_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Контекстное меню для удаления
        self.fav_tree.bind("<Button-3>", self.show_context_menu)

    def search_user(self):
        username = self.search_entry.get().strip()

        # Проверка: поле поиска не должно быть пустым
        if not username:
            messagebox.showwarning("Предупреждение", "Поле поиска не может быть пустым!")
            return

        # Очистка предыдущих результатов
        self.clear_search()

        try:
            # Поиск пользователя через GitHub API с использованием urllib
            url = f"https://api.github.com/users/{username}"

            # Создаем запрос с User-Agent (требование GitHub API)
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'GitHub-User-Finder-App/1.0')

            # Выполняем запрос
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    data = response.read().decode('utf-8')
                    user_data = json.loads(data)
                    self.display_user(user_data)

        except urllib.error.HTTPError as e:
            if e.code == 404:
                messagebox.showerror("Ошибка", f"Пользователь '{username}' не найден!")
            elif e.code == 403:
                messagebox.showerror("Ошибка", "Превышен лимит запросов к API. Попробуйте позже.")
            else:
                messagebox.showerror("Ошибка", f"Ошибка API: {e.code}")
        except urllib.error.URLError as e:
            messagebox.showerror("Ошибка", f"Ошибка соединения: {str(e.reason)}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")

    def display_user(self, user_data):
        # Отображение пользователя в таблице
        login = user_data.get('login', 'N/A')
        is_favorite = any(f.get('login') == login for f in self.favorites)

        # Получаем имя пользователя (может быть None)
        name = user_data.get('name', 'Не указано')
        if name is None:
            name = 'Не указано'

        action_text = "⭐ В избранное" if not is_favorite else "✓ В избранном"

        item_id = self.search_tree.insert("", "end", values=(
            user_data.get('id', 'N/A'),
            login,
            name,
            user_data.get('type', 'N/A'),
            user_data.get('public_repos', 0),
            action_text
        ))

        # Сохраняем полные данные пользователя
        self.search_tree.item(item_id, tags=(json.dumps(user_data),))

    def add_to_favorites_from_search(self, event):
        selected = self.search_tree.selection()
        if not selected:
            return

        item = selected[0]
        values = self.search_tree.item(item, "values")
        username = values[1]

        # Проверяем, не добавлен ли уже
        if any(f.get('login') == username for f in self.favorites):
            messagebox.showinfo("Информация", f"Пользователь {username} уже в избранном!")
            return

        # Получаем сохраненные данные пользователя из тега
        tags = self.search_tree.item(item, "tags")
        if tags:
            try:
                user_data = json.loads(tags[0])
                user_data['date_added'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.favorites.append(user_data)
                self.save_favorites()
                self.display_favorites()
                messagebox.showinfo("Успех", f"Пользователь {username} добавлен в избранное!")

                # Обновляем отображение в результатах поиска
                self.search_tree.set(item, "Действия", "✓ В избранном")
            except:
                messagebox.showerror("Ошибка", "Не удалось добавить пользователя в избранное")

    def display_favorites(self):
        # Очистка таблицы избранного
        for item in self.fav_tree.get_children():
            self.fav_tree.delete(item)

        # Заполнение таблицы избранных
        for fav in self.favorites:
            name = fav.get('name', 'Не указано')
            if name is None:
                name = 'Не указано'

            self.fav_tree.insert("", "end", values=(
                fav.get('id', 'N/A'),
                fav.get('login', 'N/A'),
                name,
                fav.get('type', 'N/A'),
                fav.get('public_repos', 0),
                fav.get('date_added', 'Unknown'),
                "🗑 Удалить"
            ))

    def show_context_menu(self, event):
        selected = self.fav_tree.selection()
        if not selected:
            return

        item = selected[0]
        values = self.fav_tree.item(item, "values")
        username = values[1]

        # Создание контекстного меню
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label=f"Удалить {username} из избранного",
                         command=lambda: self.remove_from_favorites(username))
        menu.post(event.x_root, event.y_root)

    def remove_from_favorites(self, username):
        self.favorites = [f for f in self.favorites if f.get('login') != username]
        self.save_favorites()
        self.display_favorites()
        messagebox.showinfo("Успех", f"Пользователь {username} удален из избранного!")

        # Обновляем статус в результатах поиска
        for item in self.search_tree.get_children():
            values = self.search_tree.item(item, "values")
            if values[1] == username:
                self.search_tree.set(item, "Действия", "⭐ В избранное")
                break

    def clear_search(self):
        # Очистка результатов поиска
        for item in self.search_tree.get_children():
            self.search_tree.delete(item)

    def load_favorites(self):
        if os.path.exists(self.favorites_file):
            try:
                with open(self.favorites_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_favorites(self):
        with open(self.favorites_file, 'w', encoding='utf-8') as f:
            json.dump(self.favorites, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    root = tk.Tk()
    app = GitHubUserFinder(root)
    root.mainloop()