<div align="center">

# 👥 HR Employee Attrition Analytics

### *915 employee records. 8 linked HR tables. 6 visual insights that explain why people leave.*

---

<!-- Tech Stack -->
![Python](https://img.shields.io/badge/Python-3.10%20|%203.11%20|%203.12%20|%203.13-3776AB?style=for-the-badge&logo=python&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-8.0+-4479A1?style=for-the-badge&logo=mysql&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-1.3+-150458?style=for-the-badge&logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-1.21+-013243?style=for-the-badge&logo=numpy&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-3.4+-11557c?style=for-the-badge&logo=python&logoColor=white)
![Seaborn](https://img.shields.io/badge/Seaborn-0.11+-4c72b0?style=for-the-badge&logo=python&logoColor=white)

<!-- Links -->
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Viraj%20More-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/viraj-uttam-more-a24a80391)
[![Email](https://img.shields.io/badge/Email-Contact%20Me-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:virajmore.data888@gmail.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](./LICENSE)

---

**[📊 Presentation](docs/HR_Analysis_Presentation.pdf) · [📝 Full Report](docs/HR_Analysis_Report.pdf) · [💻 Data](data/) · [📦 Output](Output/) · [📦 Requirements](requirements.txt) · [🤝 Contributing](CONTRIBUTING.md)**

</div>

---

## 👋 About This Project

This is an **end to end HR analytics pipeline** built entirely on **MySQL and Python**, going from raw relational data all the way to a stakeholder ready report and presentation.

Employee attrition is one of the most expensive, and most preventable, problems a company can face. Every employee who leaves takes hiring cost, training investment, and institutional knowledge with them. Most HR teams feel this pain but rarely have a structured, queryable view of it.

This project treats HR data the way a real company would store it: split across 8 separate relational tables (employees, departments, jobs, locations, job history, performance reviews, attendance, and attrition) rather than one flat spreadsheet. The pipeline builds the schema in MySQL, populates it with realistic and intentionally messy data, cleans and verifies it, joins everything into a single master table, and then answers concrete business questions with charts and a written report.

> If you are a recruiter or fellow analyst, the TL;DR below tells you everything in 30 seconds. The rest of the README is for anyone who wants the full pipeline detail.

---

## ⚡ TL;DR - 6 Findings That Explain Attrition

| # | Finding | Business Impact |
|---|---------|----------------|
| 1 | 📉 **15.96% overall attrition rate** across 915 employees | Roughly 1 in 6 employees leaves, a clear retention gap to close |
| 2 | 🏭 **Research & Development has the highest attrition** at 19.20% | Retention efforts should be targeted at R&D first, not applied company wide |
| 3 | ⏱️ **Overtime is linked to exits** - exited employees averaged 1.15 hrs vs 1.08 hrs for active staff | Overwork is a measurable, actionable attrition driver |
| 4 | 💰 Active employees earn **452 more on average** than exited employees | Pay gap is real but modest, tenure and overtime matter more than salary alone |
| 5 | 📆 Employees who left had stayed **6.18 years on average**, well short of the **8.13 year** company average tenure | Attrition risk concentrates before the 7 year mark |
| 6 | 🧑‍🤝‍🧑 Men leave slightly more often than women (**16.75% vs 15.27%**) | Gender gap exists but is small next to department and overtime effects |

---

## 🎯 What Makes This Project Different

Most HR attrition projects work off a single pre-cleaned CSV. This one builds the database first.

| Typical HR Project | This Project |
|---|---|
| Starts from one flat CSV | Starts from an 8-table relational MySQL schema, joined from scratch |
| Cleans one dataset | Cleans and verifies 8 tables independently, then rebuilds a verified database |
| Shows attrition percentage | Breaks attrition down by department, gender, tenure, and overtime |
| Notebook with mixed logic | Modular pipeline: fetch, clean, explore, verify, visualize, and report as separate scripts |
| One-off analysis | Reusable pipeline, rerun it against any new export of the same schema |

---

## 💡 Key Business Insights

### 1. 📉 Overall Attrition Rate

Out of 915 employees, **15.96% have left the company**. This is the headline number every department head should be tracking, and it is the baseline every other finding in this report compares against.

---

### 2. 🏭 Department-Wise Attrition

**Research & Development has the highest attrition rate at 19.20%**, noticeably above the company average. This points to department-specific pressure, whether that is workload, management style, or career growth, rather than a company-wide culture problem.

---

### 3. 💰 Salary Gap Between Active and Exited Employees

Active employees earn **452 more on average** than employees who exited (active mean 61,338 vs exited mean 60,886). The gap exists but is small, which suggests pay alone is not the main driver of attrition here, other factors carry more weight.

---

### 4. 📆 Employee Tenure

The average employee stays **8.13 years**, but employees who eventually left had only stayed **6.18 years on average** before exiting. Retention efforts have the biggest window of opportunity in an employee's first six to seven years.

---

### 5. 🧑‍🤝‍🧑 Attrition by Gender

Male employees leave at a **16.75%** rate compared to **15.27%** for female employees. The gap is real but modest, department and overtime effects are larger levers for reducing attrition than gender-targeted programs.

---

### 6. ⏱️ Overtime and Attrition

Employees who left worked more overtime on average (**1.15 hours**) than active employees (**1.08 hours**). It is a small gap, but a consistent one, and it lines up with the intuitive story that overwork pushes people out the door.

---

## 📋 Key Metrics At A Glance

| Metric | Value |
|--------|-------|
| **Total Employees** | 915 |
| **Overall Attrition Rate** | 15.96% |
| **Highest Attrition Department** | Research & Development (19.20%) |
| **Average Tenure (all employees)** | 8.13 years |
| **Average Tenure (exited employees)** | 6.18 years |
| **Male Attrition Rate** | 16.75% |
| **Female Attrition Rate** | 15.27% |
| **Highest Paying Role** | IT Manager (avg. 78,599) |
| **Active vs Exited Salary Gap** | 452 |
| **Job Satisfaction vs Performance Correlation** | 0.00 (no meaningful link) |
| **Total Departments** | 8 |
| **Total Job Titles** | 30 |
| **Office Locations** | 12 cities across India |

---

## ⚙️ Technical Architecture

Built as a fully relational pipeline rather than a single-table analysis, so the project mirrors how HR data actually lives inside a real company's systems.

| Technique | Implementation Detail |
|---|---|
| **Relational Schema Design** | 8 linked MySQL tables (locations, departments, jobs, employees, job_history, performance_reviews, attendance, attrition) with primary and foreign keys |
| **Data Cleaning** | Duplicate department IDs merged, inconsistent categorical values standardized, nulls handled per table via `cleaning.py` |
| **Verification Layer** | Cleaned tables re-checked and inserted into a brand new verified MySQL database (`verification.py`), separate from the raw source |
| **Master Table Construction** | All 8 tables joined into one 26-column master table using `ROW_NUMBER()` window functions to avoid row duplication on tied dates |
| **Exploratory Data Analysis** | Per-table categorical and numeric distribution plots plus correlation matrices via `EDA.py` |
| **Business Insight Generation** | 8 HR questions answered with `numpy` in `insights.py`, printed and saved as a text report |
| **Visualization** | 5 recruiter-ready charts built with `matplotlib` and `seaborn` in `visualization.py` |

---

## 🛠️ Skills Demonstrated

`Python` · `MySQL` · `SQLAlchemy` · `Pandas` · `NumPy` · `Matplotlib` · `Seaborn` · `Relational Database Design` · `Data Cleaning` · `Data Verification` · `Exploratory Data Analysis` · `Window Functions` · `Business Intelligence` · `Data Visualization`

---

## 🚀 Run This Project Locally

### Prerequisites
- Python 3.10 to 3.13
- MySQL 8.0 or higher (needed for window functions)
- pip

### Step 1: Clone
```bash
git clone https://github.com/Virajmore888/hr-employee-attrition-analytics.git
cd hr-employee-attrition-analytics
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Set Up the Database
```bash
mysql -u root -p < data/hr_employees_schema.sql
mysql -u root -p < data/hr_employees_data.sql
```

### Step 4: Configure Environment Variables
```bash
cp .env.example .env
# then fill in DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME, CLEAN_DB_NAME
```

### Step 5: Run the Pipeline
```bash
python fetch.py          # verifies the database connection
python cleaning.py       # cleans raw tables -> Output/cleaned_data/
python EDA.py             # exploratory plots -> Output/eda_plots/
python verification.py   # builds the verified DB and master table -> Output/master_data/
python visualization.py  # final charts -> Output/charts/
python insights.py       # insights report -> Output/reports/
```

---

## 📦 Dependencies

📄 [View requirements.txt](requirements.txt)

```
pandas
numpy
matplotlib
seaborn
sqlalchemy
pymysql
python-dotenv
```

---

## 📊 Dataset At A Glance

| Attribute | Value |
|---|---|
| **Source** | Custom-built MySQL schema with realistic, intentionally messy sample data |
| **Total Employee Records** | 915 |
| **Related Tables** | 8 (locations, departments, jobs, employees, job_history, performance_reviews, attendance, attrition) |
| **Attendance Records** | 8,400 |
| **Performance Reviews** | 1,848 |
| **Job History Entries** | 1,307 |
| **Master Table Columns** | 26 (after joining all 8 tables) |
| **Total Nulls After Cleaning** | 0 in the master table (actionable dataset) |

---

## 📂 Repository Structure

```
hr-employee-attrition-analytics/
|
+-- data/
|   +-- hr_employees_schema.sql        # Raw database schema, 8 tables
|   +-- hr_employees_data.sql          # Sample data for the raw database
|   +-- hr_employees_joins.sql         # Reference join queries
|   +-- master_table.sql               # SQL version of the master join
|
+-- python/
|   +-- fetch.py                       # SQLAlchemy engine from .env credentials
|   +-- cleaning.py                    # Cleans each raw table
|   +-- EDA.py                         # Exploratory data analysis and plots
|   +-- verification.py                # Verifies cleaned data, builds master table
|   +-- visualization.py               # 5 final insight charts
|   +-- insights.py                    # 8 HR questions answered, saved as report
|
+-- Output/
|   +-- cleaned_data/                  # 8 cleaned CSVs
|   +-- master_data/                   # master_table.csv plus 5 subset CSVs
|   +-- eda_plots/                     # Per-table exploratory plots
|   +-- charts/                        # 5 final insight charts
|   +-- reports/                       # insights_report.txt
|
+-- docs/
|   +-- HR_Analysis_Report.pdf         # Full written report
|   +-- HR_Analysis_Presentation.pdf   # Stakeholder-ready slide deck
|
+-- requirements.txt
+-- CONTRIBUTING.md
+-- .env.example
+-- .gitignore
+-- README.md
```

---

## 🤝 Connect & Contribute

- 🔗 **LinkedIn:** [Viraj More](https://www.linkedin.com/in/viraj-uttam-more-a24a80391)
- 📧 **Email:** [virajmore.data888@gmail.com](mailto:virajmore.data888@gmail.com)
- 💻 **GitHub:** [hr-employee-attrition-analytics](https://github.com/Virajmore888/hr-employee-attrition-analytics)

Found something to improve? Open an **Issue** or submit a **Pull Request**, contributions are welcome.
Read the **[Contributing Guide](CONTRIBUTING.md)** before submitting.

---

## 📄 License

MIT License, see [LICENSE](./LICENSE) for details.

---

<div align="center">

**Built end to end with Python and MySQL**

*If this project added value, consider leaving a ⭐ on the repo, it helps others find it too.*

</div>
