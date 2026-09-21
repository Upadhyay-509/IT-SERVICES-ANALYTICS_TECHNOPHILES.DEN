import os
import pandas as pd
import numpy as np

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CLEANED_DIR = os.path.join(PROJECT_ROOT, 'data', 'cleaned')

def load_cleaned_data():
    clients = pd.read_csv(os.path.join(CLEANED_DIR, 'clients_cleaned.csv'))
    projects = pd.read_csv(os.path.join(CLEANED_DIR, 'projects_cleaned.csv'))
    team = pd.read_csv(os.path.join(CLEANED_DIR, 'team_performance_cleaned.csv'))
    quality = pd.read_csv(os.path.join(CLEANED_DIR, 'project_quality_cleaned.csv'))
    finance = pd.read_csv(os.path.join(CLEANED_DIR, 'monthly_finance_cleaned.csv'))
    return clients, projects, team, quality, finance


def engineer_project_features(projects, quality, team):
    # Merge quality and team performance for project-level project features
    projects = projects.copy()
    quality = quality.copy()
    team = team.copy()

    # Convert actual_end_date and planned columns to datetime
    for col in ['start_date', 'planned_end_date', 'actual_end_date']:
        projects[col] = pd.to_datetime(projects[col], errors='coerce', format='mixed', dayfirst=True)

    # Derive profit fields
    # profit = budget - actual_cost according to requested specification
    projects['profit'] = projects['budget'] - projects['actual_cost']
    projects['budget_variance'] = projects['budget'] - projects['actual_cost']
    projects['budget_overrun_flag'] = (projects['actual_cost'] > projects['budget']).astype(int)

    # Delay days can be difference in whole days; On Time/Delayed categories
    projects['delay_days'] = (projects['actual_end_date'] - projects['planned_end_date']).dt.days
    projects['delay_days'] = projects['delay_days'].fillna(0)
    # Delay is only if actual end date > planned end date by >0
    projects['delay_status'] = np.where(projects['delay_days'] > 0, 'Delayed', 'On Time')

    # Profit margin requested as percent
    projects['profit_margin'] = np.where(projects['budget'] != 0, (projects['profit'] / projects['budget']) * 100, 0)

    # Productivity categories
    # Need team-level productivity score categories, create in team feature engineering separately.
    # Quality categories: Excellent, Good, Average, Needs Improvement
    # Use quality_score and client_satisfaction combination to create a project-performance category.
    def performance_category(row):
        score = row['quality_score']
        satisfaction = row['client_satisfaction']
        if score >= 85 and satisfaction >= 80:
            return 'Excellent'
        if score >= 70 and satisfaction >= 65:
            return 'Good'
        if score >= 50 and satisfaction >= 50:
            return 'Average'
        return 'Needs Improvement'

    quality['project_performance_category'] = quality.apply(performance_category, axis=1)

    # Create team-level feature classification categories
    # Productivity as Low, Medium, High
    def productivity_category(score):
        if score < 65:
            return 'Low'
        elif score < 85:
            return 'Medium'
        return 'High'

    # Ensure both columns integrated into team dataset before merge
    team['productivity_category'] = team['productivity_score'].apply(productivity_category)

    # Add only quality fields not already included in the project source table.
    quality_fields = ['quality_score', 'client_satisfaction', 'issues_count', 'rework_hours', 'project_performance_category']
    merge_fields = ['project_id'] + [field for field in quality_fields if field not in projects.columns]
    projects = projects.merge(quality[merge_fields], on='project_id', how='left')

    return projects, team, quality


def engineer_monthly_finance(finance):
    finance = finance.copy()
    finance['month'] = pd.to_datetime(finance['month'], errors='coerce', format='mixed', dayfirst=False)
    finance['month_name'] = finance['month'].dt.strftime('%b %Y')
    finance['year'] = finance['month'].dt.year
    finance['month_num'] = finance['month'].dt.month
    return finance


def main():
    clients, projects, team, quality, finance = load_cleaned_data()
    projects, team, quality = engineer_project_features(projects, quality, team)
    finance = engineer_monthly_finance(finance)

    # Save engineered features to same cleaned folder
    clients.to_csv(os.path.join(CLEANED_DIR, 'clients_cleaned.csv'), index=False)
    projects.to_csv(os.path.join(CLEANED_DIR, 'projects_cleaned.csv'), index=False)
    team.to_csv(os.path.join(CLEANED_DIR, 'team_performance_cleaned.csv'), index=False)
    quality.to_csv(os.path.join(CLEANED_DIR, 'project_quality_cleaned.csv'), index=False)
    finance.to_csv(os.path.join(CLEANED_DIR, 'monthly_finance_cleaned.csv'), index=False)

    print('Feature engineering complete.')
    print(f'Projects with engineered columns: {len(projects)}')
    print(f'Team records with productivity_category: {len(team)}')


if __name__ == '__main__':
    main()
