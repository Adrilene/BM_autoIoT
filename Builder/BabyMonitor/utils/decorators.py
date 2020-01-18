from functools import wraps
from flask import abort
from flask_login import current_user
from models.User import Permission


# Check if a user has permission to access a page
# Pag 115 and 116 from the Flask Web Development Book
def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Check if the user has admin rights and can access the page
def admin_required(f):
    return permission_required(Permission.ADMINISTER)(f)
