from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app import db
from app.models.user import User, Role, AuditLog
from app.services.audit_service import log_action
from app.utils.decorators import role_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/users')
@login_required
@role_required('Admin')
def users():
    users_list = User.query.all()
    roles_list = Role.query.all()
    return render_template('admin/users.html', users=users_list, roles=roles_list)


@admin_bp.route('/users/create', methods=['POST'])
@login_required
@role_required('Admin')
def create_user():
    username = request.form.get('username', '').strip()
    email = request.form.get('email', '').strip()
    fname = request.form.get('first_name', '').strip()
    lname = request.form.get('last_name', '').strip()
    role_id = int(request.form.get('role_id'))
    password = request.form.get('password', '').strip()

    if User.query.filter((User.username == username) | (User.email == email)).first():
        flash('Bu kullanıcı adı veya e-posta adresi kullanımda.', 'danger')
        return redirect(url_for('admin.users'))

    user = User(
        username=username,
        email=email,
        first_name=fname,
        last_name=lname,
        title=request.form.get('title', '').strip(),
        phone=request.form.get('phone', '').strip(),
        role_id=role_id,
        is_active=True
    )
    user.set_password(password or 'Nexora123!')
    db.session.add(user)
    db.session.commit()

    log_action("Yeni Kullanıcı Eklendi", "Sistem Yönetimi", f"{user.username} ({user.full_name})")
    flash('Kullanıcı oluşturuldu.', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/roles')
@login_required
@role_required('Admin')
def roles():
    roles_list = Role.query.all()
    return render_template('admin/roles.html', roles=roles_list)


@admin_bp.route('/audit-logs')
@login_required
@role_required('Admin', 'Yönetici')
def audit_logs():
    search = request.args.get('search', '').strip()
    module = request.args.get('module', '').strip()

    query = AuditLog.query

    if search:
        query = query.filter(
            (AuditLog.action.ilike(f'%{search}%')) |
            (AuditLog.user_name.ilike(f'%{search}%')) |
            (AuditLog.description.ilike(f'%{search}%'))
        )
    if module:
        query = query.filter(AuditLog.module == module)

    logs = query.order_by(AuditLog.timestamp.desc()).all()
    modules = db.session.query(AuditLog.module).distinct().all()
    modules = [m[0] for m in modules if m[0]]

    return render_template('admin/audit_logs.html', logs=logs, search=search, selected_module=module, modules=modules)


@admin_bp.route('/settings')
@login_required
@role_required('Admin')
def settings():
    return render_template('admin/settings.html')
