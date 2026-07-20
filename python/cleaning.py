# Import required libraries
import os
import pandas as pd
from fetch import get_engine

# Connect to database
engine = get_engine()

# Folder where cleaned CSVs get saved (Output/cleaned_data next to this
# script — same folder verification.py reads from)
FOLDER = os.path.dirname(os.path.abspath(__file__))
CLEANED_DIR = os.path.join(FOLDER, "Output", "cleaned_data")
os.makedirs(CLEANED_DIR, exist_ok=True)

# Mapping of duplicate department IDs to the main department ID
# HR(2) is the same real department as Human Resources(9)
# Ops(7) is the same real department as Operations(10)
DEPT_ID_MAP = {2: 9, 7: 10}

# All tables from the schema, in an order that respects dependencies
# (jobs must be cleaned before employees, since employees needs jobs_df)
TABLES = ['locations', 'departments', 'jobs', 'employees',
          'job_history', 'performance_reviews', 'attendance', 'attrition']


# Function to load any table into a DataFrame
def get_table(table_name):
    query = "SELECT * FROM " + table_name
    df = pd.read_sql(query, engine)
    return df


# Function to save a cleaned DataFrame as CSV
# Filename pattern matches what verification.py expects: <table>_cleaned.csv
def save_cleaned_csv(df, table_name):
    path = os.path.join(CLEANED_DIR, f"{table_name}_cleaned.csv")
    df.to_csv(path, index=False)
    print(f"Saved: {path} ({len(df)} rows)")
    return path


# Function to optimize memory usage of a DataFrame
# This runs AFTER cleaning, so wrong values don't get locked into small dtypes
def optimize_memory(df):

    before_mb = df.memory_usage(deep=True).sum() / (1024 ** 2)

    for col in df.columns:

        # Downcast integer columns to the smallest type that fits the values
        if df[col].dtype == 'int64':
            df[col] = pd.to_numeric(df[col], downcast='integer')

        # Downcast float columns to the smallest type that fits the values
        elif df[col].dtype == 'float64':
            df[col] = pd.to_numeric(df[col], downcast='float')

        # Convert text columns with few unique values into category type
        # (saves a lot of memory, e.g. gender, status, department_name)
        elif df[col].dtype == 'object':
            n_unique = df[col].nunique()
            n_total = len(df[col])
            if n_total > 0 and (n_unique / n_total) < 0.5:
                df[col] = df[col].astype('category')

    after_mb = df.memory_usage(deep=True).sum() / (1024 ** 2)

    print(f"Memory before: {round(before_mb, 3)} MB")
    print(f"Memory after:  {round(after_mb, 3)} MB")
    print(f"Reduced by:    {round(before_mb - after_mb, 3)} MB")

    return df


# Function to standardize text columns (fix casing and extra spaces)
def standardize_text(df, columns):
    for col in columns:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.title()
    return df


# Function to clean the locations table
def clean_locations(df):

    print("\nCleaning: locations")

    # Fix inconsistent casing (MUMBAI, kolkata, HYDERABAD -> Mumbai, Kolkata, Hyderabad)
    df = standardize_text(df, ['city', 'state', 'country'])

    df = df.drop_duplicates()

    return df


# Function to clean the departments table
def clean_departments(df):

    print("\nCleaning: departments")

    # Fix casing
    df = standardize_text(df, ['department_name'])

    # Title-case breaks acronyms, fix them back
    acronym_fix = {'It': 'IT', 'Hr': 'HR'}
    df['department_name'] = df['department_name'].replace(acronym_fix)

    # HR and Human Resources (also Ops and Operations) are the SAME real
    # department entered twice with different IDs. Merge them by remapping
    # the duplicate ID to the main ID, then dropping the now-duplicate row.
    df['department_id'] = df['department_id'].replace(DEPT_ID_MAP)

    # Bug fix: drop_duplicates() keeps whichever row appears FIRST in the
    # dataframe. Since the abbreviation ("HR", "Ops") happened to appear
    # before the full name ("Human Resources", "Operations") in the raw
    # data, the abbreviation was surviving instead of the full name.
    # Sorting by name length (longest first) before dropping duplicates
    # guarantees the full name is always kept.
    df = df.sort_values('department_name', key=lambda s: s.str.len(), ascending=False)
    df = df.drop_duplicates(subset='department_id')
    df = df.sort_values('department_id').reset_index(drop=True)

    return df


# Function to clean the jobs table
def clean_jobs(df):

    print("\nCleaning: jobs")

    df = standardize_text(df, ['job_title'])

    # Title-case breaks acronyms in job titles too (e.g. "It Manager"),
    # same issue as department_name in clean_departments()
    df['job_title'] = df['job_title'].str.replace(r'\bIt\b', 'IT', regex=True)
    df['job_title'] = df['job_title'].str.replace(r'\bHr\b', 'HR', regex=True)

    df = df.drop_duplicates()

    return df


# Function to clean the employees table
def clean_employees(df, jobs_df):

    print("\nCleaning: employees")

    # Fix casing on text columns (gender handled separately below)
    df = standardize_text(df, ['first_name', 'last_name', 'marital_status',
                                'education_level', 'business_travel'])

    # Fix gender abbreviations before standardizing case
    gender_map = {'M': 'Male', 'F': 'Female', 'male': 'Male', 'female': 'Female'}
    df['gender'] = df['gender'].replace(gender_map)
    df['gender'] = df['gender'].astype(str).str.strip().str.title()

    # Update department_id for employees pointing to a duplicate department
    # that got merged in clean_departments()
    df['department_id'] = df['department_id'].replace(DEPT_ID_MAP)

    # Missing email: cannot guess it, so flag it clearly instead of leaving blank
    df['email'] = df['email'].fillna('MISSING')

    # Missing salary: fill using the median salary of the same job role
    df['salary'] = df.groupby('job_id')['salary'].transform(
        lambda x: x.fillna(x.median())
    )
    # If still missing (job had no other salary data), fill with overall median
    df['salary'] = df['salary'].fillna(df['salary'].median())

    # manager_id missing is NOT an error — top-level employees have no manager
    # so we leave those as NULL on purpose

    # distance_from_home_km should never be negative (EDA found min = -52).
    # Likely a sign entry error, so take the absolute value instead of
    # dropping the row.
    df['distance_from_home_km'] = df['distance_from_home_km'].abs()

    # Fix salary values that fall outside their job's min/max range.
    # Correct them into the valid range instead of dropping the row -
    # using .loc[] so each correction is targeted and countable, rather
    # than a blanket .clip() that hides how many rows were actually wrong.
    df = df.merge(jobs_df[['job_id', 'min_salary', 'max_salary']], on='job_id', how='left')

    below_min = df['salary'] < df['min_salary']
    above_max = df['salary'] > df['max_salary']
    print(f"  Salary below job min: {below_min.sum()} rows -> raised to min_salary")
    print(f"  Salary above job max: {above_max.sum()} rows -> capped to max_salary")

    df.loc[below_min, 'salary'] = df.loc[below_min, 'min_salary']
    df.loc[above_max, 'salary'] = df.loc[above_max, 'max_salary']

    df = df.drop(columns=['min_salary', 'max_salary'])

    df = df.drop_duplicates()

    return df


# Function to clean the job_history table
def clean_job_history(df):

    print("\nCleaning: job_history")

    # Update department_id for rows pointing to a duplicate department
    df['department_id'] = df['department_id'].replace(DEPT_ID_MAP)

    # end_date being NULL is normal (means the role is still ongoing)
    df = df.drop_duplicates()

    return df


# Function to clean the performance_reviews table
def clean_performance_reviews(df):

    print("\nCleaning: performance_reviews")

    df = df.drop_duplicates()

    return df


# Function to clean the attendance table
def clean_attendance(df):

    print("\nCleaning: attendance")

    df = standardize_text(df, ['status'])

    # overtime_hours should never be negative, fix any bad values
    df['overtime_hours'] = df['overtime_hours'].clip(lower=0)

    df = df.drop_duplicates()

    return df


# Function to clean the attrition table
def clean_attrition(df):

    print("\nCleaning: attrition")

    # Missing reason: fill with a clear label instead of blank
    df['reason'] = df['reason'].fillna('Not Specified')
    df = standardize_text(df, ['reason'])

    df = df.drop_duplicates()

    return df


# ============================================================
# SECTION: CALL TABLES ONE BY ONE (manual, no auto loop)
# Prints the table name, cleans that ONE table, optimizes
# memory, and saves it via save_cleaned_csv().
# Usage:
#   jobs_df = run_cleaning('jobs')
#   emp_df  = run_cleaning('employees', jobs_df)   # employees needs jobs_df
# ============================================================

CLEAN_FUNCS = {
    'locations': clean_locations,
    'departments': clean_departments,
    'jobs': clean_jobs,
    'job_history': clean_job_history,
    'performance_reviews': clean_performance_reviews,
    'attendance': clean_attendance,
    'attrition': clean_attrition,
}


def run_cleaning(table_name, jobs_df=None):
    print("\n" + "#" * 70)
    print(f"# TABLE: {table_name}")
    print("#" * 70)

    df = get_table(table_name)

    if table_name == 'employees':
        # employees cleaning needs an already-cleaned jobs_df for the
        # salary min/max check. If not passed in, clean jobs ourselves.
        if jobs_df is None:
            jobs_df = run_cleaning('jobs')
        df = clean_employees(df, jobs_df)
    else:
        df = CLEAN_FUNCS[table_name](df)

    df = optimize_memory(df)
    save_cleaned_csv(df, table_name)

    return df


# Main program: only sets up tools, does NOT auto-run any table
# Run this file with: python -i cleaning.py
# Then call run_cleaning('table_name') for whichever table you want
if __name__ == "__main__":

    print("Setup done. Available tables:", TABLES)
    print("\nHow to use (call one table at a time yourself):")
    print("  jobs_df = run_cleaning('jobs')")
    print("  emp_df  = run_cleaning('employees', jobs_df)")
    print("  loc_df  = run_cleaning('locations')")
    print("\nNote: department_id 2->9 and 7->10 are auto-merged in cleaning")
    print("      (HR->Human Resources, Ops->Operations)")
    print("\nRun run_cleaning() for ALL 8 tables before running verification.py")
