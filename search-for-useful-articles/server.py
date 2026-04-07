import os 
import sys
import subprocess
import webbrowser
import threading
import time
from Flask import Flask, render_template, request, jsonify
# пути к папкам
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')
#если нет папки - создание 
os.makedirs(TEMPLATE_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)

app = Flask(__name__, 
            template_folder=TEMPLATE_DIR,
            static_folder=STATIC_DIR)
#запрос к main.py
MAIN_SCRIPT = os.path.join(BASE_DIR, 'main.py')
#страницы
@app.route('/')
def index():
   #главная
    return render_template('index.html')
@app.route('/search')
def search_page():
    #поиска
    return render_template('search.html')
@app.route('/api/search', methods=['POST'])
def search():
        #обработка запроса
    data = request.get_json()
    query = data.get('query', '').strip()

    if not query:
        return jsonify({'error': 'Пустой запрос'}), 400

    #существует ли main.py
    if not os.path.exists(MAIN_SCRIPT):
        return jsonify({'error': 'Файл main.py не найден'}), 500

    try:
        #запуск main.py + запрос
        result = subprocess.run(
            [sys.executable, MAIN_SCRIPT, query],
            capture_output=True,
            text=True,
            timeout=60,  # таймаут 60 секунд
            encoding='utf-8'
        )

        output = result.stdout
        error = result.stderr

        if error:
            print(f"Ошибка main.py: {error}")
            return jsonify({'error': f'Ошибка выполнения: {error[:200]}'}), 500

        return jsonify({'output': output})

    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Превышено время ожидания (60 сек)'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def open_browser():
    #старт сервера + браузера
    time.sleep(1.5)
    webbrowser.open('http://127.0.0.1:5000')


if __name__ == '__main__':
    #другой поток
    threading.Thread(target=open_browser, daemon=True).start()

    #Старт сервера
    print("Запуск сервера...")
    print("Открыть в браузере: http://127.0.0.1:5000")
    app.run(debug=False, host='127.0.0.1', port=5000)