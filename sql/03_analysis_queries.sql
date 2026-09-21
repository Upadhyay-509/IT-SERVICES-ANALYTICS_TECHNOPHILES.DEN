-- IT Services Performance Analytics - SQL Analysis Queries
-- Synthetic fictional project data.

-- Business question 1: What is total revenue?
SELECT SUM(revenue) AS total_revenue FROM monthly_finance;

-- Business question 2: What is total cost?
SELECT SUM(operating_cost) AS total_cost FROM monthly_finance;

-- Business question 3: What is total profit?
SELECT SUM(profit) AS total_profit FROM monthly_finance;

-- Business question 4: Which service generates the most revenue?
SELECT service, SUM(revenue) AS total_revenue
FROM monthly_finance
GROUP BY service
ORDER BY total_revenue DESC
LIMIT 1;

-- Business question 5: Which service has the highest profit margin?
WITH service_profit AS (
    SELECT service, SUM(profit) AS total_profit, SUM(operating_cost) AS total_cost
    FROM monthly_finance
    GROUP BY service
)
SELECT service, ROUND((total_profit / NULLIF(total_cost, 0)) * 100, 2) AS profit_margin_percent
FROM service_profit
ORDER BY profit_margin_percent DESC
LIMIT 1;

-- Business question 6: Which projects are delayed?
SELECT p.project_id, p.project_name, p.service, p.planned_end_date, p.actual_end_date
FROM projects p
WHERE p.actual_end_date > p.planned_end_date
ORDER BY p.actual_end_date DESC;

-- Business question 7: What is average delay by service?
SELECT p.service, AVG(DATE_PART('day', p.actual_end_date - p.planned_end_date)) AS avg_delay_days
FROM projects p
WHERE p.actual_end_date IS NOT NULL
GROUP BY p.service
ORDER BY avg_delay_days DESC;

-- Business question 8: What percentage of projects exceed budget?
SELECT ROUND(100.0 * SUM(CASE WHEN actual_cost > budget THEN 1 ELSE 0 END) / COUNT(*), 2) AS budget_overrun_percent
FROM projects;

-- Business question 9: Which are the top 10 clients by revenue?
SELECT c.client_id, c.client_name, SUM(p.budget) AS revenue_proxy
FROM clients c
JOIN projects p ON p.client_id = c.client_id
GROUP BY c.client_id, c.client_name
ORDER BY revenue_proxy DESC
LIMIT 10;

-- Business question 10: Which are the top 10 clients by profit?
SELECT c.client_id, c.client_name, SUM(p.budget - p.actual_cost) AS total_profit
FROM clients c
JOIN projects p ON p.client_id = c.client_id
GROUP BY c.client_id, c.client_name
ORDER BY total_profit DESC
LIMIT 10;

-- Business question 11: Rank projects by profit within each service.
SELECT service, project_id, project_name, budget - actual_cost AS profit,
       RANK() OVER (PARTITION BY service ORDER BY (budget - actual_cost) DESC) AS profit_rank
FROM projects
ORDER BY service, profit_rank;

-- Business question 12: Calculate month-over-month revenue growth using LAG.
SELECT month, service, revenue,
       LAG(revenue) OVER (PARTITION BY service ORDER BY month) AS previous_month_revenue,
       ROUND(((revenue - LAG(revenue) OVER (PARTITION BY service ORDER BY month)) / NULLIF(LAG(revenue) OVER (PARTITION BY service ORDER BY month), 0)) * 100, 2) AS month_over_month_growth_pct
FROM monthly_finance
ORDER BY service, month;

-- Business question 13: Identify months with highest revenue.
SELECT month, service, revenue
FROM monthly_finance
ORDER BY revenue DESC
LIMIT 12;

-- Business question 14: Which teams have highest productivity?
SELECT team_id, ROUND(AVG(productivity_score), 2) AS avg_productivity_score
FROM team_performance
GROUP BY team_id
ORDER BY avg_productivity_score DESC
LIMIT 10;

-- Business question 15: Analyze relationship between team utilization and project delays.
SELECT t.team_id,
       AVG(tp.utilization_rate) AS avg_utilization,
       COUNT(CASE WHEN p.actual_end_date > p.planned_end_date THEN 1 END) AS delayed_projects
FROM team_performance tp
JOIN projects p ON p.project_id = tp.project_id
JOIN (
    SELECT team_id, project_id FROM team_performance
) t ON t.project_id = tp.project_id
GROUP BY t.team_id
ORDER BY avg_utilization DESC;

-- Business question 16: Which clients have low satisfaction but high project value?
SELECT c.client_id, c.client_name, AVG(q.client_satisfaction) AS avg_satisfaction, SUM(p.budget) AS total_project_value
FROM clients c
JOIN projects p ON p.client_id = c.client_id
JOIN project_quality q ON q.project_id = p.project_id
WHERE q.client_satisfaction < 70
GROUP BY c.client_id, c.client_name
HAVING SUM(p.budget) > 150000
ORDER BY total_project_value DESC;

-- Business question 17: Which projects have largest budget overruns?
SELECT project_id, project_name, budget, actual_cost, actual_cost - budget AS budget_overrun
FROM projects
WHERE actual_cost > budget
ORDER BY budget_overrun DESC
LIMIT 20;

-- Business question 18: What percentage of projects are completed on time?
SELECT ROUND(100.0 * SUM(CASE WHEN status = 'Completed' AND actual_end_date <= planned_end_date THEN 1 ELSE 0 END) / COUNT(*), 2) AS on_time_completion_pct
FROM projects;

-- Business question 19: Which services have highest average satisfaction?
SELECT p.service, ROUND(AVG(q.client_satisfaction), 2) AS avg_satisfaction
FROM projects p
JOIN project_quality q ON q.project_id = p.project_id
GROUP BY p.service
ORDER BY avg_satisfaction DESC;

-- Business question 20: Identify underperforming projects using multiple KPIs.
WITH project_kpis AS (
    SELECT p.project_id, p.project_name, p.service,
           p.actual_cost - p.budget AS budget_overrun,
           CASE WHEN p.actual_end_date > p.planned_end_date THEN 1 ELSE 0 END AS delayed_flag,
           q.quality_score,
           q.client_satisfaction,
           tp.productivity_score,
           tp.utilization_rate
    FROM projects p
    JOIN project_quality q ON q.project_id = p.project_id
    JOIN team_performance tp ON tp.project_id = p.project_id
)
SELECT project_id, project_name, service,
       budget_overrun, delayed_flag, quality_score, client_satisfaction, productivity_score, utilization_rate
FROM project_kpis
WHERE budget_overrun > 0 OR delayed_flag = 1 OR quality_score < 60 OR client_satisfaction < 60
ORDER BY budget_overrun DESC, delayed_flag DESC;

-- Demonstrate DENSE_RANK and LEFT JOIN
-- Business question: Top services by revenue with dense rank.
SELECT service, total_revenue,
       DENSE_RANK() OVER (ORDER BY total_revenue DESC) AS revenue_rank
FROM (
    SELECT service, SUM(revenue) AS total_revenue
    FROM monthly_finance
    GROUP BY service
) x;

-- Demonstrate DATE_TRUNC monthly trend.
SELECT DATE_TRUNC('month', month) AS month_month,
       SUM(revenue) AS monthly_revenue
FROM monthly_finance
GROUP BY DATE_TRUNC('month', month)
ORDER BY month_month;

-- Demonstrate a LEFT JOIN for projects without quality records.
SELECT p.project_id, p.project_name, q.quality_score
FROM projects p
LEFT JOIN project_quality q ON q.project_id = p.project_id
ORDER BY p.project_id;
