from flask import render_template, request, session, redirect, url_for, flash
from blueprints.user import user_bp
from database.connection import get_db_connection
from blueprints.auth.utils import role_required
from werkzeug.security import check_password_hash, generate_password_hash

@user_bp.route('/dashboard')
@role_required('user')
def dashboard():
    user_id = session.get('user_id')
    stats = {'total': 0, 'requested': 0, 'approved': 0, 'rectified': 0}
    recent_requests = []
    
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            
            # Get stats
            cursor.execute("""
                SELECT status, COUNT(*) as count 
                FROM maintenance_requests 
                WHERE user_id = ?
                GROUP BY status
            """, (user_id,))
            results = cursor.fetchall()
            
            for row in results:
                status = row['status']
                count = row['count']
                stats['total'] += count
                if status == 'pending':
                    stats['requested'] += count
                elif status in ('assigned', 'in_progress'):
                    stats['approved'] += count
                elif status == 'resolved':
                    stats['rectified'] += count
            
            # Get recent requests
            cursor.execute("""
                SELECT r.id, r.title, r.status, c.name as category_name
                FROM maintenance_requests r
                LEFT JOIN categories c ON r.category_id = c.id
                WHERE r.user_id = ?
                ORDER BY r.created_at DESC LIMIT 5
            """, (user_id,))
            recent_requests = cursor.fetchall()
        except Exception as e:
            flash("Error loading dashboard data.", "error")
        finally:
            conn.close()
            
    return render_template('user/dashboard.html', stats=stats, recent_requests=recent_requests)

@user_bp.route('/my-requests')
@role_required('user')
def my_requests():
    user_id = session.get('user_id')
    requests = []
    
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT r.id, r.title, r.status, r.priority, c.name as category_name, r.created_at
                FROM maintenance_requests r
                LEFT JOIN categories c ON r.category_id = c.id
                WHERE r.user_id = ?
                ORDER BY r.created_at DESC
            """, (user_id,))
            requests = cursor.fetchall()
        except Exception:
            pass
        finally:
            conn.close()
            
    return render_template('user/my_requests.html', requests=requests)

@user_bp.route('/requests')
@role_required('user')
def requests_list():
    requests = []
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT r.id, r.title, r.status, r.priority, c.name as category_name, r.created_at, u.name as user_name
                FROM maintenance_requests r
                LEFT JOIN categories c ON r.category_id = c.id
                LEFT JOIN users u ON r.user_id = u.id
                ORDER BY r.created_at DESC
            """)
            requests = cursor.fetchall()
        except Exception:
            pass
        finally:
            conn.close()
            
    return render_template('user/requests.html', requests=requests)

@user_bp.route('/request/new', methods=['GET', 'POST'])
@role_required('user')
def create_request():
    user_id = session.get('user_id')
    
    if request.method == 'POST':
        title = request.form.get('title')
        category_id = request.form.get('category_id')
        priority = request.form.get('priority')
        location = request.form.get('location')
        description = request.form.get('description')
        
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO maintenance_requests 
                    (user_id, category_id, title, description, location, priority, status)
                    VALUES (?, ?, ?, ?, ?, ?, 'pending')
                """, (user_id, category_id, title, description, location, priority))
                
                request_id = cursor.lastrowid
                
                cursor.execute("""
                    INSERT INTO request_updates 
                    (request_id, user_id, new_status, note)
                    VALUES (?, ?, 'pending', 'Request created')
                """, (request_id, user_id))
                
                conn.commit()
                flash("Maintenance request submitted successfully.", "success")
                return redirect(url_for('user.request_details', id=request_id))
            except Exception as e:
                flash("An error occurred while submitting the request.", "error")
            finally:
                conn.close()

    categories = []
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM categories WHERE is_active = 1 ORDER BY name")
            categories = cursor.fetchall()
        except Exception:
            pass
        finally:
            conn.close()
            
    return render_template('user/create_request.html', categories=categories)

@user_bp.route('/request/<int:id>')
@role_required('user')
def request_details(id):
    req = None
    updates = []
    statuses = set()
    
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # Fetch request
            cursor.execute("""
                SELECT r.*, c.name as category_name, u.name as user_name, s.name as assigned_to_name
                FROM maintenance_requests r
                LEFT JOIN categories c ON r.category_id = c.id
                LEFT JOIN users u ON r.user_id = u.id
                LEFT JOIN users s ON r.assigned_to = s.id
                WHERE r.id = ?
            """, (id,))
            req = cursor.fetchone()
            
            if req:
                # Calculate statuses for timeline
                s = req['status']
                if s == 'pending':
                    statuses.add('pending')
                elif s == 'assigned':
                    statuses.update(['pending', 'assigned'])
                elif s == 'in_progress':
                    statuses.update(['pending', 'assigned', 'in_progress'])
                elif s == 'resolved':
                    statuses.update(['pending', 'assigned', 'in_progress', 'resolved'])
                elif s == 'closed':
                    statuses.update(['pending', 'assigned', 'in_progress', 'resolved', 'closed'])
                
                # Fetch updates
                cursor.execute("""
                    SELECT u.*, user.name as user_name, user.role as user_role
                    FROM request_updates u
                    LEFT JOIN users user ON u.user_id = user.id
                    WHERE u.request_id = ?
                    ORDER BY u.created_at ASC
                """, (id,))
                updates = cursor.fetchall()
        except Exception:
            pass
        finally:
            conn.close()
            
    if not req:
        flash("Request not found.", "error")
        return redirect(url_for('user.my_requests'))
        
    return render_template('user/request_details.html', request_id=id, req=req, updates=updates, statuses=statuses)

@user_bp.route('/feedback', methods=['GET', 'POST'])
@role_required('user')
def feedback():
    if request.method == 'POST':
        flash("Feedback submitted successfully. Thank you!", "success")
        return redirect(url_for('user.dashboard'))
    return render_template('user/feedback.html')

@user_bp.route('/profile', methods=['GET', 'POST'])
@role_required('user')
def profile():
    user_id = session.get('user_id')
    conn = get_db_connection()
    
    if request.method == 'POST':
        # Check if updating profile or changing password
        if 'current_password' in request.form:
            # Change Password
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_new_password = request.form.get('confirm_new_password')
            
            if new_password != confirm_new_password:
                flash("New passwords do not match.", "error")
            else:
                if conn:
                    try:
                        cursor = conn.cursor()
                        cursor.execute("SELECT password_hash FROM users WHERE id = ?", (user_id,))
                        user = cursor.fetchone()
                        if user and check_password_hash(user['password_hash'], current_password):
                            new_hash = generate_password_hash(new_password)
                            cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_hash, user_id))
                            conn.commit()
                            flash("Password changed successfully.", "success")
                        else:
                            flash("Incorrect current password.", "error")
                    except Exception:
                        flash("An error occurred.", "error")
        else:
            # Update Profile
            name = request.form.get('name')
            phone = request.form.get('phone')
            department = request.form.get('department')
            
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE users SET name = ?, phone = ?, department = ? WHERE id = ?", 
                                   (name, phone, department, user_id))
                    conn.commit()
                    session['name'] = name
                    flash("Profile updated successfully.", "success")
                except Exception:
                    flash("An error occurred.", "error")
                    
        return redirect(url_for('user.profile'))
    
    # GET request - fetch user data
    user_data = {}
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT name, email, phone, department FROM users WHERE id = ?", (user_id,))
            user_data = cursor.fetchone()
        except Exception:
            pass
        finally:
            conn.close()
            
    return render_template('user/profile.html', user=user_data)
