-- ============================================================
-- HR EMPLOYEES DATABASE - JOIN QUERIES
-- Data Analytics Internship Project
-- ============================================================

USE hr_employees_db;

-- ============================================================
-- 1. CORE EMPLOYEE JOIN  ⭐ (main showcase query)
-- employees + jobs + departments + locations + manager (self-join)
-- Simple, clean JOINs — this is the primary table used for
-- most analysis (salary trends, department strength, etc.)
-- ============================================================
SELECT
    e.employee_id,
    CONCAT(e.first_name, ' ', e.last_name) AS employee_name,
    e.gender,
    e.hire_date,
    e.salary,
    e.education_level,
    e.business_travel,
    e.distance_from_home_km,
    j.job_title,
    d.department_name,
    loc.city,
    loc.state,
    loc.country,
    CONCAT(mgr.first_name, ' ', mgr.last_name) AS manager_name
FROM employees e
JOIN jobs j              ON e.job_id = j.job_id
JOIN departments d        ON e.department_id = d.department_id
JOIN locations loc        ON d.location_id = loc.location_id
LEFT JOIN employees mgr   ON e.manager_id = mgr.employee_id
ORDER BY e.employee_id;


-- ============================================================
-- 2. JOB HISTORY JOIN
-- Career progression: every role/department change per employee
-- ============================================================
SELECT
    e.employee_id,
    CONCAT(e.first_name, ' ', e.last_name) AS employee_name,
    jh.start_date,
    jh.end_date,
    j.job_title        AS job_title_at_that_time,
    d.department_name  AS department_at_that_time
FROM job_history jh
JOIN employees e   ON jh.employee_id = e.employee_id
JOIN jobs j        ON jh.job_id = j.job_id
JOIN departments d ON jh.department_id = d.department_id
ORDER BY e.employee_id, jh.start_date;


-- ============================================================
-- 3. PERFORMANCE REVIEWS JOIN
-- All reviews with employee + department context
-- ============================================================
SELECT
    e.employee_id,
    CONCAT(e.first_name, ' ', e.last_name) AS employee_name,
    d.department_name,
    pr.review_date,
    pr.performance_rating,
    pr.job_satisfaction,
    pr.work_life_balance
FROM performance_reviews pr
JOIN employees e   ON pr.employee_id = e.employee_id
JOIN departments d ON e.department_id = d.department_id
ORDER BY e.employee_id, pr.review_date;


-- ============================================================
-- 4. ATTENDANCE JOIN
-- Full attendance log with employee + department context
-- ============================================================
SELECT
    e.employee_id,
    CONCAT(e.first_name, ' ', e.last_name) AS employee_name,
    d.department_name,
    att.attendance_date,
    att.status,
    att.overtime_hours
FROM attendance att
JOIN employees e   ON att.employee_id = e.employee_id
JOIN departments d ON e.department_id = d.department_id
ORDER BY e.employee_id, att.attendance_date;


-- ============================================================
-- 5. ATTRITION JOIN
-- Exited employees with job, department, location, salary
-- ============================================================
SELECT
    e.employee_id,
    CONCAT(e.first_name, ' ', e.last_name) AS employee_name,
    e.hire_date,
    atr.exit_date,
    TIMESTAMPDIFF(MONTH, e.hire_date, atr.exit_date) AS tenure_months,
    atr.reason AS exit_reason,
    j.job_title,
    d.department_name,
    loc.city,
    e.salary
FROM attrition atr
JOIN employees e   ON atr.employee_id = e.employee_id
JOIN jobs j        ON e.job_id = j.job_id
JOIN departments d ON e.department_id = d.department_id
JOIN locations loc ON d.location_id = loc.location_id
WHERE atr.is_active = FALSE
ORDER BY atr.exit_date DESC;

-- ============================================================
-- END OF JOIN QUERIES
-- (Master table combining all 8 tables is in a separate file:
--  master_table_only.sql)
-- ============================================================
