from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from database import Database
from styles import AppTheme

class SurveyList:
    def __init__(self, master=None, db=None, username=None, show_only_user_surveys=False):
        self.master = master if master else Toplevel()
        self.master.title("Список опросов")
        self.master.geometry("800x600")
        
        self.db = db if db else Database()
        self.username = username
        self.show_only_user_surveys = show_only_user_surveys
        
        # Применяем темы и стили
        self.theme = AppTheme(self.master)
        
        # Создаем интерфейс
        self.create_widgets()
        
        # Загружаем опросы
        self.load_surveys()
    
    def create_widgets(self):
        # Основной контейнер
        main_frame = Frame(self.master, bg=self.theme.colors['background'], padx=20, pady=20)
        main_frame.pack(fill=BOTH, expand=True)
        
        # Заголовок
        title_text = "Мои опросы" if self.show_only_user_surveys else "Доступные опросы"
        title = Label(main_frame, text=title_text, 
                     font=self.theme.fonts['title'],
                     fg=self.theme.colors['primary'],
                     bg=self.theme.colors['background'])
        title.pack(anchor=W, pady=(0, 20))
        
        # Кнопка создания нового опроса (только если просматриваются свои опросы)
        if self.show_only_user_surveys:
            ttk.Button(main_frame, text="+ Создать новый опрос", 
                      command=self.create_new_survey).pack(anchor=W, pady=(0, 10))
        
        # Таблица опросов
        columns = ('id', 'title', 'description', 'created_at', 'status', 'actions')
        self.survey_tree = ttk.Treeview(main_frame, columns=columns, show='headings')
        
        # Заголовки колонок
        self.survey_tree.heading('id', text='ID')
        self.survey_tree.heading('title', text='Название')
        self.survey_tree.heading('description', text='Описание')
        self.survey_tree.heading('created_at', text='Дата создания')
        self.survey_tree.heading('status', text='Статус')
        self.survey_tree.heading('actions', text='Действия')
        
        # Размеры колонок
        self.survey_tree.column('id', width=40, anchor='center')
        self.survey_tree.column('title', width=200)
        self.survey_tree.column('description', width=250)
        self.survey_tree.column('created_at', width=120, anchor='center')
        self.survey_tree.column('status', width=80, anchor='center')
        self.survey_tree.column('actions', width=100, anchor='center')
        
        # Добавляем скроллбар
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.survey_tree.yview)
        self.survey_tree.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=RIGHT, fill=Y)
        self.survey_tree.pack(fill=BOTH, expand=True)
        
        # Привязываем событие двойного клика
        self.survey_tree.bind('<Double-1>', self.on_tree_double_click)
        
        # Кнопки внизу
        button_frame = Frame(main_frame, bg=self.theme.colors['background'], pady=10)
        button_frame.pack(fill=X)
        
        if self.show_only_user_surveys:
            # Кнопки для собственных опросов
            ttk.Button(button_frame, text="Просмотр результатов", 
                      command=self.view_results).pack(side=LEFT, padx=(0, 10))
            ttk.Button(button_frame, text="Активировать/Деактивировать", 
                      command=self.toggle_status).pack(side=LEFT, padx=(0, 10))
        else:
            # Кнопки для доступных опросов
            ttk.Button(button_frame, text="Пройти выбранный опрос", 
                      command=self.take_survey).pack(side=LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="Закрыть", 
                  command=self.master.destroy).pack(side=RIGHT)
        
        # Статусная строка
        self.status_bar = Label(main_frame, text="", 
                              bg=self.theme.colors['background'],
                              fg=self.theme.colors['text_secondary'])
        self.status_bar.pack(fill=X, pady=(10, 0), anchor=W)
    
    def load_surveys(self):
        """Загружает список опросов"""
        # Очищаем текущие данные в таблице
        for item in self.survey_tree.get_children():
            self.survey_tree.delete(item)
        
        try:
            # Получаем опросы в зависимости от режима отображения
            if self.show_only_user_surveys:
                surveys = self.db.get_user_surveys(self.username)
            else:
                surveys = self.db.get_all_surveys(active_only=True)
            
            # Заполняем таблицу данными
            for survey in surveys:
                survey_id, title, description, creator_id, created_at, is_active = survey
                
                # Форматируем данные для отображения
                if description and len(description) > 50:
                    short_description = description[:50] + "..."
                else:
                    short_description = description
                
                status = "Активен" if is_active == 1 else "Неактивен"
                
                # Добавляем строку в таблицу
                self.survey_tree.insert('', END, values=(
                    survey_id, title, short_description, created_at, status, "..."
                ))
            
            # Обновляем статусную строку
            count = len(self.survey_tree.get_children())
            self.status_bar.config(text=f"Загружено опросов: {count}")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить опросы: {str(e)}")
            self.status_bar.config(text="Ошибка при загрузке опросов")
    
    def create_new_survey(self):
        """Открывает форму для создания нового опроса"""
        from survey_creator import SurveyCreator
        creator_window = Toplevel(self.master)
        app = SurveyCreator(creator_window, self.db, self.username)
        
        # Ожидаем закрытия окна создания и обновляем список
        self.master.wait_window(creator_window)
        self.load_surveys()
    
    def view_results(self):
        """Открывает аналитику по выбранному опросу"""
        selected = self.survey_tree.selection()
        if not selected:
            messagebox.showinfo("Информация", "Выберите опрос для просмотра результатов")
            return
            
        survey_id = self.survey_tree.item(selected[0])['values'][0]
        
        from survey_analytics import SurveyAnalytics
        analytics_window = Toplevel(self.master)
        app = SurveyAnalytics(analytics_window, self.db, survey_id)
    
    def toggle_status(self):
        """Изменяет статус выбранного опроса"""
        selected = self.survey_tree.selection()
        if not selected:
            messagebox.showinfo("Информация", "Выберите опрос для изменения статуса")
            return
            
        survey_id = self.survey_tree.item(selected[0])['values'][0]
        
        # Изменяем статус опроса в базе
        new_status = self.db.toggle_survey_status(survey_id)
        
        # Обновляем отображение
        status_text = "Активен" if new_status == 1 else "Неактивен"
        self.survey_tree.item(selected[0], values=(
            self.survey_tree.item(selected[0])['values'][0],
            self.survey_tree.item(selected[0])['values'][1],
            self.survey_tree.item(selected[0])['values'][2],
            self.survey_tree.item(selected[0])['values'][3],
            status_text,
            self.survey_tree.item(selected[0])['values'][5]
        ))
        
        messagebox.showinfo("Успех", f"Статус опроса изменен на '{status_text}'")
    
    def take_survey(self):
        """Открывает форму для прохождения выбранного опроса"""
        selected = self.survey_tree.selection()
        if not selected:
            messagebox.showinfo("Информация", "Выберите опрос для прохождения")
            return
            
        survey_id = self.survey_tree.item(selected[0])['values'][0]
        
        # Открываем окно для прохождения опроса
        from survey_viewer import SurveyViewer
        survey_window = Toplevel(self.master)
        app = SurveyViewer(survey_window, self.db, survey_id, self.username)
    
    def on_tree_double_click(self, event):
        """Обрабатывает двойной клик по опросу в таблице"""
        # Получаем выбранный элемент
        item = self.survey_tree.selection()
        if not item:
            return
        
        # В зависимости от режима отображения выполняем соответствующее действие
        if self.show_only_user_surveys:
            self.view_results()
        else:
            self.take_survey()