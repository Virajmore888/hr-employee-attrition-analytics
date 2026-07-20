# Import required libraries
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Save plots to file instead of opening a window (safe for mobile)
import matplotlib.pyplot as plt
import seaborn as sns
import os

from fetch import get_engine

# Connect to database
engine = get_engine()

# Folder where all plots will be saved
FOLDER = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(FOLDER, "Output", "eda_plots")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# All tables from the schema
TABLES = ['locations', 'departments', 'jobs', 'employees',
          'job_history', 'performance_reviews', 'attendance', 'attrition']

# Columns ending with "_id" are identifiers, not real numeric data
ID_SUFFIXES = ('_id',)


# Function to load any table into a DataFrame
def get_table(table_name):
    query = "SELECT * FROM " + table_name
    df = pd.read_sql(query, engine)
    return df


# Function to run statistical EDA on a table
def data_exploration(df, name):

    print("=" * 70)
    print("NOW PROCESSING TABLE:", name)
    print("=" * 70)

    # Show first 5 rows
    print("\nFirst 5 Rows")
    print(df.head())

    # Show column data types and non-null counts
    print("\nData Info")
    df.info()

    # Show number of rows and columns
    print("\nShape:", df.shape)

    # Show memory usage per column and total (raw, before any optimization)
    print("\nMemory Usage")
    mem_usage = df.memory_usage(deep=True)
    print(mem_usage)
    print("Total Memory (MB):", round(mem_usage.sum() / (1024**2), 2))

    # Show all column names
    print("\nColumn Names:", list(df.columns))

    # Show missing values count and percentage
    print("\nMissing Values (count + percentage)")
    missing = pd.DataFrame({
        "missing_count": df.isnull().sum(),
        "missing_pct": (df.isnull().mean() * 100).round(2)
    })
    print(missing[missing["missing_count"] > 0])
    print("Total Missing Values:", df.isnull().sum().sum())

    # Show number of duplicate rows
    print("\nDuplicate Rows:", df.duplicated().sum())

    # Show number of unique values per column
    print("\nUnique Values per Column")
    print(df.nunique())

    # Separate columns into groups: id, numeric, date, category
    id_cols = [c for c in df.columns if c.endswith(ID_SUFFIXES)]
    numeric_cols = [c for c in df.select_dtypes(include=['int64', 'float64']).columns
                     if c not in id_cols]
    date_cols = df.select_dtypes(include=['datetime64[ns]']).columns.tolist()
    cat_cols = df.select_dtypes(include='object').columns.tolist()

    # Show descriptive statistics only for real numeric columns (not id columns)
    if numeric_cols:
        print("\nDescriptive Statistics (numeric columns, id columns excluded)")
        print(df[numeric_cols].describe())

    # Go through each column one by one for detailed analysis
    print("\nColumn Wise Analysis")
    for col in df.columns:

        print("\n--- Column:", col, "---")
        print("Data Type:", df[col].dtype)
        print("Missing Values:", df[col].isnull().sum())

        # ID column: skip statistics, not meaningful
        if col in id_cols:
            print("Type: ID column, skipping statistics")

        # Date column: show earliest, latest, and range
        elif col in date_cols:
            print("Min Date:", df[col].min())
            print("Max Date:", df[col].max())
            print("Range (days):", (df[col].max() - df[col].min()).days)

        # Category column: show unique values and counts
        elif col in cat_cols:
            n_unique = df[col].nunique()
            print("Unique Count:", n_unique)
            if n_unique <= 30:
                print("Value Counts:")
                print(df[col].value_counts(dropna=False))
            else:
                print("Too many unique values to display fully")
                print("Top 5 Value Counts:")
                print(df[col].value_counts(dropna=False).head())

        # Numeric column: show summary stats and outlier count
        elif col in numeric_cols:
            print("Min:", df[col].min())
            print("Max:", df[col].max())
            print("Mean:", round(df[col].mean(), 2))
            print("Median:", df[col].median())
            print("Std Dev:", round(df[col].std(), 2))

            # Detect outliers using the IQR method
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR
            outliers = df[(df[col] < lower) | (df[col] > upper)]
            print("Outliers (IQR method):", len(outliers))

        else:
            print("Min:", df[col].min())
            print("Max:", df[col].max())


# Function to create visual plots for a table
def visualize_table(df, name):

    print(f"\n[VISUALIZING] {name}")

    id_cols = [c for c in df.columns if c.endswith(ID_SUFFIXES)]
    numeric_cols = [c for c in df.select_dtypes(include=['int64', 'float64']).columns
                     if c not in id_cols]
    cat_cols = df.select_dtypes(include='object').columns.tolist()

    # Create a separate folder for this table's plots
    table_dir = os.path.join(OUTPUT_DIR, name)
    os.makedirs(table_dir, exist_ok=True)

    # Plot histogram and boxplot for each numeric column
    for col in numeric_cols:
        if df[col].dropna().empty:
            continue

        fig, axes = plt.subplots(1, 2, figsize=(10, 4))

        sns.histplot(df[col].dropna(), kde=True, ax=axes[0])
        axes[0].set_title(f"{col} - Distribution")

        sns.boxplot(x=df[col].dropna(), ax=axes[1])
        axes[1].set_title(f"{col} - Outliers")

        plt.tight_layout()
        plt.savefig(os.path.join(table_dir, f"{col}_numeric.png"))
        plt.close()

    # Plot count of values for low-cardinality category columns only
    for col in cat_cols:
        n_unique = df[col].nunique()
        if n_unique == 0 or n_unique > 20:
            continue  # skip columns like email, phone_number, reason (too many unique values)

        plt.figure(figsize=(8, 4))
        order = df[col].value_counts().index
        sns.countplot(y=df[col], order=order)
        plt.title(f"{col} - Value Counts")
        plt.tight_layout()
        plt.savefig(os.path.join(table_dir, f"{col}_categorical.png"))
        plt.close()

    # Plot correlation heatmap if there are at least 2 numeric columns
    if len(numeric_cols) >= 2:
        plt.figure(figsize=(6, 5))
        corr = df[numeric_cols].corr()
        sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f")
        plt.title(f"{name} - Correlation Matrix")
        plt.tight_layout()
        plt.savefig(os.path.join(table_dir, "correlation_matrix.png"))
        plt.close()

    print(f"Plots saved in: {table_dir}/")


# Function to check for invalid foreign key references (orphan records)
def check_foreign_key(child_df, child_col, parent_df, parent_col, child_name, parent_name):
    child_ids = set(child_df[child_col].dropna())
    parent_ids = set(parent_df[parent_col].dropna())
    orphans = child_ids - parent_ids

    print(f"\n[FOREIGN KEY CHECK] {child_name}.{child_col} -> {parent_name}.{parent_col}")
    print("Invalid references found:", len(orphans))
    if orphans:
        print("Sample invalid values:", list(orphans)[:10])


# Function to check business logic rules based on the schema
# Needs a dictionary of DataFrames, build it manually when needed:
# dfs = {"employees": get_table("employees"), "jobs": get_table("jobs"),
#        "attrition": get_table("attrition"), "job_history": get_table("job_history")}
def business_logic_checks(dfs):

    print("\n" + "=" * 70)
    print("BUSINESS LOGIC CHECKS")
    print("=" * 70)

    emp = dfs['employees']
    jobs = dfs['jobs']
    attr = dfs['attrition']
    hist = dfs['job_history']

    # Check 1: salary should be within the job's min and max salary range
    merged = emp.merge(jobs, on='job_id', how='left')
    violation = merged[(merged['salary'] < merged['min_salary']) |
                        (merged['salary'] > merged['max_salary'])]
    print("\nEmployees with salary outside job's min/max range:", len(violation))

    # Check 2: is_active is False but exit_date is missing (inconsistent data)
    inconsistent1 = attr[(attr['is_active'] == False) & (attr['exit_date'].isnull())]
    print("Attrition rows: is_active=False but exit_date is NULL:", len(inconsistent1))

    # Check 3: is_active is True but exit_date is filled (inconsistent data)
    inconsistent2 = attr[(attr['is_active'] == True) & (attr['exit_date'].notnull())]
    print("Attrition rows: is_active=True but exit_date is present:", len(inconsistent2))

    # Check 4: end_date should never be before start_date
    bad_dates = hist[hist['end_date'] < hist['start_date']]
    print("job_history rows with end_date before start_date:", len(bad_dates))

    # Check 5: an employee should not be their own manager
    self_manager = emp[emp['employee_id'] == emp['manager_id']]
    print("Employees who are their own manager:", len(self_manager))


# ============================================================
# SECTION: CALL TABLES ONE BY ONE (manual, no auto loop)
# Prints the table name, then runs data_exploration() +
# visualize_table() for JUST that one table.
# Usage:  run_eda('employees')
# ============================================================

def run_eda(table_name):
    print("\n" + "#" * 70)
    print(f"# TABLE: {table_name}")
    print("#" * 70)

    df = get_table(table_name)
    data_exploration(df, table_name)
    visualize_table(df, table_name)

    return df


# Main program: only sets up tools, does NOT auto-run any table
# Run this file with: python -i EDA.py
# Then call run_eda('table_name') for whichever table you want
if __name__ == "__main__":

    print("Setup done. Available tables:", TABLES)
    print("\nHow to use (call one table at a time yourself):")
    print("  df = run_eda('employees')")
    print("  df = run_eda('jobs')")
    print("\nFor foreign key / business logic checks, build a dict manually:")
    print("  dfs = {'employees': get_table('employees'), 'jobs': get_table('jobs'), ...}")
    print("  business_logic_checks(dfs)")
