from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User
from app.services.audit_service import log_action

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username_or_email = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        remember = True if request.form.get('remember') else False

        user = User.query.filter((User.username == username_or_email) | (User.email == username_or_email)).first()

        if not user or not user.check_password(password):
            flash('Geçersiz kullanıcı adı/e-posta veya şifre.', 'danger')
            return render_template('auth/login.html')

        if not user.is_active:
            flash('Hesabınız pasif durumdadır. Sistem yöneticisi ile iletişime geçin.', 'warning')
            return render_template('auth/login.html')

        login_user(user, remember=remember)
        user.last_login = datetime.utcnow()
        db.session.commit()

        log_action("Kullanıcı Girişi", "Güvenlik", f"{user.full_name} sisteme başarılı giriş yaptı.", user=user)
        flash(f'Hoş geldiniz, {user.full_name}!', 'success')

        next_page = request.args.get('next')
        return redirect(next_page or url_for('dashboard.index'))

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    log_action("Kullanıcı Çıkışı", "Güvenlik", f"{current_user.full_name} sistemden çıkış yaptı.")
    logout_user()
    flash('Başarıyla çıkış yaptınız.', 'info')
    return redirect(url_for('auth.login'))
