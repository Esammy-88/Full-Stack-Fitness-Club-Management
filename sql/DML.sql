-- Health and Fitness Club Management System
-- DML (Data Manipulation Language) - Sample Data

-- Insert Members
INSERT INTO Member (email, password, first_name, last_name, date_of_birth, gender, phone, address) VALUES
('john.doe@email.com', 'pass123', 'John', 'Doe', '1990-05-15', 'Male', '613-555-0101', '123 Main St, Ottawa, ON'),
('jane.smith@email.com', 'pass456', 'Jane', 'Smith', '1988-08-22', 'Female', '613-555-0102', '456 Oak Ave, Ottawa, ON'),
('mike.johnson@email.com', 'pass789', 'Mike', 'Johnson', '1995-03-10', 'Male', '613-555-0103', '789 Pine Rd, Ottawa, ON'),
('sarah.williams@email.com', 'pass321', 'Sarah', 'Williams', '1992-11-30', 'Female', '613-555-0104', '321 Elm St, Ottawa, ON'),
('david.brown@email.com', 'pass654', 'David', 'Brown', '1985-07-18', 'Male', '613-555-0105', '654 Maple Dr, Ottawa, ON');

-- Insert Trainers
INSERT INTO Trainer (email, password, first_name, last_name, specialization, phone) VALUES
('alex.trainer@fitness.com', 'trainer123', 'Alex', 'Martinez', 'Strength Training', '613-555-0201'),
('lisa.coach@fitness.com', 'trainer456', 'Lisa', 'Thompson', 'Yoga & Flexibility', '613-555-0202'),
('carlos.fit@fitness.com', 'trainer789', 'Carlos', 'Rodriguez', 'Cardio & HIIT', '613-555-0203');

-- Insert Administrative Staff
INSERT INTO AdminStaff (email, password, first_name, last_name, role, phone) VALUES
('admin@fitness.com', 'admin123', 'Robert', 'Admin', 'Manager', '613-555-0301'),
('billing@fitness.com', 'admin456', 'Emily', 'Finance', 'Billing Specialist', '613-555-0302');

-- Insert Rooms
INSERT INTO Room (room_name, capacity, room_type) VALUES
('Studio A', 20, 'Group Class'),
('Studio B', 15, 'Group Class'),
('Training Room 1', 2, 'Personal Training'),
('Training Room 2', 2, 'Personal Training'),
('Gym Floor', 50, 'General Use');

-- Insert Equipment
INSERT INTO Equipment (room_id, equipment_name, purchase_date, status, last_maintenance_date, maintenance_notes) VALUES
(5, 'Treadmill #1', '2023-01-15', 'Operational', '2024-10-01', 'Routine maintenance completed'),
(5, 'Treadmill #2', '2023-01-15', 'Under Maintenance', '2024-11-15', 'Belt replacement needed'),
(5, 'Elliptical Machine', '2023-03-20', 'Operational', '2024-09-15', 'All systems functioning'),
(3, 'Weight Bench', '2023-02-10', 'Operational', '2024-08-20', 'No issues'),
(5, 'Rowing Machine', '2023-04-05', 'Operational', '2024-10-10', 'Cleaned and lubricated'),
(1, 'Yoga Mats (Set of 20)', '2023-01-01', 'Operational', NULL, 'New stock');

-- Insert Fitness Goals
INSERT INTO FitnessGoal (member_id, goal_type, target_value, current_value, target_date, status) VALUES
(1, 'Weight Loss', 180.00, 195.00, '2025-03-01', 'Active'),
(1, 'Body Fat Percentage', 15.00, 22.00, '2025-06-01', 'Active'),
(2, 'Weight Gain', 135.00, 128.00, '2025-02-15', 'Active'),
(3, 'Run 5K Time', 25.00, 32.00, '2025-01-30', 'Active'),
(4, 'Weight Loss', 150.00, 165.00, '2025-04-01', 'Active');

-- Insert Health Metrics (Historical data)
INSERT INTO HealthMetric (member_id, recorded_date, weight, height, heart_rate, blood_pressure, body_fat_percentage, notes) VALUES
(1, '2024-10-01 09:00:00', 200.00, 72.00, 75, '120/80', 24.5, 'Initial measurement'),
(1, '2024-10-15 09:00:00', 198.50, 72.00, 73, '118/78', 24.0, 'Good progress'),
(1, '2024-11-01 09:00:00', 195.00, 72.00, 72, '118/78', 22.0, 'Continuing well'),
(2, '2024-10-01 10:00:00', 128.00, 65.00, 68, '115/75', 18.5, 'Starting bulking phase'),
(2, '2024-10-20 10:00:00', 130.00, 65.00, 70, '115/75', 18.8, 'Gaining steadily'),
(3, '2024-10-05 14:00:00', 175.00, 70.00, 80, '125/82', 20.0, 'Baseline metrics'),
(4, '2024-10-10 11:00:00', 165.00, 64.00, 72, '120/80', 28.0, 'Starting fitness journey'),
(5, '2024-10-12 15:00:00', 190.00, 68.00, 78, '130/85', 25.0, 'Focus on cardio health');

-- Insert Trainer Availability
INSERT INTO TrainerAvailability (trainer_id, day_of_week, start_time, end_time) VALUES
(1, 'Monday', '09:00:00', '17:00:00'),
(1, 'Tuesday', '09:00:00', '17:00:00'),
(1, 'Wednesday', '09:00:00', '17:00:00'),
(1, 'Thursday', '09:00:00', '17:00:00'),
(1, 'Friday', '09:00:00', '15:00:00'),
(2, 'Monday', '10:00:00', '18:00:00'),
(2, 'Wednesday', '10:00:00', '18:00:00'),
(2, 'Friday', '10:00:00', '18:00:00'),
(2, 'Saturday', '08:00:00', '14:00:00'),
(3, 'Tuesday', '08:00:00', '16:00:00'),
(3, 'Thursday', '08:00:00', '16:00:00'),
(3, 'Saturday', '09:00:00', '15:00:00');

-- Insert Classes
INSERT INTO Class (class_name, trainer_id, room_id, schedule_date, start_time, end_time, capacity, current_enrollment, status) VALUES
('Morning Yoga', 2, 1, '2024-11-27', '07:00:00', '08:00:00', 20, 0, 'Scheduled'),
('HIIT Cardio', 3, 2, '2024-11-27', '18:00:00', '19:00:00', 15, 0, 'Scheduled'),
('Strength Training 101', 1, 1, '2024-11-28', '17:00:00', '18:30:00', 20, 0, 'Scheduled'),
('Evening Yoga', 2, 1, '2024-11-28', '19:00:00', '20:00:00', 20, 0, 'Scheduled'),
('Weekend Boot Camp', 3, 2, '2024-11-30', '10:00:00', '11:30:00', 15, 0, 'Scheduled'),
('Morning Yoga', 2, 1, '2024-11-20', '07:00:00', '08:00:00', 20, 5, 'Completed'),
('HIIT Cardio', 3, 2, '2024-11-21', '18:00:00', '19:00:00', 15, 8, 'Completed');

-- Insert Personal Training Sessions
INSERT INTO PersonalTrainingSession (member_id, trainer_id, room_id, session_date, start_time, end_time, status, notes) VALUES
(1, 1, 3, '2024-11-27', '10:00:00', '11:00:00', 'Scheduled', 'Focus on upper body'),
(2, 2, 3, '2024-11-27', '14:00:00', '15:00:00', 'Scheduled', 'Flexibility and core'),
(3, 3, 4, '2024-11-28', '09:00:00', '10:00:00', 'Scheduled', 'Cardio assessment'),
(1, 1, 3, '2024-11-29', '10:00:00', '11:00:00', 'Scheduled', 'Lower body workout'),
(4, 1, 3, '2024-11-30', '11:00:00', '12:00:00', 'Scheduled', 'Full body introduction'),
(1, 1, 3, '2024-11-20', '10:00:00', '11:00:00', 'Completed', 'Great session'),
(2, 2, 3, '2024-11-21', '14:00:00', '15:00:00', 'Completed', 'Good progress');

-- Insert Class Registrations
INSERT INTO ClassRegistration (member_id, class_id, status) VALUES
(1, 1, 'Registered'),
(2, 1, 'Registered'),
(3, 2, 'Registered'),
(4, 3, 'Registered'),
(5, 3, 'Registered'),
(1, 4, 'Registered'),
(2, 5, 'Registered'),
-- Past classes attended
(1, 6, 'Attended'),
(2, 6, 'Attended'),
(3, 6, 'Attended'),
(4, 6, 'Attended'),
(5, 6, 'Attended'),
(1, 7, 'Attended'),
(2, 7, 'Attended'),
(3, 7, 'Attended');

-- Insert Bills
INSERT INTO Bill (member_id, bill_date, due_date, total_amount, amount_paid, status, description) VALUES
(1, '2024-11-01', '2024-11-15', 150.00, 150.00, 'Paid', 'Monthly Membership - November 2024'),
(2, '2024-11-01', '2024-11-15', 150.00, 150.00, 'Paid', 'Monthly Membership - November 2024'),
(3, '2024-11-01', '2024-11-15', 150.00, 0.00, 'Pending', 'Monthly Membership - November 2024'),
(4, '2024-11-01', '2024-11-15', 150.00, 75.00, 'Pending', 'Monthly Membership - November 2024'),
(1, '2024-11-05', '2024-11-20', 200.00, 0.00, 'Pending', 'Personal Training Package (4 sessions)'),
(5, '2024-11-01', '2024-11-15', 150.00, 0.00, 'Pending', 'Monthly Membership - November 2024');

-- Insert Payments
INSERT INTO Payment (bill_id, payment_date, amount, payment_method, transaction_reference) VALUES
(1, '2024-11-02 10:30:00', 150.00, 'Credit Card', 'TXN-2024110201'),
(2, '2024-11-03 14:20:00', 150.00, 'Debit Card', 'TXN-2024110302'),
(4, '2024-11-05 09:15:00', 75.00, 'Cash', 'TXN-2024110503');