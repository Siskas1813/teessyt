import os

from flask import (
    Blueprint,
    abort,
    current_app,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)
from werkzeug.utils import secure_filename

from webmail.db import get_conn
from webmail.services.mail_service import MailService

mailbox_bp = Blueprint('mailbox', __name__)

ALLOWED_ATTACHMENT_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx'}


def _service() -> MailService:
    return MailService(current_app.config['DB_PATH'])


def _is_allowed_attachment(filename: str) -> bool:
    if not filename or '.' not in filename:
        return False

    extension = filename.rsplit('.', 1)[1].lower()
    return extension in ALLOWED_ATTACHMENT_EXTENSIONS


@mailbox_bp.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('auth.login_page'))

    folder = request.args.get('folder', 'inbox')
    mails = _service().list_mailbox(session['username'], folder)
    return render_template('dashboard.html', mails=mails, folder=folder, user=session)


@mailbox_bp.route('/search')
def search():
    if 'username' not in session:
        return redirect(url_for('auth.login_page'))

    query = request.args.get('q', '')
    results = _service().search(session['username'], query)
    return render_template('search_results.html', results=results, query=query)


@mailbox_bp.route('/mail/<int:mail_id>')
def mail_detail(mail_id: int):
    if 'username' not in session:
        return redirect(url_for('auth.login_page'))

    mail, attachments = _service().get_mail(mail_id)
    if mail is None:
        abort(404)

    return render_template('mail_detail.html', mail=mail, attachments=attachments)


@mailbox_bp.route('/compose', methods=['GET', 'POST'])
def compose():
    if 'username' not in session:
        return redirect(url_for('auth.login_page'))

    if request.method == 'POST':
        sender = session['username']
        recipient = request.form.get('recipient', '').strip()
        cc = request.form.get('cc', '').strip()
        subject = request.form.get('subject', '').strip()
        body = request.form.get('body', '').strip()

        if not recipient or not subject:
            return 'Получатель и тема письма обязательны', 400

        _service().compose(sender, recipient, cc, subject, body)
        _service().save_audit(sender, 'compose', f'Compose to={recipient}, subject={subject}')

        return redirect(url_for('mailbox.dashboard'))

    return render_template('compose.html')


@mailbox_bp.route('/attachments', methods=['GET', 'POST'])
def attachments_center():
    if 'username' not in session:
        return redirect(url_for('auth.login_page'))

    if request.method == 'POST':
        upload = request.files.get('attachment')
        mail_id_raw = request.form.get('mail_id', '1')

        if not upload or not upload.filename:
            return 'Файл не выбран', 400

        try:
            mail_id = int(mail_id_raw)
        except ValueError:
            return 'Некорректный идентификатор письма', 400

        original_filename = upload.filename
        safe_filename = secure_filename(original_filename)

        if not safe_filename or not _is_allowed_attachment(safe_filename):
            return 'Недопустимый тип файла', 400

        upload_dir = current_app.config['UPLOAD_DIR']
        os.makedirs(upload_dir, exist_ok=True)

        dst_path = os.path.join(upload_dir, safe_filename)
        upload.save(dst_path)

        conn = get_conn(current_app.config['DB_PATH'])
        c = conn.cursor()
        c.execute(
            """
            INSERT INTO attachments(mail_id, filename, storage_path, uploader)
            VALUES (?, ?, ?, ?)
            """,
            (mail_id, safe_filename, dst_path, session['username'])
        )
        conn.commit()
        conn.close()

    conn = get_conn(current_app.config['DB_PATH'])
    items = conn.execute('SELECT * FROM attachments ORDER BY id DESC').fetchall()
    conn.close()

    return render_template('attachments_center.html', items=items)


@mailbox_bp.route('/download')
def download():
    if 'username' not in session:
        return redirect(url_for('auth.login_page'))

    requested_path = request.args.get('path', '')
    filename = secure_filename(os.path.basename(requested_path))

    if not filename:
        abort(400)

    upload_dir = current_app.config['UPLOAD_DIR']
    file_path = os.path.join(upload_dir, filename)

    if not os.path.isfile(file_path):
        abort(404)

    return send_from_directory(upload_dir, filename, as_attachment=True)