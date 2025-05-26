
# 🏛️ oCEO Management System – IIT Gandhinagar

A full-stack web application that manages **On-Campus Employment Opportunities (oCEO)** at **IIT Gandhinagar**. It streamlines job creation, application, and timecard approvals, catering to various user roles including students, faculty, and administrators.

---

## 📌 Description

This portal enables:
- Faculty to float and manage jobs
- Students to apply, log work, and track payment statuses
- Administrative roles (Dean, SA_JS, oCEO Coordinator, Admin) to monitor and manage workflow and approvals

---

## 🖥️ Frontend

- Built using **Flask templates (Jinja2)**, **HTML/CSS**, **Flexbox**, and **Bootstrap**.
- Clean, responsive UI tailored to each user role.
- Integrated with **Google OAuth** to restrict access to IITGN users only.

---

## 🧠 Backend

- Developed using **Flask (Python)** and **MySQL**.
- Implements role-based routing and privilege-based views.
- Handles concurrent multi-user updates with **SQL table locking** for critical tables.
- Secured against common web vulnerabilities like **SQL Injection**, **XSS**, and **URL Tampering**.
- Dynamically renders different views for:
  - 👤 Students
  - 👨‍🏫 Faculty
  - 🧑‍💼 oCEO Coordinator, Dean SA, SA_JS, Admin

### 🔄 Functional Highlights

#### 👤 Student
- View & edit personal profile
- Browse and apply for jobs
- Submit and view timecards
- Track application status and mentees (PAL job)

#### 👨‍🏫 Faculty
- Create/delete jobs
- Approve/reject student applications & timecards
- View employed students
- Stop application intake

#### 🧑‍💼 Admin Roles
- **oCEO Coordinator**: Approve timecards
- **SA_JS**: Approve payments and view bank details
- **Dean SA & Admin**: Review applications, assign coordinator email

---

## ⚙️ Getting Started

### 1. 🗃️ Database Setup

Import the final MySQL schema:

```bash
# Using MySQL Workbench or CLI:
# Server > Data Import > Import from Self-Contained File
oCEO_v6.sql
```

### 2. 🚀 Run the Application

```bash
cd main_project
python main_app.py
```

### 3. 👥 Test Users

To login as administrative users, use the following credentials:

| Role               | Email                    | Password |
|--------------------|--------------------------|----------|
| Dean SA            | dean@iitgn.ac.in         | admin    |
| SA JS              | sa_js@iitgn.ac.in        | admin    |
| oCEO Coordinator   | joycee@iitgn.ac.in       | admin    |
| Admin              | admin@iitgn.ac.in        | admin    |

⚠️ Make sure to select the **correct user type**. Selecting the wrong type will lead to a **"Bad Credentials"** error.

---

## 🛡️ Security Measures

- ✅ SQL Injection defense using safe query handling and prepared statements.
- ✅ XSS defense via escaping HTML characters.
- ✅ URL tampering protection via access-level validation on each route.

---

## 🛠️ Tech Stack

- **Backend**: Python, Flask
- **Database**: MySQL
- **Frontend**: HTML, CSS, Bootstrap, Jinja2
- **Authentication**: Google OAuth 2.0
- **Security**: SQL Locking, Role Validation, Input Sanitization

---

## 👨‍👩‍👧‍👦 Contributors

Developed by **Group - DataWeavers** under **CS432: Databases (AY 2023-24)**  
Indian Institute of Technology Gandhinagar

---

## 📃 License

This project is for academic purposes. Use with attribution.
