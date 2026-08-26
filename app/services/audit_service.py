from flask import request
from flask_login import current_user
from app import db
from app.models.user import AuditLog

def log_action(action, module, description="", user=None):
    """
    Log user actions across all ERP modules.
    """
    try:
        current_u = user or (current_user if current_user and current_user.is_authenticated else None)
        user_id = current_u.id if current_u else None
        user_name = current_u.full_name if current_u else "System"
        
        ip_addr = None
        if request:
            ip_addr = request.headers.get('X-Forwarded-For', request.remote_addr)
            
        log = AuditLog(
            user_id=user_id,
            user_name=user_name,
            action=action,
            module=module,
            description=description,
            ip_address=ip_addr
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error logging action: {e}")
