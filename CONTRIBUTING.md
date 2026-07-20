# Contributing

Thanks for your interest in this project! This is primarily a personal
portfolio project, but suggestions and improvements are welcome.

## Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/<your-username>/hr-employee-analytics.git
   cd hr-employee-analytics
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and fill in your local MySQL credentials:
   ```bash
   cp .env.example .env
   ```

## Running the Pipeline

Run the scripts in this order:

```bash
python fetch.py          # verifies DB connection
python cleaning.py       # cleans raw tables -> Output/cleaned_data/
python EDA.py             # exploratory plots -> Output/eda_plots/
python verification.py   # builds master table -> Output/master_data/
python visualization.py  # final charts -> Output/charts/
python insights.py       # insights report -> Output/reports/
```

## Making Changes

1. Create a new branch: `git checkout -b feature/your-feature-name`
2. Make your changes
3. Commit with a clear message describing what and why
4. Push to your fork and open a Pull Request

## Reporting Issues

If you find a bug or have a suggestion, please open an issue describing:
- What you expected to happen
- What actually happened
- Steps to reproduce (if applicable)

## Code Style

- Keep functions small and focused
- Add comments for non-obvious data-cleaning logic
- Follow the existing pipeline structure (raw -> cleaned -> verified -> insights)
