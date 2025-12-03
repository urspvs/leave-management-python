# leave-management-python
Leave tracking app using Python, Streamlit, SQLite
[README.md](https://github.com/user-attachments/files/23913122/README.md)
# ACME Leave Management System 🏢

A comprehensive web-based leave management application built with Python, Streamlit, and SQLite for the ACME organization.

## Features ✨

### For Employees:
- **Dashboard**: View leave statistics (Total, Used, Available leaves)
- **Apply Leave**: Submit leave requests with different leave types
- **Track Leaves**: View history of all leave requests with filtering options
- **Leave Types**: Casual Leave, Sick Leave, Annual Leave, Maternity Leave, Paternity Leave

### For Managers:
- All employee features plus:
- **Approve/Reject Leaves**: Review and manage pending leave requests
- **View All Requests**: See leave requests from all employees

## Technology Stack 🛠️

- **Frontend**: Streamlit (Python web framework)
- **Backend**: SQLite database
- **Authentication**: SHA256 password hashing
- **Data Management**: Pandas for data manipulation

## Installation 📦

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
streamlit run leave_management.py
```

3. Open your browser and navigate to:
```
http://localhost:8502
```

## Demo Credentials 🔑

### Employee Account:
- **Email**: john.doe@acme.com
- **Password**: password123

### Manager Account:
- **Email**: jane.smith@acme.com
- **Password**: password123

### Other Test Accounts:
- bob.johnson@acme.com / password123 (HR Employee)
- alice.williams@acme.com / password123 (Marketing Employee)
- charlie.brown@acme.com / password123 (Sales Manager)
- diana.prince@acme.com / password123 (Engineering Employee)
- eve.davis@acme.com / password123 (HR Manager)

## Database Schema 📊

### Employees Table:
- emp_id (Primary Key)
- name
- email (Unique)
- password (Hashed)
- department
- role
- total_leaves
- used_leaves

### Leave Requests Table:
- request_id (Primary Key, Auto-increment)
- emp_id (Foreign Key)
- leave_type
- start_date
- end_date
- days
- reason
- status (Pending/Approved/Rejected)
- applied_date
- approved_by
- approved_date

## Sample Data 📝

The application comes pre-populated with:
- 7 sample employees across different departments (Engineering, HR, Marketing, Sales)
- 6 sample leave requests with various statuses
- Each employee has 20 total leaves per year

## Features in Detail 🔍

### Leave Application:
- Date validation (end date must be after start date)
- Leave balance checking
- Automatic calculation of leave days
- Reason requirement for all leave requests

### Leave Tracking:
- Filter by status (Pending, Approved, Rejected)
- Filter by leave type
- View complete leave history
- Real-time status updates

### Manager Approval:
- View all pending requests
- Quick approve/reject actions
- Automatic leave balance updates on approval
- Track approval history

### Dashboard:
- Visual statistics with gradient cards
- Recent leave requests overview
- Leave balance at a glance

## Security 🔒

- Password hashing using SHA256
- Session-based authentication
- Role-based access control (Employee vs Manager)

## Usage Tips 💡

1. **Applying for Leave**: 
   - Navigate to "Apply Leave" tab
   - Select leave type and dates
   - Provide a reason
   - Submit the request

2. **Tracking Leaves**:
   - Go to "My Leaves" tab
   - Use filters to find specific requests
   - Check status of pending requests

3. **Approving Leaves (Managers)**:
   - Switch to "Approve Leaves" tab
   - Review pending requests
   - Click ✅ to approve or ❌ to reject

## File Structure 📁

```
.
├── leave_management.py    # Main application file
├── requirements.txt       # Python dependencies
├── leave_management.db    # SQLite database (auto-created)
└── README.md             # This file
```

## Future Enhancements 🚀

Potential features for future versions:
- Email notifications for leave status updates
- Leave calendar view
- Export leave reports to PDF/Excel
- Leave carry-forward functionality
- Holiday calendar integration
- Multi-level approval workflow
- Leave cancellation feature
- Department-wise leave analytics

## Support 📧

For any issues or questions, please contact the ACME IT department.

---

**Built with ❤️ using Python & Streamlit**
