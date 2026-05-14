import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import json
import os

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.root.geometry("800x600")
        
        self.data_file = "expenses.json"
        self.expenses = []
        
        self.load_data()
        
        self.create_widgets()
        
    def create_widgets(self):

        input_frame = ttk.LabelFrame(self.root, text="Добавление расхода", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(input_frame, text="Сумма:").grid(row=0, column=0, sticky="w", padx=5)
        self.amount_var = tk.StringVar()
        self.amount_entry = ttk.Entry(input_frame, textvariable=self.amount_var, width=15)
        self.amount_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(input_frame, text="Категория:").grid(row=0, column=2, sticky="w", padx=5)
        self.category_var = tk.StringVar()
        categories = ["Еда", "Транспорт", "Развлечения", "Здоровье", "Образование", "Коммунальные услуги", "Одежда", "Другое"]
        self.category_combo = ttk.Combobox(input_frame, textvariable=self.category_var, values=categories, width=15)
        self.category_combo.grid(row=0, column=3, padx=5)
        
        ttk.Label(input_frame, text="Дата (ДД.ММ.ГГГГ):").grid(row=0, column=4, sticky="w", padx=5)
        self.date_var = tk.StringVar(value=datetime.now().strftime("%d.%m.%Y"))
        self.date_entry = ttk.Entry(input_frame, textvariable=self.date_var, width=15)
        self.date_entry.grid(row=0, column=5, padx=5)
        
        ttk.Button(input_frame, text="Добавить расход", command=self.add_expense).grid(row=0, column=6, padx=10)
        
        filter_frame = ttk.LabelFrame(self.root, text="Фильтрация", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(filter_frame, text="Категория:").grid(row=0, column=0, sticky="w", padx=5)
        self.filter_category_var = tk.StringVar(value="Все")
        categories_filter = ["Все"] + categories
        self.filter_category_combo = ttk.Combobox(filter_frame, textvariable=self.filter_category_var, 
                                                 values=categories_filter, width=15)
        self.filter_category_combo.grid(row=0, column=1, padx=5)
        
        ttk.Label(filter_frame, text="С даты:").grid(row=0, column=2, sticky="w", padx=5)
        self.filter_start_var = tk.StringVar()
        self.filter_start_entry = ttk.Entry(filter_frame, textvariable=self.filter_start_var, width=12)
        self.filter_start_entry.grid(row=0, column=3, padx=5)
        
        ttk.Label(filter_frame, text="По дату:").grid(row=0, column=4, sticky="w", padx=5)
        self.filter_end_var = tk.StringVar(value=datetime.now().strftime("%d.%m.%Y"))
        self.filter_end_entry = ttk.Entry(filter_frame, textvariable=self.filter_end_var, width=12)
        self.filter_end_entry.grid(row=0, column=5, padx=5)
        
        ttk.Button(filter_frame, text="Применить", command=self.apply_filter).grid(row=0, column=6, padx=5)
        ttk.Button(filter_frame, text="Сбросить", command=self.reset_filter).grid(row=0, column=7, padx=5)
        
        table_frame = ttk.Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        columns = ("id", "amount", "category", "date")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        self.tree.heading("id", text="ID")
        self.tree.heading("amount", text="Сумма (руб.)")
        self.tree.heading("category", text="Категория")
        self.tree.heading("date", text="Дата")
        
        self.tree.column("id", width=50)
        self.tree.column("amount", width=100)
        self.tree.column("category", width=200)
        self.tree.column("date", width=150)
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill="x", padx=10, pady=5)
        ttk.Button(button_frame, text="Удалить выбранное", command=self.delete_expense).pack(side="left", padx=5)
        
        self.total_label = ttk.Label(button_frame, text="Общая сумма: 0.00 руб.", font=("Arial", 10, "bold"))
        self.total_label.pack(side="right", padx=20)
        
        self.update_table()
        
    def validate_amount(self, amount_str):
        """Проверка корректности суммы"""
        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError("Сумма должна быть положительной")
            return True
        except ValueError as e:
            messagebox.showerror("Ошибка", "Сумма должна быть положительным числом!")
            return False
    
    def validate_date(self, date_str):
        """Проверка корректности даты"""
        try:
            datetime.strptime(date_str, "%d.%m.%Y")
            return True
        except ValueError:
            messagebox.showerror("Ошибка", "Дата должна быть в формате ДД.ММ.ГГГГ!")
            return False
    
    def add_expense(self):
        """Добавление нового расхода"""
        amount_str = self.amount_var.get().strip()
        category = self.category_var.get().strip()
        date_str = self.date_var.get().strip()
        
        if not amount_str or not category or not date_str:
            messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
            return
        
        if not self.validate_amount(amount_str):
            return
        
        if not self.validate_date(date_str):
            return
        
        amount = float(amount_str)
        
        new_id = max([expense['id'] for expense in self.expenses], default=0) + 1
        expense = {
            'id': new_id,
            'amount': amount,
            'category': category,
            'date': date_str
        }
        
        self.expenses.append(expense)
        self.save_data()
        self.update_table()
      
        self.amount_var.set("")
        self.category_var.set("")
        
        messagebox.showinfo("Успех", f"Расход {amount:.2f} руб. добавлен!")
    
    def delete_expense(self):
        """Удаление выбранного расхода"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Выберите запись для удаления!")
            return
        
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить выбранную запись?"):
            for item in selected_item:
                values = self.tree.item(item)['values']
                expense_id = int(values[0])
                self.expenses = [exp for exp in self.expenses if exp['id'] != expense_id]
            
            self.save_data()
            self.update_table()
            messagebox.showinfo("Успех", "Записи удалены!")
    
    def apply_filter(self):
        """Применение фильтров"""
        self.update_table()
    
    def reset_filter(self):
        """Сброс фильтров"""
        self.filter_category_var.set("Все")
        self.filter_start_var.set("")
        self.filter_end_var.set(datetime.now().strftime("%d.%m.%Y"))
        self.update_table()
    
    def get_filtered_expenses(self):
        """Получение отфильтрованных расходов"""
        filtered = self.expenses.copy()
        
        filter_category = self.filter_category_var.get()
        if filter_category != "Все" and filter_category:
            filtered = [exp for exp in filtered if exp['category'] == filter_category]
  
        filter_start = self.filter_start_var.get().strip()
        filter_end = self.filter_end_var.get().strip()
        
        if filter_start:
            try:
                start_date = datetime.strptime(filter_start, "%d.%m.%Y")
                filtered = [exp for exp in filtered 
                           if datetime.strptime(exp['date'], "%d.%m.%Y") >= start_date]
            except ValueError:
                pass
        
        if filter_end:
            try:
                end_date = datetime.strptime(filter_end, "%d.%m.%Y")
                filtered = [exp for exp in filtered 
                           if datetime.strptime(exp['date'], "%d.%m.%Y") <= end_date]
            except ValueError:
                pass
        
        return filtered
    
    def update_table(self):
        """Обновление таблицы"""

        for item in self.tree.get_children():
            self.tree.delete(item)
        
        filtered_expenses = self.get_filtered_expenses()

        total = 0
        for expense in filtered_expenses:
            self.tree.insert("", "end", values=(
                expense['id'],
                f"{expense['amount']:.2f}",
                expense['category'],
                expense['date']
            ))
            total += expense['amount']
        

        self.total_label.config(text=f"Общая сумма: {total:.2f} руб.")
    
    def save_data(self):
        """Сохранение данных в JSON"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.expenses, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {str(e)}")
    
    def load_data(self):
        """Загрузка данных из JSON"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.expenses = json.load(f)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {str(e)}")
                self.expenses = []
        else:
            self.expenses = []

def main():
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()

if __name__ == "__main__":
    main()
