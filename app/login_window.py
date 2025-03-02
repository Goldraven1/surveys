from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from database import Database
from styles import AppTheme

class LoginWindow:
    def __init__(self, master=None, callback=None):
        self.master = master if master else Tk()
        self.master.title("Вход в систему")
        self.master.geometry("400x500")
        self.master.configure(bg="#ecf0f1")  # Светло-серый фон
        self.db = Database()
        self.callback = callback
        
        # Применяем темы и стили
        self.theme = AppTheme(self.master)
        
        self.create_widgets()
    
    def create_widgets(self):
        # Контейнер для формы входа
        main_frame = Frame(self.master, bg=self.theme.colors['background'], padx=30, pady=30)
        main_frame.pack(fill=BOTH, expand=True)
        
        # Заголовок окна входа
        title_label = Label(main_frame, text="Вход в систему", 
                        font=self.theme.fonts['title'],
                        bg=self.theme.colors['background'], 
                        fg=self.theme.colors['primary'])
        title_label.pack(pady=20)
        
        # Форма входа в виде карточки
        login_frame = self.theme.create_card_frame(main_frame)
        login_frame.pack(fill=X, pady=10, padx=10, ipady=20)
        
        # Поле для ввода имени пользователя
        username_frame = Frame(login_frame, bg=self.theme.colors['card'], pady=10)
        username_frame.pack(fill=X, padx=20)
        
        username_label = Label(username_frame, text="Имя пользователя:", 
                          font=self.theme.fonts['normal'],
                          bg=self.theme.colors['card'], 
                          fg=self.theme.colors['text'])
        username_label.pack(anchor=W)
        
        self.username_entry = Entry(username_frame, font=self.theme.fonts['normal'],
                              width=25, bd=2, relief=SOLID)
        self.username_entry.pack(fill=X, pady=5)
        
        # Поле для ввода пароля
        password_frame = Frame(login_frame, bg=self.theme.colors['card'], pady=10)
        password_frame.pack(fill=X, padx=20)
        
        password_label = Label(password_frame, text="Пароль:", 
                          font=self.theme.fonts['normal'],
                          bg=self.theme.colors['card'], 
                          fg=self.theme.colors['text'])
        password_label.pack(anchor=W)
        
        self.password_entry = Entry(password_frame, font=self.theme.fonts['normal'],
                              width=25, bd=2, relief=SOLID, show="•")
        self.password_entry.pack(fill=X, pady=5)
        
        # Кнопки действий
        button_frame = Frame(login_frame, bg=self.theme.colors['card'], pady=20)
        button_frame.pack(fill=X)
        
        login_button = ttk.Button(button_frame, text="Войти", style="TButton",
                             command=self.login)
        login_button.pack(pady=5, fill=X, padx=20)
        
        # Разделитель
        separator = ttk.Separator(main_frame, orient=HORIZONTAL)
        separator.pack(fill=X, pady=20)
        
        # Информация внизу
        info_text = "Для доступа к системе введите\nваши учетные данные"
        info_label = Label(main_frame, text=info_text, 
                      font=self.theme.fonts['small'],
                      bg=self.theme.colors['background'], 
                      fg=self.theme.colors['text_secondary'],
                      justify=CENTER)
        info_label.pack()
    
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        # Проверка заполнения полей
        if not username or not password:
            messagebox.showerror("Ошибка", "Пожалуйста, заполните все поля")
            return
        
        # Проверка учетных данных
        if self.db.validate_login(username, password):
            if self.callback:
                self.callback(username)
            self.master.destroy()
        else:
            messagebox.showerror("Ошибка", "Неверное имя пользователя или пароль")

if __name__ == "__main__":
    app = LoginWindow()
    app.master.mainloop()
