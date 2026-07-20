import os
import numpy as np
import pandas as pd

FOLDER = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(FOLDER, "Output", "master_data", "insights_subset.csv")
REPORT_DIR = os.path.join(FOLDER, "Output", "reports")
os.makedirs(REPORT_DIR, exist_ok=True)
REPORT_PATH = os.path.join(REPORT_DIR, "insights_report.txt")


def load_insights_subset():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(
            f"insights_subset.csv not found at {DATA_PATH}\n"
            "Run verification.py -> finalize_pipeline() first to generate it."
        )
    df = pd.read_csv(DATA_PATH)
    df['hire_date'] = pd.to_datetime(df['hire_date'], errors='coerce')
    df['exit_date'] = pd.to_datetime(df['exit_date'], errors='coerce')
    return df


def q1_overall_attrition_rate(df):
    is_active = df['is_active'].to_numpy()
    rate = np.mean(is_active == False) * 100
    line = f"Q1. What is the overall attrition rate?\n-> {rate:.2f}% of employees have left the company."
    return line, rate


def q2_department_with_highest_attrition(df):
    depts = df['department_name'].unique()
    rates = {}
    for d in depts:
        mask = (df['department_name'] == d).to_numpy()
        is_active = df.loc[mask, 'is_active'].to_numpy()
        rates[d] = np.mean(is_active == False) * 100

    dept_names = np.array(list(rates.keys()))
    dept_rates = np.array(list(rates.values()))
    top_idx = np.argmax(dept_rates)

    line = (
        f"Q2. Which department has the highest attrition rate?\n"
        f"-> {dept_names[top_idx]} has the highest attrition rate at {dept_rates[top_idx]:.2f}%."
    )
    return line, (dept_names[top_idx], dept_rates[top_idx])


def q3_salary_gap_active_vs_exited(df):
    active_salary = df.loc[df['is_active'] == True, 'salary'].to_numpy()
    exited_salary = df.loc[df['is_active'] == False, 'salary'].to_numpy()

    active_mean = np.mean(active_salary)
    exited_mean = np.mean(exited_salary)
    active_median = np.median(active_salary)
    exited_median = np.median(exited_salary)
    gap = active_mean - exited_mean

    direction = "higher" if gap > 0 else "lower"
    line = (
        f"Q3. Is there a salary gap between active and exited employees?\n"
        f"-> Active employees earn {abs(gap):,.0f} on average {direction} than exited employees.\n"
        f"   Active: mean={active_mean:,.0f}, median={active_median:,.0f}\n"
        f"   Exited: mean={exited_mean:,.0f}, median={exited_median:,.0f}"
    )
    return line, gap


def q4_average_tenure(df):
    all_tenure = df['tenure_years'].to_numpy()
    exited_tenure = df.loc[df['is_active'] == False, 'tenure_years'].to_numpy()

    overall_avg = np.mean(all_tenure)
    exited_avg = np.mean(exited_tenure)

    line = (
        f"Q4. What is the average employee tenure?\n"
        f"-> On average, employees stay {overall_avg:.2f} years.\n"
        f"   Employees who left stayed {exited_avg:.2f} years on average before leaving."
    )
    return line, (overall_avg, exited_avg)


def q5_attrition_by_gender(df):
    genders = df['gender'].unique()
    rates = {}
    for g in genders:
        mask = (df['gender'] == g).to_numpy()
        is_active = df.loc[mask, 'is_active'].to_numpy()
        rates[g] = np.mean(is_active == False) * 100

    gender_names = np.array(list(rates.keys()))
    gender_rates = np.array(list(rates.values()))
    top_idx = np.argmax(gender_rates)

    lines = [f"Q5. Is attrition different between genders?"]
    for g, r in zip(gender_names, gender_rates):
        lines.append(f"   {g}: {r:.2f}% attrition rate")
    lines.append(f"-> {gender_names[top_idx]} employees leave more often, at {gender_rates[top_idx]:.2f}%.")
    line = "\n".join(lines)
    return line, dict(zip(gender_names, gender_rates))


def q6_satisfaction_performance_link(df):
    valid = df.dropna(subset=['job_satisfaction', 'performance_rating'])
    x = valid['job_satisfaction'].to_numpy()
    y = valid['performance_rating'].to_numpy()

    corr_matrix = np.corrcoef(x, y)
    corr = corr_matrix[0, 1]

    if abs(corr) < 0.1:
        strength = "almost no link"
    elif abs(corr) < 0.3:
        strength = "a weak link"
    elif abs(corr) < 0.6:
        strength = "a moderate link"
    else:
        strength = "a strong link"

    line = (
        f"Q6. Are happier employees also better performers?\n"
        f"-> The correlation between job satisfaction and performance rating is {corr:.2f}.\n"
        f"   This means there is {strength} between the two."
    )
    return line, corr


def q7_highest_paid_job_title(df):
    titles = df['job_title'].unique()
    avg_salaries = {}
    for t in titles:
        mask = (df['job_title'] == t).to_numpy()
        avg_salaries[t] = np.mean(df.loc[mask, 'salary'].to_numpy())

    title_names = np.array(list(avg_salaries.keys()))
    title_salaries = np.array(list(avg_salaries.values()))
    top_idx = np.argmax(title_salaries)

    line = (
        f"Q7. Which job title earns the most on average?\n"
        f"-> {title_names[top_idx]} has the highest average salary at {title_salaries[top_idx]:,.0f}."
    )
    return line, (title_names[top_idx], title_salaries[top_idx])


def q8_overtime_vs_attrition(df):
    valid = df.dropna(subset=['overtime_hours'])
    active_ot = valid.loc[valid['is_active'] == True, 'overtime_hours'].to_numpy()
    exited_ot = valid.loc[valid['is_active'] == False, 'overtime_hours'].to_numpy()

    active_avg = np.mean(active_ot)
    exited_avg = np.mean(exited_ot)

    if exited_avg > active_avg:
        conclusion = "Employees who left worked more overtime on average. This suggests overwork may be linked to attrition."
    else:
        conclusion = "Employees who left did not work more overtime on average. Overtime does not appear to be a major driver of attrition here."

    line = (
        f"Q8. Do employees who work more overtime leave more often?\n"
        f"-> Active employees: {active_avg:.2f} avg overtime hours.\n"
        f"   Exited employees: {exited_avg:.2f} avg overtime hours.\n"
        f"   {conclusion}"
    )
    return line, (active_avg, exited_avg)


def run_all_insights():
    df = load_insights_subset()

    header = "=" * 70 + "\nHR INSIGHTS REPORT\n" + "=" * 70 + "\n"
    footer = "\n" + "=" * 70 + f"\nReport generated from {len(df)} employee records.\n" + "=" * 70

    questions = [
        q1_overall_attrition_rate,
        q2_department_with_highest_attrition,
        q3_salary_gap_active_vs_exited,
        q4_average_tenure,
        q5_attrition_by_gender,
        q6_satisfaction_performance_link,
        q7_highest_paid_job_title,
        q8_overtime_vs_attrition,
    ]

    all_lines = [header]
    for fn in questions:
        line, _ = fn(df)
        print(line)
        print()
        all_lines.append(line)
        all_lines.append("")

    all_lines.append(footer)
    print(footer)

    with open(REPORT_PATH, "w") as f:
        f.write("\n".join(all_lines))

    print(f"\nSaved report to: {REPORT_PATH}")


if __name__ == "__main__":
    run_all_insights()
