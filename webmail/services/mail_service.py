from datetime import datetime
from webmail.db import get_conn


class MailService:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def list_mailbox(self, username: str, folder: str = 'inbox'):
        conn = get_conn(self.db_path)
        c = conn.cursor()
        rows = c.execute(
            'SELECT id, sender, recipient, subject, status, created_at FROM mails WHERE recipient = ? AND status = ? ORDER BY created_at DESC',
            (username, folder),
        ).fetchall()
        conn.close()
        return rows

    def search(self, username: str, q: str):
        conn = get_conn(self.db_path)
        c = conn.cursor()
        pattern = f'%{q}%'
        rows = c.execute(
            'SELECT id, sender, subject, body, created_at FROM mails WHERE recipient = ? AND (subject LIKE ? OR body LIKE ?)',
            (username, pattern, pattern),
        ).fetchall()
        conn.close()
        return rows

    def get_mail(self, mail_id: int):
        conn = get_conn(self.db_path)
        c = conn.cursor()
        row = c.execute('SELECT * FROM mails WHERE id = ?', (mail_id,)).fetchone()
        attachments = c.execute('SELECT * FROM attachments WHERE mail_id = ?', (mail_id,)).fetchall()
        conn.close()
        return row, attachments

    def compose(self, sender: str, recipient: str, cc: str, subject: str, body: str):
        conn = get_conn(self.db_path)
        c = conn.cursor()
        c.execute(
            'INSERT INTO mails(sender, recipient, cc, subject, body, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (sender, recipient, cc, subject, body, 'inbox', datetime.utcnow().isoformat()),
        )
        conn.commit()
        conn.close()

    def save_audit(self, username: str, event_type: str, details: str):
        conn = get_conn(self.db_path)
        c = conn.cursor()
        c.execute(
            'INSERT INTO audit_logs(username, event_type, details, created_at) VALUES (?, ?, ?, ?)',
            (username, event_type, details, datetime.utcnow().isoformat()),
        )
        conn.commit()
        conn.close()
