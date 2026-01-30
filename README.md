

***

```markdown
# 🏭 AI-Enabled Liquor Supply Chain Governance System

**Real-time monitoring, anomaly detection, and compliance tracking for liquor supply chains using machine learning and government data.**

This project implements a **Hybrid Architecture** that combines:
1.  **Real Government Data:** Analyzes actual liquor sales trends, district-wise performance, and historical anomalies using CSV data from *data.gov.in*.
2.  **Operational Simulation:** Demonstrates real-time tracking capabilities with a dynamic simulation engine for vehicle movement, production ledgers, and QR code authentication.

---

## 🎯 Key Features

### Layer 1: Operational Monitoring (Simulated Real-Time)
*   **🚛 Live Truck Tracking (Dynamic):**
    *   Real-time vehicle movement along 5 major routes (Bengaluru, Mysore, Hassan, etc.).
    *   **Geofencing Alerts:** Automatic detection of route deviations.
        *   **Green:** Compliant (< 10km deviation).
        *   **Orange:** Medium Risk (10-15km deviation).
        *   **Red:** High Risk (> 15km deviation).
    *   Time-based GPS interpolation (trucks move continuously throughout the day).
*   **🏭 Production Compliance:**
    *   Digital twin of distillery operations.
    *   Monitors Input (Molasses) vs. Output (Spirit) ratios.
    *   Automatically flags "Diversion Alerts" when output falls below theoretical efficiency.
*   **✅ Label Authentication:**
    *   Anti-counterfeit module using Batch IDs.
    *   Verifies manufacturing date, expiry, and seal integrity.

### Layer 2: Strategic Analytics (Real Data)
*   **🔍 AI Anomaly Detection:** Uses Machine Learning (Isolation Forest) to detect unusual sales spikes in specific districts.
*   **📊 Sales Analysis:** Deep dive into district-wise consumption patterns and revenue generation.
*   **🗺️ Geographic Distribution:** Interactive maps visualizing sales density across Karnataka.
*   **📈 Trend Forecasting:** Historical time-series analysis of liquor consumption.

---

## 📊 Data Sources

1.  **Strategic Data:** Real liquor sales datasets sourced from the **Government of India (data.gov.in)** and Ministry of Commerce statistics.
2.  **Operational Data:** Generated via `simulation_engine.py` to mimic real-world telemetry (GPS coordinates, IoT sensor data, and QR records) for demonstration purposes.

---

## 🛠️ Tech Stack

*   **Frontend:** Streamlit (Python)
*   **Data Processing:** Pandas, NumPy
*   **Machine Learning:** Scikit-learn (Isolation Forest)
*   **Visualization:** Plotly Express, Folium (Maps)
*   **Routing Logic:** Custom time-based interpolation algorithms

---

## 🚀 Step-by-Step Setup Guide

Follow these instructions to run the application locally.

### Prerequisites
*   Python 3.8 or higher installed.
*   Git installed.

### 1. Clone the Repository
Open your terminal or command prompt and run:

```bash
git clone https://github.com/Hrithik875/liquor-supply-chain-governance.git
cd liquor-supply-chain-governance
```

### 2. Create a Virtual Environment (Recommended)
This keeps your dependencies isolated.

**For Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**For Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
Install the required Python packages:

```bash
pip install -r requirements.txt
```

### 4. Verify Data Files
Ensure the following file exists in your project root directory. This contains the real government data used for analytics.

*   `liquor_sales_data.csv`

*(If this file is missing, please download the specific dataset from data.gov.in or use the sample provided in the repository).*

### 5. Run the Application
Launch the Streamlit dashboard:

```bash
streamlit run app.py
```

*The app will automatically open in your default web browser at `http://localhost:8501`.*

---

## 📂 Project Structure

```text
liquor-supply-chain-governance/
├── app.py                   # Main application entry point (UI & Logic integration)
├── simulation_engine.py     # Core logic for Truck GPS, Production, and QR simulation
├── data_fetcher.py          # Handles loading and cleaning of real CSV data
├── models.py                # Machine Learning models for anomaly detection
├── config.py                # Configuration constants and map coordinates
├── liquor_sales_data.csv    # Real government dataset
├── requirements.txt         # List of Python dependencies
└── README.md                # Project documentation
```

---

## 📖 User Guide

### How to use the Live Tracking Module
1.  Navigate to **"🚛 Live Tracking"** in the sidebar.
2.  **Map View:** Observe the trucks moving along grey route lines.
    *   **Green Circles:** Normal operation.
    *   **Red Circles:** Trucks that have deviated significantly from their path.
3.  **Dashboard:** Check the "Active Alerts" card. It matches the number of Red/Orange circles on the map.
4.  **Refresh:** To see trucks move, refresh the page (F5) or wait for the auto-refresh interval. The system calculates position based on the current time of day.

### How to use Production Compliance
1.  Navigate to **"🏭 Production Compliance"**.
2.  Select a **Factory** from the dropdown.
3.  Observe the **"Actual vs Theoretical Spirit"** chart.
4.  Look for red markers indicating **"Diversion Alerts"** (where output is suspiciously low compared to input).

### How to use Anomaly Detection
1.  Navigate to **"🔍 Anomaly Detection"**.
2.  The system uses the `liquor_sales_data.csv` to train an Isolation Forest model.
3.  View the table to see specific months and districts where sales were statistically abnormal.

---

## 🔧 Troubleshooting

**Issue: "Trucks are not moving on the map."**
*   **Solution:** The movement is time-based. Refresh your browser page to calculate the new positions based on the current time.

**Issue: "FileNotFoundError: liquor_sales_data.csv"**
*   **Solution:** Ensure the CSV file is located exactly in the root folder where you are running `streamlit run app.py`.

**Issue: "ModuleNotFoundError"**
*   **Solution:** Ensure you have activated your virtual environment and installed all requirements using `pip install -r requirements.txt`.

---

## 📜 License

This project is open-source and available under the MIT License.
```