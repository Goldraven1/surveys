from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from database import Database
from styles import AppTheme
import json

class SurveyCreator:
    def __init__(self, master=None, db=None, username=None, survey_id=None):
        self.master = master if master else Toplevel()
        self.master.title("Создание опроса")
        self.master.geometry("900x700")
        self.db = db if db else Database()
        self.username = username
        self.survey_id = survey_id  # None для нового опроса, id для редактирования
        self.questions = []
        
        # Применяем темы и стили
        self.theme = AppTheme(self.master)
        
        # Инициализируем интерфейс
        self.create_widgets()
        
        # Если редактирование - загружаем данные опроса
        if self.survey_id:
            self.load_survey_data()
    
    def create_widgets(self):
        # Создаем главный фрейм с паддингом
        main_frame = Frame(self.master, bg=self.theme.colors['background'], padx=20, pady=20)
        main_frame.pack(fill=BOTH, expand=True)
        
        # Заголовок
        header_text = "Создание нового опроса" if not self.survey_id else "Редактирование опроса"
        header = ttk.Label(main_frame, text=header_text, style="Title.TLabel")
        header.pack(pady=(0, 20))
        
        # Фрейм для информации об опросе
        info_frame = self.theme.create_card_frame(main_frame)
        info_frame.pack(fill=X, pady=10)
        
        # Название опроса
        ttk.Label(info_frame, text="Название опроса:").pack(anchor=W, padx=10, pady=(10, 5))
        self.title_entry = Entry(info_frame, font=self.theme.fonts['normal'], width=50)
        self.title_entry.pack(fill=X, padx=10, pady=(0, 10))
        
        # Описание опроса
        ttk.Label(info_frame, text="Описание опроса:").pack(anchor=W, padx=10, pady=(10, 5))
        self.description_text = Text(info_frame, font=self.theme.fonts['normal'], height=4)
        self.description_text.pack(fill=X, padx=10, pady=(0, 10))
        
        # Разделитель
        ttk.Separator(main_frame, orient=HORIZONTAL).pack(fill=X, pady=20)
        
        # Заголовок секции вопросов
        ttk.Label(main_frame, text="Вопросы", style="Subtitle.TLabel").pack(pady=(0, 10))
        
        # Фрейм со списком вопросов и скроллбаром
        questions_container = Frame(main_frame, bg=self.theme.colors['background'])
        questions_container.pack(fill=BOTH, expand=True, pady=10)
        
        # Скроллбар для списка вопросов
        self.canvas = Canvas(questions_container, bg=self.theme.colors['background'], highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(questions_container, orient="vertical", command=self.canvas.yview)
        
        self.questions_frame = Frame(self.canvas, bg=self.theme.colors['background'])
        self.questions_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        
        self.canvas.create_window((0, 0), window=self.questions_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Кнопки для управления вопросами
        btn_frame = Frame(main_frame, bg=self.theme.colors['background'])
        btn_frame.pack(fill=X, pady=10)
        
        ttk.Button(btn_frame, text="Добавить вопрос с одним ответом", 
                 command=lambda: self.add_question("radio")).pack(side=LEFT, padx=5)
        ttk.Button(btn_frame, text="Добавить вопрос с множественным выбором", 
                 command=lambda: self.add_question("checkbox")).pack(side=LEFT, padx=5)
        ttk.Button(btn_frame, text="Добавить текстовый вопрос", 
                 command=lambda: self.add_question("text")).pack(side=LEFT, padx=5)
        
        # Кнопка сохранения
        action_frame = Frame(main_frame, bg=self.theme.colors['background'])
        action_frame.pack(fill=X, pady=20)
        
        ttk.Button(action_frame, text="Сохранить опрос", style="Success.TButton", 
                 command=self.save_survey).pack(side=RIGHT, padx=5)
        ttk.Button(action_frame, text="Отмена", 
                 command=self.master.destroy).pack(side=RIGHT, padx=5)
    
    def add_question(self, question_type):
        """Добавляет новый вопрос в интерфейс"""
        question_frame = self.create_question_frame(len(self.questions) + 1, question_type)
        question_frame.pack(fill=X, pady=10)
        self.questions.append(question_frame)
        
        # Обновляем скроллинг
        self.master.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def create_question_frame(self, question_num, question_type, question_data=None):
        """Создает фрейм для одного вопроса"""
        frame = self.theme.create_card_frame(self.questions_frame)
        
        # Заголовок с номером вопроса и кнопкой удаления
        header_frame = Frame(frame, bg=self.theme.colors['card'])
        header_frame.pack(fill=X, padx=10, pady=5)
        
        question_type_text = {
            "radio": "Один вариант ответа",
            "checkbox": "Множественный выбор",
            "text": "Текстовый ответ"
        }
        
        Label(header_frame, text=f"Вопрос {question_num}: {question_type_text.get(question_type)}", 
             font=self.theme.fonts['normal_bold'],
             bg=self.theme.colors['card']).pack(side=LEFT)
        
        Button(header_frame, text="✖", bg=self.theme.colors['card'], 
             command=lambda f=frame: self.remove_question(f)).pack(side=RIGHT)
        
        # Поле для текста вопроса
        Label(frame, text="Текст вопроса:",
             bg=self.theme.colors['card']).pack(anchor=W, padx=10, pady=(5, 0))
        
        question_text_entry = Entry(frame, font=self.theme.fonts['normal'])
        question_text_entry.pack(fill=X, padx=10, pady=5)
        
        # Если есть данные - заполняем их
        if question_data and 'question_text' in question_data:
            question_text_entry.insert(0, question_data['question_text'])
        
        # Флаг обязательности
        required_var = IntVar(value=1)  # По умолчанию обязательный
        if question_data and 'required' in question_data:
            required_var.set(question_data['required'])
        
        required_check = Checkbutton(frame, text="Обязательный вопрос",
                                    variable=required_var,
                                    bg=self.theme.colors['card'])
        required_check.pack(anchor=W, padx=10, pady=5)
        
        # Контейнер для опций (если применимо)
        options_container = Frame(frame, bg=self.theme.colors['card'])
        options_container.pack(fill=X, padx=10, pady=5)
        
        options_list = []
        
        # Добавление вариантов ответа для radio и checkbox
        if question_type in ["radio", "checkbox"]:
            Label(options_container, text="Варианты ответа:",
                 bg=self.theme.colors['card']).pack(anchor=W)
            
            options_frame = Frame(options_container, bg=self.theme.colors['card'])
            options_frame.pack(fill=X, pady=5)
            
            # Начальные варианты ответа
            initial_options = []
            if question_data and 'options' in question_data and question_data['options']:
                initial_options = question_data['options']
            elif question_type in ["radio", "checkbox"]:
                initial_options = ["Вариант 1", "Вариант 2"]
            
            # Добавление вариантов
            for option in initial_options:
                option_entry = self.add_option(options_frame, option)
                options_list.append(option_entry)
            
            # Кнопка для добавления нового варианта
            Button(options_container, text="+ Добавить вариант", 
                 command=lambda: options_list.append(
                     self.add_option(options_frame))).pack(anchor=W)
        
        # Сохраняем данные в тег фрейма для дальнейшего использования
        frame.question_type = question_type
        frame.question_text_entry = question_text_entry
        frame.required_var = required_var
        frame.options_list = options_list
        frame.question_id = question_data['id'] if question_data and 'id' in question_data else None
        
        return frame
    
    def add_option(self, parent, initial_text=""):
        """Добавляет поле для ввода варианта ответа"""
        option_frame = Frame(parent, bg=self.theme.colors['card'])
        option_frame.pack(fill=X, pady=2)
        
        option_entry = Entry(option_frame, font=self.theme.fonts['normal'])
        option_entry.pack(side=LEFT, fill=X, expand=True, padx=(0, 5))
        
        if initial_text:
            option_entry.insert(0, initial_text)
        
        Button(option_frame, text="✖", bg=self.theme.colors['card'],
             command=lambda: option_frame.destroy()).pack(side=RIGHT)
        
        return option_entry
    
    def remove_question(self, question_frame):
        """Удаляет вопрос из интерфейса"""
        self.questions.remove(question_frame)
        question_frame.destroy()
        
        # Перенумерация оставшихся вопросов
        for i, frame in enumerate(self.questions, 1):
            header_frame = frame.winfo_children()[0]  # Первый дочерний элемент - header_frame
            label = header_frame.winfo_children()[0]  # Первый элемент в header_frame - Label
            
            # Обновляем номер в тексте
            text = label.cget('text')
            question_type_text = text.split(':', 1)[1] if ':' in text else ""
            label.config(text=f"Вопрос {i}:{question_type_text}")
    
    def save_survey(self):
        """Сохраняет опрос в БД"""
        title = self.title_entry.get()
        description = self.description_text.get('1.0', END).strip()
        
        if not title:
            messagebox.showerror("Ошибка", "Укажите название опроса")
            return
        
        if not self.questions:
            messagebox.showerror("Ошибка", "Добавьте хотя бы один вопрос")
            return
        
        # Создаем или обновляем опрос
        if self.survey_id:
            # Здесь должен быть код для обновления существующего опроса
            # (для простоты в данном примере не реализован)
            messagebox.showinfo("Информация", "Обновление существующих опросов в этой версии не поддерживается")
            return
        else:
            survey_id = self.db.create_survey(title, description, self.username)
            if not survey_id:
                messagebox.showerror("Ошибка", "Не удалось создать опрос")
                return
        
        # Сохраняем вопросы
        for position, question_frame in enumerate(self.questions, 1):
            question_text = question_frame.question_text_entry.get()
            required = question_frame.required_var.get()
            question_type = question_frame.question_type
            
            # Получаем варианты ответов, если есть
            options = None
            if question_type in ["radio", "checkbox"] and question_frame.options_list:
                options = [entry.get() for entry in question_frame.options_list if entry.get()]
            
            # Если редактирование и у вопроса есть ID, обновляем его
            # (не реализовано в этом примере)
            
            # Добавляем новый вопрос
            self.db.add_question(
                survey_id,
                question_text,
                question_type,
                required,
                options,
                position
            )
        
        messagebox.showinfo("Успех", "Опрос успешно создан")
        self.master.destroy()
    
    def load_survey_data(self):
        """Загружает данные опроса для редактирования"""
        survey = self.db.get_survey(self.survey_id)
        if not survey:
            messagebox.showerror("Ошибка", f"Опрос с ID {self.survey_id} не найден")
            self.master.destroy()
            return
        
        # Заполняем основную информацию
        self.title_entry.insert(0, survey['title'])
        self.description_text.insert('1.0', survey['description'])
        
        # Загружаем вопросы
        questions = self.db.get_questions(self.survey_id)
        for i, question in enumerate(questions, 1):
            question_frame = self.create_question_frame(i, question['question_type'], question)
            question_frame.pack(fill=X, pady=10)
            self.questions.append(question_frame)
