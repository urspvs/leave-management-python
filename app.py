import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import hashlib

# Page configuration
st.set_page_config(
    page_title="ACME Leave Management System",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
    }
    
    .stApp {
        background: transparent;
    }
    
    .block-container {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
    }
    
    h1 {
        color: #667eea;
        font-weight: 700;
        text-align: center;
        margin-bottom: 2rem;
        font-size: 2.5rem;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    h2 {
        color: #764ba2;
        font-weight: 600;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    
    h3 {
        color: #667eea;
        font-weight: 500;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    .stTextInput>div>div>input, .stSelectbox>div>div>select, .stDateInput>div>div>input, .stTextArea>div>div>textarea {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        padding: 0.75rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput>div>div>input:focus, .stSelectbox>div>div>select:focus, .stDateInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
        margin-bottom: 1rem;
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .status-pending {
        background: #fbbf24;
        color: #78350f;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    
    .status-approved {
        background: #34d399;
        color: #064e3b;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    
    .status-rejected {
        background: #f87171;
        color: #7f1d1d;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
    }
    
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
    }
    
    .success-message {
        background: #d1fae5;
        color: #065f46;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #10b981;
        margin: 1rem 0;
    }
    
    .error-message {
        background: #fee2e2;
        color: #991b1b;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #ef4444;
        margin: 1rem 0;
    }
    
    .info-card {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 4px solid #0284c7;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Database initialization
def init_db():
    conn = sqlite3.connect('leave_management.db')
    c = conn.cursor()
    
    # Create employees table
    c.execute('''CREATE TABLE IF NOT EXISTS employees
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  emp_id TEXT UNIQUE NOT NULL,
                  name TEXT NOT NULL,
                  email TEXT NOT NULL,
                  department TEXT NOT NULL,
                  position TEXT NOT NULL,
                  password TEXT NOT NULL,
                  total_leaves INTEGER DEFAULT 20,
                  used_leaves INTEGER DEFAULT 0)''')
    
    # Create leave_requests table
    c.execute('''CREATE TABLE IF NOT EXISTS leave_requests
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  emp_id TEXT NOT NULL,
                  leave_type TEXT NOT NULL,
                  start_date DATE NOT NULL,
                  end_date DATE NOT NULL,
                  days INTEGER NOT NULL,
                  reason TEXT,
                  status TEXT DEFAULT 'Pending',
                  applied_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  approved_by TEXT,
                  approved_date TIMESTAMP,
                  FOREIGN KEY (emp_id) REFERENCES employees(emp_id))''')
    
    conn.commit()
    conn.close()

# Insert sample data
def insert_sample_data():
    conn = sqlite3.connect('leave_management.db')
    c = conn.cursor()
    
    # Check if data already exists
    c.execute("SELECT COUNT(*) FROM employees")
    if c.fetchone()[0] == 0:
        # Sample employees
        employees = [
            ('EMP001', 'John Doe', 'john.doe@acme.com', 'Engineering', 'Senior Developer', hashlib.md5('password123'.encode()).hexdigest(), 20, 5),
            ('EMP002', 'Jane Smith', 'jane.smith@acme.com', 'Marketing', 'Marketing Manager', hashlib.md5('password123'.encode()).hexdigest(), 20, 3),
            ('EMP003', 'Mike Johnson', 'mike.johnson@acme.com', 'HR', 'HR Specialist', hashlib.md5('password123'.encode()).hexdigest(), 20, 8),
            ('EMP004', 'Sarah Williams', 'sarah.williams@acme.com', 'Engineering', 'Junior Developer', hashlib.md5('password123'.encode()).hexdigest(), 20, 2),
            ('EMP005', 'Robert Brown', 'robert.brown@acme.com', 'Sales', 'Sales Executive', hashlib.md5('password123'.encode()).hexdigest(), 20, 10),
            ('ADMIN', 'Admin User', 'admin@acme.com', 'Management', 'Administrator', hashlib.md5('admin123'.encode()).hexdigest(), 20, 0),
        ]
        
        c.executemany('''INSERT INTO employees 
                        (emp_id, name, email, department, position, password, total_leaves, used_leaves)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', employees)
        
        # Sample leave requests
        leave_requests = [
            ('EMP001', 'Sick Leave', '2025-11-15', '2025-11-17', 3, 'Medical appointment', 'Approved', 'ADMIN'),
            ('EMP001', 'Vacation', '2025-12-20', '2025-12-22', 2, 'Family vacation', 'Pending', None),
            ('EMP002', 'Personal Leave', '2025-11-20', '2025-11-22', 3, 'Personal matters', 'Approved', 'ADMIN'),
            ('EMP003', 'Sick Leave', '2025-11-10', '2025-11-17', 8, 'Flu recovery', 'Approved', 'ADMIN'),
            ('EMP004', 'Vacation', '2025-12-15', '2025-12-16', 2, 'Short trip', 'Pending', None),
            ('EMP005', 'Sick Leave', '2025-11-01', '2025-11-05', 5, 'Surgery recovery', 'Approved', 'ADMIN'),
            ('EMP005', 'Vacation', '2025-12-10', '2025-12-14', 5, 'Year-end vacation', 'Rejected', 'ADMIN'),
        ]
        
        c.executemany('''INSERT INTO leave_requests 
                        (emp_id, leave_type, start_date, end_date, days, reason, status, approved_by)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', leave_requests)
        
        conn.commit()
    
    conn.close()

# Authentication functions
def authenticate_user(emp_id, password):
    conn = sqlite3.connect('leave_management.db')
    c = conn.cursor()
    hashed_password = hashlib.md5(password.encode()).hexdigest()
    c.execute("SELECT * FROM employees WHERE emp_id=? AND password=?", (emp_id, hashed_password))
    user = c.fetchone()
    conn.close()
    return user

def get_employee_info(emp_id):
    conn = sqlite3.connect('leave_management.db')
    c = conn.cursor()
    c.execute("SELECT * FROM employees WHERE emp_id=?", (emp_id,))
    employee = c.fetchone()
    conn.close()
    return employee

# Leave management functions
def apply_leave(emp_id, leave_type, start_date, end_date, reason):
    conn = sqlite3.connect('leave_management.db')
    c = conn.cursor()
    
    # Calculate number of days
    days = (end_date - start_date).days + 1
    
    # Check available leaves
    employee = get_employee_info(emp_id)
    available_leaves = employee[6] - employee[7]  # total_leaves - used_leaves
    
    if days > available_leaves:
        conn.close()
        return False, f"Insufficient leave balance. Available: {available_leaves} days"
    
    c.execute('''INSERT INTO leave_requests 
                 (emp_id, leave_type, start_date, end_date, days, reason)
                 VALUES (?, ?, ?, ?, ?, ?)''',
              (emp_id, leave_type, start_date, end_date, days, reason))
    
    conn.commit()
    conn.close()
    return True, "Leave application submitted successfully!"

def get_employee_leaves(emp_id):
    conn = sqlite3.connect('leave_management.db')
    df = pd.read_sql_query(
        "SELECT * FROM leave_requests WHERE emp_id=? ORDER BY applied_date DESC",
        conn, params=(emp_id,))
    conn.close()
    return df

def get_all_leaves():
    conn = sqlite3.connect('leave_management.db')
    df = pd.read_sql_query(
        """SELECT lr.*, e.name, e.department 
           FROM leave_requests lr 
           JOIN employees e ON lr.emp_id = e.emp_id 
           ORDER BY lr.applied_date DESC""", conn)
    conn.close()
    return df

def update_leave_status(leave_id, status, approved_by):
    conn = sqlite3.connect('leave_management.db')
    c = conn.cursor()
    
    # Get leave details
    c.execute("SELECT emp_id, days, status FROM leave_requests WHERE id=?", (leave_id,))
    leave = c.fetchone()
    
    if leave:
        emp_id, days, old_status = leave
        
        # Update leave status
        c.execute('''UPDATE leave_requests 
                     SET status=?, approved_by=?, approved_date=CURRENT_TIMESTAMP 
                     WHERE id=?''', (status, approved_by, leave_id))
        
        # Update employee's used leaves if approved
        if status == 'Approved' and old_status != 'Approved':
            c.execute("UPDATE employees SET used_leaves = used_leaves + ? WHERE emp_id=?",
                     (days, emp_id))
        elif status == 'Rejected' and old_status == 'Approved':
            c.execute("UPDATE employees SET used_leaves = used_leaves - ? WHERE emp_id=?",
                     (days, emp_id))
        
        conn.commit()
    
    conn.close()

def get_dashboard_stats(emp_id=None):
    conn = sqlite3.connect('leave_management.db')
    c = conn.cursor()
    
    if emp_id:
        # Employee-specific stats
        employee = get_employee_info(emp_id)
        total_leaves = employee[6]
        used_leaves = employee[7]
        available_leaves = total_leaves - used_leaves
        
        c.execute("SELECT COUNT(*) FROM leave_requests WHERE emp_id=? AND status='Pending'", (emp_id,))
        pending_requests = c.fetchone()[0]
        
        conn.close()
        return {
            'total_leaves': total_leaves,
            'used_leaves': used_leaves,
            'available_leaves': available_leaves,
            'pending_requests': pending_requests
        }
    else:
        # Admin stats
        c.execute("SELECT COUNT(*) FROM leave_requests WHERE status='Pending'")
        pending_requests = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM employees")
        total_employees = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM leave_requests WHERE status='Approved'")
        approved_leaves = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM leave_requests")
        total_requests = c.fetchone()[0]
        
        conn.close()
        return {
            'pending_requests': pending_requests,
            'total_employees': total_employees,
            'approved_leaves': approved_leaves,
            'total_requests': total_requests
        }

# Initialize database and sample data
init_db()
insert_sample_data()

# Session state initialization
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'user_name' not in st.session_state:
    st.session_state.user_name = None
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False

# Login page
def login_page():
    st.markdown("<h1>🏢 ACME Leave Management System</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
            <div class="info-card">
                <h3 style="margin-top: 0;">Welcome to ACME Leave Management</h3>
                <p>Manage your leave requests efficiently and track your leave balance.</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🔐 Login")
        emp_id = st.text_input("Employee ID", placeholder="Enter your employee ID")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Login", use_container_width=True):
                if emp_id and password:
                    user = authenticate_user(emp_id, password)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user_id = user[1]
                        st.session_state.user_name = user[2]
                        st.session_state.is_admin = (user[1] == 'ADMIN')
                        st.rerun()
                    else:
                        st.error("Invalid credentials!")
                else:
                    st.warning("Please enter both Employee ID and Password")
        
        st.markdown("---")
        st.markdown("""
            <div style="text-align: center; color: #666;">
                <p><strong>Demo Credentials:</strong></p>
                <p>Employee: EMP001 / password123</p>
                <p>Admin: ADMIN / admin123</p>
            </div>
        """, unsafe_allow_html=True)

# Employee dashboard
def employee_dashboard():
    st.markdown(f"<h1>👋 Welcome, {st.session_state.user_name}!</h1>", unsafe_allow_html=True)
    
    # Dashboard stats
    stats = get_dashboard_stats(st.session_state.user_id)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total Leaves</div>
                <div class="metric-value">{stats['total_leaves']}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="metric-card" style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);">
                <div class="metric-label">Used Leaves</div>
                <div class="metric-value">{stats['used_leaves']}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="metric-card" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%);">
                <div class="metric-label">Available Leaves</div>
                <div class="metric-value">{stats['available_leaves']}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
            <div class="metric-card" style="background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);">
                <div class="metric-label">Pending Requests</div>
                <div class="metric-value">{stats['pending_requests']}</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Tabs for different sections
    tab1, tab2 = st.tabs(["📝 Apply Leave", "📊 My Leave History"])
    
    with tab1:
        st.markdown("## Apply for Leave")
        
        col1, col2 = st.columns(2)
        
        with col1:
            leave_type = st.selectbox(
                "Leave Type",
                ["Sick Leave", "Vacation", "Personal Leave", "Emergency Leave", "Other"]
            )
            start_date = st.date_input("Start Date", min_value=datetime.now().date())
        
        with col2:
            reason = st.text_area("Reason", placeholder="Please provide a reason for your leave request")
            end_date = st.date_input("End Date", min_value=datetime.now().date())
        
        if st.button("Submit Leave Request", use_container_width=True):
            if start_date and end_date and reason:
                if end_date >= start_date:
                    success, message = apply_leave(
                        st.session_state.user_id,
                        leave_type,
                        start_date,
                        end_date,
                        reason
                    )
                    if success:
                        st.markdown(f'<div class="success-message">✅ {message}</div>', unsafe_allow_html=True)
                        st.rerun()
                    else:
                        st.markdown(f'<div class="error-message">❌ {message}</div>', unsafe_allow_html=True)
                else:
                    st.error("End date must be after or equal to start date!")
            else:
                st.warning("Please fill in all fields!")
    
    with tab2:
        st.markdown("## My Leave History")
        
        leaves_df = get_employee_leaves(st.session_state.user_id)
        
        if not leaves_df.empty:
            # Format the dataframe for display
            display_df = leaves_df[['leave_type', 'start_date', 'end_date', 'days', 'reason', 'status', 'applied_date']].copy()
            display_df.columns = ['Leave Type', 'Start Date', 'End Date', 'Days', 'Reason', 'Status', 'Applied Date']
            
            # Apply styling to status
            def highlight_status(row):
                if row['Status'] == 'Approved':
                    return ['background-color: #d1fae5'] * len(row)
                elif row['Status'] == 'Rejected':
                    return ['background-color: #fee2e2'] * len(row)
                else:
                    return ['background-color: #fef3c7'] * len(row)
            
            st.dataframe(display_df, use_container_width=True, hide_index=True)
        else:
            st.info("No leave requests found.")

# Admin dashboard
def admin_dashboard():
    st.markdown(f"<h1>🔧 Admin Dashboard</h1>", unsafe_allow_html=True)
    
    # Dashboard stats
    stats = get_dashboard_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Pending Requests</div>
                <div class="metric-value">{stats['pending_requests']}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="metric-card" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%);">
                <div class="metric-label">Total Employees</div>
                <div class="metric-value">{stats['total_employees']}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="metric-card" style="background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);">
                <div class="metric-label">Approved Leaves</div>
                <div class="metric-value">{stats['approved_leaves']}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
            <div class="metric-card" style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);">
                <div class="metric-label">Total Requests</div>
                <div class="metric-value">{stats['total_requests']}</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Tabs for different sections
    tab1, tab2 = st.tabs(["📋 All Leave Requests", "👥 Employee Overview"])
    
    with tab1:
        st.markdown("## Manage Leave Requests")
        
        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            status_filter = st.selectbox("Filter by Status", ["All", "Pending", "Approved", "Rejected"])
        
        leaves_df = get_all_leaves()
        
        if status_filter != "All":
            leaves_df = leaves_df[leaves_df['status'] == status_filter]
        
        if not leaves_df.empty:
            for idx, row in leaves_df.iterrows():
                with st.expander(f"🗓️ {row['name']} - {row['leave_type']} ({row['start_date']} to {row['end_date']})"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"**Employee:** {row['name']}")
                        st.write(f"**Department:** {row['department']}")
                        st.write(f"**Leave Type:** {row['leave_type']}")
                    
                    with col2:
                        st.write(f"**Start Date:** {row['start_date']}")
                        st.write(f"**End Date:** {row['end_date']}")
                        st.write(f"**Days:** {row['days']}")
                    
                    with col3:
                        st.write(f"**Status:** {row['status']}")
                        st.write(f"**Applied:** {row['applied_date']}")
                    
                    st.write(f"**Reason:** {row['reason']}")
                    
                    if row['status'] == 'Pending':
                        col_a, col_b, col_c = st.columns([1, 1, 2])
                        with col_a:
                            if st.button("✅ Approve", key=f"approve_{row['id']}"):
                                update_leave_status(row['id'], 'Approved', st.session_state.user_id)
                                st.success("Leave approved!")
                                st.rerun()
                        with col_b:
                            if st.button("❌ Reject", key=f"reject_{row['id']}"):
                                update_leave_status(row['id'], 'Rejected', st.session_state.user_id)
                                st.error("Leave rejected!")
                                st.rerun()
        else:
            st.info("No leave requests found.")
    
    with tab2:
        st.markdown("## Employee Overview")
        
        conn = sqlite3.connect('leave_management.db')
        employees_df = pd.read_sql_query(
            "SELECT emp_id, name, email, department, position, total_leaves, used_leaves FROM employees WHERE emp_id != 'ADMIN'",
            conn)
        conn.close()
        
        if not employees_df.empty:
            employees_df['available_leaves'] = employees_df['total_leaves'] - employees_df['used_leaves']
            employees_df.columns = ['Employee ID', 'Name', 'Email', 'Department', 'Position', 'Total Leaves', 'Used Leaves', 'Available Leaves']
            st.dataframe(employees_df, use_container_width=True, hide_index=True)
        else:
            st.info("No employees found.")

# Main app logic
def main():
    if not st.session_state.logged_in:
        login_page()
    else:
        # Sidebar
        with st.sidebar:
            st.markdown(f"### 👤 {st.session_state.user_name}")
            st.markdown(f"**ID:** {st.session_state.user_id}")
            st.markdown("---")
            
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.user_id = None
                st.session_state.user_name = None
                st.session_state.is_admin = False
                st.rerun()
        
        # Show appropriate dashboard
        if st.session_state.is_admin:
            admin_dashboard()
        else:
            employee_dashboard()

if __name__ == "__main__":
    main()
