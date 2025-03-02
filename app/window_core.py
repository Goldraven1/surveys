from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from database import Database
from styles import AppTheme
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from PIL import Image, ImageTk
import os
import threading

class Application:
    def __init__(self):
        self.db = Database()
        self.current_user = None
        self.windows = {}
        self.current_view = None
        self.image_cache = {}
    
    def create_window(self):
        self.root = Tk()
        self.root.title("Система управления опросами")
        self.root.state('zoomed')  # Запуск в полноэкранном режиме (для Windows)
        
        # Применяем темы и стили
        self.theme = AppTheme(self.root)
        
        # Создаем меню
        self.create_menu()
        
        # Создаем главный фрейм
        self.create_main_layout()
        
        # Показываем приветственное сообщение
        self.show_welcome_screen()
        
    def create_menu(self):
        menu_bar = Menu(self.root)
        
        # Файловое меню
        file_menu = Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Выход", command=self.root.quit)
        menu_bar.add_cascade(label="Файл", menu=file_menu)
        
        # Пользовательское меню
        user_menu = Menu(menu_bar, tearoff=0)
        user_menu.add_command(label="Вход", command=self.show_login_window)
        user_menu.add_command(label="Регистрация", command=self.show_registration_window)
        menu_bar.add_cascade(label="Пользователь", menu=user_menu)
        
        # Меню опросов
        self.survey_menu = Menu(menu_bar, tearoff=0)
        self.survey_menu.add_command(label="Доступные опросы", command=self.show_available_surveys, state=DISABLED)
        self.survey_menu.add_command(label="Создать опрос", command=self.show_survey_creator, state=DISABLED)
        self.survey_menu.add_command(label="Мои опросы", command=self.show_my_surveys, state=DISABLED)
        menu_bar.add_cascade(label="Опросы", menu=self.survey_menu)
        
        # Админское меню (будет активно только для администраторов)
        self.admin_menu = Menu(menu_bar, tearoff=0)
        self.admin_menu.add_command(label="Панель администратора", command=self.show_admin_panel, state=DISABLED)
        menu_bar.add_cascade(label="Администрирование", menu=self.admin_menu)
        
        self.root.config(menu=menu_bar)
    
    def create_main_layout(self):
        # Основной контейнер с паддингами
        self.main_frame = Frame(self.root, bg=self.theme.colors['background'])
        self.main_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        # Верхняя панель (header)
        self.header_frame = Frame(self.main_frame, bg=self.theme.colors['card'], height=80)
        self.header_frame.pack(fill=X, pady=(0, 20))
        
        # Логотип или название приложения в верхней панели
        app_name = Label(self.header_frame, text="Система управления опросами", 
                        font=self.theme.fonts['title'],
                        fg=self.theme.colors['primary'],
                        bg=self.theme.colors['card'])
        app_name.pack(side=LEFT, padx=20, pady=20)
        
        # Информация о пользователе в верхней панели (справа)
        self.user_info_frame = Frame(self.header_frame, bg=self.theme.colors['card'])
        self.user_info_frame.pack(side=RIGHT, padx=20, pady=20)
        
        # Рабочая область (основной контент)
        self.content_frame = Frame(self.main_frame, bg=self.theme.colors['background'])
        self.content_frame.pack(fill=BOTH, expand=True)
        
        # Статусная строка (footer)
        self.status_frame = Frame(self.main_frame, bg=self.theme.colors['card'], height=30)
        self.status_frame.pack(fill=X, pady=(20, 0))
        
        # Текст статуса
        self.status_label = Label(self.status_frame, text="Готово", 
                                bg=self.theme.colors['card'],
                                fg=self.theme.colors['text_secondary'])
        self.status_label.pack(side=LEFT, padx=10, pady=5)
    
    def show_welcome_screen(self):
        # Очищаем рабочую область
        self.clear_content_frame()
        self.update_user_info()
        
        # Приветственное сообщение
        welcome_frame = Frame(self.content_frame, bg=self.theme.colors['background'])
        welcome_frame.pack(fill=BOTH, expand=True)
        
        # Заголовок
        title_label = Label(welcome_frame, 
                           text="Добро пожаловать в систему управления опросами", 
                           font=self.theme.fonts['title'],
                           fg=self.theme.colors['primary'],
                           bg=self.theme.colors['background'])
        title_label.pack(pady=(50, 20))
        
        # Описание системы
        description_text = """
        Эта система позволяет создавать и проходить опросы,
        а также анализировать их результаты.
        
        • Создавайте собственные опросы с различными типами вопросов
        • Проходите доступные опросы
        • Анализируйте результаты с помощью наглядных графиков
        • Экспортируйте данные для дальнейшей обработки
        """
        
        description_label = Label(welcome_frame, text=description_text,
                                 font=self.theme.fonts['normal'],
                                 justify=LEFT,
                                 wraplength=600,
                                 bg=self.theme.colors['background'])
        description_label.pack(pady=20)
        
        # Карточки с функциями (если пользователь авторизован)
        if self.current_user:
            card_container = Frame(welcome_frame, bg=self.theme.colors['background'])
            card_container.pack(fill=X, pady=30)
            
            # Карточка - доступные опросы
            surveys_card = self.theme.create_card_frame(card_container)
            surveys_card.pack(side=LEFT, fill=BOTH, expand=True, padx=10)
            
            Label(surveys_card, text="Опросы", 
                 font=self.theme.fonts['subtitle']).pack(pady=10)
            Label(surveys_card, text="Просмотр и прохождение доступных опросов", 
                 wraplength=200).pack(pady=5)
            ttk.Button(surveys_card, text="Открыть", 
                      command=self.show_available_surveys).pack(pady=10)
            
            # Карточка - создание опроса
            create_card = self.theme.create_card_frame(card_container)
            create_card.pack(side=LEFT, fill=BOTH, expand=True, padx=10)
            
            Label(create_card, text="Создать опрос", 
                 font=self.theme.fonts['subtitle']).pack(pady=10)
            Label(create_card, text="Создайте новый опрос с различными типами вопросов", 
                 wraplength=200).pack(pady=5)
            ttk.Button(create_card, text="Создать", 
                      command=self.show_survey_creator).pack(pady=10)
            
            # Карточка - мои опросы
            my_surveys_card = self.theme.create_card_frame(card_container)
            my_surveys_card.pack(side=LEFT, fill=BOTH, expand=True, padx=10)
            
            Label(my_surveys_card, text="Мои опросы", 
                 font=self.theme.fonts['subtitle']).pack(pady=10)
            Label(my_surveys_card, text="Управление и анализ созданных вами опросов", 
                 wraplength=200).pack(pady=5)
            ttk.Button(my_surveys_card, text="Открыть", 
                      command=self.show_my_surveys).pack(pady=10)
        
        # Если пользователь не авторизован - показываем кнопки для входа
        else:
            auth_frame = Frame(welcome_frame, bg=self.theme.colors['background'])
            auth_frame.pack(pady=30)
            
            Label(auth_frame, 
                 text="Для доступа к функциям системы необходимо войти в систему", 
                 font=self.theme.fonts['normal'],
                 bg=self.theme.colors['background']).pack(pady=10)
            
            button_frame = Frame(auth_frame, bg=self.theme.colors['background'])
            button_frame.pack(pady=10)
            
            ttk.Button(button_frame, text="Вход", 
                      command=self.show_login_window).pack(side=LEFT, padx=10)
            ttk.Button(button_frame, text="Регистрация", 
                      command=self.show_registration_window).pack(side=LEFT, padx=10)
    
    def update_user_info(self):
        """Обновляет информацию о пользователе в верхней панели"""
        # Очищаем текущие виджеты
        for widget in self.user_info_frame.winfo_children():
            widget.destroy()
        
        if self.current_user:
            user_text = f"Пользователь: {self.current_user}"
            if self.db.is_admin(self.current_user):
                user_text += " (Администратор)"
            
            user_label = Label(self.user_info_frame, text=user_text,
                              font=self.theme.fonts['normal_bold'],
                              bg=self.theme.colors['card'])
            user_label.pack(side=LEFT, padx=(0, 10))
            
            # Кнопка выхода
            logout_btn = ttk.Button(self.user_info_frame, text="Выйти", 
                                   command=self.logout)
            logout_btn.pack(side=LEFT)
            
            # Активируем меню опросов
            self.survey_menu.entryconfig("Доступные опросы", state=NORMAL)
            self.survey_menu.entryconfig("Создать опрос", state=NORMAL)
            self.survey_menu.entryconfig("Мои опросы", state=NORMAL)
            
            # Активируем меню админа, если пользователь - админ
            if self.db.is_admin(self.current_user):
                self.admin_menu.entryconfig("Панель администратора", state=NORMAL)
        else:
            Label(self.user_info_frame, text="Гость", 
                 font=self.theme.fonts['normal'],
                 bg=self.theme.colors['card']).pack(side=LEFT)
            
            # Деактивируем меню опросов и админа
            self.survey_menu.entryconfig("Доступные опросы", state=DISABLED)
            self.survey_menu.entryconfig("Создать опрос", state=DISABLED)
            self.survey_menu.entryconfig("Мои опросы", state=DISABLED)
            self.admin_menu.entryconfig("Панель администратора", state=DISABLED)
    
    def clear_content_frame(self):
        """Очищает рабочую область"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def show_login_window(self):
        from login_window import LoginWindow
        login_window = Toplevel(self.root)
        app = LoginWindow(login_window, self.on_login_success)
    
    def show_registration_window(self):
        from registration_window import RegistrationWindow
        reg_window = Toplevel(self.root)
        app = RegistrationWindow(reg_window, self.db)
    
    def on_login_success(self, username):
        self.current_user = username
        if self.db.is_admin(username):
            messagebox.showinfo("Вход выполнен", f"Добро пожаловать, администратор {username}!")
            # Активируем меню админа
            self.admin_menu.entryconfig("Панель администратора", state=NORMAL)
        else:
            messagebox.showinfo("Вход выполнен", f"Добро пожаловать, {username}!")
        
        # Обновляем главный экран
        self.show_welcome_screen()
    
    def logout(self):
        """Выход пользователя из системы"""
        self.current_user = None
        messagebox.showinfo("Выход", "Вы вышли из системы")
        self.show_welcome_screen()
    
    def show_admin_panel(self):
        if not self.current_user or not self.db.is_admin(self.current_user):
            messagebox.showerror("Ошибка", "У вас нет прав администратора")
            return
        
        from admin_panel import AdminPanel
        admin_window = Toplevel(self.root)
        app = AdminPanel(admin_window, self.db)
    
    def show_available_surveys(self):
        """Показывает список доступных опросов"""
        if not self.current_user:
            messagebox.showinfo("Информация", "Необходимо войти в систему")
            return
        
        # Очищаем рабочую область
        self.clear_content_frame()
        
        # Заголовок
        Label(self.content_frame, text="Доступные опросы", 
             font=self.theme.fonts['title'],
             bg=self.theme.colors['background'],
             fg=self.theme.colors['primary']).pack(pady=(0, 20))
        
        # Получаем список активных опросов
        surveys = self.db.get_all_surveys(active_only=True)
        
        if not surveys:
            Label(self.content_frame, text="Нет доступных опросов", 
                 font=self.theme.fonts['normal'],
                 bg=self.theme.colors['background']).pack(pady=30)
            return
        
        # Создаем контейнер для карточек опросов
        surveys_frame = Frame(self.content_frame, bg=self.theme.colors['background'])
        surveys_frame.pack(fill=BOTH, expand=True, pady=10)
        
        # Создаем карточку для каждого опроса
        for survey in surveys:
            survey_id, title, description, creator_id, created_at, is_active = survey
            
            # Создаем карточку опроса
            survey_card = self.theme.create_card_frame(surveys_frame)
            survey_card.pack(fill=X, pady=10)
            
            # Заголовок опроса
            Label(survey_card, text=title, 
                 font=self.theme.fonts['subtitle']).pack(anchor=W, padx=10, pady=(10, 5))
            
            # Описание опроса
            if description and len(description) > 100:
                description = description[:100] + "..."
            
            Label(survey_card, text=description, 
                 wraplength=700, justify=LEFT).pack(anchor=W, padx=10, pady=5)
            
            # Дата создания
            Label(survey_card, text=f"Создан: {created_at}", 
                 font=self.theme.fonts['small'],
                 fg=self.theme.colors['text_secondary']).pack(anchor=W, padx=10, pady=5)
            
            # Кнопка прохождения опроса
            ttk.Button(survey_card, text="Пройти опрос", 
                      command=lambda sid=survey_id: self.take_survey(sid)).pack(anchor=E, padx=10, pady=10)
    
    def take_survey(self, survey_id):
        """Открывает выбранный опрос для прохождения"""
        from survey_viewer import SurveyViewer
        survey_window = Toplevel(self.root)
        app = SurveyViewer(survey_window, self.db, survey_id, self.current_user)
    
    def show_survey_creator(self):
        """Открывает окно создания нового опроса"""
        if not self.current_user:
            messagebox.showinfo("Информация", "Необходимо войти в систему")
            return
        
        from survey_creator import SurveyCreator
        creator_window = Toplevel(self.root)
        app = SurveyCreator(creator_window, self.db, self.current_user)
    
    def show_my_surveys(self):
        """Показывает список опросов, созданных текущим пользователем"""
        if not self.current_user:
            messagebox.showinfo("Информация", "Необходимо войти в систему")
            return
        
        # Очищаем рабочую область
        self.clear_content_frame()
        
        # Заголовок
        Label(self.content_frame, text="Мои опросы", 
             font=self.theme.fonts['title'],
             bg=self.theme.colors['background'],
             fg=self.theme.colors['primary']).pack(pady=(0, 20))
        
        # Кнопка создания нового опроса
        ttk.Button(self.content_frame, text="+ Создать новый опрос", 
                  command=self.show_survey_creator).pack(anchor=W, pady=10)
        
        # Получаем список опросов пользователя
        surveys = self.db.get_user_surveys(self.current_user)
        
        if not surveys:
            Label(self.content_frame, text="У вас еще нет созданных опросов", 
                 font=self.theme.fonts['normal'],
                 bg=self.theme.colors['background']).pack(pady=30)
            return
        
        # Создаем таблицу для опросов
        columns = ('id', 'title', 'created_at', 'status', 'responses')
        tree = ttk.Treeview(self.content_frame, columns=columns, show='headings')
        
        # Определяем заголовки столбцов
        tree.heading('id', text='ID')
        tree.heading('title', text='Название')
        tree.heading('created_at', text='Дата создания')
        tree.heading('status', text='Статус')
        tree.heading('responses', text='Ответы')
        
        # Настраиваем ширину столбцов
        tree.column('id', width=50, anchor='center')
        tree.column('title', width=300)
        tree.column('created_at', width=150, anchor='center')
        tree.column('status', width=100, anchor='center')
        tree.column('responses', width=100, anchor='center')
        
        # Заполняем данные
        for survey in surveys:
            survey_id = survey[0]
            
            # Получаем количество ответов на опрос (в реальном проекте должна быть функция для этого)
            responses = len(self.db.get_survey_responses(survey_id))
            
            # Статус опроса
            status = "Активен" if survey[5] == 1 else "Неактивен"
            
            tree.insert('', END, values=(survey_id, survey[1], survey[4], status, responses))
        
        # Добавляем скроллбар
        scrollbar = ttk.Scrollbar(self.content_frame, orient=VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=Y)
        tree.pack(fill=BOTH, expand=True, pady=10)
        
        # Панель действий
        action_frame = Frame(self.content_frame, bg=self.theme.colors['background'])
        action_frame.pack(fill=X, pady=10)
        
        ttk.Button(action_frame, text="Просмотр результатов", 
                  command=lambda: self.view_survey_results(tree)).pack(side=LEFT, padx=5)
        ttk.Button(action_frame, text="Изменить статус", 
                  command=lambda: self.toggle_survey_status(tree)).pack(side=LEFT, padx=5)
        ttk.Button(action_frame, text="Редактировать", 
                  command=lambda: self.edit_survey(tree)).pack(side=LEFT, padx=5)
    
    def view_survey_results(self, tree):
        """Открывает аналитику по выбранному опросу"""
        selected = tree.selection()
        if not selected:
            messagebox.showinfo("Информация", "Выберите опрос для просмотра результатов")
            return
            
        survey_id = tree.item(selected[0])['values'][0]
        
        from survey_analytics import SurveyAnalytics
        analytics_window = Toplevel(self.root)
        app = SurveyAnalytics(analytics_window, self.db, survey_id)
    
    def toggle_survey_status(self, tree):
        """Изменяет статус опроса (активен/неактивен)"""
        selected = tree.selection()
        if not selected:
            messagebox.showinfo("Информация", "Выберите опрос для изменения статуса")
            return
            
        survey_id = tree.item(selected[0])['values'][0]
        
        # Изменяем статус опроса и получаем новый статус
        new_status = self.db.toggle_survey_status(survey_id)
        
        # Обновляем отображение в таблице
        status_text = "Активен" if new_status == 1 else "Неактивен"
        tree.item(selected[0], values=(
            tree.item(selected[0])['values'][0],
            tree.item(selected[0])['values'][1],
            tree.item(selected[0])['values'][2],
            status_text,
            tree.item(selected[0])['values'][4]
        ))
        
        messagebox.showinfo("Успех", f"Статус опроса изменен на '{status_text}'")
    
    def edit_survey(self, tree):
        """Открывает окно редактирования опроса"""
        selected = tree.selection()
        if not selected:
            messagebox.showinfo("Информация", "Выберите опрос для редактирования")
            return
            
        survey_id = tree.item(selected[0])['values'][0]
        
        # В полной реализации здесь должно быть открытие окна редактирования
        messagebox.showinfo("Информация", 
                           "В данной версии редактирование существующих опросов не поддерживается")
    
    def start(self):
        self.root.mainloop()