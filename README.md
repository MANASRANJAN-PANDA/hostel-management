# HostelPulse - Professional College Hostel Management System

A production-grade, full-stack **Hostel Management System** built with **Django 5.2**, **MySQL 8.0**, **HTML5**, **CSS3**, **Vanilla JavaScript**, and **Bootstrap 5**.

Designed with a modern SaaS admin dashboard aesthetic (Navy `#0F172A`, Royal Blue `#2563EB`, and Slate `#F8FAFC`), this system provides complete digital management of residential hostel operations across three distinct roles: **Super Admin**, **Hostel Warden**, and **Student**.

---

## 🌟 Core Modules & Features

### 1. Role-Based Authentication & Approval Workflow
- **Multi-Role Access Control**: Super Admin, Hostel Warden, and Student with dedicated dashboards and URL permissions.
- **Student Registration & Approval Workflow**: Students register online; registration stays in a `PENDING_APPROVAL` queue until verified by the Warden or Super Admin.
- **Credential Security**: Email or username login, "Remember Me" session duration management, show/hide password toggles, and password hashing with PBKDF2/SHA256.
- **IDOR Protection**: Strict permission checks prevent cross-account data access by altering IDs in URLs.

### 2. Super Admin Dashboard
- **Real-Time Database KPIs**: Total Students, Active Residents, Total Rooms, Occupied Beds, Available Beds, Total Wardens, Pending Fee Balances, All-Time Fee Collections, and Pending Complaints.
- **Interactive Visualizations (Chart.js)**:
  - 6-Month Monthly Fee Collection Bar Chart.
  - Bed Occupancy & Capacity Doughnut Ratio.
- **Live Activity Streams**: Recent student registrations, pending complaints, and recent payment receipts.

### 3. Student Management
- Complete profile directory with search (by Name, Reg No, Roll No, Email, Phone).
- Filter by Course, Department, Academic Year, and Hostel Building.
- Manage profile pictures, permanent addresses, guardian details, and emergency contacts.
- Approve or reject pending student registrations with one click.
- Comprehensive student profile page displaying allocated room, roommates, fee ledger, and attendance stats.

### 4. Warden Management
- Add, update, and manage hostel wardens.
- Assign wardens to specific hostel buildings (e.g. Boys Hostel vs Girls Hostel).
- One-click account activation / deactivation toggle.

### 5. Hostel & Room Management
- Multi-hostel building support with gender policies (Boys, Girls, Co-ed).
- Multi-floor mapping per building.
- Room sharing types: Single Sharing (1), Double Sharing (2), Triple Sharing (3), and Four Sharing (4).
- Automatic bed occupancy and status tracking (`AVAILABLE`, `PARTIALLY_OCCUPIED`, `FULL`, `MAINTENANCE`).
- Over-allocation prevention (capacity cannot be exceeded).

### 6. Room Allocation System
- Assign rooms to approved students with capacity checks.
- Prevent duplicate active allocations (students cannot hold two active beds simultaneously).
- Atomic room transfer between buildings or rooms with transfer history notes.
- Room checkout and clearance vacating workflow.

### 7. Fee Management System
- Configure tariff categories: Hostel Room Rent, Mess Charges, Electricity, Maintenance, and Others.
- Individual student invoicing and **Batch Fee Generation** across entire hostels or active students.
- Record payments with support for **UPI**, **Cash**, **Bank Transfer**, and **Other**.
- Auto-calculated remaining balances and payment statuses (`PAID`, `PARTIALLY_PAID`, `PENDING`, `OVERDUE`).
- Printable payment receipts with unique receipt numbers (`RCP-YYYYMM-XXXXXX`), college letterhead, student details, and authorized signature blocks.

### 8. Complaint Management System
- Students can submit maintenance tickets with optional photo uploads across categories: Room Issues, Electricity, Water Supply, Cleaning, Food/Mess, Internet/Wi-Fi, Security, and Other.
- Wardens can update status (`Submitted`, `Under Review`, `In Progress`, `Resolved`, `Rejected`), assign technicians, and record resolution notes.
- Complete audit history trail (`ComplaintHistory`) for each ticket.

### 9. Attendance Management System
- Daily roll call with fast batch sheet (Mark All Present / Mark All Absent controls).
- Individual student attendance tracking.
- Unique date constraint prevents duplicate roll records for the same student on the same day.
- Monthly attendance calendars and percentage compliance tracking on student dashboards.

### 10. Notice Management System
- Broadcast official bulletins and circulars with target audience controls (`All Users`, `Students Only`, `Wardens Only`).
- Publication and expiry dates with downloadable PDF/document attachments.
- Public notice board view for residents.

### 11. Visitor Management System
- Log visitor entries: visitor name, phone, address, visited student, relation, purpose, ID proof type & number.
- One-click checkout timestamping for visitor gate departure.
- Live tracker for visitors currently inside campus.

### 12. Reports & Analytics
- 7 Comprehensive Institutional Reports:
  1. Student Enrolment Report
  2. Facility Room Occupancy Audit
  3. Fee Collections Statement
  4. Outstanding Dues & Defaulters Report
  5. Complaints Resolution & Maintenance Audit
  6. Institutional Attendance Statement
  7. Visitor Gate Pass Report
- Date range filtering, search, print-ready CSS views, and **one-click CSV data exports** for all reports.

---

## 🗄️ Database Architecture & Tech Stack

- **Backend**: Python 3.13 / 3.14, Django 5.2 (Django ORM, Transactions, Custom User Model)
- **Database**: MySQL 8.0 (configured via PyMySQL driver)
- **Frontend**: HTML5, CSS3 Variables, Vanilla JS, Bootstrap 5, Font Awesome 6, Chart.js

---

## 🚀 Installation & Setup Guide

### 1. Prerequisites
- Python 3.10+ (Python 3.13 recommended)
- MySQL Server 8.0+ running on `localhost:3306`

### 2. MySQL Database Setup
Open MySQL command prompt or MySQL Workbench:
```sql
CREATE DATABASE IF NOT EXISTS hostel_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 3. Environment Configuration
Check or edit the `.env` file in the project root:
```env
SECRET_KEY=django-insecure-hostel-mgmt-system-secret-key-prod-2026-v1
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,*

DB_ENGINE=mysql
DB_NAME=hostel_db
DB_USER=root
DB_PASSWORD=root
DB_HOST=127.0.0.1
DB_PORT=3306
```

### 4. Virtual Environment & Dependencies
In terminal / PowerShell inside the project directory:
```powershell
# Create virtual environment (if not already created)
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install required dependencies
pip install -r requirements.txt
```

### 5. Apply Database Migrations
```powershell
python manage.py migrate
```

### 6. Populate Realistic Demonstration Data
To populate the database with hostels, rooms, wardens, students, fee records, attendance logs, and notices:
```powershell
python manage.py seed_data
```

### 7. Run the Application
```powershell
python manage.py runserver
```
Open your browser and navigate to: **`http://127.0.0.1:8000/`**

---

## 🔑 Default Demonstration Accounts

All accounts below are pre-seeded in the database:

| Role | Username | Password | Notes |
|---|---|---|---|
| **Super Admin** | `admin` | `AdminPassword123!` | Access to all management modules, analytics & settings |
| **Hostel Warden** | `warden1` | `WardenPassword123!` | Assigned to Aryabhata Boys Hostel (BH-1) |
| **Hostel Warden** | `warden2` | `WardenPassword123!` | Assigned to Sarojini Naidu Girls Hostel (GH-1) |
| **Student (Active)** | `student1` | `StudentPassword123!` | Room 101, B.Tech CSE, Reg: `REG-2026-001` |
| **Student (Active)** | `student2` | `StudentPassword123!` | Room 101 (Roommate with student1), Reg: `REG-2026-002` |
| **Student (Active)** | `student3` | `StudentPassword123!` | Room 101 (GH-1), B.Tech ECE, Reg: `REG-2026-003` |
| **Student (Pending)** | `student_pending` | `StudentPassword123!` | Demonstrates the "Awaiting Admin Approval" workflow |

---

## 🧪 Running Automated Unit Tests
To run the automated test suite verifying room allocations, capacity enforcement, fee calculations, and permissions:
```powershell
python manage.py test accounts
```

---

## 📁 Project Structure

```
HOSTEL/
├── manage.py
├── requirements.txt
├── .env
├── .env.example
├── README.md
├── config/
│   ├── __init__.py        (PyMySQL initialization)
│   ├── settings.py        (MySQL settings, auth, static/media, context processors)
│   ├── urls.py            (Root URL dispatcher)
│   ├── wsgi.py
│   └── asgi.py
├── accounts/              (Custom User model, auth views, dashboards, seed command)
├── students/              (StudentProfile, directory, profiles, approval views)
├── wardens/               (WardenProfile, hostel building assignment)
├── hostels/               (Hostel buildings and floor configurations)
├── rooms/                 (Rooms, types, capacities, dynamic floor loading)
├── allocations/           (Room allocation, transfer, vacate workflows)
├── fees/                  (FeeCategory, FeeRecord, Payment, receipts)
├── complaints/            (Complaint tickets, category handling, audit history)
├── attendance/            (Daily attendance, batch mark sheet roll call)
├── notices/               (Public bulletins, target audiences, attachments)
├── visitors/              (Visitor registry, gate pass check-in/out)
├── reports/               (7 Institutional reports, print views, CSV export)
├── templates/
│   ├── base/              (Base layout, typography, Bootstrap & Chart.js)
│   ├── components/        (Sidebar, top navbar, alerts, pagination)
│   ├── authentication/    (Login, registration, pending approval, password change)
│   ├── admin/             (Admin dashboard, students, wardens, hostels, rooms, fees, etc.)
│   ├── warden/            (Warden dashboard)
│   ├── student/           (Student dashboard, my room, my fees, complaints, attendance)
│   └── reports/           (Tabular reports with print & CSV export)
├── static/
│   ├── css/style.css      (Custom design system)
│   └── js/main.js         (Mobile sidebar toggle, password visibility, dynamic filters)
└── media/                 (User profile photos, attachments)
```
