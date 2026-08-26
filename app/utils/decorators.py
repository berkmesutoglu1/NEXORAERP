from functools import wraps
from flask import flash, redirect, url_for, abort
from flask_login import current_user

def role_required(*roles):
    """
    Decorator to enforce backend Role authorization on Flask routes.
    Example: @role_required('Admin', 'Yönetici', 'Satış Personeli')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Bu sayfaya erişmek için önce giriş yapmalısınız.', 'warning')
                return redirect(url_for('auth.login'))
            
            if current_user.role.name not in roles and current_user.role.name != 'Admin':
                flash('Bu işlem veya sayfaya erişim yetkiniz bulunmamaktadır.', 'danger')
                return abort(403)
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def permission_required(permission_code):
    """
    Decorator to enforce specific Permission code check.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Bu sayfaya erişmek için giriş yapmalısınız.', 'warning')
                return redirect(url_for('auth.login'))
                
            if not current_user.has_permission(permission_code):
                flash('Bu işlem için yetkiniz yetersizdir.', 'danger')
                return abort(403)
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator
