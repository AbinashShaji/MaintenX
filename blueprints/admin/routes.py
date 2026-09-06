from flask import render_template, request, session, redirect, url_for, flash
from blueprints.admin import admin_bp
from database.connection import get_db_connection
from blueprints.auth.utils import role_required

@admin_bp.route('/dashboard')
@role_required('admin')
def dashboard():
    stats = {'total': 0, 'pending': 0, 'active': 0, 'resolved_today': 0}
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM maintenance_requests")
            stats['total'] = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM maintenance_requests WHERE status = 'pending'")
            stats['pending'] = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM maintenance_requests WHERE status IN ('assigned', 'in_progress')")
            stats['active'] = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM maintenance_requests WHERE status = 'resolved' AND DATE(resolved_at) = DATE('now')")
            stats['resolved_today'] = cursor.fetchone()['count']
            
        except Exception:
            pass
        finally:
            conn.close()
    return render_template('admin/dashboard.html', stats=stats)

@admin_bp.route('/requests')
@role_required('admin')
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
    return render_template('admin/requests.html', requests=requests)

@admin_bp.route('/request/<int:id>', methods=['GET', 'POST'])
@role_required('admin')
def request_details(id):
    conn = get_db_connection()
    if request.method == 'POST':
        staff_id = request.form.get('staff_id')
        new_status = request.form.get('status')
        admin_id = session.get('user_id')
        
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT status FROM maintenance_requests WHERE id = ?", (id,))
                req = cursor.fetchone()
                if req:
                    current_status = req['status']
                    
                    if staff_id and current_status == 'pending':
                        new_status = 'assigned'
                        cursor.execute("UPDATE maintenance_requests SET status = ?, assigned_to = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (new_status, staff_id, id))
                        cursor.execute("INSERT INTO request_updates (request_id, user_id, old_status, new_status, note) VALUES (?, ?, ?, ?, ?)", (id, admin_id, current_status, new_status, 'Assigned to staff by Admin'))
                        conn.commit()
                        flash("Staff assigned successfully.", "success")
                        
                    elif new_status and new_status != current_status:
                        cursor.execute("UPDATE maintenance_requests SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (new_status, id))
                        if new_status == 'closed':
                            cursor.execute("UPDATE maintenance_requests SET closed_at = CURRENT_TIMESTAMP WHERE id = ?", (id,))
                        cursor.execute("INSERT INTO request_updates (request_id, user_id, old_status, new_status, note) VALUES (?, ?, ?, ?, ?)", (id, admin_id, current_status, new_status, 'Status updated by Admin'))
                        conn.commit()
                        flash("Status updated successfully.", "success")
            except Exception as e:
                flash("An error occurred.", "error")
        return redirect(url_for('admin.request_details', id=id))

    # GET request
    req = None
    updates = []
    staff_members = []
    statuses = set()
    
    if conn:
        try:
            cursor = conn.cursor()
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
                    
                cursor.execute("""
                    SELECT u.*, user.name as user_name, user.role as user_role
                    FROM request_updates u
                    LEFT JOIN users user ON u.user_id = user.id
                    WHERE u.request_id = ?
                    ORDER BY u.created_at ASC
                """, (id,))
                updates = cursor.fetchall()
                
                cursor.execute("SELECT id, name FROM users WHERE role = 'staff' AND is_active = 1")
                staff_members = cursor.fetchall()
        except Exception:
            pass
        finally:
            conn.close()
            
    if not req:
        flash("Request not found.", "error")
        return redirect(url_for('admin.requests_list'))
        
    return render_template('admin/request_details.html', request_id=id, req=req, updates=updates, statuses=statuses, staff_members=staff_members)

@admin_bp.route('/users')
@role_required('admin')
def users():
    users_list = []
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, email, department, phone, is_active FROM users WHERE role = 'user' ORDER BY name")
            users_list = cursor.fetchall()
        except Exception:
            pass
        finally:
            conn.close()
    return render_template('admin/users.html', users=users_list)

@admin_bp.route('/staff')
@role_required('admin')
def staff():
    staff_list = []
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, email, department, phone, is_active FROM users WHERE role = 'staff' ORDER BY name")
            staff_list = cursor.fetchall()
        except Exception:
            pass
        finally:
            conn.close()
    return render_template('admin/staff.html', staff=staff_list)

@admin_bp.route('/categories', methods=['GET', 'POST'])
@role_required('admin')
def categories():
    conn = get_db_connection()
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO categories (name, description) VALUES (?, ?)", (name, description))
                conn.commit()
                flash("Category added successfully.", "success")
            except Exception:
                flash("Error adding category.", "error")
        return redirect(url_for('admin.categories'))
        
    categories_list = []
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM categories ORDER BY name")
            categories_list = cursor.fetchall()
        except Exception:
            pass
        finally:
            conn.close()
    return render_template('admin/categories.html', categories=categories_list)

@admin_bp.route('/reports')
@role_required('admin')
def reports():
    return render_template('admin/reports.html')

@admin_bp.route('/feedback')
@role_required('admin')
def feedback():
    return render_template('admin/feedback.html')

@admin_bp.route('/bug-reports')
@role_required('admin')
def bug_reports():
    return render_template('admin/bug_reports.html')
