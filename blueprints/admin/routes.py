import csv
import io
from datetime import datetime
from flask import render_template, request, session, redirect, url_for, flash, Response
from werkzeug.security import generate_password_hash
from blueprints.admin import admin_bp
from database.connection import get_db_connection
from blueprints.auth.utils import role_required
from blueprints.workflow import validate_transition, log_request_update, STATUS_ASSIGNED, STATUS_CLOSED

@admin_bp.route('/dashboard')
@role_required('admin')
def dashboard():
    stats = {'total': 0, 'pending': 0, 'active': 0, 'resolved_today': 0}
    needs_assignment = []
    critical_requests = []
    
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
            
            # Fetch requests needing assignment (pending status)
            cursor.execute("""
                SELECT r.id, r.title, r.priority, r.location, r.created_at, 
                       c.name as category_name, u.name as user_name
                FROM maintenance_requests r
                LEFT JOIN categories c ON r.category_id = c.id
                LEFT JOIN users u ON r.user_id = u.id
                WHERE r.status = 'pending'
                ORDER BY r.created_at DESC
                LIMIT 5
            """)
            needs_assignment = cursor.fetchall()
            
            # Fetch active critical priority requests
            cursor.execute("""
                SELECT r.id, r.title, r.status, r.location, r.created_at, 
                       c.name as category_name, u.name as user_name
                FROM maintenance_requests r
                LEFT JOIN categories c ON r.category_id = c.id
                LEFT JOIN users u ON r.user_id = u.id
                WHERE r.priority = 'critical' AND r.status NOT IN ('closed', 'resolved')
                ORDER BY r.created_at DESC
                LIMIT 5
            """)
            critical_requests = cursor.fetchall()
            
        except Exception:
            flash("Error loading dashboard metrics.", "error")
        finally:
            conn.close()
            
    return render_template(
        'admin/dashboard.html', 
        stats=stats, 
        needs_assignment=needs_assignment, 
        critical_requests=critical_requests
    )

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
        # Backward-compatible handler for generic form submissions
        staff_id = request.form.get('staff_id')
        new_status = request.form.get('status')
        new_priority = request.form.get('priority')
        
        if staff_id:
            return assign_request(id)
        elif new_priority:
            return update_priority(id)
        elif new_status == 'closed':
            return close_request(id)
            
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
                
                cursor.execute("SELECT id, name, department FROM users WHERE role = 'staff' AND is_active = 1 ORDER BY name")
                staff_members = cursor.fetchall()
        except Exception:
            pass
        finally:
            conn.close()
            
    if not req:
        flash("Request not found.", "error")
        return redirect(url_for('admin.requests_list'))
        
    return render_template(
        'admin/request_details.html', 
        request_id=id, 
        req=req, 
        updates=updates, 
        statuses=statuses, 
        staff_members=staff_members
    )

# --- Dedicated Request Action Routes ---

@admin_bp.route('/request/<int:id>/assign', methods=['POST'])
@role_required('admin')
def assign_request(id):
    staff_id = request.form.get('staff_id')
    if not staff_id:
        flash("Please select a staff member to assign.", "error")
        return redirect(url_for('admin.request_details', id=id))
        
    admin_id = session.get('user_id')
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, status FROM maintenance_requests WHERE id = ?", (id,))
            req = cursor.fetchone()
            if not req:
                flash("Request not found.", "error")
                return redirect(url_for('admin.requests_list'))
                
            cursor.execute("SELECT id, name FROM users WHERE id = ? AND role = 'staff' AND is_active = 1", (staff_id,))
            staff = cursor.fetchone()
            if not staff:
                flash("Selected user is not an active staff member.", "error")
                return redirect(url_for('admin.request_details', id=id))
                
            current_status = req['status']
            new_status = STATUS_ASSIGNED
            is_valid, err_msg = validate_transition(current_status, new_status)
            if not is_valid:
                flash(err_msg, "error")
                return redirect(url_for('admin.request_details', id=id))

            cursor.execute("""
                UPDATE maintenance_requests 
                SET status = ?, assigned_to = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            """, (new_status, staff['id'], id))
            
            log_request_update(cursor, id, admin_id, current_status, new_status, f"Assigned to {staff['name']} by Admin")
            
            conn.commit()
            flash(f"Staff '{staff['name']}' assigned successfully.", "success")
        except Exception:
            flash("Failed to assign staff member.", "error")
        finally:
            conn.close()
            
    return redirect(url_for('admin.request_details', id=id))

@admin_bp.route('/request/<int:id>/priority', methods=['POST'])
@role_required('admin')
def update_priority(id):
    priority = request.form.get('priority')
    if priority not in ('low', 'medium', 'high', 'critical'):
        flash("Invalid priority level selected.", "error")
        return redirect(url_for('admin.request_details', id=id))
        
    admin_id = session.get('user_id')
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, priority, status FROM maintenance_requests WHERE id = ?", (id,))
            req = cursor.fetchone()
            if not req:
                flash("Request not found.", "error")
                return redirect(url_for('admin.requests_list'))
                
            if req['status'] == STATUS_CLOSED:
                flash("Cannot modify priority of a closed request.", "error")
                return redirect(url_for('admin.request_details', id=id))

            old_priority = req['priority']
            if old_priority != priority:
                cursor.execute("""
                    UPDATE maintenance_requests 
                    SET priority = ?, updated_at = CURRENT_TIMESTAMP 
                    WHERE id = ?
                """, (priority, id))
                
                log_request_update(
                    cursor, id, admin_id, req['status'], req['status'],
                    f"Priority changed from {old_priority.capitalize()} to {priority.capitalize()} by Admin"
                )
                
                conn.commit()
                flash(f"Priority updated to {priority.capitalize()}.", "success")
            else:
                flash("Priority is already set to this level.", "info")
        except Exception:
            flash("Failed to update priority.", "error")
        finally:
            conn.close()
            
    return redirect(url_for('admin.request_details', id=id))

@admin_bp.route('/request/<int:id>/close', methods=['POST'])
@role_required('admin')
def close_request(id):
    close_note = request.form.get('close_note', 'Verified and closed by Admin').strip()
    if not close_note:
        close_note = 'Verified and closed by Admin'
        
    admin_id = session.get('user_id')
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, status FROM maintenance_requests WHERE id = ?", (id,))
            req = cursor.fetchone()
            if not req:
                flash("Request not found.", "error")
                return redirect(url_for('admin.requests_list'))
                
            current_status = req['status']
            new_status = STATUS_CLOSED
            is_valid, err_msg = validate_transition(current_status, new_status)
            if not is_valid:
                flash(err_msg, "error")
                return redirect(url_for('admin.request_details', id=id))
                
            cursor.execute("""
                UPDATE maintenance_requests 
                SET status = ?, closed_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            """, (new_status, id))
            
            log_request_update(cursor, id, admin_id, current_status, new_status, close_note)
            
            conn.commit()
            flash("Request verified and closed successfully.", "success")
        except Exception:
            flash("Failed to close request.", "error")
        finally:
            conn.close()
            
    return redirect(url_for('admin.request_details', id=id))

# --- User Management ---

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

@admin_bp.route('/user/<int:id>/toggle-status', methods=['POST'])
@role_required('admin')
def toggle_user_status(id):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, is_active FROM users WHERE id = ? AND role = 'user'", (id,))
            user = cursor.fetchone()
            if not user:
                flash("User not found.", "error")
            else:
                new_status = 0 if user['is_active'] == 1 else 1
                cursor.execute("UPDATE users SET is_active = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (new_status, id))
                conn.commit()
                status_label = "activated" if new_status == 1 else "deactivated"
                flash(f"User account '{user['name']}' has been {status_label}.", "success")
        except Exception:
            flash("Error updating user account status.", "error")
        finally:
            conn.close()
    return redirect(url_for('admin.users'))

# --- Staff Management ---

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

@admin_bp.route('/staff/new', methods=['GET', 'POST'])
@role_required('admin')
def create_staff():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        department = request.form.get('department', '').strip()
        password = request.form.get('password', '').strip()
        
        if not name or not email or not password:
            flash("Name, email, and password are required.", "error")
            return render_template('admin/create_staff.html')
            
        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "error")
            return render_template('admin/create_staff.html')
            
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
                if cursor.fetchone():
                    flash("An account with this email already exists.", "error")
                    return render_template('admin/create_staff.html')
                    
                password_hash = generate_password_hash(password)
                cursor.execute("""
                    INSERT INTO users (name, email, phone, department, password_hash, role, is_active)
                    VALUES (?, ?, ?, ?, ?, 'staff', 1)
                """, (name, email, phone, department, password_hash))
                conn.commit()
                flash(f"Staff account for '{name}' created successfully.", "success")
                return redirect(url_for('admin.staff'))
            except Exception:
                flash("Error creating staff account.", "error")
            finally:
                conn.close()
                
    return render_template('admin/create_staff.html')

@admin_bp.route('/staff/<int:id>/edit', methods=['GET', 'POST'])
@role_required('admin')
def edit_staff(id):
    conn = get_db_connection()
    staff_member = None
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        department = request.form.get('department', '').strip()
        password = request.form.get('password', '').strip()
        is_active = 1 if request.form.get('is_active') == '1' else 0
        
        if not name or not email:
            flash("Name and email are required.", "error")
        else:
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute("SELECT id FROM users WHERE email = ? AND id != ?", (email, id))
                    if cursor.fetchone():
                        flash("Email already in use by another user.", "error")
                    else:
                        if password:
                            if len(password) < 6:
                                flash("New password must be at least 6 characters long.", "error")
                                cursor.execute("SELECT id, name, email, phone, department, is_active FROM users WHERE id = ? AND role = 'staff'", (id,))
                                staff_member = cursor.fetchone()
                                return render_template('admin/edit_staff.html', staff=staff_member)
                            password_hash = generate_password_hash(password)
                            cursor.execute("""
                                UPDATE users 
                                SET name = ?, email = ?, phone = ?, department = ?, password_hash = ?, is_active = ?, updated_at = CURRENT_TIMESTAMP
                                WHERE id = ? AND role = 'staff'
                            """, (name, email, phone, department, password_hash, is_active, id))
                        else:
                            cursor.execute("""
                                UPDATE users 
                                SET name = ?, email = ?, phone = ?, department = ?, is_active = ?, updated_at = CURRENT_TIMESTAMP
                                WHERE id = ? AND role = 'staff'
                            """, (name, email, phone, department, is_active, id))
                            
                        conn.commit()
                        flash(f"Staff member '{name}' updated successfully.", "success")
                        return redirect(url_for('admin.staff'))
                except Exception:
                    flash("Error updating staff member.", "error")
                    
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, email, phone, department, is_active FROM users WHERE id = ? AND role = 'staff'", (id,))
            staff_member = cursor.fetchone()
        except Exception:
            pass
        finally:
            conn.close()
            
    if not staff_member:
        flash("Staff member not found.", "error")
        return redirect(url_for('admin.staff'))
        
    return render_template('admin/edit_staff.html', staff=staff_member)

@admin_bp.route('/staff/<int:id>/toggle-status', methods=['POST'])
@role_required('admin')
def toggle_staff_status(id):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, is_active FROM users WHERE id = ? AND role = 'staff'", (id,))
            staff_member = cursor.fetchone()
            if not staff_member:
                flash("Staff member not found.", "error")
            else:
                new_status = 0 if staff_member['is_active'] == 1 else 1
                cursor.execute("UPDATE users SET is_active = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (new_status, id))
                conn.commit()
                status_label = "activated" if new_status == 1 else "deactivated"
                flash(f"Staff account '{staff_member['name']}' has been {status_label}.", "success")
        except Exception:
            flash("Error updating staff status.", "error")
        finally:
            conn.close()
    return redirect(url_for('admin.staff'))

# --- Category Management ---

@admin_bp.route('/categories', methods=['GET', 'POST'])
@role_required('admin')
def categories():
    conn = get_db_connection()
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        if not name:
            flash("Category name is required.", "error")
        elif conn:
            try:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO categories (name, description, is_active) VALUES (?, ?, 1)", (name, description))
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

@admin_bp.route('/categories/<int:id>/edit', methods=['GET', 'POST'])
@role_required('admin')
def edit_category(id):
    conn = get_db_connection()
    category = None
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        is_active = 1 if request.form.get('is_active') == '1' else 0
        
        if not name:
            flash("Category name is required.", "error")
        elif conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE categories 
                    SET name = ?, description = ?, is_active = ? 
                    WHERE id = ?
                """, (name, description, is_active, id))
                conn.commit()
                flash(f"Category '{name}' updated successfully.", "success")
                return redirect(url_for('admin.categories'))
            except Exception:
                flash("Error updating category.", "error")
                
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM categories WHERE id = ?", (id,))
            category = cursor.fetchone()
        except Exception:
            pass
        finally:
            conn.close()
            
    if not category:
        flash("Category not found.", "error")
        return redirect(url_for('admin.categories'))
        
    return render_template('admin/edit_category.html', category=category)

@admin_bp.route('/categories/<int:id>/toggle-status', methods=['POST'])
@role_required('admin')
def toggle_category_status(id):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, is_active FROM categories WHERE id = ?", (id,))
            cat = cursor.fetchone()
            if not cat:
                flash("Category not found.", "error")
            else:
                new_status = 0 if cat['is_active'] == 1 else 1
                cursor.execute("UPDATE categories SET is_active = ? WHERE id = ?", (new_status, id))
                conn.commit()
                status_label = "activated" if new_status == 1 else "deactivated"
                flash(f"Category '{cat['name']}' has been {status_label}.", "success")
        except Exception:
            flash("Error updating category status.", "error")
        finally:
            conn.close()
    return redirect(url_for('admin.categories'))

# --- Reports & Analytics ---

def format_resolution_time(hours):
    if hours is None:
        return "N/A"
    if hours < 1:
        mins = max(1, round(hours * 60))
        return f"{mins} min{'s' if mins != 1 else ''}"
    if hours < 24:
        return f"{hours:.1f} hrs"
    days = hours / 24
    return f"{days:.1f} days"

def get_reports_data():
    conn = get_db_connection()
    data = {
        'summary': {
            'total': 0,
            'resolved': 0,
            'active': 0,
            'pending': 0,
            'resolution_rate': 0.0,
            'avg_resolution_time': 'N/A'
        },
        'categories': [],
        'priorities': [],
        'statuses': [],
        'staff_workload': [],
        'monthly_trends': []
    }
    if not conn:
        return data

    try:
        cursor = conn.cursor()

        # 1. Summary Counts & Avg Resolution Time
        cursor.execute("SELECT COUNT(*) as total FROM maintenance_requests")
        total = cursor.fetchone()['total']

        cursor.execute("SELECT COUNT(*) as resolved FROM maintenance_requests WHERE status IN ('resolved', 'closed')")
        resolved = cursor.fetchone()['resolved']

        cursor.execute("SELECT COUNT(*) as active FROM maintenance_requests WHERE status IN ('assigned', 'in_progress')")
        active = cursor.fetchone()['active']

        cursor.execute("SELECT COUNT(*) as pending FROM maintenance_requests WHERE status = 'pending'")
        pending = cursor.fetchone()['pending']

        cursor.execute("SELECT AVG((julianday(resolved_at) - julianday(created_at)) * 24) as avg_hrs FROM maintenance_requests WHERE resolved_at IS NOT NULL")
        avg_hrs_row = cursor.fetchone()
        avg_hrs = avg_hrs_row['avg_hrs'] if avg_hrs_row else None

        resolution_rate = round((resolved * 100.0 / total), 1) if total > 0 else 0.0

        data['summary'] = {
            'total': total,
            'resolved': resolved,
            'active': active,
            'pending': pending,
            'resolution_rate': resolution_rate,
            'avg_resolution_time': format_resolution_time(avg_hrs)
        }

        # 2. Requests by Category
        cursor.execute("""
            SELECT c.id, c.name, COUNT(r.id) as count
            FROM categories c
            LEFT JOIN maintenance_requests r ON r.category_id = c.id
            GROUP BY c.id, c.name
            ORDER BY count DESC, c.name ASC
        """)
        cat_rows = cursor.fetchall()
        categories = []
        for row in cat_rows:
            cnt = row['count']
            pct = round((cnt * 100.0 / total), 1) if total > 0 else 0.0
            categories.append({
                'name': row['name'],
                'count': cnt,
                'percentage': pct
            })
        data['categories'] = categories

        # 3. Requests by Priority
        cursor.execute("""
            SELECT priority, COUNT(*) as count 
            FROM maintenance_requests 
            GROUP BY priority
        """)
        priority_counts = {r['priority']: r['count'] for r in cursor.fetchall()}
        priorities = []
        for p in ['critical', 'high', 'medium', 'low']:
            cnt = priority_counts.get(p, 0)
            pct = round((cnt * 100.0 / total), 1) if total > 0 else 0.0
            priorities.append({
                'priority': p,
                'label': p.capitalize(),
                'count': cnt,
                'percentage': pct
            })
        data['priorities'] = priorities

        # 4. Requests by Status
        cursor.execute("""
            SELECT status, COUNT(*) as count 
            FROM maintenance_requests 
            GROUP BY status
        """)
        status_counts = {r['status']: r['count'] for r in cursor.fetchall()}
        status_labels = [
            ('pending', 'Requested'),
            ('assigned', 'Approved'),
            ('in_progress', 'On Work'),
            ('resolved', 'Rectified'),
            ('closed', 'Closed')
        ]
        statuses = []
        for s, lbl in status_labels:
            cnt = status_counts.get(s, 0)
            pct = round((cnt * 100.0 / total), 1) if total > 0 else 0.0
            statuses.append({
                'status': s,
                'label': lbl,
                'count': cnt,
                'percentage': pct
            })
        data['statuses'] = statuses

        # 5. Staff Workload Distribution
        cursor.execute("""
            SELECT 
                u.id, 
                u.name, 
                u.department,
                COUNT(CASE WHEN r.status IN ('assigned', 'in_progress') THEN 1 END) as active_jobs,
                COUNT(CASE WHEN r.status IN ('resolved', 'closed') THEN 1 END) as resolved_jobs,
                COUNT(r.id) as total_jobs,
                AVG(CASE WHEN r.resolved_at IS NOT NULL THEN (julianday(r.resolved_at) - julianday(r.created_at)) * 24 END) as avg_resolution_hours
            FROM users u
            LEFT JOIN maintenance_requests r ON r.assigned_to = u.id
            WHERE u.role = 'staff' AND u.is_active = 1
            GROUP BY u.id, u.name, u.department
            ORDER BY active_jobs DESC, resolved_jobs DESC
        """)
        staff_workload = []
        for row in cursor.fetchall():
            staff_workload.append({
                'id': row['id'],
                'name': row['name'],
                'department': row['department'] or 'General Maintenance',
                'active_jobs': row['active_jobs'],
                'resolved_jobs': row['resolved_jobs'],
                'total_jobs': row['total_jobs'],
                'avg_resolution_time': format_resolution_time(row['avg_resolution_hours'])
            })
        data['staff_workload'] = staff_workload

        # 6. Monthly Request Count
        cursor.execute("""
            SELECT 
                strftime('%Y-%m', created_at) as month_key,
                COUNT(*) as total_count,
                COUNT(CASE WHEN status IN ('resolved', 'closed') THEN 1 END) as resolved_count
            FROM maintenance_requests
            GROUP BY strftime('%Y-%m', created_at)
            ORDER BY month_key DESC
            LIMIT 12
        """)
        monthly_trends = []
        for row in cursor.fetchall():
            m_key = row['month_key'] or 'Unknown'
            m_lbl = m_key
            try:
                m_lbl = datetime.strptime(m_key, '%Y-%m').strftime('%B %Y')
            except Exception:
                pass
            t_cnt = row['total_count']
            r_cnt = row['resolved_count']
            rate = round((r_cnt * 100.0 / t_cnt), 1) if t_cnt > 0 else 0.0
            monthly_trends.append({
                'month_key': m_key,
                'month_label': m_lbl,
                'total_count': t_cnt,
                'resolved_count': r_cnt,
                'resolution_rate': rate
            })
        data['monthly_trends'] = monthly_trends

    except Exception:
        pass
    finally:
        conn.close()

    return data

@admin_bp.route('/reports')
@role_required('admin')
def reports():
    data = get_reports_data()
    return render_template('admin/reports.html', data=data)

@admin_bp.route('/reports/export-csv')
@role_required('admin')
def export_reports_csv():
    conn = get_db_connection()
    if not conn:
        flash("Database connection error.", "error")
        return redirect(url_for('admin.reports'))

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                r.id,
                r.title,
                COALESCE(c.name, 'Uncategorized') as category,
                COALESCE(r.location, 'N/A') as location,
                r.priority,
                r.status,
                COALESCE(u.name, 'Unknown') as reported_by,
                COALESCE(u.email, 'N/A') as reporter_email,
                COALESCE(s.name, 'Unassigned') as assigned_staff,
                COALESCE(r.created_at, '') as created_at,
                COALESCE(r.updated_at, '') as updated_at,
                COALESCE(r.resolved_at, '') as resolved_at,
                COALESCE(r.closed_at, '') as closed_at,
                COALESCE(r.resolution_note, '') as resolution_note
            FROM maintenance_requests r
            LEFT JOIN categories c ON r.category_id = c.id
            LEFT JOIN users u ON r.user_id = u.id
            LEFT JOIN users s ON r.assigned_to = s.id
            ORDER BY r.id DESC
        """)
        rows = cursor.fetchall()

        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            'Request ID', 'Title', 'Category', 'Location', 'Priority',
            'Status', 'Reported By', 'Reporter Email', 'Assigned Staff',
            'Created At', 'Updated At', 'Resolved At', 'Closed At', 'Resolution Note'
        ])

        for row in rows:
            writer.writerow([
                row['id'],
                row['title'],
                row['category'],
                row['location'],
                row['priority'].capitalize() if row['priority'] else '',
                row['status'].replace('_', ' ').capitalize() if row['status'] else '',
                row['reported_by'],
                row['reporter_email'],
                row['assigned_staff'],
                row['created_at'],
                row['updated_at'],
                row['resolved_at'],
                row['closed_at'],
                row['resolution_note']
            ])

        filename = f"maintenx_maintenance_report_{datetime.now().strftime('%Y%m%d')}.csv"
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception:
        flash("Error generating CSV export.", "error")
        return redirect(url_for('admin.reports'))
    finally:
        conn.close()

@admin_bp.route('/reports/print')
@role_required('admin')
def print_report():
    data = get_reports_data()
    generated_at = datetime.now().strftime('%B %d, %Y - %I:%M %p')
    return render_template('admin/print_report.html', data=data, generated_at=generated_at)

@admin_bp.route('/feedback')
@role_required('admin')
def feedback():
    return render_template('admin/feedback.html')

@admin_bp.route('/bug-reports')
@role_required('admin')
def bug_reports():
    return render_template('admin/bug_reports.html')
