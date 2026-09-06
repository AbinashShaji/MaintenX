from flask import render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from blueprints.auth import auth_bp
from database.connection import get_db_connection

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT id, name, email, password_hash, role, is_active FROM users WHERE email = ?", (email,))
                user = cursor.fetchone()
                
                if user and check_password_hash(user['password_hash'], password):
                    if not user['is_active']:
                        flash("Your account has been deactivated.", "error")
                        return redirect(url_for('auth.login'))
                    
                    session.clear()
                    session['user_id'] = user['id']
                    session['name'] = user['name']
                    session['role'] = user['role']
                    
                    if user['role'] == 'admin':
                        return redirect(url_for('admin.dashboard'))
                    elif user['role'] == 'staff':
                        return redirect(url_for('staff.dashboard'))
                    else:
                        return redirect(url_for('user.dashboard'))
                else:
                    flash("Invalid email or password.", "error")
            except Exception as e:
                flash("An error occurred during login.", "error")
            finally:
                conn.close()
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone', '')
        department = request.form.get('department', '')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return redirect(url_for('auth.register'))
            
        password_hash = generate_password_hash(password)
        
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
                if cursor.fetchone():
                    flash("Email address already registered.", "error")
                    return redirect(url_for('auth.register'))
                
                cursor.execute("""
                    INSERT INTO users (name, email, phone, department, password_hash, role)
                    VALUES (?, ?, ?, ?, ?, 'user')
                """, (name, email, phone, department, password_hash))
                conn.commit()
                flash("Account created successfully. Please log in.", "success")
                return redirect(url_for('auth.login'))
            except Exception as e:
                flash("An error occurred during registration.", "error")
            finally:
                conn.close()
                
    return render_template('auth/signup.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))
