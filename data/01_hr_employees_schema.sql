-- ============================================================
-- HR EMPLOYEES DATABASE - SCHEMA
-- Data Analytics Internship Project
-- ============================================================

CREATE DATABASE IF NOT EXISTS hr_employees_db;
USE hr_employees_db;

-- ============================================================
-- 1. LOCATIONS
-- ============================================================
CREATE TABLE locations (
    location_id     INT AUTO_INCREMENT PRIMARY KEY,
    city            VARCHAR(50) NOT NULL,
    state           VARCHAR(50),
    country         VARCHAR(50) NOT NULL DEFAULT 'India'
);

-- ============================================================
-- 2. DEPARTMENTS
-- ============================================================
CREATE TABLE departments (
    department_id   INT AUTO_INCREMENT PRIMARY KEY,
    department_name VARCHAR(100) NOT NULL,
    location_id     INT,
    CONSTRAINT fk_dept_location
        FOREIGN KEY (location_id) REFERENCES locations(location_id)
        ON DELETE SET NULL
);

-- ============================================================
-- 3. JOBS
-- ============================================================
CREATE TABLE jobs (
    job_id          INT AUTO_INCREMENT PRIMARY KEY,
    job_title       VARCHAR(100) NOT NULL,
    min_salary      DECIMAL(10,2),
    max_salary      DECIMAL(10,2)
);

-- ============================================================
-- 4. EMPLOYEES  (self-referencing manager_id)
-- ============================================================
CREATE TABLE employees (
    employee_id     INT AUTO_INCREMENT PRIMARY KEY,
    first_name      VARCHAR(50) NOT NULL,
    last_name       VARCHAR(50) NOT NULL,
    email           VARCHAR(100) UNIQUE,
    phone_number    VARCHAR(20),
    gender          VARCHAR(20),
    dob             DATE,
    marital_status  VARCHAR(20),
    hire_date       DATE NOT NULL,
    job_id          INT,
    department_id   INT,
    salary          DECIMAL(10,2) CHECK (salary >= 0),
    manager_id      INT,
    education_level VARCHAR(30),
    business_travel VARCHAR(30),
    distance_from_home_km INT,
    CONSTRAINT fk_emp_job
        FOREIGN KEY (job_id) REFERENCES jobs(job_id)
        ON DELETE SET NULL,
    CONSTRAINT fk_emp_department
        FOREIGN KEY (department_id) REFERENCES departments(department_id)
        ON DELETE SET NULL,
    CONSTRAINT fk_emp_manager
        FOREIGN KEY (manager_id) REFERENCES employees(employee_id)
        ON DELETE SET NULL
);

-- ============================================================
-- 5. JOB_HISTORY  (tracks role/department changes over time)
-- ============================================================
CREATE TABLE job_history (
    history_id      INT AUTO_INCREMENT PRIMARY KEY,
    employee_id     INT NOT NULL,
    start_date      DATE NOT NULL,
    end_date        DATE,
    job_id          INT,
    department_id   INT,
    CONSTRAINT fk_hist_employee
        FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_hist_job
        FOREIGN KEY (job_id) REFERENCES jobs(job_id)
        ON DELETE SET NULL,
    CONSTRAINT fk_hist_department
        FOREIGN KEY (department_id) REFERENCES departments(department_id)
        ON DELETE SET NULL,
    CONSTRAINT chk_hist_dates CHECK (end_date IS NULL OR end_date >= start_date)
);

-- ============================================================
-- 6. PERFORMANCE_REVIEWS
-- ============================================================
CREATE TABLE performance_reviews (
    review_id           INT AUTO_INCREMENT PRIMARY KEY,
    employee_id         INT NOT NULL,
    review_date         DATE NOT NULL,
    performance_rating  TINYINT CHECK (performance_rating BETWEEN 1 AND 5),
    job_satisfaction    TINYINT CHECK (job_satisfaction BETWEEN 1 AND 5),
    work_life_balance   TINYINT CHECK (work_life_balance BETWEEN 1 AND 5),
    CONSTRAINT fk_review_employee
        FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
        ON DELETE CASCADE
);

-- ============================================================
-- 7. ATTENDANCE
-- ============================================================
CREATE TABLE attendance (
    attendance_id   INT AUTO_INCREMENT PRIMARY KEY,
    employee_id     INT NOT NULL,
    attendance_date DATE NOT NULL,
    status          VARCHAR(30) NOT NULL,
    overtime_hours  DECIMAL(4,2) DEFAULT 0,
    CONSTRAINT fk_att_employee
        FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
        ON DELETE CASCADE,
    CONSTRAINT uq_emp_date UNIQUE (employee_id, attendance_date)
);

-- ============================================================
-- 8. ATTRITION  (separate table to track exits - useful for analytics)
-- ============================================================
CREATE TABLE attrition (
    attrition_id    INT AUTO_INCREMENT PRIMARY KEY,
    employee_id     INT NOT NULL UNIQUE,
    exit_date       DATE,
    reason          VARCHAR(200),
    is_active       BOOLEAN DEFAULT TRUE,
    CONSTRAINT fk_attr_employee
        FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
        ON DELETE CASCADE
);

-- ============================================================
-- USEFUL INDEXES FOR ANALYTICS QUERIES
-- ============================================================
CREATE INDEX idx_emp_department ON employees(department_id);
CREATE INDEX idx_emp_job ON employees(job_id);
CREATE INDEX idx_emp_manager ON employees(manager_id);
CREATE INDEX idx_review_employee ON performance_reviews(employee_id);
CREATE INDEX idx_attendance_employee_date ON attendance(employee_id, attendance_date);

-- ============================================================
-- END OF SCHEMA
-- ============================================================
