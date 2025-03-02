from tkinter import ttk, font
from tkinter import *
import os
from PIL import Image, ImageTk

class AppTheme:
    def __init__(self, root):
        self.root = root
        self.colors = {
            'primary': '#3498db',       # Синий
            'primary_dark': '#2980b9',  # Темный синий
            'accent': '#e74c3c',        # Красный
            'success': '#2ecc71',       # Зеленый
            'warning': '#f39c12',       # Оранжевый
            'text': '#2c3e50',          # Темно-синий
            'text_secondary': '#7f8c8d', # Серый
            'background': '#ecf0f1',    # Светло-серый
            'card': '#ffffff',          # Белый
            'border': '#bdc3c7',        # Светло-серый
        }
        
        self.font_family = "Helvetica"
        self.fonts = {
            'title': font.Font(family=self.font_family, size=24, weight="bold"),
            'subtitle': font.Font(family=self.font_family, size=18, weight="bold"),
            'heading': font.Font(family=self.font_family, size=16, weight="bold"),
            'normal': font.Font(family=self.font_family, size=12),
            'normal_bold': font.Font(family=self.font_family, size=12, weight="bold"),
            'small': font.Font(family=self.font_family, size=10),
        }
        
        # Инициализируем стили
        self.initialize_styles()
        
    def initialize_styles(self):
        # Настройка общего стиля приложения
        self.root.configure(bg=self.colors['background'])
        
        # Настраиваем стиль для ttk
        style = ttk.Style()
        
        # Общий стиль
        style.configure(".", 
                      font=self.fonts['normal'],
                      background=self.colors['background'],
                      foreground=self.colors['text'])
        
        # Стиль для кнопок
        style.configure("TButton", 
                      padding=(10, 5),
                      background=self.colors['primary'],
                      foreground="white")
        
        style.map("TButton",
                background=[('active', self.colors['primary_dark'])],
                foreground=[('active', 'white')])
        
        # Стиль для заголовков в Treeview
        style.configure("Treeview.Heading", 
                      font=self.fonts['normal_bold'],
                      background=self.colors['primary'],
                      foreground="white")
        
        # Стиль для элементов в Treeview
        style.configure("Treeview", 
                      background=self.colors['card'],
                      foreground=self.colors['text'],
                      rowheight=25,
                      fieldbackground=self.colors['card'])
        
        style.map("Treeview",
                background=[('selected', self.colors['primary'])],
                foreground=[('selected', 'white')])
        
        # Стиль для разных типов кнопок
        self._create_custom_button_style(style, "Success.TButton", 
                                      self.colors['success'], "#27ae60")
        self._create_custom_button_style(style, "Danger.TButton", 
                                      self.colors['accent'], "#c0392b")
        self._create_custom_button_style(style, "Warning.TButton", 
                                      self.colors['warning'], "#d35400")
        
        # Стиль для меток
        style.configure("Title.TLabel", 
                      font=self.fonts['title'],
                      background=self.colors['background'],
                      foreground=self.colors['primary'])
        
        style.configure("Subtitle.TLabel", 
                      font=self.fonts['subtitle'],
                      background=self.colors['background'],
                      foreground=self.colors['text'])
        
        style.configure("Heading.TLabel", 
                      font=self.fonts['heading'],
                      background=self.colors['background'],
                      foreground=self.colors['text'])
        
        # Стиль для рамок
        style.configure("Card.TFrame", 
                      background=self.colors['card'],
                      relief="raised",
                      borderwidth=1)
        
        # Стиль для Notebook (вкладок)
        style.configure("TNotebook", 
                      background=self.colors['background'],
                      tabmargins=[2, 5, 2, 0])
        
        style.configure("TNotebook.Tab", 
                      background=self.colors['background'],
                      foreground=self.colors['text'],
                      padding=[10, 5],
                      font=self.fonts['normal'])
        
        style.map("TNotebook.Tab",
                background=[('selected', self.colors['primary'])],
                foreground=[('selected', 'white')],
                expand=[('selected', [1, 1, 1, 0])])
    
    def _create_custom_button_style(self, style, name, bg_color, active_bg_color):
        """Создает пользовательский стиль кнопки"""
        style.configure(name, 
                      background=bg_color,
                      foreground="white")
        
        style.map(name,
                background=[('active', active_bg_color)],
                foreground=[('active', 'white')])
    
    def create_rounded_button(self, parent, text, command=None, background=None, foreground="white", width=None, height=None):
        """Создает кнопку с округленными краями (использует Canvas)"""
        if background is None:
            background = self.colors['primary']
            
        btn_frame = Frame(parent, bg=self.colors['background'])
        
        canvas = Canvas(btn_frame, bg=self.colors['background'], 
                     highlightthickness=0, width=width, height=height)
        canvas.pack()
        
        if width and height:
            x0, y0, x1, y1 = 0, 0, width, height
        else:
            text_width = self.fonts['normal'].measure(text) + 20
            text_height = self.fonts['normal'].metrics("linespace") + 10
            width = width or text_width
            height = height or text_height
            x0, y0, x1, y1 = 0, 0, width, height
        
        # Радиус скругления
        radius = 10
        
        # Создаем скругленный прямоугольник
        canvas.create_oval(x0, y0, x0 + 2*radius, y0 + 2*radius, fill=background, outline="")
        canvas.create_oval(x1 - 2*radius, y0, x1, y0 + 2*radius, fill=background, outline="")
        canvas.create_oval(x0, y1 - 2*radius, x0 + 2*radius, y1, fill=background, outline="")
        canvas.create_oval(x1 - 2*radius, y1 - 2*radius, x1, y1, fill=background, outline="")
        
        canvas.create_rectangle(x0 + radius, y0, x1 - radius, y0 + radius, fill=background, outline="")
        canvas.create_rectangle(x0, y0 + radius, x1, y1 - radius, fill=background, outline="")
        canvas.create_rectangle(x0 + radius, y1 - radius, x1 - radius, y1, fill=background, outline="")
        
        # Добавляем текст
        canvas.create_text(width/2, height/2, text=text, fill=foreground, font=self.fonts['normal'])
        
        if command:
            canvas.bind("<Button-1>", lambda event: command())
            
        return btn_frame
    
    def load_and_resize_image(self, path, width, height):
        """Загружает и изменяет размер изображения"""
        try:
            # Проверяем существует ли файл
            if not os.path.exists(path):
                return None
                
            img = Image.open(path)
            img = img.resize((width, height), Image.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Ошибка загрузки изображения: {e}")
            return None

    def create_card_frame(self, parent, padding=10):
        """Создает рамку-карточку с тенью"""
        card = ttk.Frame(parent, style="Card.TFrame", padding=padding)
        return card
        
    def apply_hover_style(self, widget, enter_color, leave_color):
        """Применяет стиль наведения для виджетов"""
        if hasattr(widget, 'configure'):  # Проверяем, что виджет поддерживает configure
            orig_bg = widget.cget('background') if 'background' in widget.keys() else leave_color
            
            def on_enter(e):
                widget.configure(background=enter_color)
                
            def on_leave(e):
                widget.configure(background=orig_bg)
                
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
