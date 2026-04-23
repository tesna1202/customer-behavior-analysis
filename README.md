Customer Behavior Analysis (End-to-End Data Project)

📌 Overview

This project demonstrates a complete data analytics pipeline, starting from raw data to business insights.

The workflow includes:
Data Cleaning & Exploration using Python
Data Storage & Analysis using SQL Server
Interactive Dashboard using Power BI

🛠️ Tech Stack

Python (Pandas, NumPy, Seaborn, Matplotlib)
SQL Server
Power BI
SQLAlchemy & PyODBC

🔄 Workflow

Load raw data using Python
Clean and preprocess dataset
Create new features (e.g., spending categories)
Load cleaned data into SQL Server
Perform analysis using SQL queries
Build dashboard in Power BI

🚀 How to Run the Project

1. Clone Repository

git clone

2. Install Dependencies

pip install -r requirements.txt

3. Run Jupyter Notebook

python -m notebook

Open:
notebooks/01_data_cleaning_eda.ipynb

4. Setup Database

Create database in SQL Server:
CREATE DATABASE customer_analysis;

5. Load Data into SQL Server

Run:
df.to_sql('customer_data', engine, if_exists='replace', index=False)

6. Run SQL Queries

Open sql/analysis_queries.sql in SSMS and execute queries

7. Open Power BI Dashboard

Open:
powerbi/dashboard.pbix
