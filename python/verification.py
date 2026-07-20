# ============================================================
# VERIFICATION.PY
# Flow: read cleaned CSVs -> verify each -> insert verified
#       tables into a NEW cleaned DB -> build master CSV
#       (join) -> build subset CSVs from the master CSV
# All CSVs read/written from the SAME folder as this script.
# ============================================================

import os
import pandas as pd
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# SECTION 1: CONFIG
# ============================================================

# Folder where all cleaned CSVs live and where master/subset
# CSVs will be written. Same folder as this script.
FOLDER = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(FOLDER, "Output")

# Folder cleaning.py saved the <table>_cleaned.csv files into
CLEANED_DIR = os.path.join(OUTPUT_DIR, "cleaned_data")

# Folder where master_table.csv and the subset CSVs get saved
MASTER_DIR = os.path.join(OUTPUT_DIR, "master_data")
os.makedirs(MASTER_DIR, exist_ok=True)

# Name of the NEW database that will hold verified/cleaned tables
CLEAN_DB_NAME = os.getenv("CLEAN_DB_NAME", "hr_employees_cleaned_db")

# Old duplicate department IDs -> merged into these (same as cleaning.py)
DEPT_ID_MAP = {2: 9, 7: 10}

# Order matters: employees needs jobs_df for its salary-range check
TABLE_ORDER = ['locations', 'departments', 'jobs', 'employees',
               'job_history', 'performance_reviews', 'attendance', 'attrition']


# ============================================================
# SECTION 2: SMALL HELPERS (csv i/o, printing)
# ============================================================

def csv_path(name):
    return os.path.join(CLEANED_DIR, f"{name}_cleaned.csv")


def load_csv(name):
    path = csv_path(name)
    df = pd.read_csv(path)
    print(f"Loaded {name}: {len(df)} rows from {path}")
    return df


def save_csv(df, filename):
    path = os.path.join(MASTER_DIR, filename)
    df.to_csv(path, index=False)
    print(f"Saved: {path} ({len(df)} rows, {len(df.columns)} cols)")
    return path


def report(check_name, is_ok, detail=""):
    status = "PASS" if is_ok else "FAIL"
    print(f"[{status}] {check_name}", f"- {detail}" if detail else "")
    return is_ok


# ============================================================
# SECTION 3: VERIFY FUNCTIONS (one per table)
# Each returns True only if ALL checks for that table pass.
# ============================================================

def verify_locations(df):
    print("\nVerifying: locations")
    checks = []
    bad_casing = df[df['city'] != df['city'].str.title()]
    checks.append(report("City casing standardized", len(bad_casing) == 0, f"{len(bad_casing)} bad rows"))
    checks.append(report("No duplicate rows", df.duplicated().sum() == 0))
    return all(checks)


def verify_departments(df):
    print("\nVerifying: departments")
    checks = []
    bad_names = df[df['department_name'].isin(['Hr', 'Ops'])]
    checks.append(report("No leftover abbreviation names", len(bad_names) == 0, f"{len(bad_names)} bad rows"))

    leftover_ids = df[df['department_id'].isin(DEPT_ID_MAP.keys())]
    checks.append(report("No duplicate department IDs remain", len(leftover_ids) == 0, f"{len(leftover_ids)} rows"))

    name_counts = df['department_name'].value_counts()
    still_duplicated = name_counts[name_counts > 1]
    checks.append(report("No department name mapped to multiple IDs", len(still_duplicated) == 0,
                          f"{dict(still_duplicated)}" if len(still_duplicated) else ""))

    checks.append(report("No duplicate rows", df.duplicated().sum() == 0))
    return all(checks)


def verify_jobs(df):
    print("\nVerifying: jobs")
    checks = [report("No duplicate rows", df.duplicated().sum() == 0)]
    return all(checks)


def verify_employees(df, jobs_df):
    print("\nVerifying: employees")
    checks = []
    checks.append(report("No missing salary", df['salary'].isnull().sum() == 0, f"{df['salary'].isnull().sum()} missing"))
    checks.append(report("No missing email", df['email'].isnull().sum() == 0, f"{df['email'].isnull().sum()} missing"))

    bad_gender = df[~df['gender'].isin(['Male', 'Female'])]
    checks.append(report("Gender values standardized", len(bad_gender) == 0, f"{len(bad_gender)} bad rows"))

    bad_dept = df[df['department_id'].isin(DEPT_ID_MAP.keys())]
    checks.append(report("No employees on duplicate department IDs", len(bad_dept) == 0, f"{len(bad_dept)} rows"))

    merged = df.merge(jobs_df[['job_id', 'min_salary', 'max_salary']], on='job_id', how='left')
    violation = merged[(merged['salary'] < merged['min_salary']) | (merged['salary'] > merged['max_salary'])]
    checks.append(report("Salary within job's min/max range", len(violation) == 0, f"{len(violation)} violations"))

    self_manager = df[df['employee_id'] == df['manager_id']]
    checks.append(report("No self-manager records", len(self_manager) == 0, f"{len(self_manager)} rows"))

    bad_distance = df[df['distance_from_home_km'] < 0]
    checks.append(report("No negative distance_from_home_km", len(bad_distance) == 0, f"{len(bad_distance)} rows"))

    checks.append(report("No duplicate rows", df.duplicated().sum() == 0))
    return all(checks)


def verify_job_history(df):
    print("\nVerifying: job_history")
    checks = [report("No duplicate rows", df.duplicated().sum() == 0)]
    return all(checks)


def verify_performance_reviews(df):
    print("\nVerifying: performance_reviews")
    checks = [report("No duplicate rows", df.duplicated().sum() == 0)]
    return all(checks)


def verify_attendance(df):
    print("\nVerifying: attendance")
    checks = []
    negative_hours = df[df['overtime_hours'] < 0]
    checks.append(report("No negative overtime_hours", len(negative_hours) == 0, f"{len(negative_hours)} rows"))
    checks.append(report("No duplicate rows", df.duplicated().sum() == 0))
    return all(checks)


def verify_attrition(df):
    print("\nVerifying: attrition")
    checks = []
    checks.append(report("No missing reason", df['reason'].isnull().sum() == 0, f"{df['reason'].isnull().sum()} missing"))
    inconsistent = df[(df['is_active'] == 0) & (df['exit_date'].isnull())]
    checks.append(report("is_active/exit_date consistent", len(inconsistent) == 0, f"{len(inconsistent)} rows"))
    checks.append(report("No duplicate rows", df.duplicated().sum() == 0))
    return all(checks)


def verify_memory(df, name, max_expected_mb=None):
    mem_mb = round(df.memory_usage(deep=True).sum() / (1024 ** 2), 3)
    print(f"\n{name} memory usage: {mem_mb} MB")
    if max_expected_mb is not None:
        report("Memory within expected limit", mem_mb <= max_expected_mb, f"{mem_mb} MB vs limit {max_expected_mb} MB")


VERIFY_FUNCS = {
    'locations': verify_locations,
    'departments': verify_departments,
    'jobs': verify_jobs,
    'job_history': verify_job_history,
    'performance_reviews': verify_performance_reviews,
    'attendance': verify_attendance,
    'attrition': verify_attrition,
}


# ============================================================
# SECTION: CALL TABLES ONE BY ONE (manual, no auto loop)
# Prints the table name, loads that ONE cleaned CSV, and runs
# its verification checks.
# Usage:
#   jobs_df = run_verification('jobs')
#   emp_df  = run_verification('employees', jobs_df)   # employees needs jobs_df
# ============================================================

def run_verification(table_name, jobs_df=None):
    print("\n" + "#" * 70)
    print(f"# TABLE: {table_name}")
    print("#" * 70)

    df = load_csv(table_name)

    if table_name == 'employees':
        if jobs_df is None:
            jobs_df = load_csv('jobs')
        passed = verify_employees(df, jobs_df)
    else:
        passed = VERIFY_FUNCS[table_name](df)

    verify_memory(df, table_name)

    if passed:
        # Only store the table once it has PASSED verification.
        # finalize_pipeline() checks this dict before doing anything.
        VERIFIED_DFS[table_name] = df
        print(f"\n✅ '{table_name}' PASSED and is ready for DB insert.")
    else:
        # Failed tables are NOT stored, so finalize_pipeline() will
        # correctly refuse to proceed until this table is fixed and re-verified.
        VERIFIED_DFS.pop(table_name, None)
        print(f"\n⚠️  '{table_name}' FAILED verification. It will NOT be inserted "
              f"into the database until it passes.")

    remaining = [t for t in TABLE_ORDER if t not in VERIFIED_DFS]
    print(f"Verified so far: {len(VERIFIED_DFS)}/{len(TABLE_ORDER)}"
          + (f"  (still need: {remaining})" if remaining else "  — ALL TABLES VERIFIED"))

    return df


# ============================================================
# SECTION 3B: FINALIZE (only runs once ALL 8 tables are verified)
# Call this after you have run_verification()'d every table and
# they have all PASSED. If even one table hasn't passed yet, this
# refuses to insert anything and tells you what's missing.
# Usage:
#   finalize_pipeline()
# ============================================================

VERIFIED_DFS = {}  # {table_name: df} — filled only by run_verification() on PASS


def finalize_pipeline():
    missing = [t for t in TABLE_ORDER if t not in VERIFIED_DFS]

    if missing:
        print("\n⚠️  Cannot proceed — not all tables have passed verification yet.")
        print(f"Still missing / failed: {missing}")
        print("Run run_verification() for each of these (and make sure they PASS) first.")
        return

    print("\n" + "=" * 60)
    print("All 8 tables verified — proceeding with insert + master + subsets")
    print("=" * 60)

    # ---- Step 1: insert verified tables into NEW database ----
    insert_all_cleaned_tables(VERIFIED_DFS)

    # ---- Step 2: build + save master CSV ----
    master_df = build_master_table(VERIFIED_DFS)
    master_path = save_csv(master_df, "master_table.csv")

    # ---- Step 3: re-read master CSV from disk, build subsets from it ----
    master_from_disk = pd.read_csv(master_path)
    subsets = build_subsets(master_from_disk)
    subsets['insights_subset'] = build_insights_subset(master_from_disk)
    for subset_name, subset_df in subsets.items():
        save_csv(subset_df, f"{subset_name}.csv")

    print("\n✅ Pipeline complete: verified -> inserted into DB -> master CSV -> subset CSVs")


# ============================================================
# SECTION 4: DATABASE INSERT (into a NEW cleaned database)
# ============================================================

def get_cleaned_db_engine():
    """Engine for the NEW cleaned database. Creates the database
    if it doesn't already exist, using the same server creds
    as the raw DB (from .env)."""

    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")

    missing = [n for n, v in [("DB_HOST", host), ("DB_PORT", port),
                               ("DB_USER", user), ("DB_PASSWORD", password)] if not v]
    if missing:
        raise ValueError(f"Missing values in .env: {missing}")

    safe_password = quote_plus(password)

    # connect without a database first, to create it if missing
    server_engine = create_engine(f"mysql+pymysql://{user}:{safe_password}@{host}:{port}/")
    with server_engine.connect() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {CLEAN_DB_NAME}"))
        conn.commit()

    db_engine = create_engine(f"mysql+pymysql://{user}:{safe_password}@{host}:{port}/{CLEAN_DB_NAME}")
    return db_engine


def insert_table(df, table_name, engine):
    df.to_sql(table_name, engine, if_exists='replace', index=False)
    print(f"Inserted into '{CLEAN_DB_NAME}': {table_name} ({len(df)} rows)")


def insert_all_cleaned_tables(verified_dfs):
    """verified_dfs: dict of {table_name: df} that already PASSED verification."""
    print("\n" + "=" * 60)
    print(f"Inserting verified tables into database: {CLEAN_DB_NAME}")
    print("=" * 60)
    engine = get_cleaned_db_engine()
    for name, df in verified_dfs.items():
        insert_table(df, name, engine)


# ============================================================
# SECTION 5: MASTER CSV BUILDER (joins all 8 tables, one row
# per employee, latest job_history / review / attendance)
# ============================================================

def build_master_table(dfs):
    print("\n" + "=" * 60)
    print("Building master table (all tables joined)")
    print("=" * 60)

    emp = dfs['employees'].copy()
    jobs = dfs['jobs']
    dept = dfs['departments']
    loc = dfs['locations']
    job_hist = dfs['job_history']
    perf = dfs['performance_reviews']
    att = dfs['attendance']
    atr = dfs['attrition']

    emp['employee_name'] = emp['first_name'] + ' ' + emp['last_name']

    df = emp.merge(jobs, on='job_id', how='left')
    df = df.merge(dept, on='department_id', how='left')
    df = df.merge(loc, on='location_id', how='left')

    # self-join for manager name
    mgr = emp[['employee_id', 'employee_name']].rename(
        columns={'employee_id': 'manager_id', 'employee_name': 'manager_name'})
    df = df.merge(mgr, on='manager_id', how='left')

    # latest job_history row per employee
    jh_latest = (job_hist.sort_values(['employee_id', 'start_date', 'history_id'], ascending=[True, False, False])
                          .drop_duplicates(subset='employee_id', keep='first')
                          .rename(columns={'start_date': 'latest_history_start', 'end_date': 'latest_history_end'})
                          [['employee_id', 'latest_history_start', 'latest_history_end']])
    df = df.merge(jh_latest, on='employee_id', how='left')

    # latest performance review per employee
    pr_latest = (perf.sort_values(['employee_id', 'review_date', 'review_id'], ascending=[True, False, False])
                      .drop_duplicates(subset='employee_id', keep='first')
                      .rename(columns={'review_date': 'latest_review_date'})
                      [['employee_id', 'latest_review_date', 'performance_rating', 'job_satisfaction', 'work_life_balance']])
    df = df.merge(pr_latest, on='employee_id', how='left')

    # latest attendance row per employee
    att_latest = (att.sort_values(['employee_id', 'attendance_date', 'attendance_id'], ascending=[True, False, False])
                      .drop_duplicates(subset='employee_id', keep='first')
                      .rename(columns={'attendance_date': 'latest_attendance_date', 'status': 'latest_attendance_status'})
                      [['employee_id', 'latest_attendance_date', 'latest_attendance_status', 'overtime_hours']])
    df = df.merge(att_latest, on='employee_id', how='left')

    # attrition (one row per employee already)
    atr_cols = atr.rename(columns={'reason': 'exit_reason'})[['employee_id', 'exit_date', 'exit_reason', 'is_active']]
    df = df.merge(atr_cols, on='employee_id', how='left')

    # BUG FIX: attrition table only has rows for employees who LEFT.
    # Employees with no attrition row (i.e. still employed) get is_active
    # = NaN after the left join above, when it should be True. Left as
    # NaN, this silently broke: insights.py Q3/Q8 (any check using
    # is_active == True matched zero rows -> NaN results) and
    # visualization.py charts #2/#3 (.map({True:.., False:..}) turns
    # every NaN row into NaN, wiping out the active-employee group).
    df['is_active'] = df['is_active'].fillna(True).astype(bool)

    final_cols = [
        'employee_id', 'employee_name', 'gender', 'hire_date', 'salary', 'education_level',
        'business_travel', 'distance_from_home_km', 'job_title', 'department_name',
        'city', 'state', 'country', 'manager_name',
        'latest_history_start', 'latest_history_end',
        'latest_review_date', 'performance_rating', 'job_satisfaction', 'work_life_balance',
        'latest_attendance_date', 'latest_attendance_status', 'overtime_hours',
        'exit_date', 'exit_reason', 'is_active',
    ]
    df = df[final_cols].sort_values('employee_id').reset_index(drop=True)
    print(f"Master table built: {len(df)} rows, {len(df.columns)} columns")
    return df


# ============================================================
# SECTION 6: SUBSET CSV BUILDER
# IMPORTANT: subsets are built from the MASTER CSV that was
# actually saved to disk (re-read with pd.read_csv), so column
# names always match the real master file, not the raw tables.
# ============================================================

def build_subsets(master_df):
    subsets = {}

    subsets['core_employee_subset'] = master_df[[
        'employee_id', 'employee_name', 'gender', 'hire_date', 'salary',
        'education_level', 'business_travel', 'distance_from_home_km',
        'job_title', 'department_name', 'city', 'state', 'country', 'manager_name'
    ]]

    subsets['performance_subset'] = master_df[[
        'employee_id', 'employee_name', 'department_name',
        'latest_review_date', 'performance_rating', 'job_satisfaction', 'work_life_balance'
    ]].dropna(subset=['latest_review_date'])

    subsets['attendance_subset'] = master_df[[
        'employee_id', 'employee_name', 'department_name',
        'latest_attendance_date', 'latest_attendance_status', 'overtime_hours'
    ]].dropna(subset=['latest_attendance_date'])

    subsets['attrition_subset'] = master_df[master_df['is_active'] == False][[
        'employee_id', 'employee_name', 'hire_date', 'exit_date', 'exit_reason',
        'job_title', 'department_name', 'city', 'salary'
    ]]

    return subsets


# ============================================================
# SECTION 6A: INSIGHTS / VISUALIZATION SUBSET
# One well-rounded subset built specifically for charts and
# analytics: every dimension you'd normally group/plot by
# (gender, department, job, location, manager), the key metrics
# (salary, performance, attendance, overtime), the attrition
# signal (exit_date/reason/is_active), and a computed
# tenure_years column (very useful for attrition/retention charts).
# ============================================================

def build_insights_subset(master_df):
    df = master_df.copy()

    df['hire_date'] = pd.to_datetime(df['hire_date'], errors='coerce')
    df['exit_date'] = pd.to_datetime(df['exit_date'], errors='coerce')

    # Tenure = exit_date - hire_date for employees who left,
    # otherwise today - hire_date for employees still active
    today = pd.Timestamp.today().normalize()
    end_date = df['exit_date'].fillna(today)
    df['tenure_years'] = ((end_date - df['hire_date']).dt.days / 365.25).round(2)

    insights_cols = [
        'employee_id', 'employee_name', 'gender', 'department_name', 'job_title',
        'city', 'state', 'country', 'manager_name',
        'hire_date', 'tenure_years',
        'salary', 'education_level', 'business_travel', 'distance_from_home_km',
        'performance_rating', 'job_satisfaction', 'work_life_balance',
        'latest_attendance_status', 'overtime_hours',
        'exit_date', 'exit_reason', 'is_active',
    ]

    return df[insights_cols]


# ============================================================
# SECTION 6B: CUSTOM SUBSET (YOUR OWN COLUMN CHOICE)
# Reads the master_table.csv that's already saved on disk, and
# lets you pick whichever columns you want to make your own CSV.
# Usage:
#   build_custom_subset(['employee_id', 'employee_name', 'salary', 'department_name'],
#                        'my_custom_subset')
# ============================================================

def build_custom_subset(columns, output_name):
    master_path = os.path.join(FOLDER, "master_table.csv")

    if not os.path.exists(master_path):
        print(f"\n⚠️  master_table.csv not found at {master_path}")
        print("Run finalize_pipeline() first so the master table gets built.")
        return None

    master_df = pd.read_csv(master_path)

    missing_cols = [c for c in columns if c not in master_df.columns]
    if missing_cols:
        print(f"\n⚠️  These columns don't exist in master_table.csv: {missing_cols}")
        print("Available columns:", list(master_df.columns))
        return None

    subset_df = master_df[columns]
    path = save_csv(subset_df, f"{output_name}.csv")
    return subset_df


# ============================================================
# Run: python -i verification.py
# Then call run_verification('table_name') for each of the 8
# tables yourself. Only once ALL 8 have PASSED, call
# finalize_pipeline() to insert into the DB + build master + subsets.
# ============================================================
if __name__ == "__main__":
    print("Setup done. Tables to verify:", TABLE_ORDER)
    print("\nHow to use (call one table at a time yourself):")
    print("  jobs_df = run_verification('jobs')")
    print("  emp_df  = run_verification('employees', jobs_df)")
    print("  run_verification('locations')")
    print("  ... (repeat for all 8 tables)")
    print("\nOnce all 8 have PASSED:")
    print("  finalize_pipeline()   # inserts into DB, builds master_table.csv + subset CSVs")
    print("\nWant your OWN custom subset from the master table (your own column picks)?")
    print("  build_custom_subset(['employee_id', 'employee_name', 'salary', 'department_name'], 'my_subset')")
