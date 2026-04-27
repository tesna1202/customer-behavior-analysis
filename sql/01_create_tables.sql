CREATE TABLE dbo.customer_behavior_enriched (
    customer_id INT,
    age INT,
    gender VARCHAR(20),
    item_purchased VARCHAR(100),
    category VARCHAR(100),
    purchase_amount DECIMAL(10, 2),
    location VARCHAR(100),
    size VARCHAR(10),
    color VARCHAR(50),
    season VARCHAR(20),
    review_rating DECIMAL(3, 1),
    subscription_status VARCHAR(10),
    shipping_type VARCHAR(50),
    discount_applied VARCHAR(10),
    promo_code_used VARCHAR(10),
    previous_purchases INT,
    payment_method VARCHAR(50),
    frequency_of_purchases VARCHAR(50),
    purchase_frequency_days INT,
    age_group VARCHAR(20),
    customer_segment VARCHAR(20),
    high_value_customer_flag BIT,
    inactive_customer_flag BIT,
    churn_risk_flag BIT,
    snapshot_date DATE
);

CREATE TABLE dbo.kpi_snapshot (
    snapshot_date DATE,
    kpi_name VARCHAR(100),
    kpi_value DECIMAL(18, 2),
    unit VARCHAR(20),
    status VARCHAR(20),
    notes VARCHAR(255)
);

CREATE TABLE dbo.customer_watchlist (
    customer_id INT,
    gender VARCHAR(20),
    category VARCHAR(100),
    purchase_amount DECIMAL(10, 2),
    subscription_status VARCHAR(10),
    frequency_of_purchases VARCHAR(50),
    customer_segment VARCHAR(20),
    high_value_customer_flag BIT,
    churn_risk_flag BIT,
    inactive_customer_flag BIT,
    snapshot_date DATE,
    priority_label VARCHAR(20)
);

CREATE TABLE dbo.automation_alerts (
    snapshot_date DATE,
    alert_type VARCHAR(100),
    severity VARCHAR(20),
    message VARCHAR(255)
);
