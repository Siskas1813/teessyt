import os
from uuid import uuid4
from flask import Blueprint, render_template, request, session, redirect, url_for, current_app, send_from_directory, abort
from werkzeug.utils import secure_filename
from webmail.services.mail_service import MailService
from webmail.db import get_conn

mailbox_bp = Blueprint('mailbox', __name__)
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'docx'}


def _service() -> MailService:
    return MailService(current_app.config['DB_PATH'])


def _require_login():
    if 'username' not in session:
        return redirect(url_for('auth.login_page'))
    return None


@mailbox_bp.route('/dashboard')
def dashboard():
    redirect_response = _require_login()
    if redirect_response:
        return redirect_response

    folder = request.args.get('folder', 'inbox')
    if folder not in {'inbox', 'sent'}:
        folder = 'inbox'
    mails = _service().list_mailbox(session['username'], folder)
    return render_template('dashboard.html', mails=mails, folder=folder, user=session)


@mailbox_bp.route('/search')
def search():
    redirect_response = _require_login()
    if redirect_response:
        return redirect_response

    query = request.args.get('q', '').strip()
    results = _service().search(session['username'], query)
    return render_template('search_results.html', results=results, query=query)


@mailbox_bp.route('/mail/<int:mail_id>')
def mail_detail(mail_id):
    redirect_response = _require_login()
    if redirect_response:
        return redirect_response

    mail, attachments = _service().get_mail(mail_id)
    if not mail:
        return 'Письмо не найдено', 404
    if session['username'] not in {mail['recipient'], mail['sender']} and session.get('role') != 'admin':
        return 'Forbidden', 403
    return render_template('mail_detail.html', mail=mail, attachments=attachments)


@mailbox_bp.route('/compose', methods=['GET', 'POST'])
def compose():
    redirect_response = _require_login()
    if redirect_response:
        return redirect_response

    if request.method == 'POST':
        sender = session['username']
        recipient = request.form.get('recipient', '').strip()
        cc = request.form.get('cc', '').strip()
        subject = request.form.get('subject', '').strip()[:200]
        body = request.form.get('body', '').strip()
        if not recipient or not subject:
            return 'Заполните обязательные поля', 400

        _service().compose(sender, recipient, cc, subject, body)
        _service().save_audit(sender, 'compose', f'Compose to={recipient}, subject={subject}')

        return redirect(url_for('mailbox.dashboard'))

    return render_template('compose.html')


@mailbox_bp.route('/attachments', methods=['GET', 'POST'])
def attachments_center():
    redirect_response = _require_login()
    if redirect_response:
        return redirect_response

    if request.method == 'POST':
        upload = request.files.get('attachment')
        mail_id = request.form.get('mail_id', '1')
        if not upload or not upload.filename:
            return 'Нет файла', 400

        try:
            mail_id_int = int(mail_id)
        except ValueError:
            return 'Некорректный mail_id', 400

        ext = upload.filename.rsplit('.', 1)[-1].lower() if '.' in upload.filename else ''
        if ext not in ALLOWED_EXTENSIONS:
            return 'Недопустимый тип файла', 400

        os.makedirs(current_app.config['UPLOAD_DIR'], exist_ok=True)
        safe_name = secure_filename(upload.filename)
        stored_name = f'{uuid4().hex}_{safe_name}'
        dst_path = os.path.join(current_app.config['UPLOAD_DIR'], stored_name)
        upload.save(dst_path)

        conn = get_conn(current_app.config['DB_PATH'])
        c = conn.cursor()
        c.execute(
            'INSERT INTO attachments(mail_id, filename, storage_path, uploader) VALUES (?, ?, ?, ?)',
            (mail_id_int, safe_name, stored_name, session['username']),
        )
        conn.commit()
        conn.close()

    conn = get_conn(current_app.config['DB_PATH'])
    items = conn.execute('SELECT * FROM attachments ORDER BY id DESC').fetchall()
    conn.close()

    return render_template('attachments_center.html', items=items)


@mailbox_bp.route('/download/<path:stored_name>')
def download(stored_name):
    redirect_response = _require_login()
    if redirect_response:
        return redirect_response

    base_dir = current_app.config['UPLOAD_DIR']
    normalized = os.path.normpath(stored_name)
    if normalized.startswith('..') or os.path.isabs(normalized):
        abort(400)
    return send_from_directory(base_dir, normalized, as_attachment=True)
