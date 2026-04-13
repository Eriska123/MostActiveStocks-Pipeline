# 📊 Most Active Stocks Data Pipeline & Dashboard

## 🚀 Overview
This project is a full end-to-end data pipeline that:
- Fetches real-time stock data from Yahoo Finance
- Stores it in SQL Server
- Prevents duplicate records using business logic
- Visualizes insights via a Streamlit dashboard

---

## 🏗 Architecture

API → Python ETL → SQL Server → Streamlit Dashboard

---
## 🗄️ Database Setup

This project uses SQL Server.

### Step 1: Create Database
Run the script:
database/schema.sql


### Step 2: Configure Connection

Update `db.py`:
SERVER=localhost\SQLEXPRESS
DATABASE=StockDB


---

## 🔐 Deduplication Logic

The system prevents duplicate records using a UNIQUE INDEX on:

- stock_id
- price
- change
- percent_change
- volume

## ⚙️ Features

- Automated data pipeline (Windows Task Scheduler)
- Deduplication using business keys
- Real-time dashboard with auto-refresh
- KPI analytics (Top stocks, volume, changes)

---

## 🛠 Tech Stack

- Python (pandas, requests, pyodbc)
- SQL Server
- Streamlit
- Task Scheduler

---

## ▶️ How to Run

### 1. Run pipeline
python pipeline/stocks_pipeline.py


### 2. Launch dashboard
streamlit run app/app.py


---

## 📸 Dashboard Preview

### 🔹 KPI Overview
![KPI](images/kpi.png)

### 🔹 TOP 10 STOCKS BY VOLUME Overview
![Chart](images/chart.png)

### 🔹 Market Trends
![Trend](images/trend.png)

### 🔹 Stock Table
![Table](images/table.png)

---

## 📌 Author
Joseph Yaw Torsu