-- ============================================================
-- HR EMPLOYEES DATABASE - MASTER TABLE (all 8 tables joined)
-- FIXED VERSION: uses ROW_NUMBER() instead of MAX()-date subqueries
-- to avoid row duplication when two records share the same
-- "latest" date (e.g. two performance reviews on the same date).
-- Original bug: MAX(review_date) subquery + join back on that date
-- matched BOTH tied rows, duplicating the employee. Employees 1015
-- and 1035 were duplicated in the sample data because of this.
-- Requires MySQL 8.0+ (window functions).
-- ============================================================

USE hr_employees_db;

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
    CONCAT(mgr.first_name, ' ', mgr.last_name) AS manager_name,
    jh.start_date       AS latest_history_start,
    jh.end_date         AS latest_history_end,
    pr.review_date       AS latest_review_date,
    pr.performance_rating,
    pr.job_satisfaction,
    pr.work_life_balance,
    att.attendance_date  AS latest_attendance_date,
    att.status            AS latest_attendance_status,
    att.overtime_hours,
    atr.exit_date,
    atr.reason           AS exit_reason,
    atr.is_active
FROM employees e
JOIN jobs j              ON e.job_id = j.job_id
JOIN departments d        ON e.department_id = d.department_id
JOIN locations loc        ON d.location_id = loc.location_id
LEFT JOIN employees mgr   ON e.manager_id = mgr.employee_id
LEFT JOIN (
    SELECT *,
           ROW_NUMBER() OVER (
               PARTITION BY employee_id
               ORDER BY start_date DESC, history_id DESC
           ) AS rn
    FROM job_history
) jh ON jh.employee_id = e.employee_id AND jh.rn = 1
LEFT JOIN (
    SELECT *,
           ROW_NUMBER() OVER (
               PARTITION BY employee_id
               ORDER BY review_date DESC, review_id DESC
           ) AS rn
    FROM performance_reviews
) pr ON pr.employee_id = e.employee_id AND pr.rn = 1
LEFT JOIN (
    SELECT *,
           ROW_NUMBER() OVER (
               PARTITION BY employee_id
               ORDER BY attendance_date DESC, attendance_id DESC
           ) AS rn
    FROM attendance
) att ON att.employee_id = e.employee_id AND att.rn = 1
LEFT JOIN attrition atr ON atr.employee_id = e.employee_id
ORDER BY e.employee_id;
