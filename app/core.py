import sys
import os

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from window_core import Application

if __name__ == "__main__":
    app = Application()
    app.create_window()
    app.start()