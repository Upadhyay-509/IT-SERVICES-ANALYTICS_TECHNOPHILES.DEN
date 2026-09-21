-- IT Services Performance Analytics - SQL Schema
-- Fictional synthetic data project.

DROP TABLE IF EXISTS monthly_finance;
DROP TABLE IF EXISTS project_quality;
DROP TABLE IF EXISTS team_performance;
DROP TABLE IF EXISTS projects;
DROP TABLE IF EXISTS clients;

CREATE TABLE clients (
    client_id VARCHAR(20) PRIMARY KEY,
    client_name VARCHAR(200) NOT NULL,
    industry VARCHAR(50) NOT NULL,
    country VARCHAR(50) NOT NULL,
    client_type VARCHAR(50) NOT NULL,
    start_date DATE NOT NULL
);

CREATE TABLE projects (
    project_id VARCHAR(20) PRIMARY KEY,
    client_id VARCHAR(20) NOT NULL,
    project_name VARCHAR(200) NOT NULL,
    service VARCHAR(80) NOT NULL,
    start_date DATE NOT NULL,
    planned_end_date DATE NOT NULL,
    actual_end_date DATE,
    budget NUMERIC(12,2) NOT NULL,
    actual_cost NUMERIC(12,2) NOT NULL,
    status VARCHAR(30) NOT NULL CHECK (status IN ('Completed', 'Ongoing', 'On Hold')),
    team_size INTEGER NOT NULL,
    FOREIGN KEY (client_id) REFERENCES clients(client_id)
);

CREATE TABLE team_performance (
    project_id VARCHAR(20) PRIMARY KEY,
    team_id VARCHAR(50) NOT NULL,
    employee_count INTEGER NOT NULL,
    hours_allocated INTEGER NOT NULL,
    hours_worked INTEGER NOT NULL,
    utilization_rate NUMERIC(5,2) NOT NULL,
    productivity_score NUMERIC(5,2) NOT NULL,
    FOREIGN KEY (project_id) REFERENCES projects(project_id)
);

CREATE TABLE project_quality (
    project_id VARCHAR(20) PRIMARY KEY,
    quality_score NUMERIC(5,2) NOT NULL,
    client_satisfaction NUMERIC(5,2) NOT NULL,
    issues_count INTEGER NOT NULL,
    rework_hours INTEGER NOT NULL,
    FOREIGN KEY (project_id) REFERENCES projects(project_id)
);

CREATE TABLE monthly_finance (
    month DATE NOT NULL,
    service VARCHAR(80) NOT NULL,
    revenue NUMERIC(12,2) NOT NULL,
    operating_cost NUMERIC(12,2) NOT NULL,
    profit NUMERIC(12,2) NOT NULL
);

CREATE INDEX idx_projects_client_id ON projects(client_id);
CREATE INDEX idx_projects_service ON projects(service);
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_start_date ON projects(start_date);
CREATE INDEX idx_team_performance_team_id ON team_performance(team_id);
CREATE INDEX idx_team_performance_utilization_rate ON team_performance(utilization_rate);
CREATE INDEX idx_project_quality_score ON project_quality(quality_score);
CREATE INDEX idx_monthly_finance_service_month ON monthly_finance(service, month);
