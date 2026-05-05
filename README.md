# teessyt

## Corp Mail Enterprise (исправленная версия)

Это безопасная версия учебного почтового веб-приложения.

### Что исправлено
- SQL-запросы переведены на параметризованные выражения.
- Удалено выполнение произвольного SQL и отключена SQL-консоль администратора.
- Убраны опасные `|safe` в шаблонах.
- Убрана небезопасная десериализация `pickle.load`.
- Добавлена проверка расширений и безопасные имена файлов для загрузок.
- Устранён directory traversal в загрузке/скачивании вложений.
- API защищён ключом `X-API-Key`, удалены небезопасные endpoint-ы токенов/конфига.

## Запуск
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

После старта: `http://127.0.0.1:5000`

Демо-аккаунты:
- `employee / employee123`
- `manager / manager123`
- `admin / admin123`

Демо API key для `/api/v1/mail/search`:
- `X-API-Key: corp-mail-demo-key-001`
