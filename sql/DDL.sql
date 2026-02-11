-- Health and Fitness Club Management System
-- DDL (Data Definition Language)

-- Drop tables if they exist (for clean setup)
DROP TABLE IF EXISTS Payment CASCADE;
DROP TABLE IF EXISTS Bill CASCADE;
DROP TABLE IF EXISTS ClassRegistration CASCADE;
DROP TABLE IF EXISTS PersonalTrainingSession CASCADE;
DROP TABLE IF EXISTS Class CASCADE;
DROP TABLE IF EXISTS TrainerAvailability CASCADE;
DROP TABLE IF EXISTS HealthMetric CASCADE;
DROP TABLE IF EXISTS FitnessGoal CASCADE;
DROP TABLE IF EXISTS Equipment CASCADE;
DROP TABLE IF EXISTS Room CASCADE;
DROP TABLE IF EXISTS Trainer CASCADE;
DROP TABLE IF EXISTS Member CASCADE;
DROP TABLE IF EXISTS AdminStaff CASCADE;

-- Member Table
CREATE TABLE Member (
    member_id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    date_of_birth DATE NOT NULL,
    gender VARCHAR(20),
    phone VARCHAR(20),
    address TEXT,
    registration_date DATE DEFAULT CURRENT_DATE,
    CONSTRAINT valid_email CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

-- Trainer Table
CREATE TABLE Trainer (
    trainer_id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    specialization VARCHAR(100),
    phone VARCHAR(20),
    hire_date DATE DEFAULT CURRENT_DATE
);

-- Administrative Staff Table
CREATE TABLE AdminStaff (
    admin_id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    role VARCHAR(50) NOT NULL,
    phone VARCHAR(20)
);

-- Room Table
CREATE TABLE Room (
    room_id SERIAL PRIMARY KEY,
    room_name VARCHAR(100) NOT NULL,
    capacity INT NOT NULL CHECK (capacity > 0),
    room_type VARCHAR(50)
);

-- Equipment Table
CREATE TABLE Equipment (
    equipment_id SERIAL PRIMARY KEY,
    room_id INT REFERENCES Room(room_id) ON DELETE SET NULL,
    equipment_name VARCHAR(100) NOT NULL,
    purchase_date DATE,
    status VARCHAR(50) DEFAULT 'Operational',
    last_maintenance_date DATE,
    maintenance_notes TEXT,
    CONSTRAINT valid_status CHECK (status IN ('Operational', 'Under Maintenance', 'Out of Service'))
);

-- Fitness Goal Table
CREATE TABLE FitnessGoal (
    goal_id SERIAL PRIMARY KEY,
    member_id INT REFERENCES Member(member_id) ON DELETE CASCADE,
    goal_type VARCHAR(100) NOT NULL,
    target_value DECIMAL(10, 2),
    current_value DECIMAL(10, 2),
    target_date DATE,
    created_date DATE DEFAULT CURRENT_DATE,
    status VARCHAR(50) DEFAULT 'Active',
    CONSTRAINT valid_goal_status CHECK (status IN ('Active', 'Achieved', 'Abandoned'))
);

-- Health Metric Table (Historical tracking)
CREATE TABLE HealthMetric (
    metric_id SERIAL PRIMARY KEY,
    member_id INT REFERENCES Member(member_id) ON DELETE CASCADE,
    recorded_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    weight DECIMAL(5, 2),
    height DECIMAL(5, 2),
    heart_rate INT,
    blood_pressure VARCHAR(20),
    body_fat_percentage DECIMAL(5, 2),
    notes TEXT
);

-- Trainer Availability Table
CREATE TABLE TrainerAvailability (
    availability_id SERIAL PRIMARY KEY,
    trainer_id INT REFERENCES Trainer(trainer_id) ON DELETE CASCADE,
    day_of_week VARCHAR(20) NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    CONSTRAINT valid_day CHECK (day_of_week IN ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')),
    CONSTRAINT valid_time_range CHECK (start_time < end_time),
    CONSTRAINT no_overlap UNIQUE (trainer_id, day_of_week, start_time, end_time)
);

-- Class Table
CREATE TABLE Class (
    class_id SERIAL PRIMARY KEY,
    class_name VARCHAR(100) NOT NULL,
    trainer_id INT REFERENCES Trainer(trainer_id) ON DELETE SET NULL,
    room_id INT REFERENCES Room(room_id) ON DELETE SET NULL,
    schedule_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    capacity INT NOT NULL CHECK (capacity > 0),
    current_enrollment INT DEFAULT 0 CHECK (current_enrollment >= 0),
    status VARCHAR(50) DEFAULT 'Scheduled',
    CONSTRAINT valid_class_time CHECK (start_time < end_time),
    CONSTRAINT capacity_check CHECK (current_enrollment <= capacity),
    CONSTRAINT valid_class_status CHECK (status IN ('Scheduled', 'Completed', 'Cancelled'))
);

-- Personal Training Session Table
CREATE TABLE PersonalTrainingSession (
    session_id SERIAL PRIMARY KEY,
    member_id INT REFERENCES Member(member_id) ON DELETE CASCADE,
    trainer_id INT REFERENCES Trainer(trainer_id) ON DELETE SET NULL,
    room_id INT REFERENCES Room(room_id) ON DELETE SET NULL,
    session_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    status VARCHAR(50) DEFAULT 'Scheduled',
    notes TEXT,
    CONSTRAINT valid_session_time CHECK (start_time < end_time),
    CONSTRAINT valid_session_status CHECK (status IN ('Scheduled', 'Completed', 'Cancelled'))
);

-- Class Registration Table
CREATE TABLE ClassRegistration (
    registration_id SERIAL PRIMARY KEY,
    member_id INT REFERENCES Member(member_id) ON DELETE CASCADE,
    class_id INT REFERENCES Class(class_id) ON DELETE CASCADE,
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'Registered',
    CONSTRAINT valid_registration_status CHECK (status IN ('Registered', 'Attended', 'Cancelled')),
    CONSTRAINT unique_registration UNIQUE (member_id, class_id)
);

-- Bill Table
CREATE TABLE Bill (
    bill_id SERIAL PRIMARY KEY,
    member_id INT REFERENCES Member(member_id) ON DELETE CASCADE,
    bill_date DATE DEFAULT CURRENT_DATE,
    due_date DATE NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL CHECK (total_amount >= 0),
    amount_paid DECIMAL(10, 2) DEFAULT 0 CHECK (amount_paid >= 0),
    status VARCHAR(50) DEFAULT 'Pending',
    description TEXT,
    CONSTRAINT valid_bill_status CHECK (status IN ('Pending', 'Paid', 'Overdue', 'Cancelled'))
);

-- Payment Table
CREATE TABLE Payment (
    payment_id SERIAL PRIMARY KEY,
    bill_id INT REFERENCES Bill(bill_id) ON DELETE CASCADE,
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    amount DECIMAL(10, 2) NOT NULL CHECK (amount > 0),
    payment_method VARCHAR(50) NOT NULL,
    transaction_reference VARCHAR(100),
    CONSTRAINT valid_payment_method CHECK (payment_method IN ('Cash', 'Credit Card', 'Debit Card', 'Bank Transfer', 'Other'))
);

-- Create Index for performance optimization
CREATE INDEX idx_member_email ON Member(email);
CREATE INDEX idx_health_metric_member_date ON HealthMetric(member_id, recorded_date DESC);
CREATE INDEX idx_class_schedule ON Class(schedule_date, start_time);
CREATE INDEX idx_session_trainer_date ON PersonalTrainingSession(trainer_id, session_date);

-- Create View: Member Dashboard Summary
CREATE OR REPLACE VIEW MemberDashboard AS
SELECT 
    m.member_id,
    m.first_name,
    m.last_name,
    m.email,
    -- Latest health metrics
    (SELECT weight FROM HealthMetric WHERE member_id = m.member_id ORDER BY recorded_date DESC LIMIT 1) AS latest_weight,
    (SELECT heart_rate FROM HealthMetric WHERE member_id = m.member_id ORDER BY recorded_date DESC LIMIT 1) AS latest_heart_rate,
    (SELECT recorded_date FROM HealthMetric WHERE member_id = m.member_id ORDER BY recorded_date DESC LIMIT 1) AS last_metric_date,
    -- Active goals count
    (SELECT COUNT(*) FROM FitnessGoal WHERE member_id = m.member_id AND status = 'Active') AS active_goals,
    -- Upcoming sessions count
    (SELECT COUNT(*) FROM PersonalTrainingSession 
     WHERE member_id = m.member_id AND session_date >= CURRENT_DATE AND status = 'Scheduled') AS upcoming_sessions,
    -- Total classes attended
    (SELECT COUNT(*) FROM ClassRegistration 
     WHERE member_id = m.member_id AND status = 'Attended') AS classes_attended,
    -- Pending bill amount
    (SELECT COALESCE(SUM(total_amount - amount_paid), 0) FROM Bill 
     WHERE member_id = m.member_id AND status = 'Pending') AS pending_balance
FROM Member m;

-- Trigger: Automatically update class enrollment count
CREATE OR REPLACE FUNCTION update_class_enrollment()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' AND NEW.status = 'Registered' THEN
        UPDATE Class 
        SET current_enrollment = current_enrollment + 1 
        WHERE class_id = NEW.class_id;
    ELSIF TG_OP = 'UPDATE' AND OLD.status = 'Registered' AND NEW.status = 'Cancelled' THEN
        UPDATE Class 
        SET current_enrollment = current_enrollment - 1 
        WHERE class_id = NEW.class_id;
    ELSIF TG_OP = 'DELETE' AND OLD.status = 'Registered' THEN
        UPDATE Class 
        SET current_enrollment = current_enrollment - 1 
        WHERE class_id = OLD.class_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER class_enrollment_trigger
AFTER INSERT OR UPDATE OR DELETE ON ClassRegistration
FOR EACH ROW
EXECUTE FUNCTION update_class_enrollment();

-- Trigger: Update bill status when payment is made
CREATE OR REPLACE FUNCTION update_bill_status()
RETURNS TRIGGER AS $$
DECLARE
    total_paid DECIMAL(10, 2);
    bill_total DECIMAL(10, 2);
BEGIN
    SELECT COALESCE(SUM(amount), 0) INTO total_paid
    FROM Payment
    WHERE bill_id = NEW.bill_id;
    
    SELECT total_amount INTO bill_total
    FROM Bill
    WHERE bill_id = NEW.bill_id;
    
    UPDATE Bill
    SET amount_paid = total_paid,
        status = CASE 
            WHEN total_paid >= bill_total THEN 'Paid'
            ELSE 'Pending'
        END
    WHERE bill_id = NEW.bill_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER payment_bill_update_trigger
AFTER INSERT ON Payment
FOR EACH ROW
EXECUTE FUNCTION update_bill_status();