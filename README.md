# 🏭 AI-Enabled Liquor Supply Chain Governance System

Real-time monitoring, anomaly detection, and compliance tracking for liquor supply chains using machine learning and real government data.

## 🎯 Features

- **Permit Reconciliation:** Detect over-production and diversion
- **Route Tracking:** Real-time vehicle monitoring with geofencing
- **Label Authentication:** AI-powered counterfeit detection
- **Live Dashboard:** Real-time KPI monitoring
- **Real Data Integration:** Government APIs, OSRM, Kaggle datasets

## 📊 Real Data Sources

- India excise license data (data.gov.in)
- Ministry of Commerce statistics
- OSRM routing for real coordinates
- Kaggle public datasets
- OpenStreetMap

## 🚀 Quick Start

### Local Development

\`\`\`bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/liquor-supply-chain-governance.git
cd liquor-supply-chain-governance

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your API keys

# Run Streamlit app
streamlit run app/app.py
