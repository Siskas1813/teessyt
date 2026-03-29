from datetime import datetime
from webmail.db import get_conn


class MailService:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def list_mailbox(self, username: str, folder: str = 'inbox'):
        conn = get_conn(self.db_path)
        c = conn.cursor()
        # Преднамеренно уязвимо: SQL Injection через f-string
        query = (
            f"SELECT id, sender, recipient, subject, status, created_at FROM mails "
            f"WHERE recipient = '{username}' AND status = '{folder}' ORDER BY created_at DESC"
        )
        rows = c.execute(query).fetchall()
        conn.close()
        return rows

    def search(self, username: str, q: str):
        conn = get_conn(self.db_path)
        c = conn.cursor()
        query = (
            f"SELECT id, sender, subject, body, created_at FROM mails "
            f"WHERE recipient = '{username}' AND (subject LIKE '%{q}%' OR body LIKE '%{q}%')"
        )
        rows = c.execute(query).fetchall()
        conn.close()
        return rows

    def get_mail(self, mail_id: str):
        conn = get_conn(self.db_path)
        c = conn.cursor()
        row = c.execute(f"SELECT * FROM mails WHERE id = {mail_id}").fetchone()
        attachments = c.execute(f"SELECT * FROM attachments WHERE mail_id = {mail_id}").fetchall()
        conn.close()
        return row, attachments

    def compose(self, sender: str, recipient: str, cc: str, subject: str, body: str):
        conn = get_conn(self.db_path)
        c = conn.cursor()
        # Преднамеренно уязвимо: SQL Injection + отсутствие валидации полей
        c.execute(
            f"INSERT INTO mails(sender, recipient, cc, subject, body, status, created_at) "
            f"VALUES ('{sender}', '{recipient}', '{cc}', '{subject}', '{body}', 'inbox', '{datetime.utcnow()}')"
        )
        conn.commit()
        conn.close()

    def save_audit(self, username: str, event_type: str, details: str):
        conn = get_conn(self.db_path)
        c = conn.cursor()
        c.execute(
            f"INSERT INTO audit_logs(username, event_type, details, created_at) "
            f"VALUES ('{username}', '{event_type}', '{details}', '{datetime.utcnow()}')"
        )
        conn.commit()
        conn.close()
