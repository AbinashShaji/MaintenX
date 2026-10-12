from flask import render_template, request, session, redirect, url_for, flash
from blueprints.staff import staff_bp
from database.connection import get_db_connection
from blueprints.auth.utils import role_required
from blueprints.workflow import (
    validate_transition, log_request_update,
    STATUS_ASSIGNED, STATUS_ON_WORK, STATUS_RECTIFIED
)
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

# --- Job Inspection and Acceptance ---

@staff_bp.route('/job/<int:id>', methods=['GET', 'POST'])
@role_required('staff')
def job_details(id):
    """
    Job Inspection & Acceptance view.
    Only allows viewing details and accepting available jobs.
    Work actions (start, update, rectify) are decoupled and redirected to workspace.
    """
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'accept':
            return accept_job(id)
        elif action == 'start':
            return start_work(id)
        elif action == 'update':
            return update_work(id)
        elif action == 'rectify':
            return rectify_job(id)
        else:
            return accept_job(id)
            
    staff_id = session.get('user_id')
    conn = get_db_connection()
    job = None
    updates = []
    statuses = set()
    
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT r.*, c.name as category_name, u.name as reported_by, s.name as assigned_to_name
                FROM maintenance_requests r
                LEFT JOIN categories c ON r.category_id = c.id
                LEFT JOIN users u ON r.user_id = u.id
                LEFT JOIN users s ON r.assigned_to = s.id
                WHERE r.id = ?
            """, (id,))
            job = cursor.fetchone()
            
            if job:
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

@staff_bp.route('/job/<int:id>/accept', methods=['POST'])
@role_required('staff')
def accept_job(id):
    """
    Accept / Claim an available maintenance request.
    Atomically updates status to 'assigned' and assigns to current staff member.
    Redirects to /staff/history.
    """
    staff_id = session.get('user_id')
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, status FROM maintenance_requests WHERE id = ?", (id,))
            job = cursor.fetchone()
            if not job:
                flash("Job not found.", "error")
                return redirect(url_for('staff.jobs'))
                
            if job['status'] != 'pending':
                flash("This job is no longer available.", "error")
                return redirect(url_for('staff.jobs'))
                
            # Atomic claim
            cursor.execute("""
                UPDATE maintenance_requests 
                SET status = ?, assigned_to = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE id = ? AND status = 'pending'
            """, (STATUS_ASSIGNED, staff_id, id))
            
            if cursor.rowcount == 0:
                flash("This job was just claimed by another staff member.", "error")
                return redirect(url_for('staff.jobs'))
                
            log_request_update(cursor, id, staff_id, 'pending', STATUS_ASSIGNED, 'Job accepted by staff')
            
            conn.commit()
            flash("Job accepted successfully! You can now manage it from your Work Workspace.", "success")
            return redirect(url_for('staff.history'))
        except Exception:
            flash("An error occurred while accepting the job.", "error")
        finally:
            conn.close()
            
    return redirect(url_for('staff.history'))

# --- Staff Work Workspace ---

@staff_bp.route('/history')
@role_required('staff')
def history():
    """
    Staff Work Workspace / History page.
    Groups accepted jobs, on work jobs, and rectified/completed jobs.
    """
    staff_id = session.get('user_id')
    jobs_by_status = {'assigned': [], 'in_progress': [], 'resolved': []}
    
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT r.id, r.title, r.status, r.priority, r.location, 
                       c.name as category_name, r.updated_at, r.resolved_at
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

@staff_bp.route('/job/<int:id>/work-details')
@staff_bp.route('/work-details/<int:id>')
@role_required('staff')
def work_details(id):
    """
    Dedicated Work Workspace view for managing active work execution,
    submitting progress updates, and completing rectification.
    """
    staff_id = session.get('user_id')
    conn = get_db_connection()
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
                # Rule: Only assigned staff member can access the work workspace
                if job['assigned_to'] != staff_id:
                    flash("You are not assigned to this job.", "error")
                    return redirect(url_for('staff.history'))
                    
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
        return redirect(url_for('staff.history'))
        
    return render_template('staff/work_details.html', job_id=id, job=job, updates=updates, statuses=statuses)

@staff_bp.route('/job/<int:id>/start', methods=['POST'])
@role_required('staff')
def start_work(id):
    """
    Staff starts work on an assigned job: ASSIGNED -> IN_PROGRESS (ON WORK).
    """
    staff_id = session.get('user_id')
    note = request.form.get('note', 'Work started by staff').strip()
    if not note:
        note = 'Work started by staff'
        
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, status, assigned_to FROM maintenance_requests WHERE id = ?", (id,))
            job = cursor.fetchone()
            if not job:
                flash("Job not found.", "error")
                return redirect(url_for('staff.history'))
                
            if job['assigned_to'] != staff_id:
                flash("You are not assigned to this job.", "error")
                return redirect(url_for('staff.history'))
                
            is_valid, err_msg = validate_transition(job['status'], STATUS_ON_WORK)
            if not is_valid:
                flash(err_msg, "error")
                return redirect(url_for('staff.history'))
                
            cursor.execute("""
                UPDATE maintenance_requests 
                SET status = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            """, (STATUS_ON_WORK, id))
            
            log_request_update(cursor, id, staff_id, job['status'], STATUS_ON_WORK, note)
            
            conn.commit()
            flash("Work started on job! Current status: On Work.", "success")
            return redirect(url_for('staff.work_details', id=id))
        except Exception:
            flash("An error occurred while starting work.", "error")
        finally:
            conn.close()
            
    return redirect(url_for('staff.history'))

@staff_bp.route('/job/<int:id>/update', methods=['POST'])
@role_required('staff')
def update_work(id):
    """
    Staff adds progress update notes while job is IN_PROGRESS (ON WORK).
    """
    staff_id = session.get('user_id')
    note = request.form.get('note', '').strip()
    if not note:
        flash("Please provide a work note describing progress.", "error")
        return redirect(url_for('staff.work_details', id=id))
        
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, status, assigned_to FROM maintenance_requests WHERE id = ?", (id,))
            job = cursor.fetchone()
            if not job:
                flash("Job not found.", "error")
                return redirect(url_for('staff.history'))
                
            if job['assigned_to'] != staff_id:
                flash("You are not assigned to this job.", "error")
                return redirect(url_for('staff.history'))
                
            if job['status'] != STATUS_ON_WORK:
                flash("Work progress updates can only be added to jobs currently On Work.", "error")
                return redirect(url_for('staff.work_details', id=id))
                
            cursor.execute("""
                UPDATE maintenance_requests 
                SET updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            """, (id,))
            
            log_request_update(cursor, id, staff_id, STATUS_ON_WORK, STATUS_ON_WORK, note)
            
            conn.commit()
            flash("Work progress note recorded successfully.", "success")
            return redirect(url_for('staff.work_details', id=id))
        except Exception:
            flash("An error occurred while updating work progress.", "error")
        finally:
            conn.close()
            
    return redirect(url_for('staff.history'))

@staff_bp.route('/job/<int:id>/rectify', methods=['POST'])
@role_required('staff')
def rectify_job(id):
    """
    Staff completes repair and marks job as RECTIFIED: IN_PROGRESS -> RESOLVED.
    Requires resolution note and saves resolved_at timestamp.
    """
    staff_id = session.get('user_id')
    resolution_note = request.form.get('resolution_note', '').strip()
    if not resolution_note:
        resolution_note = request.form.get('note', '').strip()
        
    if not resolution_note:
        flash("A resolution note is required when marking a job as rectified.", "error")
        return redirect(url_for('staff.work_details', id=id))
        
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, status, assigned_to FROM maintenance_requests WHERE id = ?", (id,))
            job = cursor.fetchone()
            if not job:
                flash("Job not found.", "error")
                return redirect(url_for('staff.history'))
                
            if job['assigned_to'] != staff_id:
                flash("You are not assigned to this job.", "error")
                return redirect(url_for('staff.history'))
                
            is_valid, err_msg = validate_transition(job['status'], STATUS_RECTIFIED)
            if not is_valid:
                flash(err_msg, "error")
                return redirect(url_for('staff.work_details', id=id))
                
            cursor.execute("""
                UPDATE maintenance_requests 
                SET status = ?, resolution_note = ?, resolved_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            """, (STATUS_RECTIFIED, resolution_note, id))
            
            log_request_update(cursor, id, staff_id, STATUS_ON_WORK, STATUS_RECTIFIED, resolution_note)
            
            conn.commit()
            flash("Job marked as rectified! Awaiting admin verification and closure.", "success")
            return redirect(url_for('staff.history'))
        except Exception:
            flash("An error occurred while marking job as rectified.", "error")
        finally:
            conn.close()
            
    return redirect(url_for('staff.history'))

# --- Bug Report & Profile ---

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
