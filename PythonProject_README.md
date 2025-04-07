


---

# Hospital Management System (HMS)

A web-based Hospital Management System built using Flask to manage patients, doctors, medications, diagnostic tests, and hospital resources efficiently.

## Features

- **Admin Dashboard**: Manage patients, assign doctors, and allocate beds.
- **Doctor Dashboard**: Prescribe medications, add medical notes, and order diagnostic tests.
- **Pharmacy Dashboard**: View prescribed medications and mark them as dispensed.
- **Diagnostic Dashboard**: Manage diagnostic tests and update test results.
- **Role-Based Access Control**: Separate dashboards for Admins, Doctors, Pharmacy staff, and Diagnostic staff.

---

## Prerequisites

Before you begin, ensure you have the following installed on your system:

- Python 3.8 or higher
- pip (Python package manager)
- Git (optional, for cloning the repository)

---

## Installation Steps

### Step 1: Clone the project repository or download the zip file

Clone the project repository from GitHub (or download it as a ZIP file):

```bash
git clone https://github.com/yourusername/hospital-management-system.git
cd hospital-management-system
```


### Step 2: Create a Virtual Environment

Set up a virtual environment to isolate project dependencies:

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```


### Step 3: Install Dependencies

Install all required Python packages using `pip`:

```bash
pip install -r requirements.txt
```


### Step 4: Set Up the Database

Initialize the database by creating tables and adding default data:

```bash
python
&gt;&gt;&gt; from app import db, app
&gt;&gt;&gt; with app.app_context():
...     db.create_all()
...
```


### Step 5: Run the Application

Start the Flask development server:

```bash
python run.py
```

The application will be accessible at:

```
http://127.0.0.1:5000/
```

---

## Usage

### Default Admin Credentials:

- **Username**: `admin`
- **Password**: `admin123`


### User Roles:

1. **Admin**: Full access to manage patients, doctors, beds, and resources.
2. **Doctor**: Can view assigned patients, prescribe medications, add medical notes, and order diagnostic tests.
3. **Pharmacy Staff**: Can view prescribed medications and mark them as dispensed.
4. **Diagnostic Staff**: Can view ordered tests and update test results.

---

## Project Structure

```
hospital-management-system/
├── app.py                  # Main application file with routes and logic
├── models.py               # Database models for Patients, Doctors, Medications, etc.
├── run.py                  # Entry point to start the Flask app
├── requirements.txt        # Python dependencies for the project
├── static/                 # Static files (CSS, JS, images)
│   ├── css/
│   ├── js/
│   └── img/
└── templates/              # HTML templates for rendering pages
    ├── admin/
    ├── doctor/
    ├── pharmacy/
    ├── diagnostic/
    └── base.html           # Base layout template for all pages
```

---

## Troubleshooting

1. **Database Errors**:
    - If you encounter errors related to missing tables or columns:

```bash
python run.py  # Ensure database tables are created automatically on startup.
```

2. **Dependencies Not Installed**:
    - Ensure all dependencies in `requirements.txt` are installed:

```bash
pip install -r requirements.txt
```

3. **Permission Denied Errors**:
    - Ensure your user has write permissions to the project directory.
4. **Virtual Environment Issues**:
    - If commands like `flask` or `python` don't work as expected, ensure your virtual environment is activated.

---

## Future Enhancements

1. Add billing and payment management functionality.
2. Implement appointment scheduling with email/SMS notifications.
3. Create analytics dashboards for hospital administrators.

---

## Contributors

- **Daivik (Member 1)**: Medicines Dashboard and Bed Management (Backend \& Frontend Development)
- **Shourya (Member 2)**: Doctor Dashboard (Backend \& Frontend Development)
- **Lakshmi (Member 3)**: Admin Dashboard \& Diagnostic Dashboard (Backend \& Frontend Integration)

---


