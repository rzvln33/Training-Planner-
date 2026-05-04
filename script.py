import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime


class TrainingPlanner:
    def __init__(self, root):
        self.root = root
        self.root.title("Training Planner - План тренировок")
        self.root.geometry("800x600")

        # Данные тренировок
        self.trainings = []
        self.filtered_trainings = []

        # Файл для сохранения данных
        self.data_file = "trainings.json"

        # Создание интерфейса
        self.create_widgets()

        # Загрузка данных при старте
        self.load_from_json()

    def create_widgets(self):
        # Рамка для ввода данных
        input_frame = ttk.LabelFrame(self.root, text="Добавление тренировки", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        # Поле Дата
        ttk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.date_entry = ttk.Entry(input_frame, width=20)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # Поле Тип тренировки
        ttk.Label(input_frame, text="Тип тренировки:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.training_type = tk.StringVar()
        self.type_combo = ttk.Combobox(input_frame, textvariable=self.training_type, width=20)
        self.type_combo['values'] = ('Бег', 'Плавание', 'Йога', 'Велосипед', 'Фитнес', 'Лыжи', 'Другое')
        self.type_combo.grid(row=1, column=1, padx=5, pady=5)
        self.type_combo.current(0)

        # Поле Длительность
        ttk.Label(input_frame, text="Длительность (мин):").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.duration_entry = ttk.Entry(input_frame, width=20)
        self.duration_entry.grid(row=2, column=1, padx=5, pady=5)

        # Кнопка Добавить
        self.add_button = ttk.Button(input_frame, text="Добавить тренировку", command=self.add_training)
        self.add_button.grid(row=3, column=0, columnspan=2, pady=10)

        # Рамка для фильтрации
        filter_frame = ttk.LabelFrame(self.root, text="Фильтрация", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        # Фильтр по типу
        ttk.Label(filter_frame, text="Тип тренировки:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.filter_type = tk.StringVar()
        self.filter_type_combo = ttk.Combobox(filter_frame, textvariable=self.filter_type, width=20)
        self.filter_type_combo['values'] = ('Все', 'Бег', 'Плавание', 'Йога', 'Велосипед', 'Фитнес', 'Лыжи', 'Другое')
        self.filter_type_combo.grid(row=0, column=1, padx=5, pady=5)
        self.filter_type_combo.current(0)

        # Фильтр по дате
        ttk.Label(filter_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.filter_date = ttk.Entry(filter_frame, width=20)
        self.filter_date.grid(row=1, column=1, padx=5, pady=5)

        # Кнопки фильтрации
        button_frame = ttk.Frame(filter_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)

        self.apply_filter_btn = ttk.Button(button_frame, text="Применить фильтр", command=self.apply_filter)
        self.apply_filter_btn.pack(side="left", padx=5)

        self.reset_filter_btn = ttk.Button(button_frame, text="Сбросить фильтр", command=self.reset_filter)
        self.reset_filter_btn.pack(side="left", padx=5)

        # Рамка для кнопок JSON
        json_frame = ttk.Frame(self.root)
        json_frame.pack(fill="x", padx=10, pady=5)

        self.save_btn = ttk.Button(json_frame, text="💾 Сохранить в JSON", command=self.save_to_json)
        self.save_btn.pack(side="left", padx=5)

        self.load_btn = ttk.Button(json_frame, text="📂 Загрузить из JSON", command=self.load_from_json)
        self.load_btn.pack(side="left", padx=5)

        # Таблица для отображения тренировок
        table_frame = ttk.LabelFrame(self.root, text="Список тренировок", padding=10)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Создание таблицы
        columns = ('Дата', 'Тип тренировки', 'Длительность (мин)')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)

        # Настройка заголовков
        self.tree.heading('Дата', text='Дата')
        self.tree.heading('Тип тренировки', text='Тип тренировки')
        self.tree.heading('Длительность (мин)', text='Длительность (мин)')

        # Настройка ширины колонок
        self.tree.column('Дата', width=150)
        self.tree.column('Тип тренировки', width=200)
        self.tree.column('Длительность (мин)', width=150)

        # Добавление скроллбара
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def validate_date(self, date_string):
        """Проверка корректности даты"""
        try:
            datetime.strptime(date_string, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def validate_duration(self, duration_string):
        """Проверка корректности длительности"""
        try:
            duration = float(duration_string)
            if duration > 0:
                return True, duration
            else:
                return False, None
        except ValueError:
            return False, None

    def add_training(self):
        """Добавление новой тренировки"""
        # Получение данных
        date = self.date_entry.get().strip()
        training_type = self.training_type.get()
        duration_str = self.duration_entry.get().strip()

        # Валидация даты
        if not self.validate_date(date):
            messagebox.showerror("Ошибка", "Неверный формат даты!\nИспользуйте формат: ГГГГ-ММ-ДД\nПример: 2026-05-04")
            return

        # Валидация длительности
        is_valid, duration = self.validate_duration(duration_str)
        if not is_valid:
            messagebox.showerror("Ошибка", "Длительность должна быть положительным числом!\nПример: 30, 45.5")
            return

        # Добавление тренировки
        training = {
            'date': date,
            'type': training_type,
            'duration': duration
        }

        self.trainings.append(training)
        self.apply_filter()  # Обновление отображения с текущим фильтром

        # Очистка поля длительности для удобства
        self.duration_entry.delete(0, tk.END)

        # Автоматическое сохранение после добавления
        self.save_to_json()

        messagebox.showinfo("Успех", "Тренировка успешно добавлена!")

    def apply_filter(self):
        """Применение фильтров к списку тренировок"""
        filter_type = self.filter_type.get()
        filter_date = self.filter_date.get().strip()

        self.filtered_trainings = self.trainings.copy()

        # Фильтрация по типу
        if filter_type != 'Все':
            self.filtered_trainings = [t for t in self.filtered_trainings if t['type'] == filter_type]

        # Фильтрация по дате
        if filter_date:
            if self.validate_date(filter_date):
                self.filtered_trainings = [t for t in self.filtered_trainings if t['date'] == filter_date]
            else:
                messagebox.showwarning("Предупреждение", "Неверный формат даты фильтра!\nИспользуйте: ГГГГ-ММ-ДД")

        self.update_table()

    def reset_filter(self):
        """Сброс всех фильтров"""
        self.filter_type.set('Все')
        self.filter_date.delete(0, tk.END)
        self.filtered_trainings = self.trainings.copy()
        self.update_table()

    def update_table(self):
        """Обновление таблицы с текущими отфильтрованными данными"""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Заполнение таблицы
        for training in self.filtered_trainings:
            self.tree.insert('', 'end', values=(
                training['date'],
                training['type'],
                f"{training['duration']:.1f}" if isinstance(training['duration'], float)
                else str(training['duration'])
            ))

    def save_to_json(self):
        """Сохранение данных в JSON файл"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.trainings, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Успех", f"Данные успешно сохранены в файл {self.data_file}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {str(e)}")

    def load_from_json(self):
        """Загрузка данных из JSON файла"""
        if not os.path.exists(self.data_file):
            messagebox.showinfo("Информация", f"Файл {self.data_file} не найден. Будет создан новый при сохранении.")
            return

        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                self.trainings = json.load(f)
            self.apply_filter()
            messagebox.showinfo("Успех", f"Данные успешно загружены из файла {self.data_file}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = TrainingPlanner(root)
    root.mainloop()