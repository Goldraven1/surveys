from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from database import Database
from styles import AppTheme
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from collections import Counter
import datetime

class SurveyAnalytics:
    def __init__(self, master=None, db=None, survey_id=None):
        self.master = master if master else Toplevel()
        self.master.title("Анализ результатов опроса")
        self.master.geometry("1000x800")
        self.db = db if db else Database()
        self.survey_id = survey_id
        
        # Данные
        self.survey = None
        self.questions = []
        self.responses = {}
        
        # Применяем темы и стили
        self.theme = AppTheme(self.master)
        
        # Загружаем данные
        self.load_data()
        
        # Создаем интерфейс
        self.create_widgets()
    
    def load_data(self):
        """Загружает данные опроса и ответы"""
        # Получаем информацию об опросе
        conn = self.db.db_path
        import sqlite3
        conn = sqlite3.connect(conn)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        c.execute("SELECT * FROM surveys WHERE id = ?", (self.survey_id,))
        survey_data = c.fetchone()
        conn.close()
        
        if not survey_data:
            messagebox.showerror("Ошибка", f"Опрос с ID {self.survey_id} не найден")
            self.master.destroy()
            return
            
        self.survey = dict(survey_data)
        
        # Получаем вопросы опроса
        self.questions = self.db.get_questions(self.survey_id)
        
        # Получаем ответы на опрос
        self.responses = self.db.get_survey_responses(self.survey_id)
    
    def create_widgets(self):
        """Создает интерфейс аналитики"""
        if not self.survey:
            return
        
        # Основной контейнер
        main_frame = Frame(self.master, bg=self.theme.colors['background'])
        main_frame.pack(fill=BOTH, expand=True)
        
        # Верхний информационный блок
        info_frame = Frame(main_frame, bg=self.theme.colors['background'], padx=20, pady=20)
        info_frame.pack(fill=X)
        
        Label(info_frame, text=f"Аналитика опроса: {self.survey['title']}", 
             font=self.theme.fonts['title'],
             bg=self.theme.colors['background'],
             fg=self.theme.colors['primary']).pack(anchor=W)
        
        # Информация о количестве ответов
        response_count = len(self.responses)
        response_info = f"Всего ответов: {response_count}"
        
        if response_count > 0:
            # Определяем первый и последний ответ
            dates = [r['completed_at'] for r in self.responses.values()]
            dates.sort()
            first_date = dates[0] if dates else "н/д"
            last_date = dates[-1] if dates else "н/д"
            
            response_info += f" | Первый ответ: {first_date} | Последний ответ: {last_date}"
        
        Label(info_frame, text=response_info, 
             font=self.theme.fonts['normal'],
             bg=self.theme.colors['background'],
             fg=self.theme.colors['text_secondary']).pack(anchor=W, pady=(10, 0))
        
        # Если нет ответов, показываем сообщение
        if not self.responses:
            no_data_frame = Frame(main_frame, bg=self.theme.colors['background'], padx=20, pady=40)
            no_data_frame.pack(fill=BOTH, expand=True)
            
            Label(no_data_frame, text="На данный опрос еще нет ответов", 
                 font=self.theme.fonts['subtitle'],
                 bg=self.theme.colors['background'],
                 fg=self.theme.colors['text']).pack()
            
            return
        
        # Создаем вкладки для разных видов аналитики
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        # Вкладка с сырыми данными ответов
        raw_data_frame = Frame(notebook, bg=self.theme.colors['background'])
        notebook.add(raw_data_frame, text="Сырые данные")
        self.create_raw_data_tab(raw_data_frame)
        
        # Вкладка с графиками
        charts_frame = Frame(notebook, bg=self.theme.colors['background'])
        notebook.add(charts_frame, text="Графики")
        self.create_charts_tab(charts_frame)
        
        # Вкладка с сводными данными
        summary_frame = Frame(notebook, bg=self.theme.colors['background'])
        notebook.add(summary_frame, text="Сводка")
        self.create_summary_tab(summary_frame)
        
        # Кнопка для экспорта данных
        export_button = ttk.Button(main_frame, text="Экспорт данных", 
                                command=self.export_data, style="TButton")
        export_button.pack(pady=10)
        
        # Кнопка закрытия
        close_button = ttk.Button(main_frame, text="Закрыть", 
                               command=self.master.destroy, style="TButton")
        close_button.pack(pady=10)
    
    def create_raw_data_tab(self, parent):
        """Создает вкладку с сырыми данными ответов"""
        # Создаем фрейм с прокруткой
        main_frame = Frame(parent, bg=self.theme.colors['card'])
        main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Создаем холст с прокруткой
        canvas = Canvas(main_frame, bg=self.theme.colors['card'])
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = Frame(canvas, bg=self.theme.colors['card'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Заголовок
        Label(scrollable_frame, text="Ответы респондентов", 
             font=self.theme.fonts['subtitle'],
             bg=self.theme.colors['card'],
             fg=self.theme.colors['text']).pack(anchor=W, padx=20, pady=10)
        
        # Добавляем карточку для каждого ответа
        for response_id, response_data in self.responses.items():
            response_frame = self.theme.create_card_frame(scrollable_frame)
            response_frame.pack(fill=X, padx=20, pady=10)
            
            # Информация о респонденте
            Label(response_frame, text=f"Респондент: {response_data['respondent']}", 
                 font=self.theme.fonts['normal_bold']).pack(anchor=W, padx=10, pady=5)
            
            Label(response_frame, text=f"Дата: {response_data['completed_at']}", 
                 font=self.theme.fonts['small']).pack(anchor=W, padx=10)
            
            # Разделитель
            ttk.Separator(response_frame, orient=HORIZONTAL).pack(fill=X, padx=10, pady=10)
            
            # Ответы на вопросы
            for question in self.questions:
                q_id = question['id']
                if q_id in response_data['answers']:
                    answer = response_data['answers'][q_id]
                    
                    # Вопрос
                    Label(response_frame, text=question['question_text'], 
                         font=self.theme.fonts['normal'],
                         wraplength=700).pack(anchor=W, padx=10, pady=5)
                    
                    # Ответ
                    answer_text = answer['answer_text']
                    answer_frame = Frame(response_frame, bg=self.theme.colors['background'], padx=5, pady=5)
                    answer_frame.pack(fill=X, padx=20, pady=5)
                    
                    Label(answer_frame, text=f"Ответ: {answer_text}", 
                         font=self.theme.fonts['normal'],
                         bg=self.theme.colors['background'],
                         wraplength=650).pack(anchor=W, padx=5)
    
    def create_charts_tab(self, parent):
        """Создает вкладку с графиками"""
        # Проверяем наличие данных
        if not self.responses:
            Label(parent, text="Нет данных для отображения графиков", 
                 font=self.theme.fonts['subtitle']).pack(pady=50)
            return
        
        # Создаем фрейм с прокруткой
        main_frame = Frame(parent, bg=self.theme.colors['card'])
        main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Создаем холст с прокруткой
        canvas = Canvas(main_frame, bg=self.theme.colors['card'])
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = Frame(canvas, bg=self.theme.colors['card'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Генерируем графики для каждого вопроса, где это возможно
        for question in self.questions:
            q_id = question['id']
            q_type = question['question_type']
            
            # Собираем все ответы на этот вопрос
            answers = []
            for response in self.responses.values():
                if q_id in response['answers']:
                    answers.append(response['answers'][q_id]['answer_text'])
            
            if not answers:
                continue
            
            # Создаем фрейм для графика
            chart_frame = self.theme.create_card_frame(scrollable_frame)
            chart_frame.pack(fill=X, padx=20, pady=10)
            
            # Заголовок графика
            Label(chart_frame, text=question['question_text'], 
                 font=self.theme.fonts['normal_bold']).pack(anchor=W, padx=10, pady=5)
            
            # Генерируем график в зависимости от типа вопроса
            if q_type in ['radio', 'checkbox', 'select']:
                # Для вариантов ответов - столбчатая диаграмма
                if q_type == 'checkbox':
                    # Для чекбоксов разбиваем ответы по запятым
                    all_options = []
                    for answer in answers:
                        options = [o.strip() for o in answer.split(',')]
                        all_options.extend(options)
                    
                    counts = Counter(all_options)
                else:
                    counts = Counter(answers)
                
                # Создаем фигуру
                fig, ax = plt.subplots(figsize=(8, 4))
                
                # Данные для диаграммы
                labels = list(counts.keys())
                values = list(counts.values())
                
                # Ограничиваем количество отображаемых вариантов
                if len(labels) > 10:
                    # Сортируем по частоте и берем топ-10
                    sorted_items = sorted(counts.items(), key=lambda x: x[1], reverse=True)
                    labels = [item[0] for item in sorted_items[:10]]
                    values = [item[1] for item in sorted_items[:10]]
                
                # Горизонтальная столбчатая диаграмма для лучшей читаемости длинных меток
                y_pos = np.arange(len(labels))
                ax.barh(y_pos, values, align='center', color=self.theme.colors['primary'])
                ax.set_yticks(y_pos)
                ax.set_yticklabels(labels)
                ax.invert_yaxis()  # Метки сверху вниз
                ax.set_xlabel('Количество')
                ax.set_title('Распределение ответов')
                
                # Добавляем числовые значения на столбцы
                for i, v in enumerate(values):
                    ax.text(v + 0.1, i, str(v), color='black', va='center')
                
                plt.tight_layout()
                
                # Размещаем график в интерфейсе
                chart_canvas = FigureCanvasTkAgg(fig, master=chart_frame)
                chart_canvas.draw()
                chart_canvas.get_tk_widget().pack(fill=BOTH, padx=10, pady=10)
                
            elif q_type in ['text', 'textarea']:
                # Для текстовых ответов - показываем облако слов или статистику длины
                Label(chart_frame, text="Текстовые ответы - статистика", 
                     font=self.theme.fonts['small']).pack(pady=5)
                
                # Статистика по длине ответов
                lengths = [len(a) for a in answers]
                avg_len = sum(lengths) / len(lengths) if lengths else 0
                
                stats_text = f"Количество ответов: {len(answers)}\n"
                stats_text += f"Средняя длина ответа: {avg_len:.1f} символов\n"
                stats_text += f"Самый короткий ответ: {min(lengths)} символов\n"
                stats_text += f"Самый длинный ответ: {max(lengths)} символов"
                
                Label(chart_frame, text=stats_text).pack(pady=10)
                
                # Гистограмма длины ответов
                fig, ax = plt.subplots(figsize=(8, 3))
                ax.hist(lengths, bins=10, color=self.theme.colors['primary'])
                ax.set_xlabel('Длина ответа (символов)')
                ax.set_ylabel('Частота')
                ax.set_title('Распределение длин ответов')
                
                plt.tight_layout()
                
                # Размещаем график в интерфейсе
                chart_canvas = FigureCanvasTkAgg(fig, master=chart_frame)
                chart_canvas.draw()
                chart_canvas.get_tk_widget().pack(fill=BOTH, padx=10, pady=10)
                
            elif q_type == 'number':
                # Для числовых ответов - гистограмма
                try:
                    numeric_answers = [float(a) for a in answers]
                    
                    # Статистика
                    avg = sum(numeric_answers) / len(numeric_answers) if numeric_answers else 0
                    
                    stats_text = f"Количество ответов: {len(numeric_answers)}\n"
                    stats_text += f"Среднее значение: {avg:.2f}\n"
                    stats_text += f"Минимум: {min(numeric_answers)}\n"
                    stats_text += f"Максимум: {max(numeric_answers)}"
                    
                    Label(chart_frame, text=stats_text).pack(pady=10)
                    
                    # Гистограмма
                    fig, ax = plt.subplots(figsize=(8, 3))
                    ax.hist(numeric_answers, bins=10, color=self.theme.colors['primary'])
                    ax.set_xlabel('Значение')
                    ax.set_ylabel('Частота')
                    ax.set_title('Распределение числовых ответов')
                    
                    plt.tight_layout()
                    
                    # Размещаем график в интерфейсе
                    chart_canvas = FigureCanvasTkAgg(fig, master=chart_frame)
                    chart_canvas.draw()
                    chart_canvas.get_tk_widget().pack(fill=BOTH, padx=10, pady=10)
                    
                except ValueError:
                    # Если не удалось преобразовать в числа
                    Label(chart_frame, text="Невозможно создать график для этих данных").pack(pady=10)
    
    def create_summary_tab(self, parent):
        """Создает вкладку с сводными данными"""
        # Проверяем наличие данных
        if not self.responses:
            Label(parent, text="Нет данных для отображения сводки", 
                 font=self.theme.fonts['subtitle']).pack(pady=50)
            return
        
        # Фрейм для сводной информации
        summary_frame = Frame(parent, bg=self.theme.colors['card'], padx=20, pady=20)
        summary_frame.pack(fill=BOTH, expand=True)
        
        # Заголовок
        Label(summary_frame, text="Сводная информация", 
             font=self.theme.fonts['subtitle'],
             bg=self.theme.colors['card']).pack(anchor=W, pady=(0, 20))
        
        # Общая статистика
        stats_frame = self.theme.create_card_frame(summary_frame)
        stats_frame.pack(fill=X, pady=10)
        
        Label(stats_frame, text="Общая статистика", 
             font=self.theme.fonts['normal_bold']).pack(anchor=W, padx=10, pady=5)
        
        total_responses = len(self.responses)
        
        # Определяем даты ответов
        dates = {}
        for r in self.responses.values():
            date_str = r['completed_at'].split()[0]  # Берем только дату без времени
            if date_str in dates:
                dates[date_str] += 1
            else:
                dates[date_str] = 1
        
        stats_text = f"Всего ответов: {total_responses}\n"
        stats_text += f"Количество уникальных респондентов: {len(set(r['respondent'] for r in self.responses.values()))}\n"
        stats_text += f"Количество дней с ответами: {len(dates)}\n"
        
        if dates:
            max_date = max(dates.items(), key=lambda x: x[1])
            stats_text += f"Наиболее активный день: {max_date[0]} ({max_date[1]} ответов)"
        
        Label(stats_frame, text=stats_text, justify=LEFT).pack(anchor=W, padx=20, pady=10)
        
        # Динамика ответов по дням
        if len(dates) > 1:
            fig, ax = plt.subplots(figsize=(8, 4))
            
            sorted_dates = sorted(dates.items())
            x = [d[0] for d in sorted_dates]
            y = [d[1] for d in sorted_dates]
            
            ax.plot(x, y, marker='o', linestyle='-', color=self.theme.colors['primary'])
            ax.set_xlabel('Дата')
            ax.set_ylabel('Количество ответов')
            ax.set_title('Динамика ответов по дням')
            
            # Поворачиваем метки дат для лучшей читаемости
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            chart_frame = Frame(summary_frame, bg=self.theme.colors['card'])
            chart_frame.pack(fill=BOTH, pady=10)
            
            chart_canvas = FigureCanvasTkAgg(fig, master=chart_frame)
            chart_canvas.draw()
            chart_canvas.get_tk_widget().pack(fill=BOTH)
    
    def export_data(self):
        """Экспортирует данные опроса в CSV файл"""
        import csv
        from tkinter import filedialog
        import os
        
        if not self.responses:
            messagebox.showinfo("Информация", "Нет данных для экспорта")
            return
        
        # Диалог выбора файла
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV файлы", "*.csv"), ("Все файлы", "*.*")],
            title="Сохранить данные опроса"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                csvwriter = csv.writer(csvfile)
                
                # Собираем заголовки
                headers = ['ID ответа', 'Респондент', 'Дата завершения']
                question_map = {}
                
                for q in self.questions:
                    headers.append(q['question_text'])
                    question_map[q['id']] = len(headers) - 1
                
                csvwriter.writerow(headers)
                
                # Записываем данные
                for response_id, response_data in self.responses.items():
                    row = [response_id, response_data['respondent'], response_data['completed_at']]
                    
                    # Заполняем пустые значения для всех вопросов
                    row.extend([''] * len(self.questions))
                    
                    # Заполняем имеющиеся ответы
                    for q_id, answer in response_data['answers'].items():
                        if q_id in question_map:
                            col_index = question_map[q_id]
                            row[col_index] = answer['answer_text']
                    
                    csvwriter.writerow(row)
            
            messagebox.showinfo("Успех", f"Данные успешно экспортированы в\n{file_path}")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось экспортировать данные: {str(e)}")

if __name__ == "__main__":
    # Пример использования
    app = SurveyAnalytics(survey_id=1)
    app.master.mainloop()
