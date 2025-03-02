import sqlite3
import os
import datetime
import json

class Database:
    def __init__(self, db_name="app_database.db"):
        # Определяем путь к директории приложения
        app_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(app_dir, "data")
        
        # Создаем директорию для данных, если она не существует
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        
        # Путь к БД
        self.db_path = os.path.join(data_dir, db_name)
        
        # Создаем БД и таблицы, если они не существуют
        self.initialize_db()
    
    def initialize_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Таблица пользователей
        c.execute('''CREATE TABLE IF NOT EXISTS users 
                     (id INTEGER PRIMARY KEY, username TEXT UNIQUE, 
                      password TEXT, is_admin INTEGER, created_at TEXT)''')
        
        # Таблица опросов
        c.execute('''CREATE TABLE IF NOT EXISTS surveys
                     (id INTEGER PRIMARY KEY, title TEXT, description TEXT,
                      creator_id INTEGER, created_at TEXT, 
                      is_active INTEGER DEFAULT 1,
                      FOREIGN KEY (creator_id) REFERENCES users (id))''')
        
        # Таблица вопросов
        c.execute('''CREATE TABLE IF NOT EXISTS questions
                     (id INTEGER PRIMARY KEY, survey_id INTEGER,
                      question_text TEXT, question_type TEXT,
                      required INTEGER DEFAULT 1, options TEXT,
                      position INTEGER,
                      FOREIGN KEY (survey_id) REFERENCES surveys (id))''')
        
        # Таблица ответов
        c.execute('''CREATE TABLE IF NOT EXISTS responses
                     (id INTEGER PRIMARY KEY, survey_id INTEGER,
                      respondent_id INTEGER, started_at TEXT,
                      completed_at TEXT,
                      FOREIGN KEY (survey_id) REFERENCES surveys (id),
                      FOREIGN KEY (respondent_id) REFERENCES users (id))''')
        
        # Таблица ответов на вопросы
        c.execute('''CREATE TABLE IF NOT EXISTS answers
                     (id INTEGER PRIMARY KEY, response_id INTEGER,
                      question_id INTEGER, answer_text TEXT,
                      FOREIGN KEY (response_id) REFERENCES responses (id),
                      FOREIGN KEY (question_id) REFERENCES questions (id))''')
        
        conn.commit()
        conn.close()
        
        # Добавляем администратора, если он еще не существует
        if not self.get_user_by_name("admin"):
            self.register_user("admin", "admin", is_admin=1)
    
    # Методы для работы с пользователями
    def register_user(self, username, password, is_admin=0):
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute("INSERT INTO users (username, password, is_admin, created_at) VALUES (?, ?, ?, ?)",
                     (username, password, is_admin, now))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            conn.close()
            return False
    
    def validate_login(self, username, password):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = c.fetchone()
        conn.close()
        return user is not None
    
    def is_admin(self, username):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT is_admin FROM users WHERE username = ?", (username,))
        result = c.fetchone()
        conn.close()
        return result and result[0] == 1
    
    def get_user_by_name(self, username):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        conn.close()
        return user
    
    def get_user_id(self, username):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT id FROM users WHERE username = ?", (username,))
        user_id = c.fetchone()
        conn.close()
        return user_id[0] if user_id else None
    
    def get_all_users(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT id, username, is_admin, created_at FROM users")
        users = c.fetchall()
        conn.close()
        return users
    
    def delete_user(self, user_id):
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
            conn.close()
            return True
        except:
            conn.close()
            return False
    
    # Методы для работы с опросами
    def create_survey(self, title, description, creator_username):
        try:
            creator_id = self.get_user_id(creator_username)
            if not creator_id:
                return False
            
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute("""INSERT INTO surveys (title, description, creator_id, created_at, is_active) 
                       VALUES (?, ?, ?, ?, 1)""", (title, description, creator_id, now))
            survey_id = c.lastrowid
            conn.commit()
            conn.close()
            return survey_id
        except Exception as e:
            print(f"Ошибка создания опроса: {e}")
            return False
    
    def get_survey(self, survey_id):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM surveys WHERE id = ?", (survey_id,))
        survey = dict(c.fetchone()) if c.fetchone() else None
        conn.close()
        return survey
    
    def get_all_surveys(self, active_only=False):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        query = "SELECT * FROM surveys"
        if active_only:
            query += " WHERE is_active = 1"
        c.execute(query)
        surveys = c.fetchall()
        conn.close()
        return surveys
    
    def get_user_surveys(self, username):
        user_id = self.get_user_id(username)
        if not user_id:
            return []
            
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT * FROM surveys WHERE creator_id = ?", (user_id,))
        surveys = c.fetchall()
        conn.close()
        return surveys
    
    def add_question(self, survey_id, question_text, question_type, required=1, options=None, position=None):
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            # Определяем позицию для нового вопроса, если не указана
            if position is None:
                c.execute("SELECT MAX(position) FROM questions WHERE survey_id = ?", (survey_id,))
                max_pos = c.fetchone()[0]
                position = 1 if max_pos is None else max_pos + 1
            
            # Конвертируем список опций в JSON, если они есть
            options_json = json.dumps(options) if options else None
            
            c.execute("""INSERT INTO questions (survey_id, question_text, question_type, required, options, position) 
                       VALUES (?, ?, ?, ?, ?, ?)""", 
                     (survey_id, question_text, question_type, required, options_json, position))
            
            question_id = c.lastrowid
            conn.commit()
            conn.close()
            return question_id
        except Exception as e:
            print(f"Ошибка добавления вопроса: {e}")
            return False
    
    def get_questions(self, survey_id):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM questions WHERE survey_id = ? ORDER BY position", (survey_id,))
        
        questions = []
        for question in c.fetchall():
            q_dict = dict(question)
            # Распаковываем JSON с опциями, если они есть
            if q_dict['options']:
                q_dict['options'] = json.loads(q_dict['options'])
            questions.append(q_dict)
        
        conn.close()
        return questions
    
    def save_response(self, survey_id, respondent_username, answers):
        try:
            respondent_id = self.get_user_id(respondent_username)
            
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Создаем запись ответа на опрос
            c.execute("""INSERT INTO responses (survey_id, respondent_id, started_at, completed_at) 
                       VALUES (?, ?, ?, ?)""", (survey_id, respondent_id, now, now))
            response_id = c.lastrowid
            
            # Сохраняем ответы на вопросы
            for question_id, answer_text in answers.items():
                c.execute("""INSERT INTO answers (response_id, question_id, answer_text) 
                           VALUES (?, ?, ?)""", (response_id, question_id, answer_text))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Ошибка сохранения ответов: {e}")
            return False
    
    def get_survey_responses(self, survey_id):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        # Получаем все ответы на опрос
        c.execute("""
            SELECT r.id as response_id, r.completed_at, u.username, 
                   q.id as question_id, q.question_text, q.question_type, 
                   a.answer_text
            FROM responses r
            JOIN users u ON r.respondent_id = u.id
            JOIN answers a ON r.id = a.response_id
            JOIN questions q ON a.question_id = q.id
            WHERE r.survey_id = ?
            ORDER BY r.id, q.position
        """, (survey_id,))
        
        raw_data = c.fetchall()
        conn.close()
        
        # Структурируем данные по ответам
        responses = {}
        for row in raw_data:
            response_id = row['response_id']
            if response_id not in responses:
                responses[response_id] = {
                    'respondent': row['username'],
                    'completed_at': row['completed_at'],
                    'answers': {}
                }
            
            responses[response_id]['answers'][row['question_id']] = {
                'question_text': row['question_text'],
                'question_type': row['question_type'],
                'answer_text': row['answer_text']
            }
        
        return responses
    
    def toggle_survey_status(self, survey_id):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Получаем текущий статус опроса
        c.execute("SELECT is_active FROM surveys WHERE id = ?", (survey_id,))
        current_status = c.fetchone()[0]
        
        # Изменяем статус на противоположный
        new_status = 1 if current_status == 0 else 0
        c.execute("UPDATE surveys SET is_active = ? WHERE id = ?", (new_status, survey_id))
        
        conn.commit()
        conn.close()
        return new_status
