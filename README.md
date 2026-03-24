# teessyt

## Corp Mail Enterprise (учебный стенд)

Расширенное пилотное веб-приложение, моделирующее внутренний корпоративный почтовый веб-сервис в «компании»: 
- аутентификация сотрудников;
- папка входящих и просмотр писем;
- отправка писем;
- поиск по почте;
- центр загрузки вложений;
- админ-раздел (пользователи + SQL-консоль);
- API-эндпоинты интеграции.

## Архитектура
- `app.py` — точка входа;
- `webmail/__init__.py` — фабрика приложения и конфигурация;
- `webmail/db.py` — инициализация/сидирование БД и raw SQL helper;
- `webmail/services/mail_service.py` — сервисный слой бизнес-логики почты;
- `webmail/routes/*.py` — маршруты по доменам (`auth`, `mailbox`, `admin`, `api`);
- `templates/` — шаблоны UI, приближенные к «корпоративной» веб-почте.

## Преднамеренно добавленные уязвимости (для практики)
1. **Отсутствие фильтрации пользовательского ввода**
   - `|safe` в нескольких шаблонах (`dashboard`, `mail_detail`, `search_results`, `attachments_center`).
2. **Небезопасная обработка данных**
   - SQL Injection во многих запросах (`auth`, `mail_service`, `mailbox`, `api`);
   - выполнение произвольного SQL в `/admin/sql`;
   - небезопасная десериализация `pickle.load` при загрузке `.pkl`;
   - Directory Traversal в `/download`.
3. **Уязвимые/устаревшие зависимости**
   - зафиксированы старые версии библиотек в `requirements.txt`.
4. **Чувствительные данные в коде**
   - `SECRET_KEY`, SMTP/JWT ключи, API key в сидируемых данных.
5. **Небезопасный API-дизайн**
   - `/api/v1/config` возвращает конфиденциальные параметры;
   - `/api/v1/token` создаёт токен без криптографической подписи.

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

> Важно: это **специально уязвимый** учебный стенд для лабораторных работ по AppSec/SAST/DAST.

## Ошибка `cannot import name 'soft_unicode' from markupsafe`
Если при запуске возникает ошибка вида:
`ImportError: cannot import name 'soft_unicode' from 'markupsafe'`,
значит установилась несовместимая версия `MarkupSafe` для старой ветки `Jinja2`.

Исправление:
```bash
pip install -r requirements.txt --upgrade --force-reinstall
```

В этом репозитории `MarkupSafe` уже зафиксирован как `1.1.1`, что совместимо с `Jinja2==2.11.3`.
