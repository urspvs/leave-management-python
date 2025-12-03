import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import hashlib

# Database setup
def init_database():
    """Initialize the SQLite database with tables and sample data"""
    conn = sqlite3.connect('leave_management.db')
    cursor = conn.cursor()
    
    # Create employees table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            emp_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            department TEXT NOT NULL,
            role TEXT NOT NULL,
            total_leaves INTEGER DEFAULT 20,
            used_leaves INTEGER DEFAULT 0
        )
    ''')
    
    # Create leave_requests table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leave_requests (
            request_id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id INTEGER NOT NULL,
            leave_type TEXT NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            days INTEGER NOT NULL,
            reason TEXT,
            status TEXT DEFAULT 'Pending',
            applied_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            approved_by INTEGER,
            approved_date TIMESTAMP,
            FOREIGN KEY (emp_id) REFERENCES employees(emp_id)
        )
    ''')
    
    # Check if sample data already exists
    cursor.execute('SELECT COUNT(*) FROM employees')
    if cursor.fetchone()[0] == 0:
        # Insert sample employees (password is 'password123' hashed)
        sample_employees = [
            (1001, 'John Doe', 'john.doe@acme.com', hashlib.sha256('password123'.encode()).hexdigest(), 'Engineering', 'Employee', 20, 5),
            (1002, 'Jane Smith', 'jane.smith@acme.com', hashlib.sha256('password123'.encode()).hexdigest(), 'Engineering', 'Manager', 20, 3),
            (1003, 'Bob Johnson', 'bob.johnson@acme.com', hashlib.sha256('password123'.encode()).hexdigest(), 'HR', 'Employee', 20, 8),
            (1004, 'Alice Williams', 'alice.williams@acme.com', hashlib.sha256('password123'.encode()).hexdigest(), 'Marketing', 'Employee', 20, 2),
            (1005, 'Charlie Brown', 'charlie.brown@acme.com', hashlib.sha256('password123'.encode()).hexdigest(), 'Sales', 'Manager', 20, 4),
            (1006, 'Diana Prince', 'diana.prince@acme.com', hashlib.sha256('password123'.encode()).hexdigest(), 'Engineering', 'Employee', 20, 6),
            (1007, 'Eve Davis', 'eve.davis@acme.com', hashlib.sha256('password123'.encode()).hexdigest(), 'HR', 'Manager', 20, 1),
        ]
        
        cursor.executemany('''
            INSERT INTO employees (emp_id, name, email, password, department, role, total_leaves, used_leaves)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_employees)
        
        # Insert sample leave requests
        sample_leaves = [
            (1001, 'Sick Leave', '2025-11-15', '2025-11-17', 3, 'Medical appointment', 'Approved', 1002),
            (1001, 'Casual Leave', '2025-12-20', '2025-12-22', 2, 'Personal work', 'Pending', None),
            (1003, 'Annual Leave', '2025-11-01', '2025-11-08', 8, 'Vacation', 'Approved', 1007),
            (1004, 'Casual Leave', '2025-11-25', '2025-11-26', 2, 'Family function', 'Approved', 1002),
            (1006, 'Sick Leave', '2025-12-01', '2025-12-03', 3, 'Flu', 'Rejected', 1002),
            (1006, 'Casual Leave', '2025-12-15', '2025-12-17', 3, 'Personal work', 'Pending', None),
        ]
        
        cursor.executemany('''
            INSERT INTO leave_requests (emp_id, leave_type, start_date, end_date, days, reason, status, approved_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_leaves)
        
        conn.commit()
    
    conn.close()

# Authentication functions
def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate_user(email, password):
    """Authenticate user credentials"""
    conn = sqlite3.connect('leave_management.db')
    cursor = conn.cursor()
    
    hashed_password = hash_password(password)
    cursor.execute('''
        SELECT emp_id, name, email, department, role, total_leaves, used_leaves
        FROM employees
        WHERE email = ? AND password = ?
    ''', (email, hashed_password))
    
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return {
            'emp_id': user[0],
            'name': user[1],
            'email': user[2],
            'department': user[3],
            'role': user[4],
            'total_leaves': user[5],
            'used_leaves': user[6]
        }
    return None

# Leave management functions
def apply_leave(emp_id, leave_type, start_date, end_date, reason):
    """Apply for a new leave"""
    conn = sqlite3.connect('leave_management.db')
    cursor = conn.cursor()
    
    # Calculate number of days
    days = (end_date - start_date).days + 1
    
    cursor.execute('''
        INSERT INTO leave_requests (emp_id, leave_type, start_date, end_date, days, reason, status)
        VALUES (?, ?, ?, ?, ?, ?, 'Pending')
    ''', (emp_id, leave_type, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), days, reason))
    
    conn.commit()
    conn.close()
    return True

def get_employee_leaves(emp_id):
    """Get all leave requests for an employee"""
    conn = sqlite3.connect('leave_management.db')
    query = '''
        SELECT request_id, leave_type, start_date, end_date, days, reason, status, applied_date
        FROM leave_requests
        WHERE emp_id = ?
        ORDER BY applied_date DESC
    '''
    df = pd.read_sql_query(query, conn, params=(emp_id,))
    conn.close()
    return df

def get_all_leave_requests():
    """Get all leave requests (for managers)"""
    conn = sqlite3.connect('leave_management.db')
    query = '''
        SELECT lr.request_id, e.name, e.department, lr.leave_type, 
               lr.start_date, lr.end_date, lr.days, lr.reason, lr.status, lr.applied_date
        FROM leave_requests lr
        JOIN employees e ON lr.emp_id = e.emp_id
        ORDER BY lr.applied_date DESC
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def update_leave_status(request_id, status, manager_id):
    """Update leave request status"""
    conn = sqlite3.connect('leave_management.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE leave_requests
        SET status = ?, approved_by = ?, approved_date = CURRENT_TIMESTAMP
        WHERE request_id = ?
    ''', (status, manager_id, request_id))
    
    # If approved, update employee's used leaves
    if status == 'Approved':
        cursor.execute('''
            UPDATE employees
            SET used_leaves = used_leaves + (
                SELECT days FROM leave_requests WHERE request_id = ?
            )
            WHERE emp_id = (
                SELECT emp_id FROM leave_requests WHERE request_id = ?
            )
        ''', (request_id, request_id))
    
    conn.commit()
    conn.close()

def get_leave_statistics(emp_id):
    """Get leave statistics for an employee"""
    conn = sqlite3.connect('leave_management.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT total_leaves, used_leaves
        FROM employees
        WHERE emp_id = ?
    ''', (emp_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        total, used = result
        return {
            'total': total,
            'used': used,
            'available': total - used
        }
    return None

# Streamlit UI
def main():
    st.set_page_config(
        page_title="ACME Leave Management System",
        page_icon="🏢",
        layout="wide"
    )
    
    # Initialize database
    init_database()
    
    # Custom CSS
    st.markdown("""
        <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            color: #1f77b4;
            text-align: center;
            margin-bottom: 2rem;
        }
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1.5rem;
            border-radius: 10px;
            color: white;
            text-align: center;
            margin: 0.5rem 0;
        }
        .stat-value {
            font-size: 2rem;
            font-weight: bold;
        }
        .stat-label {
            font-size: 0.9rem;
            opacity: 0.9;
        }
        .status-pending {
            background-color: #ffc107;
            color: black;
            padding: 0.3rem 0.8rem;
            border-radius: 15px;
            font-weight: bold;
        }
        .status-approved {
            background-color: #28a745;
            color: white;
            padding: 0.3rem 0.8rem;
            border-radius: 15px;
            font-weight: bold;
        }
        .status-rejected {
            background-color: #dc3545;
            color: white;
            padding: 0.3rem 0.8rem;
            border-radius: 15px;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Session state initialization
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user = None
    
    # Login page
    if not st.session_state.logged_in:
        st.markdown('<div class="main-header">🏢 ACME Leave Management System</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("### 🔐 Login")
            
            with st.form("login_form"):
                email = st.text_input("Email", placeholder="your.email@acme.com")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                submit = st.form_submit_button("Login", use_container_width=True)
                
                if submit:
                    user = authenticate_user(email, password)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user = user
                        st.rerun()
                    else:
                        st.error("❌ Invalid credentials. Please try again.")
            
            st.info("💡 **Demo Credentials:**\n\n**Employee:** john.doe@acme.com / password123\n\n**Manager:** jane.smith@acme.com / password123")
    
    # Main application
    else:
        user = st.session_state.user
        
        # Header
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f'<div class="main-header">🏢 ACME Leave Management System</div>', unsafe_allow_html=True)
        with col2:
            st.write(f"**Welcome, {user['name']}**")
            st.write(f"*{user['role']} - {user['department']}*")
            if st.button("Logout", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.user = None
                st.rerun()
        
        st.divider()
        
        # Navigation tabs
        if user['role'] == 'Manager':
            tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "➕ Apply Leave", "📋 My Leaves", "✅ Approve Leaves"])
        else:
            tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "➕ Apply Leave", "📋 My Leaves"])
        
        # Dashboard Tab
        with tab1:
            st.header("📊 Leave Dashboard")
            
            stats = get_leave_statistics(user['emp_id'])
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                    <div class="stat-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                        <div class="stat-value">{stats['total']}</div>
                        <div class="stat-label">Total Leaves</div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                    <div class="stat-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                        <div class="stat-value">{stats['used']}</div>
                        <div class="stat-label">Used Leaves</div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                    <div class="stat-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
                        <div class="stat-value">{stats['available']}</div>
                        <div class="stat-label">Available Leaves</div>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Recent leave requests
            st.subheader("📅 Recent Leave Requests")
            leaves_df = get_employee_leaves(user['emp_id'])
            
            if not leaves_df.empty:
                # Format the dataframe for display
                display_df = leaves_df.copy()
                display_df['start_date'] = pd.to_datetime(display_df['start_date']).dt.strftime('%Y-%m-%d')
                display_df['end_date'] = pd.to_datetime(display_df['end_date']).dt.strftime('%Y-%m-%d')
                display_df['applied_date'] = pd.to_datetime(display_df['applied_date']).dt.strftime('%Y-%m-%d %H:%M')
                
                st.dataframe(
                    display_df,
                    column_config={
                        "request_id": "Request ID",
                        "leave_type": "Leave Type",
                        "start_date": "Start Date",
                        "end_date": "End Date",
                        "days": "Days",
                        "reason": "Reason",
                        "status": st.column_config.TextColumn(
                            "Status",
                        ),
                        "applied_date": "Applied On"
                    },
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.info("No leave requests found.")
        
        # Apply Leave Tab
        with tab2:
            st.header("➕ Apply for Leave")
            
            col1, col2 = st.columns(2)
            
            with col1:
                leave_type = st.selectbox(
                    "Leave Type",
                    ["Casual Leave", "Sick Leave", "Annual Leave", "Maternity Leave", "Paternity Leave"]
                )
                start_date = st.date_input("Start Date", min_value=datetime.now().date())
            
            with col2:
                end_date = st.date_input("End Date", min_value=datetime.now().date())
                
            reason = st.text_area("Reason for Leave", placeholder="Please provide a reason for your leave request...")
            
            if st.button("Submit Leave Request", type="primary", use_container_width=True):
                if start_date > end_date:
                    st.error("❌ End date must be after start date!")
                elif not reason.strip():
                    st.error("❌ Please provide a reason for your leave request!")
                else:
                    days_requested = (end_date - start_date).days + 1
                    stats = get_leave_statistics(user['emp_id'])
                    
                    if days_requested > stats['available']:
                        st.error(f"❌ Insufficient leave balance! You have only {stats['available']} days available.")
                    else:
                        apply_leave(user['emp_id'], leave_type, start_date, end_date, reason)
                        st.success(f"✅ Leave request submitted successfully for {days_requested} days!")
                        st.balloons()
        
        # My Leaves Tab
        with tab3:
            st.header("📋 My Leave History")
            
            leaves_df = get_employee_leaves(user['emp_id'])
            
            if not leaves_df.empty:
                # Filter options
                col1, col2 = st.columns(2)
                with col1:
                    status_filter = st.multiselect(
                        "Filter by Status",
                        options=['Pending', 'Approved', 'Rejected'],
                        default=['Pending', 'Approved', 'Rejected']
                    )
                
                with col2:
                    leave_type_filter = st.multiselect(
                        "Filter by Leave Type",
                        options=leaves_df['leave_type'].unique(),
                        default=leaves_df['leave_type'].unique()
                    )
                
                # Apply filters
                filtered_df = leaves_df[
                    (leaves_df['status'].isin(status_filter)) &
                    (leaves_df['leave_type'].isin(leave_type_filter))
                ]
                
                # Format the dataframe
                display_df = filtered_df.copy()
                display_df['start_date'] = pd.to_datetime(display_df['start_date']).dt.strftime('%Y-%m-%d')
                display_df['end_date'] = pd.to_datetime(display_df['end_date']).dt.strftime('%Y-%m-%d')
                display_df['applied_date'] = pd.to_datetime(display_df['applied_date']).dt.strftime('%Y-%m-%d %H:%M')
                
                st.dataframe(
                    display_df,
                    column_config={
                        "request_id": "Request ID",
                        "leave_type": "Leave Type",
                        "start_date": "Start Date",
                        "end_date": "End Date",
                        "days": "Days",
                        "reason": "Reason",
                        "status": "Status",
                        "applied_date": "Applied On"
                    },
                    hide_index=True,
                    use_container_width=True
                )
                
                st.info(f"📊 Showing {len(filtered_df)} of {len(leaves_df)} leave requests")
            else:
                st.info("No leave requests found.")
        
        # Approve Leaves Tab (Manager only)
        if user['role'] == 'Manager':
            with tab4:
                st.header("✅ Approve Leave Requests")
                
                all_leaves_df = get_all_leave_requests()
                
                if not all_leaves_df.empty:
                    # Filter for pending requests
                    pending_df = all_leaves_df[all_leaves_df['status'] == 'Pending']
                    
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.subheader(f"Pending Requests ({len(pending_df)})")
                    with col2:
                        show_all = st.checkbox("Show All Requests")
                    
                    display_df = all_leaves_df if show_all else pending_df
                    
                    if not display_df.empty:
                        for idx, row in display_df.iterrows():
                            with st.container():
                                col1, col2, col3, col4 = st.columns([2, 2, 3, 2])
                                
                                with col1:
                                    st.write(f"**{row['name']}**")
                                    st.caption(f"{row['department']}")
                                
                                with col2:
                                    st.write(f"**{row['leave_type']}**")
                                    st.caption(f"{row['days']} days")
                                
                                with col3:
                                    st.write(f"{row['start_date']} to {row['end_date']}")
                                    st.caption(f"Reason: {row['reason']}")
                                
                                with col4:
                                    if row['status'] == 'Pending':
                                        col_a, col_b = st.columns(2)
                                        with col_a:
                                            if st.button("✅", key=f"approve_{row['request_id']}", use_container_width=True):
                                                update_leave_status(row['request_id'], 'Approved', user['emp_id'])
                                                st.success("Approved!")
                                                st.rerun()
                                        with col_b:
                                            if st.button("❌", key=f"reject_{row['request_id']}", use_container_width=True):
                                                update_leave_status(row['request_id'], 'Rejected', user['emp_id'])
                                                st.error("Rejected!")
                                                st.rerun()
                                    else:
                                        status_color = "green" if row['status'] == 'Approved' else "red"
                                        st.markdown(f":{status_color}[{row['status']}]")
                                
                                st.divider()
                    else:
                        st.info("No pending leave requests.")
                else:
                    st.info("No leave requests found.")

if __name__ == "__main__":
    main()
