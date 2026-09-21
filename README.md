# IT Services Performance Analytics Pipeline

This project is a fictional, synthetic end-to-end data analytics project for an IT services company. It demonstrates a realistic analytics workflow from data generation and validation through SQL analysis and Power BI dashboard planning.

Technophiles DEN dataset statistics:

- 45 clients
- 50 projects
- 50 team performance records
- 50 project quality records
- 72 monthly finance records covering Aug 2025 to Mar 2026

## Project Objective

The objective is to analyze service-wise performance, client outcomes, operational delivery, team productivity, budget health, and monthly financial trends for a fictional IT services company.

## Business Problem

Management needs visibility into:

- Revenue, cost, and profit across services
- Delivery delays and project completion status
- Budget variance and overruns
- Client satisfaction and project quality
- Team performance and utilization
- Monthly business trends

## Dataset Description

The supplied data files include records for:

- 45 fictional clients
- 50 fictional projects
- 50 team performance records
- 50 project quality records
- 8 months of monthly finance records from Aug 2025 to Mar 2026

## Architecture / Workflow

Raw Data
   ↓
Python / Pandas
   ↓
Data Cleaning
   ↓
Feature Engineering
   ↓
PostgreSQL
   ↓
SQL Analysis
   ↓
Power BI
   ↓
Business Insights

## Technology Stack

- Python
- Pandas
- NumPy
- Matplotlib
- Seaborn
- Jupyter Notebook
- PostgreSQL
- SQL
- Power BI

## Folder Structure

```text
IT-Services-Performance-Analytics/
├── data/
│   ├── raw/
│   └── cleaned/
├── notebooks/
│   └── 01_exploratory_analysis.ipynb
├── src/
│   ├── data_generation.py
│   ├── data_cleaning.py
│   ├── feature_engineering.py
│   └── analysis.py
├── sql/
│   ├── 01_create_tables.sql
│   ├── 02_insert_data.sql
│   └── 03_analysis_queries.sql
├── powerbi/
│   └── POWERBI_DASHBOARD_GUIDE.md
├── reports/
│   └── business_insights.md
├── requirements.txt
├── README.md
└── .gitignore
```

## Python Workflow

1. Set `TECHNOPHILES_DATA_DIR` to the folder containing the supplied `*_Raw.csv` files, then run `python src/data_generation.py` to import them into `data/raw/`. If the files are already in `data/raw/`, the environment variable is optional.
2. Run `python src/data_cleaning.py` to validate and rebuild the cleaned datasets.
3. Run `python src/feature_engineering.py` to create or refresh business features.
4. Run `python src/analysis.py` to create the project summary and business insights.

## SQL Workflow

1. Use `sql/01_create_tables.sql` to create PostgreSQL-compatible tables.
2. Use `sql/02_insert_data.sql` as the data load template.
3. Use `sql/03_analysis_queries.sql` for business analysis statements.

## Power BI Dashboard

Detailed dashboard instructions are available in `powerbi/POWERBI_DASHBOARD_GUIDE.md`.

## Business Questions

The project analyzes the following business questions:

- Total revenue, cost, and profit
- Service-level contribution and margin
- Delay and project completion distribution
- Client quality and satisfaction analysis
- Budget overrun rates
- Team productivity and utilization
- Monthly revenue and profit trends

## Key Insights

The actual generated dataset will produce business insights in the `reports/business_insights.md` file after the analysis script creates the report.

## How to Run the Project

```bash
pip install -r requirements.txt
python src/data_generation.py
python src/data_cleaning.py
python src/feature_engineering.py
python src/analysis.py
```

## PostgreSQL Setup Instructions

1. Create a PostgreSQL database named `it_services_analytics`.
2. Set environment variables for the database connection if using Python.
3. Run the SQL schema file:

```bash
psql -d it_services_analytics -f sql/01_create_tables.sql
```

4. Load the generated CSVs using `psql` `COPY` or a Python loader.

## Power BI Connection Instructions

1. Open Power BI Desktop.
2. Import the cleaned CSV files.
3. Create relationships between the CSV tables.
4. Build the three dashboard pages described in the Power BI guide.

## Future Improvements

- Add automated data quality scoring.
- Add forecast models for revenue and utilization.
- Add a metadata-driven data pipeline.
- Extend the project with a complete Power BI semantic model and publish workflow.
