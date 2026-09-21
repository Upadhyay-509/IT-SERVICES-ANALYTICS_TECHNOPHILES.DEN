import os
import shutil

import pandas as pd


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
RAW_DIR = os.path.join(PROJECT_ROOT, 'data', 'raw')
SOURCE_DIR = os.getenv('TECHNOPHILES_DATA_DIR', RAW_DIR)

DATASETS = {
    'clients.csv': {
        'source_suffix': 'Clients_Raw.csv',
        'required_columns': {'client_id', 'client_name', 'industry', 'country', 'client_type', 'start_date'},
    },
    'monthly_finance.csv': {
        'source_suffix': 'MonthlyFinance_Raw.csv',
        'required_columns': {'month', 'service', 'revenue', 'operating_cost', 'profit'},
    },
    'project_quality.csv': {
        'source_suffix': 'ProjectQuality_Raw.csv',
        'required_columns': {'project_id', 'quality_score', 'client_satisfaction', 'issues_count', 'rework_hours'},
    },
    'projects.csv': {
        'source_suffix': 'Projects_Raw.csv',
        'required_columns': {'project_id', 'client_id', 'project_name', 'service', 'start_date', 'planned_end_date', 'actual_end_date', 'budget', 'actual_cost', 'status', 'team_size'},
    },
    'team_performance.csv': {
        'source_suffix': 'TeamPerformance_Raw.csv',
        'required_columns': {'project_id', 'team_id', 'employee_count', 'hours_allocated', 'hours_worked', 'utilization_rate', 'productivity_score'},
    },
}


def find_source_file(source_suffix):
    if not os.path.isdir(SOURCE_DIR):
        raise FileNotFoundError(f'Data source directory not found: {SOURCE_DIR}')

    candidates = [
        os.path.join(SOURCE_DIR, name)
        for name in os.listdir(SOURCE_DIR)
        if name.endswith(source_suffix)
    ]
    if not candidates:
        raise FileNotFoundError(f'No source file ending with {source_suffix} found in {SOURCE_DIR}')
    return candidates[0]


def import_company_data():
    os.makedirs(RAW_DIR, exist_ok=True)
    imported = {}

    for destination_name, metadata in DATASETS.items():
        destination_path = os.path.join(RAW_DIR, destination_name)
        try:
            source_path = find_source_file(metadata['source_suffix'])
        except FileNotFoundError:
            if not os.path.isfile(destination_path):
                raise
            source_path = destination_path
        frame = pd.read_csv(source_path)
        missing_columns = metadata['required_columns'] - set(frame.columns)
        if missing_columns:
            missing = ', '.join(sorted(missing_columns))
            raise ValueError(f'{os.path.basename(source_path)} is missing columns: {missing}')

        if os.path.abspath(source_path) != os.path.abspath(destination_path):
            shutil.copy2(source_path, destination_path)
        imported[destination_name] = len(frame)

    return imported


def main():
    imported = import_company_data()
    print('Company raw datasets imported successfully.')
    for dataset_name, row_count in imported.items():
        print(f'{dataset_name}: {row_count} rows')


if __name__ == '__main__':
    main()
