import os
import pandas as pd
import numpy as np

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
RAW_DIR = os.path.join(PROJECT_ROOT, 'data', 'raw')
CLEANED_DIR = os.path.join(PROJECT_ROOT, 'data', 'cleaned')
os.makedirs(CLEANED_DIR, exist_ok=True)

DATASET_ORDER = [
    'clients',
    'projects',
    'team_performance',
    'project_quality',
    'monthly_finance'
]


def load_and_profile(file_path):
    df = pd.read_csv(file_path)
    print(f"\nDataset: {os.path.basename(file_path)}")
    print(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}")
    print(f"Columns: {list(df.columns)}")
    print(f"Data types:\n{df.dtypes}")
    print(f"Missing values:\n{df.isna().sum()}")
    print(f"Duplicate rows: {df.duplicated().sum()}")
    return df


def clean_clients(df):
    df = df.copy()
    # Clean id/name strings
    df['client_id'] = df['client_id'].astype(str).str.strip()
    df['client_name'] = df['client_name'].astype(str).str.replace('\n', ' ', regex=False).str.strip()
    df['industry'] = df['industry'].astype(str).str.strip()
    df['country'] = df['country'].astype(str).str.strip()
    df['client_type'] = df['client_type'].astype(str).str.strip()

    # Parse date
    df['start_date'] = pd.to_datetime(df['start_date'], errors='coerce', format='mixed', dayfirst=True)
    invalid_date_count = df['start_date'].isna().sum()
    if invalid_date_count:
        print(f'Clients invalid dates found: {invalid_date_count}. Rows with invalid dates will be dropped.')
        df = df.dropna(subset=['start_date'])

    # Keep source-specific category values while removing incomplete records.
    df = df.dropna(subset=['client_id', 'client_name', 'industry', 'country', 'client_type'])

    # Sort and reset index
    df = df.sort_values('client_id').reset_index(drop=True)
    return df


def clean_projects(df):
    df = df.copy()
    # Normalize identifiers and text columns
    df['project_id'] = df['project_id'].astype(str).str.strip()
    df['client_id'] = df['client_id'].astype(str).str.strip()
    df['project_name'] = df['project_name'].astype(str).str.replace('\n', ' ', regex=False).str.strip()
    df['service'] = df['service'].astype(str).str.strip()
    df['status'] = df['status'].astype(str).str.strip()

    # Parse dates
    for col in ['start_date', 'planned_end_date', 'actual_end_date']:
        df[col] = pd.to_datetime(df[col], errors='coerce', format='mixed', dayfirst=True)

    # Keep ongoing projects without a planned end date; delay metrics will skip them.
    df = df.dropna(subset=['project_id', 'client_id', 'project_name', 'service', 'start_date'])

    # Ensure logical relationships: actual_end_date after start_date when available
    df['actual_end_date'] = pd.to_datetime(df['actual_end_date'], errors='coerce', format='mixed', dayfirst=True)
    # If actual_end_date exists and is before start_date, correct to planned+1 day
    mask = df['actual_end_date'].notna() & (df['actual_end_date'] < df['start_date'])
    df.loc[mask, 'actual_end_date'] = df.loc[mask, 'start_date'] + pd.to_timedelta(1, unit='D')

    # Validate numeric columns
    for col in ['budget', 'actual_cost', 'team_size']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Treat impossible negative numbers as missing then fill median
    for col in ['budget', 'actual_cost', 'team_size']:
        df[col] = df[col].replace(0, np.nan)
    # Remove rows with impossible or empty numerical values
    df = df.dropna(subset=['budget', 'actual_cost', 'team_size'])

    # Keep source-specific service values while removing incomplete records.
    df = df.dropna(subset=['service', 'status'])

    # Validate status
    valid_statuses = {'Completed', 'Ongoing', 'On Hold'}
    df = df[df['status'].isin(valid_statuses)]

    # Actual cost must not be less than 0
    df = df[df['budget'] > 0]
    df = df[df['actual_cost'] > 0]

    # status and dates logic
    # On-going projects may have blank actual_end_date; recorded as NaT
    df = df.reset_index(drop=True)
    return df


def clean_team_performance(df):
    df = df.copy()
    df['project_id'] = df['project_id'].astype(str).str.strip()
    df['team_id'] = df['team_id'].astype(str).str.strip()
    df['employee_count'] = pd.to_numeric(df['employee_count'], errors='coerce')
    df['hours_allocated'] = pd.to_numeric(df['hours_allocated'], errors='coerce')
    df['hours_worked'] = pd.to_numeric(df['hours_worked'], errors='coerce')
    df['utilization_rate'] = pd.to_numeric(df['utilization_rate'], errors='coerce')
    df['productivity_score'] = pd.to_numeric(df['productivity_score'], errors='coerce')

    # Validate impossible productivity and utilization
    df = df.dropna(subset=['project_id', 'team_id', 'employee_count', 'hours_allocated', 'hours_worked'])
    df = df[(df['employee_count'] > 0) & (df['hours_allocated'] > 0) & (df['hours_worked'] >= 0)]
    df = df[(df['utilization_rate'] >= 0) & (df['utilization_rate'] <= 150)]
    df = df[(df['productivity_score'] >= 0) & (df['productivity_score'] <= 100)]

    # Correct derived utilization where necessary
    # If rounded usage is suspicious, compute from hours_worked / hours_allocated *100
    df['utilization_rate'] = np.where(df['hours_allocated'] != 0, df['hours_worked'] / df['hours_allocated'] * 100, np.nan)
    df = df.dropna(subset=['utilization_rate'])

    return df


def clean_project_quality(df):
    df = df.copy()
    df['project_id'] = df['project_id'].astype(str).str.strip()
    for col in ['quality_score', 'client_satisfaction', 'issues_count', 'rework_hours']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.dropna(subset=['project_id', 'quality_score', 'client_satisfaction', 'issues_count', 'rework_hours'])
    df = df[(df['quality_score'] >= 0) & (df['quality_score'] <= 100)]
    df = df[(df['client_satisfaction'] >= 0) & (df['client_satisfaction'] <= 100)]
    df = df[(df['issues_count'] >= 0)]
    df = df[(df['rework_hours'] >= 0)]
    return df


def clean_monthly_finance(df):
    df = df.copy()
    df['month'] = pd.to_datetime(df['month'], errors='coerce', format='mixed', dayfirst=False)
    df['service'] = df['service'].astype(str).str.strip()
    for col in ['revenue', 'operating_cost', 'profit']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.dropna(subset=['month', 'service', 'revenue', 'operating_cost', 'profit'])
    # calculate profit if necessary and flag anomalies
    df['profit'] = df['revenue'] - df['operating_cost']
    return df


def validate_relationships(clients, projects, team, quality, finance):
    print('\nRelationship validation:')
    # Foreign key clients -> projects
    missing_client_projects = set(projects['client_id']) - set(clients['client_id'])
    print(f'Missing client_id relationships in projects: {len(missing_client_projects)}')

    # Project relationships
    missing_project_team = set(team['project_id']) - set(projects['project_id'])
    missing_project_quality = set(quality['project_id']) - set(projects['project_id'])
    print(f'Missing project_id relationships in team_performance: {len(missing_project_team)}')
    print(f'Missing project_id relationships in project_quality: {len(missing_project_quality)}')

    print(f'Finance services found: {finance["service"].nunique()}')


def save_cleaned(df, table_name):
    out_file = os.path.join(CLEANED_DIR, f'{table_name}_cleaned.csv')
    df.to_csv(out_file, index=False)
    print(f'Saved cleaned table: {out_file}')


def main():
    print('Starting data cleaning pipeline...')

    clients_raw = load_and_profile(os.path.join(RAW_DIR, 'clients.csv'))
    projects_raw = load_and_profile(os.path.join(RAW_DIR, 'projects.csv'))
    team_raw = load_and_profile(os.path.join(RAW_DIR, 'team_performance.csv'))
    quality_raw = load_and_profile(os.path.join(RAW_DIR, 'project_quality.csv'))
    finance_raw = load_and_profile(os.path.join(RAW_DIR, 'monthly_finance.csv'))

    clients_clean = clean_clients(clients_raw)
    projects_clean = clean_projects(projects_raw)
    team_clean = clean_team_performance(team_raw)
    quality_clean = clean_project_quality(quality_raw)
    finance_clean = clean_monthly_finance(finance_raw)

    # Drop quality rows and team rows for projects not in cleaned projects
    projects_project_ids = set(projects_clean['project_id'])
    team_clean = team_clean[team_clean['project_id'].isin(projects_project_ids)].reset_index(drop=True)
    quality_clean = quality_clean[quality_clean['project_id'].isin(projects_project_ids)].reset_index(drop=True)

    validate_relationships(clients_clean, projects_clean, team_clean, quality_clean, finance_clean)

    # Save cleaned tables
    save_cleaned(clients_clean, 'clients')
    save_cleaned(projects_clean, 'projects')
    save_cleaned(team_clean, 'team_performance')
    save_cleaned(quality_clean, 'project_quality')
    save_cleaned(finance_clean, 'monthly_finance')

    print('\nData quality report:')
    for table, df in {
        'clients': clients_clean,
        'projects': projects_clean,
        'team_performance': team_clean,
        'project_quality': quality_clean,
        'monthly_finance': finance_clean,
    }.items():
        print(f"{table}: Rows={len(df)}, Columns={len(df.columns)}, Missing={df.isna().sum().sum()}, Duplicates={df.duplicated().sum()}")

    print('\nCleaning complete. Cleaned CSV files created in data/cleaned/.')


if __name__ == '__main__':
    main()
