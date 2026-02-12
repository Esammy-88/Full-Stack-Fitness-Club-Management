# 🏋️ Full-Stack Fitness Club Management System

A comprehensive web-based fitness club management platform built with **Python Flask** and **PostgreSQL**, deployed live on Render. This full-stack application covers member self-service, trainer scheduling, and admin operations — all in one unified system.

🔗 **Live Demo:** [full-stack-fitness-club-management.onrender.com](https://full-stack-fitness-club-management.onrender.com)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Database Design](#database-design)
- [User Roles](#user-roles)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [Deploying to Render](#deploying-to-render)
- [Demo Credentials](#demo-credentials)
- [Screenshots](#screenshots)

---

## Overview

This platform simulates a real-world fitness club management system with three distinct user portals — **Members**, **Trainers**, and **Admins** — each with tailored dashboards and functionality. Built as a full-stack project, it demonstrates end-to-end software development: relational database design, server-side routing, session-based authentication, and a responsive front-end.

---

## Features

### 👤 Member Portal
- Register and log in securely
- View personal dashboard with health stats, upcoming sessions, and class registrations
- Track health metrics (weight, heart rate, blood pressure, body fat)
- Set and monitor fitness goals
- Book personal training sessions with available trainers
- Browse and register for group fitness classes

### 🏃 Trainer Portal
- Log in and view full weekly schedule
- See upcoming personal training sessions and group classes
- Set and manage availability by day and time slot
- View assigned member profiles, health metrics, and active goals

### 🛠️ Admin Portal
- Dashboard with system-wide stats: total members, trainers, upcoming classes, pending revenue
- Room management — view all rooms and capacities
- Equipment management — update maintenance status and notes
- Billing — generate bills for members and record payments

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3, Flask |
| Database | PostgreSQL (via Render Managed Postgres) |
| DB Driver | psycopg3 (`psycopg`) |
| Connection Pooling | `psycopg_pool.ConnectionPool` |
| Password Security | `werkzeug.security` (PBKDF2 hashing) |
| Templating | Jinja2 |
| Frontend | HTML5, CSS3, Jinja2 templates |
| Deployment | Render (Web Service + PostgreSQL) |

---

## Project Structure

```
Full-Stack-Fitness-Club-Management/
│
├── app.py                  # Main Flask application — all routes and DB logic
├── requirements.txt        # Python dependencies
├── runtime.txt             # Python version for Render
│
├── sql/
│   ├── ddl.sql             # Database schema (CREATE TABLE statements)
│   ├── dml.sql             # Seed data (INSERT statements for demo users)
│   └── views.sql           # SQL views (e.g. MemberDashboard)
│
├── static/
│   └── css/
│       └── style.css       # Global styles
│
└── templates/
    ├── index.html          # Landing page
    ├── about.html          # About page
    ├── member/
    │   ├── login.html
    │   ├── register.html
    │   ├── dashboard.html
    │   ├── profile.html
    │   ├── classes.html
    │   └── schedule_training.html
    ├── trainer/
    │   ├── login.html
    │   ├── schedule.html
    │   ├── availability.html
    │   ├── members.html
    │   └── member_detail.html
    ├── admin/
    │   ├── login.html
    │   ├── dashboard.html
    │   ├── rooms.html
    │   ├── equipment.html
    │   └── billing.html
    └── errors/
        ├── 404.html
        └── 500.html
```

---

## Database Design

The PostgreSQL schema includes the following core tables:

| Table | Description |
|---|---|
| `Member` | Registered gym members |
| `Trainer` | Fitness trainers |
| `AdminStaff` | Admin users |
| `TrainerAvailability` | Weekly availability slots per trainer |
| `PersonalTrainingSession` | Booked 1-on-1 sessions |
| `Class` | Scheduled group fitness classes |
| `ClassRegistration` | Member enrolments in classes |
| `Room` | Club rooms (Personal Training, Group Fitness, etc.) |
| `Equipment` | Equipment inventory with maintenance tracking |
| `HealthMetric` | Member health measurements over time |
| `FitnessGoal` | Member fitness goals with progress tracking |
| `Bill` | Member billing records |
| `Payment` | Payment transactions against bills |

A `MemberDashboard` **view** aggregates the most important stats (latest weight, heart rate, active goals, upcoming sessions, pending balance) into a single query used by the member dashboard route.

---

## User Roles

The app uses Flask `session`-based authentication with a `login_required(user_type)` decorator that enforces role separation across all routes.

| Role | Login URL | Default Redirect |
|---|---|---|
| Member | `/member/login` | `/member/dashboard` |
| Trainer | `/trainer/login` | `/trainer/schedule` |
| Admin | `/admin/login` | `/admin/dashboard` |

Password storage uses **werkzeug's PBKDF2 hashing** (`generate_password_hash` / `check_password_hash`). A `verify_password()` helper also supports a plain-text fallback for legacy DML seed users, ensuring demo credentials always work.

---

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- `pip`

### Local Setup

**1. Clone the repository**
```bash
git clone https://github.com/Esammy-88/Full-Stack-Fitness-Club-Management.git
cd Full-Stack-Fitness-Club-Management
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Set up the database**

Create a local PostgreSQL database, then run the SQL files in order:
```bash
psql -U postgres -d fitness_club -f sql/ddl.sql
psql -U postgres -d fitness_club -f sql/dml.sql
```

**4. Set environment variables**
```bash
export DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/fitness_club
export SECRET_KEY=your-secret-key
```

**5. Run the app**
```bash
python app.py
```

Visit `http://localhost:5000`

---

## Environment Variables

| Variable | Description | Required |
|---|---|---|
| `DATABASE_URL` | Full PostgreSQL connection string | ✅ Yes |
| `SECRET_KEY` | Flask session secret key | ✅ Yes |
| `DB_HOST` | DB host (fallback if no DATABASE_URL) | Optional |
| `DB_NAME` | DB name (fallback) | Optional |
| `DB_USER` | DB user (fallback) | Optional |
| `DB_PASSWORD` | DB password (fallback) | Optional |
| `DB_PORT` | DB port, default `5432` (fallback) | Optional |

> **Note:** The app automatically appends `sslmode=require` to `DATABASE_URL` when deploying on Render — no manual changes needed.

---

## Deploying to Render

1. Create a **PostgreSQL** database on Render and copy the **Internal Database URL**
2. Create a **Web Service** connected to this repository
3. Set the following environment variables in Render → Environment:
   - `DATABASE_URL` → your Render Postgres internal URL
   - `SECRET_KEY` → any strong random string
4. Set the **Start Command** to:
   ```
   gunicorn app:app
   ```
5. Ensure `gunicorn` is in `requirements.txt`
6. Deploy — Render will automatically install dependencies and start the server

---

## Demo Credentials

Use these to explore the live app without registering:

| Role | Email | Password |
|---|---|---|
| Member | `john.doe@email.com` | `pass123` |
| Trainer | `alex.trainer@fitness.com` | `trainer123` |
| Admin | `admin@fitness.com` | `admin123` |

> Seed data is loaded from `sql/dml.sql`. All demo users are pre-inserted with these credentials.

---

## Languages

![Python](https://img.shields.io/badge/Python-29.9%25-3776AB?style=flat-square&logo=python&logoColor=white)
![HTML](https://img.shields.io/badge/HTML-56.5%25-E34F26?style=flat-square&logo=html5&logoColor=white)
![PLpgSQL](https://img.shields.io/badge/PLpgSQL-8.2%25-336791?style=flat-square&logo=postgresql&logoColor=white)
![CSS](https://img.shields.io/badge/CSS-5.4%25-1572B6?style=flat-square&logo=css3&logoColor=white)

---

## Author

**Esammy-88** — [github.com/Esammy-88](https://github.com/Esammy-88)

