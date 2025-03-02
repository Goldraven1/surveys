from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from database import Database

class AdminPanel:
    def __init__(self, master=None, db=None):
        self.master = master if master else Tk()
        self.master.title("Панель администратора")
        self.master.geometry("800x600")
        self.db = db if db else Database()
        self.create_widgets()

    def create_widgets(self):
        # Заголовок панели администратора
        Label(self.master, text="Панель администратора", font=("Helvetica", 16)).pack(pady=10)
        
        # Фрейм для управления пользователями
        user_frame = LabelFrame(self.master, text="Управление пользователями")
        user_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        # Создаем таблицу пользователей
        columns = ('id', 'username', 'is_admin', 'created_at')
        self.users_tree = ttk.Treeview(user_frame, columns=columns, show='headings')
        
        # Определяем заголовки столбцов
        self.users_tree.heading('id', text='ID')
        self.users_tree.heading('username', text='Имя пользователя')
        self.users_tree.heading('is_admin', text='Администратор')
        self.users_tree.heading('created_at', text='Дата регистрации')
        
        # Настраиваем ширину столбцов
        self.users_tree.column('id', width=50)
        self.users_tree.column('username', width=200)
        self.users_tree.column('is_admin', width=100)
        self.users_tree.column('created_at', width=200)
        
        # Добавляем скроллбар
        scrollbar = ttk.Scrollbar(user_frame, orient=VERTICAL, command=self.users_tree.yview)
        self.users_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.users_tree.pack(fill=BOTH, expand=True, pady=10)
        
        # Загружаем данные о пользователях
        self.load_users()
        
        # Кнопки управления пользователями
        btn_frame = Frame(user_frame)
        btn_frame.pack(fill=X, pady=10)
        
        Button(btn_frame, text="Обновить список", command=self.load_users).pack(side=LEFT, padx=5)
        Button(btn_frame, text="Добавить администратора", command=self.add_admin).pack(side=LEFT, padx=5)
        Button(btn_frame, text="Удалить пользователя", command=self.delete_user).pack(side=LEFT, padx=5)
        
        # Кнопка закрытия
        Button(self.master, text="Закрыть", command=self.master.destroy).pack(pady=10)

    def load_users(self):
        # Очищаем текущую таблицу
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)
        
        # Получаем всех пользователей
        users = self.db.get_all_users()
        for user in users:
            # Преобразуем флаг админа в текст
            user_data = list(user)
            user_data[2] = "Да" if user_data[2] == 1 else "Нет"
            self.users_tree.insert('', END, values=user_data)
    
    def add_admin(self):
        # Создаем окно для добавления администратора
        add_window = Toplevel(self.master)
        add_window.title("Добавить администратора")
        add_window.geometry("300x200")
        
        Label(add_window, text="Имя пользователя:").pack(pady=(10,0))
        username_entry = Entry(add_window)
        username_entry.pack(pady=(5,0))
        
        Label(add_window, text="Пароль:").pack(pady=(10,0))
        password_entry = Entry(add_window, show="*")
        password_entry.pack(pady=(5,0))
        
        def save_admin():
            username = username_entry.get()
            password = password_entry.get()
            
            if not username or not password:
                messagebox.showerror("Ошибка", "Заполните все поля", parent=add_window)
                return
            
            if self.db.register_user(username, password, is_admin=1):
                messagebox.showinfo("Успех", f"Администратор {username} добавлен", parent=add_window)
                add_window.destroy()
                self.load_users()
            else:
                messagebox.showerror("Ошибка", "Пользователь с таким именем уже существует", parent=add_window)
        
        Button(add_window, text="Сохранить", command=save_admin).pack(pady=20)
        Button(add_window, text="Отмена", command=add_window.destroy).pack()
    
    def delete_user(self):
        # Получаем выбранного пользователя
        selected_item = self.users_tree.selection()
        if not selected_item:
            messagebox.showerror("Ошибка", "Выберите пользователя")
            return
        
        # В реальном приложении здесь должно быть удаление из базы
        # Сейчас просто сообщение, т.к. метод удаления не реализован в Database
        user_id = self.users_tree.item(selected_item)['values'][0]
        messagebox.showinfo("Информация", f"Функция удаления пользователя с ID={user_id} не реализована")
        
        # В полной реализации нужно добавить метод в Database и вызвать его здесь

if __name__ == "__main__":
    app = AdminPanel()
    app.master.mainloop()
