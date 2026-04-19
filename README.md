# 🏋️ Gym Management System

A full-featured gym management tool built with Django & Python, styled to match your custom homepage design.

---

## ✅ Features

| Module | What it does |
|---|---|
| **Public Website** | Your custom homepage with gym info |
| **Dashboard** | Overview: members, check-ins, revenue, alerts |
| **Members** | Add/edit/delete members with photo, plan, expiry |
| **Attendance** | Quick check-in, daily log, browse by date |
| **Payments** | Record & track payments, monthly revenue |
| **Plans** | Create membership plans (Monthly/Quarterly/Annual) |
| **Settings** | Update gym name, owner, contact — reflects on website |

---

## 🚀 Quick Start

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
pip install python-dateutil
```

### 2. Run setup (creates DB + admin user + default plans)

```bash
python setup.py
```

### 3. Start the server

```bash
python manage.py runserver
```

### 4. Open in browser

| Page | URL |
|---|---|
| Public Website | http://127.0.0.1:8000/ |
| Admin Panel | http://127.0.0.1:8000/admin-panel/ |
| Login | http://127.0.0.1:8000/admin-panel/login/ |

---

## 📁 Project Structure

```
gymmanager/
├── manage.py
├── setup.py              ← Run this first!
├── requirements.txt
├── db.sqlite3            ← Created after setup
├── gymmanager/
│   ├── settings.py
│   └── urls.py
├── gym/
│   ├── models.py         ← Member, Plan, Attendance, Payment
│   ├── views.py          ← All page logic
│   ├── urls.py           ← URL routes
│   ├── forms.py          ← Form definitions
│   └── templates/gym/
│       ├── home.html     ← Your custom public homepage
│       ├── login.html
│       ├── base_admin.html
│       ├── dashboard.html
│       ├── members/
│       ├── attendance/
│       ├── payments/
│       ├── plans/
│       └── settings.html
└── media/                ← Member photos (auto-created)
```

---

## 🔐 Default Login

- **Username:** admin
- **Password:** admin123

> Change your password after first login via Django admin at `/django-admin/`

---

## 💡 Tips

- The **public homepage** auto-populates from your Gym Settings (name, phone, email, owner)
- Membership **plan end date is auto-calculated** from the plan's duration when adding a member
- Members expiring within 7 days appear as **alerts on the dashboard**
- Members who haven't visited in a week show up as **inactive alerts**
