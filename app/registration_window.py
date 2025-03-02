from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from database import Database

class RegistrationWindow:
    def __init__(self, master=None, db=None):
        self.master = master if master else Tk()
        self.master.title("Регистрация")
        self.master.geometry("400x300")
        self.db = db if db else Database()
        self.create_widgets()

    def create_widgets(self):
        # Заголовок окна регистрации
        Label(self.master, text="Регистрация", font=("Helvetica", 16)).pack(pady=10)
        
        # Поле для ввода имени пользователя
        Label(self.master, text="Имя пользователя:").pack()
        self.username_entry = Entry(self.master)
        self.username_entry.pack()
        
        # Поле для ввода пароля
        Label(self.master, text="Пароль:").pack(pady=(10,0))
        self.password_entry = Entry(self.master, show="*")
        self.password_entry.pack()
        
        # Поле для повторного ввода пароля
        Label(self.master, text="Повторите пароль:").pack(pady=(10,0))
        self.confirm_password_entry = Entry(self.master, show="*")
        self.confirm_password_entry.pack()
        
        # Кнопка регистрации
        Button(self.master, text="Зарегистрироваться", command=self.register).pack(pady=20)
        
        # Кнопка закрытия
        Button(self.master, text="Закрыть", command=self.master.destroy).pack()

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        
        # Проверка заполнения полей
        if not username or not password:
            messagebox.showerror("Ошибка", "Пожалуйста, заполните все поля")
            return
        
        # Проверка совпадения паролей
        if password != confirm_password:
            messagebox.showerror("Ошибка", "Пароли не совпадают")
            return
        
        # Регистрация пользователя
        if self.db.register_user(username, password):
            messagebox.showinfo("Успех", f"Пользователь {username} успешно зарегистрирован")
            self.master.destroy()
        else:
            messagebox.showerror("Ошибка", "Пользователь с таким именем уже существует")

if __name__ == "__main__":
    app = RegistrationWindow()
    app.master.mainloop()
