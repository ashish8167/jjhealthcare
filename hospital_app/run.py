import os
import webbrowser
import threading

def open_browser():
    webbrowser.open("http://127.0.0.1:8000")

if __name__ == "__main__":
    threading.Timer(2, open_browser).start()
    os.system("python3 manage.py runserver 127.0.0.1:8000")