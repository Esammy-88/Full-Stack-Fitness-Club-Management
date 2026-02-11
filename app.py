"""
Health and Fitness Club Management System - Flask Web Application
A comprehensive web-based fitness club management platform
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps
import psycopg
from psycopg import pool
from datetime import datetime, date, time
import os
from psycopg_pool import ConnectionPool


app = Flask(__name__)
app.secret_key = os.environ.get(
    'SECRET_KEY', 'dev-secret-key-change-in-production'
)

init_db_pool()


# Database connection pool
connection_pool = None


def init_db_pool():
    """Initialize database connection pool"""
    global connection_pool

    database_url = os.environ.get("DATABASE_URL")

    try:
        if database_url:
            connection_pool = psycopg2.pool.SimpleConnectionPool(
                1, 20,
                dsn=database_url
            )
        else:
            connection_pool = psycopg2.pool.SimpleConnectionPool(
                1, 20,
                host=os.environ.get("DB_HOST", "localhost"),
                database=os.environ.get("DB_NAME", "fitness_club"),
                user=os.environ.get("DB_USER", "postgres"),
                password=os.environ.get("DB_PASSWORD"),
                port=os.environ.get("DB_PORT", "5432")
            )

        print("✓ Database connection pool initialized")

    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        raise


def get_db_connection():
    """Get connection from pool"""
    return connection_pool.getconn()


def return_db_connection(conn):
    """Return connection to pool"""
    connection_pool.putconn(conn)

# Decorators for authentication


def login_required(user_type):
    """Decorator to require login for specific user types"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session or session.get('user_type') != user_type:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ============================================================================
# MAIN ROUTES
# ============================================================================


@app.route('/')
def index():
    """Landing page"""
    return render_template('index.html')


@app.route('/about')
def about():
    """About the developer"""
    return render_template('about.html')

# ============================================================================
# MEMBER ROUTES
# ============================================================================


@app.route('/member/register', methods=['GET', 'POST'])
def member_register():
    """Member registration"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        dob = request.form.get('date_of_birth')
        gender = request.form.get('gender')
        phone = request.form.get('phone')
        address = request.form.get('address')

        conn = get_db_connection()
        try:
            cursor = conn.cursor()

            # Check if email exists
            cursor.execute(
                "SELECT email FROM Member WHERE email = %s", (email,))
            if cursor.fetchone():
                flash('Email already registered!', 'danger')
                return redirect(url_for('member_register'))

            # Insert new member
            cursor.execute("""
                INSERT INTO Member (email, password, first_name, last_name, date_of_birth, 
                                   gender, phone, address)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING member_id
            """, (email, password, first_name, last_name, dob, gender, phone, address))

            member_id = cursor.fetchone()[0]
            conn.commit()

            flash(f"Registration successful! Welcome, {first_name}!", 'success')
            return redirect(url_for('member_login'))
        
        except Exception as e:
            conn.rollback()
            flash(f'Error: {str(e)}', 'danger')
        finally:
            cursor.close()
            return_db_connection(conn)

    return render_template('member/register.html')


@app.route('/member/login', methods=['GET', 'POST'])
def member_login():
    """Member login"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT member_id, first_name, last_name
                FROM Member
                WHERE email = %s AND password = %s
            """, (email, password))

            user = cursor.fetchone()
            if user:
                session['user_id'] = user[0]
                session['user_type'] = 'member'
                session['user_name'] = f"{user[1]} {user[2]}"
                flash(f'Welcome back, {user[1]}!', 'success')
                return redirect(url_for('member_dashboard'))
            else:
                flash('Invalid credentials!', 'danger')
        finally:
            cursor.close()
            return_db_connection(conn)

    return render_template('member/login.html')


@app.route('/member/dashboard')
@login_required('member')
def member_dashboard():
    """Member dashboard"""
    member_id = session['user_id']
    conn = get_db_connection()

    try:
        cursor = conn.cursor()

        # Get dashboard data
        cursor.execute("""
            SELECT first_name, last_name, email, latest_weight, latest_heart_rate,
                   last_metric_date, active_goals, upcoming_sessions, 
                   classes_attended, pending_balance
            FROM MemberDashboard
            WHERE member_id = %s
        """, (member_id,))

        dashboard_data = cursor.fetchone()

        # Get active goals
        cursor.execute("""
            SELECT goal_id, goal_type, current_value, target_value, target_date, status
            FROM FitnessGoal
            WHERE member_id = %s AND status = 'Active'
            ORDER BY target_date
        """, (member_id,))
        goals = cursor.fetchall()

        # Get upcoming sessions
        cursor.execute("""
            SELECT pts.session_id, pts.session_date, pts.start_time, pts.end_time,
                   t.first_name || ' ' || t.last_name as trainer_name,
                   r.room_name
            FROM PersonalTrainingSession pts
            JOIN Trainer t ON pts.trainer_id = t.trainer_id
            JOIN Room r ON pts.room_id = r.room_id
            WHERE pts.member_id = %s 
              AND pts.session_date >= CURRENT_DATE 
              AND pts.status = 'Scheduled'
            ORDER BY pts.session_date, pts.start_time
            LIMIT 5
        """, (member_id,))
        sessions = cursor.fetchall()

        # Get registered classes
        cursor.execute("""
            SELECT c.class_id, c.class_name, c.schedule_date, c.start_time, c.end_time,
                   t.first_name || ' ' || t.last_name as trainer_name,
                   cr.status
            FROM ClassRegistration cr
            JOIN Class c ON cr.class_id = c.class_id
            JOIN Trainer t ON c.trainer_id = t.trainer_id
            WHERE cr.member_id = %s 
              AND c.schedule_date >= CURRENT_DATE
              AND cr.status = 'Registered'
            ORDER BY c.schedule_date, c.start_time
        """, (member_id,))
        classes = cursor.fetchall()

        return render_template('member/dashboard.html',
                               dashboard=dashboard_data,
                               goals=goals,
                               sessions=sessions,
                               classes=classes)
    finally:
        cursor.close()
        return_db_connection(conn)


@app.route('/member/profile', methods=['GET', 'POST'])
@login_required('member')
def member_profile():
    """Member profile management"""
    member_id = session['user_id']

    if request.method == 'POST':
        action = request.form.get('action')
        conn = get_db_connection()

        try:
            cursor = conn.cursor()

            if action == 'update_info':
                phone = request.form.get('phone')
                address = request.form.get('address')

                cursor.execute("""
                    UPDATE Member 
                    SET phone = %s, address = %s 
                    WHERE member_id = %s
                """, (phone, address, member_id))
                conn.commit()
                flash('Profile updated successfully!', 'success')

            elif action == 'add_goal':
                goal_type = request.form.get('goal_type')
                target_value = request.form.get('target_value')
                current_value = request.form.get('current_value')
                target_date = request.form.get('target_date')

                cursor.execute("""
                    INSERT INTO FitnessGoal (member_id, goal_type, target_value, 
                                            current_value, target_date, status)
                    VALUES (%s, %s, %s, %s, %s, 'Active')
                """, (member_id, goal_type, target_value, current_value, target_date))
                conn.commit()
                flash('Fitness goal added!', 'success')

            elif action == 'add_metric':
                weight = request.form.get('weight')
                height = request.form.get('height')
                heart_rate = request.form.get('heart_rate')
                blood_pressure = request.form.get('blood_pressure')
                body_fat = request.form.get('body_fat')
                notes = request.form.get('notes')

                cursor.execute("""
                    INSERT INTO HealthMetric (member_id, weight, height, heart_rate, 
                                             blood_pressure, body_fat_percentage, notes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (member_id,
                      float(weight) if weight else None,
                      float(height) if height else None,
                      int(heart_rate) if heart_rate else None,
                      blood_pressure if blood_pressure else None,
                      float(body_fat) if body_fat else None,
                      notes if notes else None))
                conn.commit()
                flash('Health metric recorded!', 'success')

        except Exception as e:
            conn.rollback()
            flash(f'Error: {str(e)}', 'danger')
        finally:
            cursor.close()
            return_db_connection(conn)

        return redirect(url_for('member_profile'))

    # GET request - fetch profile data
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT email, first_name, last_name, date_of_birth, gender, phone, address
            FROM Member WHERE member_id = %s
        """, (member_id,))
        profile = cursor.fetchone()

        # Get health metrics history
        cursor.execute("""
            SELECT metric_id, recorded_date, weight, heart_rate, blood_pressure, 
                   body_fat_percentage, notes
            FROM HealthMetric
            WHERE member_id = %s
            ORDER BY recorded_date DESC
            LIMIT 10
        """, (member_id,))
        metrics = cursor.fetchall()

        # Get all goals
        cursor.execute("""
            SELECT goal_id, goal_type, current_value, target_value, target_date, status
            FROM FitnessGoal
            WHERE member_id = %s
            ORDER BY created_date DESC
        """, (member_id,))
        goals = cursor.fetchall()

        return render_template('member/profile.html',
                               profile=profile,
                               metrics=metrics,
                               goals=goals)
    finally:
        cursor.close()
        return_db_connection(conn)


@app.route('/member/schedule-training', methods=['GET', 'POST'])
@login_required('member')
def schedule_training():
    """Schedule personal training session"""
    member_id = session['user_id']

    if request.method == 'POST':
        trainer_id = request.form.get('trainer_id')
        session_date = request.form.get('session_date')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        notes = request.form.get('notes')

        conn = get_db_connection()
        try:
            cursor = conn.cursor()

            # Check trainer availability
            day_of_week = datetime.strptime(
                session_date, '%Y-%m-%d').strftime('%A')

            cursor.execute("""
                SELECT availability_id
                FROM TrainerAvailability
                WHERE trainer_id = %s 
                  AND day_of_week = %s
                  AND start_time <= %s
                  AND end_time >= %s
            """, (trainer_id, day_of_week, start_time, end_time))

            if not cursor.fetchone():
                flash('Trainer not available at this time!', 'danger')
                return redirect(url_for('schedule_training'))

            # Check for conflicts
            cursor.execute("""
                SELECT session_id FROM PersonalTrainingSession
                WHERE trainer_id = %s 
                  AND session_date = %s
                  AND status = 'Scheduled'
                  AND (
                      (start_time <= %s AND end_time > %s) OR
                      (start_time < %s AND end_time >= %s) OR
                      (start_time >= %s AND end_time <= %s)
                  )
            """, (trainer_id, session_date, start_time, start_time,
                  end_time, end_time, start_time, end_time))

            if cursor.fetchone():
                flash('Trainer already has a session at this time!', 'danger')
                return redirect(url_for('schedule_training'))

            # Find available room
            cursor.execute("""
                SELECT room_id FROM Room
                WHERE room_type = 'Personal Training'
                  AND room_id NOT IN (
                      SELECT room_id FROM PersonalTrainingSession
                      WHERE session_date = %s
                        AND status = 'Scheduled'
                        AND (
                            (start_time <= %s AND end_time > %s) OR
                            (start_time < %s AND end_time >= %s) OR
                            (start_time >= %s AND end_time <= %s)
                        )
                  )
                LIMIT 1
            """, (session_date, start_time, start_time, end_time, end_time,
                  start_time, end_time))

            room = cursor.fetchone()
            if not room:
                flash('No rooms available at this time!', 'danger')
                return redirect(url_for('schedule_training'))

            room_id = room[0]

            # Book the session
            cursor.execute("""
                INSERT INTO PersonalTrainingSession 
                    (member_id, trainer_id, room_id, session_date, start_time, end_time, status, notes)
                VALUES (%s, %s, %s, %s, %s, %s, 'Scheduled', %s)
                RETURNING session_id
            """, (member_id, trainer_id, room_id, session_date, start_time, end_time, notes))

            session_id = cursor.fetchone()[0]
            conn.commit()

            flash('Session booked successfully!', 'success')
            return redirect(url_for('member_dashboard'))

        except Exception as e:
            conn.rollback()
            flash(f'Error: {str(e)}', 'danger')
        finally:
            cursor.close()
            return_db_connection(conn)

    # GET - show available trainers
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT trainer_id, first_name, last_name, specialization
            FROM Trainer
            ORDER BY trainer_id
        """)
        trainers = cursor.fetchall()

        return render_template('member/schedule_training.html', trainers=trainers)
    finally:
        cursor.close()
        return_db_connection(conn)


@app.route('/member/classes', methods=['GET', 'POST'])
@login_required('member')
def member_classes():
    """View and register for classes"""
    member_id = session['user_id']

    if request.method == 'POST':
        class_id = request.form.get('class_id')

        conn = get_db_connection()
        try:
            cursor = conn.cursor()

            # Check if already registered
            cursor.execute("""
                SELECT registration_id FROM ClassRegistration
                WHERE member_id = %s AND class_id = %s
            """, (member_id, class_id))

            if cursor.fetchone():
                flash('Already registered for this class!', 'warning')
            else:
                cursor.execute("""
                    INSERT INTO ClassRegistration (member_id, class_id, status)
                    VALUES (%s, %s, 'Registered')
                """, (member_id, class_id))
                conn.commit()
                flash('Successfully registered for class!', 'success')

        except Exception as e:
            conn.rollback()
            flash(f'Error: {str(e)}', 'danger')
        finally:
            cursor.close()
            return_db_connection(conn)

    # GET - show available classes
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.class_id, c.class_name, c.schedule_date, c.start_time, c.end_time,
                   t.first_name || ' ' || t.last_name as trainer_name,
                   c.current_enrollment, c.capacity,
                   (c.capacity - c.current_enrollment) as spots_left
            FROM Class c
            JOIN Trainer t ON c.trainer_id = t.trainer_id
            WHERE c.schedule_date >= CURRENT_DATE
              AND c.status = 'Scheduled'
              AND c.current_enrollment < c.capacity
            ORDER BY c.schedule_date, c.start_time
        """)
        classes = cursor.fetchall()

        return render_template('member/classes.html', classes=classes)
    finally:
        cursor.close()
        return_db_connection(conn)

# ============================================================================
# TRAINER ROUTES
# ============================================================================


@app.route('/trainer/login', methods=['GET', 'POST'])
def trainer_login():
    """Trainer login"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT trainer_id, first_name, last_name
                FROM Trainer
                WHERE email = %s AND password = %s
            """, (email, password))

            user = cursor.fetchone()
            if user:
                session['user_id'] = user[0]
                session['user_type'] = 'trainer'
                session['user_name'] = f"{user[1]} {user[2]}"
                flash(f'Welcome back, {user[1]}!', 'success')
                return redirect(url_for('trainer_schedule'))
            else:
                flash('Invalid credentials!', 'danger')
        finally:
            cursor.close()
            return_db_connection(conn)

    return render_template('trainer/login.html')


@app.route('/trainer/schedule')
@login_required('trainer')
def trainer_schedule():
    """Trainer schedule view"""
    trainer_id = session['user_id']
    conn = get_db_connection()

    try:
        cursor = conn.cursor()

        # Get personal training sessions
        cursor.execute("""
            SELECT pts.session_id, pts.session_date, pts.start_time, pts.end_time,
                   m.first_name || ' ' || m.last_name as member_name,
                   r.room_name, pts.status, pts.notes
            FROM PersonalTrainingSession pts
            JOIN Member m ON pts.member_id = m.member_id
            JOIN Room r ON pts.room_id = r.room_id
            WHERE pts.trainer_id = %s
              AND pts.session_date >= CURRENT_DATE
              AND pts.status = 'Scheduled'
            ORDER BY pts.session_date, pts.start_time
        """, (trainer_id,))
        sessions = cursor.fetchall()

        # Get group classes
        cursor.execute("""
            SELECT c.class_id, c.class_name, c.schedule_date, c.start_time, c.end_time,
                   r.room_name, c.current_enrollment, c.capacity
            FROM Class c
            JOIN Room r ON c.room_id = r.room_id
            WHERE c.trainer_id = %s
              AND c.schedule_date >= CURRENT_DATE
              AND c.status = 'Scheduled'
            ORDER BY c.schedule_date, c.start_time
        """, (trainer_id,))
        classes = cursor.fetchall()

        # Get availability
        cursor.execute("""
            SELECT availability_id, day_of_week, start_time, end_time
            FROM TrainerAvailability
            WHERE trainer_id = %s
            ORDER BY 
                CASE day_of_week
                    WHEN 'Monday' THEN 1
                    WHEN 'Tuesday' THEN 2
                    WHEN 'Wednesday' THEN 3
                    WHEN 'Thursday' THEN 4
                    WHEN 'Friday' THEN 5
                    WHEN 'Saturday' THEN 6
                    WHEN 'Sunday' THEN 7
                END,
                start_time
        """, (trainer_id,))
        availability = cursor.fetchall()

        return render_template('trainer/schedule.html',
                               sessions=sessions,
                               classes=classes,
                               availability=availability)
    finally:
        cursor.close()
        return_db_connection(conn)


@app.route('/trainer/availability', methods=['GET', 'POST'])
@login_required('trainer')
def trainer_availability():
    """Set trainer availability"""
    trainer_id = session['user_id']

    if request.method == 'POST':
        day_of_week = request.form.get('day_of_week')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')

        conn = get_db_connection()
        try:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO TrainerAvailability (trainer_id, day_of_week, start_time, end_time)
                VALUES (%s, %s, %s, %s)
            """, (trainer_id, day_of_week, start_time, end_time))
            conn.commit()

            flash('Availability set successfully!', 'success')
            return redirect(url_for('trainer_schedule'))

        except Exception as e:
            conn.rollback()
            flash(f'Error: {str(e)}', 'danger')
        finally:
            cursor.close()
            return_db_connection(conn)

    return render_template('trainer/availability.html')


@app.route('/trainer/members')
@login_required('trainer')
def trainer_members():
    """View members"""
    trainer_id = session['user_id']
    conn = get_db_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT DISTINCT m.member_id, m.first_name, m.last_name, m.email, m.phone
            FROM Member m
            JOIN PersonalTrainingSession pts ON m.member_id = pts.member_id
            WHERE pts.trainer_id = %s
            ORDER BY m.last_name, m.first_name
        """, (trainer_id,))
        members = cursor.fetchall()

        return render_template('trainer/members.html', members=members)
    finally:
        cursor.close()
        return_db_connection(conn)


@app.route('/trainer/member/<int:member_id>')
@login_required('trainer')
def trainer_member_detail(member_id):
    """View member details"""
    trainer_id = session['user_id']
    conn = get_db_connection()

    try:
        cursor = conn.cursor()

        # Get member info
        cursor.execute("""
            SELECT first_name, last_name, email, date_of_birth, phone
            FROM Member
            WHERE member_id = %s
        """, (member_id,))
        member = cursor.fetchone()

        # Get latest health metric
        cursor.execute("""
            SELECT weight, height, heart_rate, blood_pressure, body_fat_percentage, recorded_date
            FROM HealthMetric
            WHERE member_id = %s
            ORDER BY recorded_date DESC
            LIMIT 1
        """, (member_id,))
        metric = cursor.fetchone()

        # Get active goals
        cursor.execute("""
            SELECT goal_type, current_value, target_value, target_date
            FROM FitnessGoal
            WHERE member_id = %s AND status = 'Active'
        """, (member_id,))
        goals = cursor.fetchall()

        return render_template('trainer/member_detail.html',
                               member=member,
                               metric=metric,
                               goals=goals,
                               member_id=member_id)
    finally:
        cursor.close()
        return_db_connection(conn)

# ============================================================================
# ADMIN ROUTES
# ============================================================================


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT admin_id, first_name, last_name
                FROM AdminStaff
                WHERE email = %s AND password = %s
            """, (email, password))

            user = cursor.fetchone()
            if user:
                session['user_id'] = user[0]
                session['user_type'] = 'admin'
                session['user_name'] = f"{user[1]} {user[2]}"
                flash(f'Welcome back, {user[1]}!', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Invalid credentials!', 'danger')
        finally:
            cursor.close()
            return_db_connection(conn)

    return render_template('admin/login.html')


@app.route('/admin/dashboard')
@login_required('admin')
def admin_dashboard():
    """Admin dashboard"""
    conn = get_db_connection()

    try:
        cursor = conn.cursor()

        # Get statistics
        cursor.execute("SELECT COUNT(*) FROM Member")
        total_members = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM Trainer")
        total_trainers = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*) FROM Class 
            WHERE schedule_date >= CURRENT_DATE AND status = 'Scheduled'
        """)
        upcoming_classes = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COALESCE(SUM(total_amount - amount_paid), 0) 
            FROM Bill WHERE status = 'Pending'
        """)
        pending_revenue = cursor.fetchone()[0]

        return render_template('admin/dashboard.html',
                               total_members=total_members,
                               total_trainers=total_trainers,
                               upcoming_classes=upcoming_classes,
                               pending_revenue=pending_revenue)
    finally:
        cursor.close()
        return_db_connection(conn)


@app.route('/admin/rooms')
@login_required('admin')
def admin_rooms():
    """Room management"""
    conn = get_db_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT room_id, room_name, capacity, room_type
            FROM Room
            ORDER BY room_id
        """)
        rooms = cursor.fetchall()

        return render_template('admin/rooms.html', rooms=rooms)
    finally:
        cursor.close()
        return_db_connection(conn)


@app.route('/admin/equipment', methods=['GET', 'POST'])
@login_required('admin')
def admin_equipment():
    """Equipment management"""
    if request.method == 'POST':
        action = request.form.get('action')
        equipment_id = request.form.get('equipment_id')

        conn = get_db_connection()
        try:
            cursor = conn.cursor()

            if action == 'update_status':
                status = request.form.get('status')
                notes = request.form.get('notes')

                cursor.execute("""
                    UPDATE Equipment
                    SET status = %s,
                        maintenance_notes = %s,
                        last_maintenance_date = CURRENT_DATE
                    WHERE equipment_id = %s
                """, (status, notes, equipment_id))
                conn.commit()
                flash('Equipment status updated!', 'success')

        except Exception as e:
            conn.rollback()
            flash(f'Error: {str(e)}', 'danger')
        finally:
            cursor.close()
            return_db_connection(conn)

        return redirect(url_for('admin_equipment'))

    # GET
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT e.equipment_id, e.equipment_name, r.room_name, e.status,
                   e.last_maintenance_date, e.maintenance_notes
            FROM Equipment e
            LEFT JOIN Room r ON e.room_id = r.room_id
            ORDER BY e.status DESC, e.equipment_name
        """)
        equipment = cursor.fetchall()

        return render_template('admin/equipment.html', equipment=equipment)
    finally:
        cursor.close()
        return_db_connection(conn)


@app.route('/admin/billing', methods=['GET', 'POST'])
@login_required('admin')
def admin_billing():
    """Billing management"""
    if request.method == 'POST':
        action = request.form.get('action')

        conn = get_db_connection()
        try:
            cursor = conn.cursor()

            if action == 'generate_bill':
                member_id = request.form.get('member_id')
                description = request.form.get('description')
                amount = request.form.get('amount')
                due_days = request.form.get('due_days')

                cursor.execute("""
                    INSERT INTO Bill (member_id, due_date, total_amount, description)
                    VALUES (%s, CURRENT_DATE + INTERVAL '%s days', %s, %s)
                """, (member_id, due_days, amount, description))
                conn.commit()
                flash('Bill generated successfully!', 'success')

            elif action == 'record_payment':
                bill_id = request.form.get('bill_id')
                amount = request.form.get('amount')
                method = request.form.get('payment_method')
                reference = request.form.get('reference')

                cursor.execute("""
                    INSERT INTO Payment (bill_id, amount, payment_method, transaction_reference)
                    VALUES (%s, %s, %s, %s)
                """, (bill_id, amount, method, reference if reference else None))
                conn.commit()
                flash('Payment recorded successfully!', 'success')

        except Exception as e:
            conn.rollback()
            flash(f'Error: {str(e)}', 'danger')
        finally:
            cursor.close()
            return_db_connection(conn)

        return redirect(url_for('admin_billing'))

    # GET
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        # Get all bills
        cursor.execute("""
            SELECT b.bill_id, m.first_name || ' ' || m.last_name as member_name,
                   b.bill_date, b.due_date, b.total_amount, b.amount_paid,
                   b.status, b.description
            FROM Bill b
            JOIN Member m ON b.member_id = m.member_id
            ORDER BY b.bill_date DESC
            LIMIT 50
        """)
        bills = cursor.fetchall()

        return render_template('admin/billing.html', bills=bills)
    finally:
        cursor.close()
        return_db_connection(conn)

# ============================================================================
# UTILITY ROUTES
# ============================================================================


@app.route('/logout')
def logout():
    """Logout"""
    user_name = session.get('user_name', 'User')
    session.clear()
    flash(f'Goodbye, {user_name}!', 'info')
    return redirect(url_for('index'))


@app.errorhandler(404)
def page_not_found(e):
    """404 error handler"""
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_error(e):
    """500 error handler"""
    return render_template('errors/500.html'), 500

# ============================================================================
# APPLICATION INITIALIZATION
# ============================================================================


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
