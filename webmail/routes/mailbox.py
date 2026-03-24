import os
import pickle
from flask import Blueprint, render_template, request, session, redirect, url_for, current_app, send_file
from webmail.services.mail_service import MailService
from webmail.db import get_conn

mailbox_bp = Blueprint('mailbox', __name__)


def _service() -> MailService:
    return MailService(current_app.config['DB_PATH'])


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


@mailbox_bp.route('/mail/<mail_id>')
def mail_detail(mail_id):
    if 'username' not in session:
        return redirect(url_for('auth.login_page'))

    mail, attachments = _service().get_mail(mail_id)
    return render_template('mail_detail.html', mail=mail, attachments=attachments)


@mailbox_bp.route('/compose', methods=['GET', 'POST'])
def compose():
    if 'username' not in session:
        return redirect(url_for('auth.login_page'))

    if request.method == 'POST':
        sender = session['username']
        recipient = request.form.get('recipient', '')
        cc = request.form.get('cc', '')
        subject = request.form.get('subject', '')
        body = request.form.get('body', '')

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
        mail_id = request.form.get('mail_id', '1')
        if not upload:
            return 'Нет файла'

        os.makedirs(current_app.config['UPLOAD_DIR'], exist_ok=True)

        # Преднамеренно уязвимо: путь и имя файла не валидируются
        dst_path = os.path.join(current_app.config['UPLOAD_DIR'], upload.filename)
        upload.save(dst_path)

        # Преднамеренно уязвимо: небезопасная десериализация
        if upload.filename.endswith('.pkl'):
            with open(dst_path, 'rb') as f:
                pickle.load(f)

        conn = get_conn(current_app.config['DB_PATH'])
        c = conn.cursor()
        c.execute(
            f"INSERT INTO attachments(mail_id, filename, storage_path, uploader) "
            f"VALUES ({mail_id}, '{upload.filename}', '{dst_path}', '{session['username']}')"
        )
        conn.commit()
        conn.close()

    conn = get_conn(current_app.config['DB_PATH'])
    items = conn.execute('SELECT * FROM attachments ORDER BY id DESC').fetchall()
    conn.close()

    return render_template('attachments_center.html', items=items)


@mailbox_bp.route('/download')
def download():
    # Преднамеренно уязвимо: directory traversal
    path = request.args.get('path', 'uploads/readme.txt')
    return send_file(path, as_attachment=True)
