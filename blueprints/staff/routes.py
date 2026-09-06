from flask import render_template, request, session, redirect, url_for, flash
from blueprints.staff import staff_bp
from database.connection import get_db_connection
from blueprints.auth.utils import role_required
from werkzeug.security import check_password_hash, generate_password_hash

@staff_bp.route('/dashboard')
@role_required('staff')
def dashboard():
    staff_id = session.get('user_id')
    stats = {'available': 0, 'accepted': 0, 'on_work': 0, 'rectified': 0, 'high_priority': 0}
    available_jobs = []
    active_work = []
    
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            
            # Count Available jobs
            cursor.execute("SELECT COUNT(*) as count FROM maintenance_requests WHERE status = 'pending'")
            stats['available'] = cursor.fetchone()['count']
            
            # Count staff's jobs
            cursor.execute("SELECT status, COUNT(*) as count FROM maintenance_requests WHERE assigned_to = ? GROUP BY status", (staff_id,))
            for row in cursor.fetchall():
                if row['status'] == 'assigned':
                    stats['accepted'] += row['count']
                elif row['status'] == 'in_progress':
                    stats['on_work'] += row['count']
                elif row['status'] == 'resolved':
                    stats['rectified'] += row['count']
                    
            # Count staff's high priority jobs
            cursor.execute("SELECT COUNT(*) as count FROM maintenance_requests WHERE assigned_to = ? AND priority IN ('high', 'critical') AND status IN ('assigned', 'in_progress')", (staff_id,))
            stats['high_priority'] = cursor.fetchone()['count']
            
            # Get 5 available jobs
            cursor.execute("""
                SELECT r.id, r.title, r.priority, c.name as category_name
                FROM maintenance_requests r
                LEFT JOIN categories c ON r.category_id = c.id
                WHERE r.status = 'pending'
                ORDER BY r.created_at DESC LIMIT 5
            """)
            available_jobs = cursor.fetchall()
            
            # Get 5 active works
            cursor.execute("""
                SELECT r.id, r.title, r.status, r.priority, c.name as category_name
                FROM maintenance_requests r
                LEFT JOIN categories c ON r.category_id = c.id
                WHERE r.assigned_to = ? AND r.status IN ('assigned', 'in_progress')
                ORDER BY r.updated_at DESC LIMIT 5
            """, (staff_id,))
            active_work = cursor.fetchall()
            
        except Exception:
            flash("Error loading dashboard data.", "error")
        finally:
            conn.close()
            
    return render_template('staff/dashboard.html', stats=stats, available_jobs=available_jobs, active_work=active_work)

@staff_bp.route('/jobs')
@role_required('staff')
def jobs():
    available_jobs = []
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT r.id, r.title, r.priority, r.location, c.name as category_name, r.created_at
                FROM maintenance_requests r
                LEFT JOIN categories c ON r.category_id = c.id
                WHERE r.status = 'pending'
                ORDER BY r.created_at DESC
            """)
            available_jobs = cursor.fetchall()
        except Exception:
            pass
        finally:
            conn.close()
            
    return render_template('staff/jobs.html', available_jobs=available_jobs)

@staff_bp.route('/job/<int:id>', methods=['GET', 'POST'])
@role_required('staff')
def job_details(id):
    staff_id = session.get('user_id')
    conn = get_db_connection()
    
    if request.method == 'POST':
        action = request.form.get('action')
        note = request.form.get('note', '')
        
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT status FROM maintenance_requests WHERE id = ?", (id,))
                req = cursor.fetchone()
                
                if not req:
                    flash("Job not found.", "error")
                    return redirect(url_for('staff.jobs'))
                    
                current_status = req['status']
                
                if action == 'accept':
                    if current_status != 'pending':
                        flash("Job is no longer available.", "error")
                    else:
                        cursor.execute("UPDATE maintenance_requests SET status = 'assigned', assigned_to = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (staff_id, id))
                        cursor.execute("INSERT INTO request_updates (request_id, user_id, old_status, new_status, note) VALUES (?, ?, 'pending', 'assigned', 'Job accepted by staff')", (id, staff_id))
                        conn.commit()
                        flash("Job accepted successfully.", "success")
                        
                elif action in ['start', 'update', 'rectify']:
                    # Must be assigned to this staff member
                    cursor.execute("SELECT assigned_to FROM maintenance_requests WHERE id = ?", (id,))
                    assigned_req = cursor.fetchone()
                    if not assigned_req or assigned_req['assigned_to'] != staff_id:
                        flash("You are not assigned to this job.", "error")
                        return redirect(url_for('staff.job_details', id=id))
                        
                    new_status = current_status
                    if action == 'start':
                        new_status = 'in_progress'
                        if not note:
                            note = 'Work started'
                    elif action == 'rectify':
                        new_status = 'resolved'
                        if not note:
                            note = 'Job marked as rectified'
                            
                    cursor.execute("UPDATE maintenance_requests SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (new_status, id))
                    if action == 'rectify':
                        cursor.execute("UPDATE maintenance_requests SET resolved_at = CURRENT_TIMESTAMP WHERE id = ?", (id,))
                        
                    cursor.execute("INSERT INTO request_updates (request_id, user_id, old_status, new_status, note) VALUES (?, ?, ?, ?, ?)", (id, staff_id, current_status, new_status, note))
                    conn.commit()
                    flash("Job progress updated.", "success")
                    
            except Exception as e:
                flash("An error occurred.", "error")
                
        return redirect(url_for('staff.job_details', id=id))
    
    # GET method
    job = None
    updates = []
    statuses = set()
    
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT r.*, c.name as category_name, u.name as reported_by
                FROM maintenance_requests r
                LEFT JOIN categories c ON r.category_id = c.id
                LEFT JOIN users u ON r.user_id = u.id
                WHERE r.id = ?
            """, (id,))
            job = cursor.fetchone()
            
            if job:
                # Timeline calculation
                s = job['status']
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
            
    if not job:
        flash("Job not found.", "error")
        return redirect(url_for('staff.jobs'))
        
    return render_template('staff/job_details.html', job_id=id, job=job, updates=updates, statuses=statuses)

@staff_bp.route('/history')
@role_required('staff')
def history():
    staff_id = session.get('user_id')
    jobs_by_status = {'assigned': [], 'in_progress': [], 'resolved': []}
    
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT r.id, r.title, r.status, r.priority, c.name as category_name, r.updated_at
                FROM maintenance_requests r
                LEFT JOIN categories c ON r.category_id = c.id
                WHERE r.assigned_to = ? AND r.status IN ('assigned', 'in_progress', 'resolved', 'closed')
                ORDER BY r.updated_at DESC
            """, (staff_id,))
            
            for row in cursor.fetchall():
                if row['status'] == 'assigned':
                    jobs_by_status['assigned'].append(row)
                elif row['status'] == 'in_progress':
                    jobs_by_status['in_progress'].append(row)
                elif row['status'] in ('resolved', 'closed'):
                    jobs_by_status['resolved'].append(row)
                    
        except Exception:
            pass
        finally:
            conn.close()
            
    return render_template('staff/history.html', jobs=jobs_by_status)

@staff_bp.route('/bug-report', methods=['GET', 'POST'])
@role_required('staff')
def bug_report():
    if request.method == 'POST':
        flash("Bug report submitted to administration. Thank you.", "success")
        return redirect(url_for('staff.dashboard'))
    return render_template('staff/bug_report.html')

@staff_bp.route('/profile', methods=['GET', 'POST'])
@role_required('staff')
def profile():
    user_id = session.get('user_id')
    conn = get_db_connection()
    
    if request.method == 'POST':
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
                    
        return redirect(url_for('staff.profile'))
    
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
            
    return render_template('staff/profile.html', user=user_data)
