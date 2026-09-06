from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in to access this page.", "error")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash("Please log in to access this page.", "error")
                return redirect(url_for('auth.login'))
            if session.get('role') != role:
                flash("You do not have permission to access this page.", "error")
                # Redirect to appropriate dashboard based on their actual role
                actual_role = session.get('role')
                if actual_role == 'admin':
                    return redirect(url_for('admin.dashboard'))
                elif actual_role == 'staff':
                    return redirect(url_for('staff.dashboard'))
                else:
                    return redirect(url_for('user.dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator
