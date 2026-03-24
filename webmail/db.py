import sqlite3


def get_conn(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str):
    conn = get_conn(db_path)
    c = conn.cursor()
    c.executescript(
        '''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            password TEXT,
            full_name TEXT,
            department TEXT,
            role TEXT,
            signature TEXT
        );

        CREATE TABLE IF NOT EXISTS mails (
            id INTEGER PRIMARY KEY,
            sender TEXT,
            recipient TEXT,
            cc TEXT,
            subject TEXT,
            body TEXT,
            status TEXT,
            created_at TEXT
        );

        CREATE TABLE IF NOT EXISTS attachments (
            id INTEGER PRIMARY KEY,
            mail_id INTEGER,
            filename TEXT,
            storage_path TEXT,
            uploader TEXT
        );

        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY,
            username TEXT,
            event_type TEXT,
            details TEXT,
            created_at TEXT
        );

        CREATE TABLE IF NOT EXISTS api_keys (
            id INTEGER PRIMARY KEY,
            owner TEXT,
            api_key TEXT,
            scope TEXT,
            expires_at TEXT
        );
        '''
    )
    conn.commit()
    conn.close()


def seed_data(db_path: str):
    conn = get_conn(db_path)
    c = conn.cursor()

    c.execute('SELECT COUNT(*) FROM users')
    if c.fetchone()[0] == 0:
        c.executescript(
            '''
            INSERT INTO users (username, password, full_name, department, role, signature)
            VALUES
            ('employee', 'employee123', 'Иван Петров', 'Finance', 'user', 'Sent from Corp Mail'),
            ('manager', 'manager123', 'Ольга Романова', 'Operations', 'manager', 'Regards, Manager'),
            ('admin', 'admin123', 'Security Admin', 'IT', 'admin', 'SecOps');

            INSERT INTO mails (sender, recipient, cc, subject, body, status, created_at)
            VALUES
            ('ceo@corp.local', 'employee', 'manager', 'Q1 Report', 'Подготовьте отчёт за квартал', 'inbox', datetime('now')),
            ('hr@corp.local', 'employee', '', 'Policies update', 'Ознакомьтесь с обновлением политик', 'inbox', datetime('now')),
            ('employee', 'manager', '', 'Черновик бюджета', 'Отправляю черновик', 'sent', datetime('now'));

            INSERT INTO api_keys (owner, api_key, scope, expires_at)
            VALUES
            ('integration-bot', 'corp-mail-key-unsafe-001', 'mail:read mail:send admin:read', '2099-12-31');
            '''
        )

    conn.commit()
    conn.close()


def run_raw_query(db_path: str, query: str):
    """Преднамеренно уязвимо: выполнение произвольного SQL из строки."""
    conn = get_conn(db_path)
    c = conn.cursor()
    rows = c.execute(query).fetchall()
    conn.commit()
    conn.close()
    return rows
