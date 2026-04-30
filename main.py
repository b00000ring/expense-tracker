import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

DATA_FILE = "data.json"


class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.root.geometry("950x600")
        self.root.resizable(False, False)

        self.expenses = []

        self.create_ui()
        self.load_data()

        # Автосохранение при закрытии
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    # ================= UI =================

    def create_ui(self):
        main_frame = tk.Frame(self.root, padx=10, pady=10)
        main_frame.pack(fill="both", expand=True)

        # ===== Форма добавления =====
        form_frame = tk.LabelFrame(main_frame, text="Добавить расход", padx=10, pady=10)
        form_frame.pack(fill="x", pady=5)

        tk.Label(form_frame, text="Сумма:").grid(row=0, column=0)
        self.amount_entry = ttk.Entry(form_frame)
        self.amount_entry.grid(row=0, column=1, padx=5)

        tk.Label(form_frame, text="Категория:").grid(row=0, column=2)
        self.category_entry = ttk.Entry(form_frame)
        self.category_entry.grid(row=0, column=3, padx=5)

        tk.Label(form_frame, text="Дата (YYYY-MM-DD):").grid(row=0, column=4)
        self.date_entry = ttk.Entry(form_frame)
        self.date_entry.grid(row=0, column=5, padx=5)

        ttk.Button(form_frame, text="Добавить", command=self.add_expense).grid(row=0, column=6, padx=10)

        # ===== Фильтрация =====
        filter_frame = tk.LabelFrame(main_frame, text="Фильтрация", padx=10, pady=10)
        filter_frame.pack(fill="x", pady=5)

        tk.Label(filter_frame, text="Категория:").grid(row=0, column=0)
        self.filter_category = ttk.Entry(filter_frame)
        self.filter_category.grid(row=0, column=1, padx=5)

        tk.Label(filter_frame, text="С даты:").grid(row=0, column=2)
        self.filter_from = ttk.Entry(filter_frame)
        self.filter_from.grid(row=0, column=3, padx=5)

        tk.Label(filter_frame, text="По дату:").grid(row=0, column=4)
        self.filter_to = ttk.Entry(filter_frame)
        self.filter_to.grid(row=0, column=5, padx=5)

        ttk.Button(filter_frame, text="Применить", command=self.apply_filter).grid(row=0, column=6, padx=5)
        ttk.Button(filter_frame, text="Сбросить", command=self.refresh_table).grid(row=0, column=7, padx=5)

        # ===== Таблица =====
        table_frame = tk.Frame(main_frame)
        table_frame.pack(fill="both", expand=True, pady=5)

        columns = ("amount", "category", "date")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        self.tree.heading("amount", text="Сумма")
        self.tree.heading("category", text="Категория")
        self.tree.heading("date", text="Дата")

        self.tree.column("amount", width=100)
        self.tree.column("category", width=200)
        self.tree.column("date", width=150)

        self.tree.pack(fill="both", expand=True)

        # ===== Нижняя панель =====
        bottom_frame = tk.Frame(main_frame)
        bottom_frame.pack(fill="x", pady=5)

        ttk.Button(bottom_frame, text="Удалить выбранный", command=self.delete_selected).pack(side="left", padx=5)
        ttk.Button(bottom_frame, text="Подсчитать за период", command=self.calculate_total).pack(side="left", padx=5)
        ttk.Button(bottom_frame, text="Сохранить", command=self.save_data).pack(side="right", padx=5)

        self.total_label = tk.Label(bottom_frame, text="Итого: 0", font=("Arial", 12, "bold"))
        self.total_label.pack(side="right", padx=10)

    # ================= Логика =================

    def add_expense(self):
        amount = self.amount_entry.get().strip()
        category = self.category_entry.get().strip()
        date = self.date_entry.get().strip()

        # Проверка суммы
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Сумма должна быть положительным числом.")
            return

        # Проверка даты
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Ошибка", "Дата должна быть в формате YYYY-MM-DD.")
            return

        if not category:
            messagebox.showerror("Ошибка", "Категория не может быть пустой.")
            return

        expense = {"amount": amount, "category": category, "date": date}
        self.expenses.append(expense)
        self.refresh_table()
        self.clear_entries()

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите запись для удаления.")
            return

        for item in selected:
            values = self.tree.item(item)["values"]
            for expense in self.expenses:
                if (
                    expense["amount"] == float(values[0])
                    and expense["category"] == values[1]
                    and expense["date"] == values[2]
                ):
                    self.expenses.remove(expense)
                    break

        self.refresh_table()

    def refresh_table(self, data=None):
        for row in self.tree.get_children():
            self.tree.delete(row)

        dataset = data if data is not None else self.expenses

        for expense in dataset:
            self.tree.insert("", "end", values=(expense["amount"], expense["category"], expense["date"]))

    def apply_filter(self):
        filtered = self.expenses
        category = self.filter_category.get().strip().lower()
        from_date = self.filter_from.get().strip()
        to_date = self.filter_to.get().strip()

        if category:
            filtered = [e for e in filtered if category in e["category"].lower()]

        if from_date:
            filtered = [e for e in filtered if e["date"] >= from_date]

        if to_date:
            filtered = [e for e in filtered if e["date"] <= to_date]

        self.refresh_table(filtered)

    def calculate_total(self):
        from_date = self.filter_from.get().strip()
        to_date = self.filter_to.get().strip()

        filtered = self.expenses

        if from_date:
            filtered = [e for e in filtered if e["date"] >= from_date]

        if to_date:
            filtered = [e for e in filtered if e["date"] <= to_date]

        total = sum(e["amount"] for e in filtered)
        self.total_label.config(text=f"Итого: {total:.2f}")

    def save_data(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.expenses, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("Успех", "Данные сохранены.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сохранения: {e}")

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.expenses = json.load(f)
            except:
                self.expenses = []
        self.refresh_table()

    def clear_entries(self):
        self.amount_entry.delete(0, tk.END)
        self.category_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)

    def on_closing(self):
        self.save_data()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()