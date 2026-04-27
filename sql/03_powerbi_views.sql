CREATE OR ALTER VIEW dbo.vw_kpi_summary AS
SELECT
    snapshot_date,
    kpi_name,
    kpi_value,
    unit,
    status,
    notes
FROM dbo.kpi_snapshot;
GO

CREATE OR ALTER VIEW dbo.vw_customer_watchlist AS
SELECT
    customer_id,
    category,
    purchase_amount,
    customer_segment,
    subscription_status,
    frequency_of_purchases,
    high_value_customer_flag,
    churn_risk_flag,
    inactive_customer_flag,
    priority_label,
    snapshot_date
FROM dbo.customer_watchlist;
GO

CREATE OR ALTER VIEW dbo.vw_automation_alerts AS
SELECT
    snapshot_date,
    alert_type,
    severity,
    message
FROM dbo.automation_alerts;
GO
