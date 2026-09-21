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


def basic_summary(projects, clients, team, quality, finance):
    print('\n=== Enterprise Analytics Summary ===')
    print(f'Total projects: {len(projects)}')
    print(f'Total clients: {len(clients)}')
    print(f'Total team records: {len(team)}')
    print(f'Total quality records: {len(quality)}')
    print(f'Total finance records: {len(finance)}')

    print('\nService distribution:')
    print(projects['service'].value_counts())

    print('\nStatus distribution:')
    print(projects['status'].value_counts())

    print('\nRevenue by service:')
    revenue_map = finance.groupby('service')['revenue'].sum().sort_values(ascending=False)
    print(revenue_map)

    print('\nProject profitability summary:')
    print(projects[['budget', 'actual_cost', 'profit', 'profit_margin']].describe())


def write_business_insights(clients, projects, team, quality, finance):
    # Prepare date fields and derived fields needed for true business metrics
    projects = projects.copy()
    projects['planned_end_date'] = pd.to_datetime(projects['planned_end_date'], errors='coerce', format='mixed', dayfirst=True)
    projects['actual_end_date'] = pd.to_datetime(projects['actual_end_date'], errors='coerce', format='mixed', dayfirst=True)

    # Delay days should be human-readable and non-negative for reporting.
    # Early completions are treated as zero delay for narrative and metric consistency.
    projects['delay_days'] = (projects['actual_end_date'] - projects['planned_end_date']).dt.days
    projects.loc[projects['delay_days'] < 0, 'delay_days'] = 0

    finance['month'] = pd.to_datetime(finance['month'], errors='coerce', format='mixed', dayfirst=False)

    # Service revenue and profit totals from monthly_finance
    service_revenue = finance.groupby('service', as_index=False)['revenue'].sum().sort_values('revenue', ascending=False)
    highest_revenue_service = service_revenue.iloc[0]['service']
    highest_revenue_value = service_revenue.iloc[0]['revenue']

    service_profit = finance.groupby('service', as_index=False)['profit'].sum().sort_values('profit', ascending=False)
    most_profitable_service = service_profit.iloc[0]['service']
    most_profitable_value = service_profit.iloc[0]['profit']

    # Average project delay by service based on actual end dates only
    valid_delay_projects = projects.dropna(subset=['actual_end_date']).copy()
    avg_delay_by_service = valid_delay_projects.groupby('service')['delay_days'].mean().sort_values(ascending=False)
    highest_delay_service = avg_delay_by_service.index[0]
    highest_delay_value = round(avg_delay_by_service.iloc[0], 2)

    # Budget overrun percentage
    budget_overrun_count = int((projects['actual_cost'] > projects['budget']).sum())
    budget_overrun_pct = round((budget_overrun_count / len(projects)) * 100, 2)

    # Top clients by revenue
    client_names = clients.set_index('client_id')['client_name'].to_dict()
    top_clients_by_revenue = projects.groupby('client_id', as_index=False)['budget'].sum().sort_values('budget', ascending=False).head(5)
    top_clients_text = []
    for _, row in top_clients_by_revenue.iterrows():
        top_clients_text.append(f"{client_names.get(row['client_id'], row['client_id'])}: {round(row['budget'], 2)}")

    # Best performing teams by productivity score
    team_summary = team.groupby('team_id', as_index=False).agg(avg_productivity=('productivity_score', 'mean'), avg_utilization=('utilization_rate', 'mean'))
    best_team = team_summary.sort_values('avg_productivity', ascending=False).head(1)
    best_team_id = best_team.iloc[0]['team_id']
    best_team_productivity = round(best_team.iloc[0]['avg_productivity'], 2)

    # Monthly revenue trend and highest month
    monthly_revenue = finance.groupby(finance['month'].dt.to_period('M'), as_index=False)['revenue'].sum()
    monthly_revenue['month'] = monthly_revenue['month'].dt.to_timestamp()
    monthly_revenue = monthly_revenue.sort_values('month')
    highest_revenue_month = monthly_revenue.sort_values('revenue', ascending=False).iloc[0]

    # Utilization and delay relationship
    util_delay = projects.merge(team, on='project_id', how='left')
    util_delay = util_delay.dropna(subset=['actual_end_date'])
    correlation = util_delay['utilization_rate'].corr(util_delay['delay_days'])

    # Client satisfaction findings
    avg_satisfaction = quality['client_satisfaction'].mean()
    avg_quality = quality['quality_score'].mean()
    low_satisfaction_records = quality[quality['client_satisfaction'] < 70]
    correlation_direction = 'positive' if correlation > 0 else 'negative' if correlation < 0 else 'neutral'
    satisfaction_record_label = 'record' if len(low_satisfaction_records) == 1 else 'records'

    # Build humanized markdown report
    output = []
    output.append('# Business Insights')
    output.append('')
    output.append('This synthetic report describes a fictional IT services operation and its portfolio of client, delivery, quality, team, and finance activity.')
    output.append('')
    output.append('## Executive Summary')
    output.append(f'Across the generated dataset, {highest_revenue_service} is the strongest revenue service, producing {round(highest_revenue_value, 2)} in revenue. {most_profitable_service} is the most profitable service by profit contribution, creating {round(most_profitable_value, 2)} in synthetic profit.')
    output.append(f'In a delivery sense, {highest_delay_service} shows the longest average delay, with an average of {highest_delay_value} delay days across dated projects. This gives the business a clear signal to review capacity and planning for that service.')
    output.append(f'Budget awareness also needs attention. {budget_overrun_pct}% of the {len(projects)} projects exceed the budget, which suggests that scope control and cost review are important commercial controls.')
    output.append('')
    output.append('## Observation')
    output.append(f'- Revenue is led by {highest_revenue_service}, which generated {round(highest_revenue_value, 2)} in the sample finance dataset.')
    output.append(f'- Profit is led by {most_profitable_service}, which generated {round(most_profitable_value, 2)} in profit contribution.')
    output.append(f'- Delivery pressure is highest in {highest_delay_service}, where the average project delay is {highest_delay_value} days.')
    output.append(f'- Budget overruns are present in {budget_overrun_count} of {len(projects)} projects, or {budget_overrun_pct}% of the portfolio.')
    output.append(f'- The main clients by revenue are {", ".join(top_clients_text)}.')
    output.append(f'- The strongest productivity result came from team {best_team_id}, with an average productivity score of {best_team_productivity}.')
    output.append(f'- The highest monthly revenue point occurs in {highest_revenue_month["month"].strftime("%b %Y")} with {round(highest_revenue_month["revenue"], 2)} in revenue.')
    output.append(f'- The relationship between utilization and delay in the generated records is a {correlation_direction} correlation of {round(correlation, 3)}.')
    output.append(f'- Average client satisfaction is {round(avg_satisfaction, 2)} and average quality score is {round(avg_quality, 2)}; there are {len(low_satisfaction_records)} {satisfaction_record_label} where client satisfaction is below 70.')
    output.append('')
    output.append('## Insight')
    output.append(f'Revenue is concentrated in {highest_revenue_service}, while the strongest profit contribution also comes from {most_profitable_service}. This pattern suggests that the services with the highest commercial demand are also points where delivery discipline and pricing decisions matter most.')
    output.append(f'The delivery story is not uniform. {highest_delay_service} carries the greatest average delivery delay, suggesting that the service has more risk related to planning complexity, dependency management, or staffing mix.')
    output.append(f'The budget variance picture is also a management signal. With {budget_overrun_pct}% of projects exceeding budget, the business should keep a closer watch on scope changes, cost assumptions, and project review checkpoints.')
    output.append(f'Customer experience is mostly healthy, but satisfaction falls below 70 for {len(low_satisfaction_records)} {satisfaction_record_label}. These project outcomes should be reviewed in the context of project quality, service complexity, and delivery confidence.')
    output.append('')
    output.append('## Recommendation')
    output.append(f'Management should create a focused capacity and estimation review for {highest_delay_service} before approving future high-complexity work.')
    output.append('Budget governance should include additional stage-gate checks for work that is close to or above budget, especially when scope changes are expected.')
    output.append('The customer success team should follow up with clients whose projects show low satisfaction and pair those reviews with delivery-or-team-quality checks.')
    output.append('Team utilization and productivity should be used as part of a weekly staffing review so project delivery remains balanced across services.')
    output.append('')

    insights_path = os.path.join(PROJECT_ROOT, 'reports', 'business_insights.md')
    with open(insights_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output))

    print('\nAnalysis complete. Humanized business insight file prepared.')


def run_analysis():
    clients, projects, team, quality, finance = load_cleaned_data()
    basic_summary(projects, clients, team, quality, finance)
    write_business_insights(clients, projects, team, quality, finance)


if __name__ == '__main__':
    run_analysis()
