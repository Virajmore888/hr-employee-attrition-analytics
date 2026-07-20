import os
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

FOLDER = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(FOLDER, "Output", "master_data", "insights_subset.csv")
OUTPUT_DIR = os.path.join(FOLDER, "Output", "charts")
os.makedirs(OUTPUT_DIR, exist_ok=True)


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


def plot_attrition_by_department(df, title="Attrition Rate by Department"):
    sns.set_theme(
        context='talk',
        style='white',
        palette='viridis',
        rc={"axes.spines.right": False, "axes.spines.top": False}
    )
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica', 'sans-serif']
    plt.rcParams['figure.dpi'] = 100

    dept_stats = (
        df.groupby('department_name')['is_active']
          .apply(lambda s: (s == False).mean() * 100)
          .reset_index(name='attrition_rate')
          .sort_values('attrition_rate', ascending=False)
    )

    fig, ax = plt.subplots(figsize=(12, 7), dpi=100)

    sns.barplot(
        data=dept_stats,
        x='department_name',
        y='attrition_rate',
        hue='department_name',
        legend=False,
        estimator='mean',
        errorbar=None,
        capsize=0.1,
        alpha=0.85,
        ax=ax
    )

    for container in ax.containers:
        ax.bar_label(container, fmt='%.1f%%', padding=4, fontsize=10, fontweight='medium')

    overall_avg = dept_stats['attrition_rate'].mean()
    ax.axhline(overall_avg, color='#e74c3c', linestyle='--', linewidth=1.5,
               label=f'Overall Avg: {overall_avg:.1f}%', alpha=0.7)

    ax.set_title(title, loc='left', fontsize=20, pad=20, fontweight='bold')
    ax.set_xlabel("Department", fontsize=12, labelpad=10)
    ax.set_ylabel("Attrition Rate (%)", fontsize=12, labelpad=10)
    plt.xticks(rotation=30, ha='right')

    ax.legend(frameon=False, loc='upper right')

    plt.grid(axis='y', linestyle=':', alpha=0.5)
    plt.tight_layout()

    path = os.path.join(OUTPUT_DIR, "1_attrition_rate_by_department.png")
    plt.savefig(path, dpi=500, transparent=False, bbox_inches="tight")
    print(f"Saved: {path}")
    return plt


def plot_salary_active_vs_exited(df, title="Salary Dispersion: Active vs Exited Employees"):
    sns.set_theme(style="white", context="talk")
    plt.rcParams['figure.dpi'] = 100

    plot_df = df.copy()
    plot_df['employment_status'] = plot_df['is_active'].map({True: 'Active', False: 'Exited'})

    fig, ax = plt.subplots(figsize=(10, 8))

    sns.boxplot(
        data=plot_df,
        x='employment_status',
        y='salary',
        hue='employment_status',
        palette='viridis',
        width=0.5,
        linewidth=2,
        fliersize=6,
        flierprops={"marker": "x", "markeredgecolor": "red"},
        showmeans=True,
        meanprops={"marker": "D", "markerfacecolor": "white", "markeredgecolor": "black", "markersize": "7"},
        legend=False,
        ax=ax
    )

    overall_median = plot_df['salary'].median()
    ax.axhline(overall_median, color='grey', linestyle='--', alpha=0.5,
               label=f'Global Median: {overall_median:,.0f}')

    ax.set_title(title, loc='left', fontsize=22, fontweight='bold', pad=30)
    ax.set_xlabel("Employment Status", fontsize=14, fontweight='semibold')
    ax.set_ylabel("Salary", fontsize=14, fontweight='semibold')

    sns.despine(trim=True)
    ax.grid(axis='y', linestyle=':', alpha=0.3)
    ax.legend(frameon=False, loc='upper right')

    plt.tight_layout()

    path = os.path.join(OUTPUT_DIR, "2_salary_active_vs_exited.png")
    plt.savefig(path, dpi=500, transparent=False, bbox_inches="tight")
    print(f"Saved: {path}")
    return plt


def plot_tenure_distribution(df, title="Employee Tenure Distribution"):
    sns.set_theme(
        style="white",
        context="talk",
        rc={"axes.spines.right": False, "axes.spines.top": False}
    )
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica', 'sans-serif']
    plt.rcParams['figure.dpi'] = 100

    plot_df = df.copy()
    plot_df['employment_status'] = plot_df['is_active'].map({True: 'Active', False: 'Exited'})

    fig, ax = plt.subplots(figsize=(12, 7), dpi=100)

    sns.histplot(
        data=plot_df,
        x='tenure_years',
        hue='employment_status',
        bins=25,
        multiple='dodge',
        stat='percent',
        common_norm=False,
        kde=True,
        palette='viridis',
        shrink=0.8,
        alpha=0.6,
        ax=ax
    )

    mean_val = plot_df['tenure_years'].mean()
    ax.axvline(mean_val, color='#d35400', linestyle='--', linewidth=2, alpha=0.8,
               label=f'Avg: {mean_val:.2f} yrs')
    ax.text(mean_val * 1.02, ax.get_ylim()[1] * 0.9, "Avg: {:.2f} yrs".format(mean_val),
            color='#d35400', fontweight='bold', fontsize=11)

    ax.set_title(title, loc='left', fontsize=22, pad=25, fontweight='bold')
    ax.set_xlabel("Tenure (Years)", fontsize=13, labelpad=12)
    ax.set_ylabel("Proportion of Employees (%)", fontsize=13, labelpad=12)

    ax.legend(title="Employment Status", bbox_to_anchor=(1, 1), loc='upper left', frameon=False)
    ax.grid(axis='y', linestyle='-', alpha=0.1)

    plt.tight_layout()

    path = os.path.join(OUTPUT_DIR, "3_tenure_distribution.png")
    plt.savefig(path, dpi=500, transparent=False, bbox_inches="tight")
    print(f"Saved: {path}")
    return plt


def plot_correlation_heatmap(df, title="Feature Correlation: HR Metrics"):
    sns.set_theme(style="white", context="talk")
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica', 'sans-serif']
    plt.rcParams['figure.dpi'] = 100

    numeric_cols = ['salary', 'distance_from_home_km', 'tenure_years',
                     'performance_rating', 'job_satisfaction',
                     'work_life_balance', 'overtime_hours']
    numeric_cols = [c for c in numeric_cols if c in df.columns]

    corr = df[numeric_cols].corr(numeric_only=True)

    mask = np.triu(np.ones_like(corr, dtype=bool))

    fig, ax = plt.subplots(figsize=(12, 10), dpi=100)
    sns.heatmap(
        corr,
        mask=mask,
        cmap='RdBu_r',
        vmax=1, vmin=-1, center=0,
        annot=True, fmt='.2f',
        square=True,
        linewidths=.8,
        cbar_kws={"shrink": .7, "label": "Pearson Correlation Coefficient"},
        ax=ax
    )

    ax.set_title(title, loc='left', fontsize=22, fontweight='bold', pad=30)
    plt.xticks(rotation=45, ha='right', fontsize=12)
    plt.yticks(rotation=0, fontsize=12)

    plt.tight_layout()

    path = os.path.join(OUTPUT_DIR, "4_correlation_heatmap.png")
    plt.savefig(path, dpi=500, transparent=False, bbox_inches="tight")
    print(f"Saved: {path}")
    return plt


def plot_headcount_by_department_gender(df, title="Headcount by Department & Gender"):
    sns.set_theme(
        context='talk',
        style='white',
        palette='magma',
        rc={"axes.spines.right": False, "axes.spines.top": False}
    )
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica', 'sans-serif']
    plt.rcParams['figure.dpi'] = 100

    headcount = (
        df.groupby(['department_name', 'gender'])
          .size()
          .reset_index(name='headcount')
    )

    fig, ax = plt.subplots(figsize=(12, 7), dpi=100)

    sns.barplot(
        data=headcount,
        x='department_name',
        y='headcount',
        hue='gender',
        estimator='sum',
        errorbar=None,
        capsize=0.1,
        alpha=0.85,
        ax=ax
    )

    for container in ax.containers:
        ax.bar_label(container, fmt='%.0f', padding=4, fontsize=10, fontweight='medium')

    overall_avg = headcount.groupby('department_name')['headcount'].sum().mean()
    ax.axhline(overall_avg, color='#e74c3c', linestyle='--', linewidth=1.5, label='Avg Dept Size', alpha=0.7)

    ax.set_title(title, loc='left', fontsize=20, pad=20, fontweight='bold')
    ax.set_xlabel("Department", fontsize=12, labelpad=10)
    ax.set_ylabel("Headcount", fontsize=12, labelpad=10)
    plt.xticks(rotation=30, ha='right')

    ax.legend(title="Gender", frameon=False, bbox_to_anchor=(1, 1), loc='upper left')

    plt.grid(axis='y', linestyle=':', alpha=0.5)
    plt.tight_layout()

    path = os.path.join(OUTPUT_DIR, "5_headcount_by_department_gender.png")
    plt.savefig(path, dpi=500, transparent=False, bbox_inches="tight")
    print(f"Saved: {path}")
    return plt


def run_all_visuals():
    df = load_insights_subset()
    print(f"Loaded insights_subset.csv: {len(df)} rows, {len(df.columns)} columns")

    plot_attrition_by_department(df)
    plot_salary_active_vs_exited(df)
    plot_tenure_distribution(df)
    plot_correlation_heatmap(df)
    plot_headcount_by_department_gender(df)

    print(f"\nAll 5 charts saved in: {OUTPUT_DIR}/")


if __name__ == "__main__":
    print("Setup done. insights_subset.csv expected at:", DATA_PATH)
    print("Charts will be saved to:", OUTPUT_DIR)
    print("\nRun all 5 charts:  run_all_visuals()")
    print("Or call individually, e.g.:")
    print("  df = load_insights_subset()")
    print("  plot_attrition_by_department(df)")
