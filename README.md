# Ekvira Transport Dashboard

A complete full-stack web application designed for a coal transport business that owns **10 tipper trucks** transporting coal from a loading mine to multiple power plants and factories. The project features operational logs, real-time fleet simulation on Leaflet maps, detailed expense/revenue bookkeeping, automatic certification alerts, and custom AI forecasting models built in pure Python.

Developed as a premium final year project for B.Tech AIML.

---

## Technical Stack

* **Backend Framework**: Python (Flask)
* **Database Access**: SQLAlchemy ORM (supports SQLite fallback and MySQL)
* **Forms & Validation**: Flask-WTF / WTForms
* **Authentication**: Flask-Login (secure sessions & password hashing)
* **GPS Fleet Tracking**: Leaflet.js (Map layer integration)
* **Charts & Analytics**: Chart.js
* **Reporting Engines**: ReportLab (PDF) & OpenPyXL (Excel)
* **AI Engine**: Custom Linear & Logistic Regression solvers in Pure Python (fully compatible with Python 3.14+ without VS Build Tools requirements)

---

## Features

1. **Operations Dashboard**:
   * Responsive KPI metrics cards with glassmorphic visuals and hover effects.
   * Real-time charts showing Daily Revenue, Expense Distribution, Plant-wise Coal Delivery, and Trip Statuses.
   * Live alerts widget displaying upcoming certification expiries.

2. **Interactive GPS Tracking (Leaflet)**:
   * Maps current locations of all 10 vehicles.
   * Trucks on active trips dynamically move along routes (Chhattisgarh mining routes).
   * Popups display vehicle numbers, speeds, destinations, status, driver, and remaining ETA.
   * Color-coded markers based on status (Green: Running, Yellow: Idle, Red: Maintenance).

3. **Fleet & Driver CRUD Logs**:
   * Add, edit, view, search, and filter tippers and driver details.
   * Detailed Tipper History tabs tracking past trips, fuel receipts, and service tickets.
   * Driver Profiles showing total tonnage hauled and total revenue contributed.

4. **Trip Management**:
   * Dispatch tippers by setting source, destination, and coal weight.
   * Closing a trip calculates diesel cost, toll cost, and misc expenses, and updates the vehicle's odometer.
   * Automates bookkeeping: records income in the income ledger and trip expenses in the expense ledger.

5. **AI Predictions**:
   * **Maintenance Forecaster**: Logistic regression model predicting if a vehicle needs service in the next 30 days based on recent odometer updates and last service date.
   * **Fuel Budget Estimator**: Linear regression model forecasting monthly liters of diesel needed for scheduled distance.
   * **Trip Duration Forecaster**: Predicts hours a trip will take based on load weight, route distance, and truck capacity.
   * **Monthly Profit Timeline**: Extrapolates future net profit based on previous months' net balances.

6. **Professional Exporters**:
   * PDF Report generation styled with ReportLab.
   * Excel sheet compile scripts using OpenPyXL.

---

## Project Structure

```
smart_transport_dashboard/
├── run.py                 # Application entry point & CLI seed manager
├── config.py              # Configuration manager (loads env, handles SQLite fallback)
├── requirements.txt       # Dependencies
├── .env                   # Local variables configuration
├── schema.sql             # SQL Schema for manual MySQL import
├── README.md              # Documentation
└── app/
    ├── __init__.py        # App factory, blueprints, and filters registrations
    ├── models/            # SQLAlchemy database schemas
    ├── routes/            # MVC Controllers (auth, CRUDs, reports, APIs)
    ├── forms/             # Input WTForms validation rules
    ├── services/          # Core Business logic (AI engine, GPS simulator)
    ├── utils/             # Helpers and database seeder
    ├── templates/         # HTML Layouts (Glassmorphic CSS dashboard)
    └── static/
        ├── css/           # style.css (custom dark/light properties, blurs)
        └── js/            # Client scripts (dark_mode.js, live_map.js, charts.js)
```

---

## Quick Setup Instructions

### 1. Extract and Navigate
Make sure you are in the project root folder:
```bash
cd smart_transport_dashboard
```

### 2. Install Dependencies
Install Flask, SQLAlchemy, ReportLab, and other utilities:
```bash
pip install -r requirements.txt
```

### 3. Initialize and Seed Database
Generate the database file (`instance/transport.db` by default) and seed realistic operational history spanning the past 10 months:
```bash
python run.py --seed
```

### 4. Run the Server
Start the local server:
```bash
python run.py
```
Open [http://localhost:5000](http://localhost:5000) in your web browser.

---

## Credentials

Use these credentials to sign in:

* **Administrator role**:
  * Username: `EkviraTransport`
  * Password: `Ekviratransport@3230`
* **Manager role**:
  * Username: `manager`
  * Password: `manager123`

---

## Configuring MySQL Database (Optional)
If you wish to run the app using local MySQL instead of the default SQLite fallback, edit the `.env` file:
```env
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=smart_transport
```
Ensure you create the database in MySQL before running the seeding script:
```sql
CREATE DATABASE smart_transport;
```
Then run the seeding script `python run.py --seed` to populate MySQL.
