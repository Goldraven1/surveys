from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from database import Database
from styles import AppTheme
import json

class SurveyViewer:
    def __init__(self, master=None, db=None, survey_id=None, username=None):
        self.master = master if master else Toplevel()
        self.db = db if db else Database()
        self.survey_id = survey_id
        self.username = username
        
        # Данные опроса
        self.survey = None
        self.questions = []
        self.answers = {}  # Словарь для хранения ответов пользователя
        
        # Виджеты для ответов
        self.answer_widgets = {}
        
        # Применяем темы и стили
        self.theme = AppTheme(self.master)
        
        # Загружаем данные опроса
        self.load_survey_data()
        
        # Создаем интерфейс
        self.create_widgets()
    
    def load_survey_data(self):
        """Загружает данные опроса из базы данных"""
        try:
            # Получаем информацию об опросе
            import sqlite3
            conn = sqlite3.connect(self.db.db_path)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            
            c.execute("SELECT * FROM surveys WHERE id = ?", (self.survey_id,))
            survey = c.fetchone()
            
            if not survey:
                messagebox.showerror("Ошибка", f"Опрос с ID {self.survey_id} не найден")
                self.master.destroy()
                return
            
            self.survey = dict(survey)
            self.master.title(f"Опрос: {self.survey['title']}")
            
            # Получаем вопросы опроса
            self.questions = self.db.get_questions(self.survey_id)
            
            conn.close()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные опроса: {str(e)}")
            self.master.destroy()
    
    def create_widgets(self):
        """Создает интерфейс для прохождения опроса"""
        if not self.survey:
            return
        
        # Основной контейнер с паддингами
        main_frame = Frame(self.master, bg=self.theme.colors['background'], padx=20, pady=20)
        main_frame.pack(fill=BOTH, expand=True)
        
        # Заголовок опроса
        title_label = Label(main_frame, text=self.survey['title'], 
                           font=self.theme.fonts['title'],
                           bg=self.theme.colors['background'],
                           fg=self.theme.colors['primary'])
        title_label.pack(pady=(0, 10))
        
        # Описание опроса
        if self.survey['description']:
            description_frame = self.theme.create_card_frame(main_frame)
            description_frame.pack(fill=X, pady=10)
            
            description_label = Label(description_frame, text=self.survey['description'], 
                                    wraplength=600, justify=LEFT,
                                    padding=10)
            description_label.pack(padx=10, pady=10, anchor=W)
        
        # Создаем прокручиваемую область для вопросов
        canvas = Canvas(main_frame, bg=self.theme.colors['background'])
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        
        questions_frame = Frame(canvas, bg=self.theme.colors['background'])
        questions_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=questions_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Создаем интерфейс для каждого вопроса
        for i, question in enumerate(self.questions, start=1):
            self.create_question_ui(questions_frame, question, i)
        
        # Кнопки внизу
        button_frame = Frame(main_frame, bg=self.theme.colors['background'], pady=20)
        button_frame.pack(fill=X)
        
        ttk.Button(button_frame, text="Отправить ответы", style="Success.TButton",
                  command=self.submit_survey).pack(side=RIGHT, padx=5)
        ttk.Button(button_frame, text="Отмена", 
                  command=self.master.destroy).pack(side=RIGHT, padx=5)
    
    def create_question_ui(self, parent, question, question_num):
        """Создает интерфейс для одного вопроса"""
        # Карточка вопроса
        question_frame = self.theme.create_card_frame(parent)
        question_frame.pack(fill=X, pady=10)
        
        # Номер и текст вопроса
        q_header = Frame(question_frame, bg=self.theme.colors['card'])
        q_header.pack(fill=X, padx=10, pady=10)
        
        # Индикатор обязательности
        required_text = "*" if question['required'] == 1 else ""
        Label(q_header, text=f"{question_num}. {question['question_text']} {required_text}", 
             font=self.theme.fonts['normal_bold'],
             bg=self.theme.colors['card']).pack(anchor=W)
        
        if question['required'] == 1:
            Label(q_header, text="(обязательный вопрос)", 
                 font=self.theme.fonts['small'],
                 fg=self.theme.colors['accent'],
                 bg=self.theme.colors['card']).pack(anchor=W)
        
        # Создаем виджеты для ответа в зависимости от типа вопроса
        answer_frame = Frame(question_frame, bg=self.theme.colors['card'], padx=10, pady=10)
        answer_frame.pack(fill=X)
        
        q_id = question['id']
        q_type = question['question_type']
        
        if q_type == 'text':
            # Текстовое поле для ответа
            answer_widget = Text(answer_frame, height=4, width=50, font=self.theme.fonts['normal'])
            answer_widget.pack(fill=X, pady=5)
            self.answer_widgets[q_id] = answer_widget
            
        elif q_type == 'radio':
            # Переменная для хранения выбранного значения
            var = StringVar()
            self.answer_widgets[q_id] = var
            
            # Создаем радиокнопки для каждого варианта
            options = question['options'] if question['options'] else []
            for i, option in enumerate(options):
                rb = Radiobutton(answer_frame, text=option, variable=var, value=option, 
                               bg=self.theme.colors['card'])
                rb.pack(anchor=W, pady=2)
                
        elif q_type == 'checkbox':
            # Создаем чекбоксы для множественного выбора
            options = question['options'] if question['options'] else []
            checkboxes = []
            
            for option in options:
                var = IntVar()
                cb = Checkbutton(answer_frame, text=option, variable=var, 
                               bg=self.theme.colors['card'])
                cb.pack(anchor=W, pady=2)
                checkboxes.append((option, var))
            
            self.answer_widgets[q_id] = checkboxes
    
    def get_answer_value(self, question_id, question_type):
        """Извлекает значение ответа из виджета"""
        widget = self.answer_widgets.get(question_id)
        
        if not widget:
            return ""
        
        if question_type == 'text':
            return widget.get('1.0', END).strip()
            
        elif question_type == 'radio':
            return widget.get()
            
        elif question_type == 'checkbox':
            selected = []
            for option, var in widget:
                if var.get() == 1:
                    selected.append(option)
            return ', '.join(selected) if selected else ""
    
    def validate_answers(self):
        """Проверяет, что на все обязательные вопросы даны ответы"""
        for question in self.questions:
            q_id = question['id']
            required = question['required'] == 1
            
            if required:
                answer = self.get_answer_value(q_id, question['question_type'])
                if not answer:
                    return False, question['question_text']
        
        return True, None
    
    def submit_survey(self):
        """Отправляет ответы на опрос"""
        # Проверяем, что все обязательные поля заполнены
        valid, question_text = self.validate_answers()
        if not valid:
            messagebox.showerror("Ошибка", f"Вы не ответили на обязательный вопрос:\n{question_text}")
            return
        
        # Собираем ответы
        answers = {}
        for question in self.questions:
            q_id = question['id']
            answer = self.get_answer_value(q_id, question['question_type'])
            answers[q_id] = answer
        
        # Сохраняем ответы в базе
        if self.db.save_response(self.survey_id, self.username, answers):
            messagebox.showinfo("Успех", "Ваши ответы успешно отправлены!")
            self.master.destroy()
        else:
            messagebox.showerror("Ошибка", "Не удалось сохранить ваши ответы. Пожалуйста, попробуйте еще раз.")

if __name__ == "__main__":
    # Пример использования
    app = SurveyViewer(survey_id=1, username="test_user")
    app.master.mainloop()
