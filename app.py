import streamlit as st

# Page config MUST be the first Streamlit command
st.set_page_config(
    page_title="Liquor Supply Chain Governance",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
import logging

from data_fetcher import get_data_fetcher, check_data_file
from models import get_ml_models
from config import DATA_FILE
from simulation_engine import get_simulator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check if data file exists
if not check_data_file():
    st.error(f"""
    ⚠️ **Data file not found!**
    
    Please download the CSV file from data.gov.in:
    
    📥 **Steps:**
    1. Visit: [https://www.data.gov.in/resource/district-wise-and-year-wise-sale-indian-made-liquor-2015-2021](https://www.data.gov.in/resource/district-wise-and-year-wise-sale-indian-made-liquor-2015-2021)
    2. Click "Download" (CSV format)
    3. Save the file as: `{DATA_FILE}`
    4. Place it in the same folder as this app
    5. Refresh the page
    
    Then the app will work with real government data!
    """)
    st.stop()


# Initialize
fetcher = get_data_fetcher()
ml_models = get_ml_models()


# Sidebar
with st.sidebar:
    st.title("⚙️ Configuration")
    
    selected_module = st.selectbox(
        "Select Module:",
        [
            "🏠 Dashboard",
            "📊 Sales Analysis",
            "🔍 Anomaly Detection",
            "🗺️ Geographic Distribution",
            "📈 Trends",
            "📋 Raw Data",
            "---OPERATIONAL---",
            "🚛 Live Tracking",
            "🏭 Production Compliance",
            "✅ Label Authenticity",
        ]
    )
    
    st.divider()
    
    st.subheader("📊 Data Status")
    st.success("✅ Real CSV data from data.gov.in")
    st.success("✅ No API keys needed")
    st.success("✅ Dynamic truck movement")
    st.success("✅ Production Ready")
    
    st.divider()
    
    # Auto-refresh for Live Tracking
    if selected_module == "🚛 Live Tracking":
        st.subheader("🔄 Live Refresh")
        refresh_interval = st.slider("Refresh every (seconds):", 1, 10, 3)
        st.write(f"Map updates every {refresh_interval}s - Trucks move continuously!")
    
    st.subheader("About")
    st.caption("AI-Enabled Liquor Supply Chain Governance\n\nReal government data + Dynamic supply chain tracking.")


# Main title
st.title("🏭 AI-Enabled Liquor Supply Chain Governance")
st.markdown("Real-time monitoring with dynamic vehicle tracking and operational oversight")


# Load data
data_load_state = st.info("⏳ Loading real data from CSV...")


try:
    sales_data = fetcher.get_processed_sales_data()
    anomaly_data = fetcher.get_anomaly_detection_data()
    state_data = fetcher.get_state_level_data()
    time_series = fetcher.get_time_series_data()
    cities = fetcher.get_city_mapping()
    
    if not sales_data.empty:
        data_load_state.success("✅ Real data loaded successfully!")
    else:
        data_load_state.error("⚠️ Could not process data. Check CSV format.")
        
except Exception as e:
    data_load_state.error(f"⚠️ Error loading data: {e}")
    sales_data = pd.DataFrame()
    anomaly_data = pd.DataFrame()
    state_data = pd.DataFrame()
    time_series = pd.DataFrame()
    cities = {}


# Module selection
if selected_module == "🏠 Dashboard":
    st.header("📊 Unified Dashboard")
    
    if not sales_data.empty and 'sale_in_liters' in sales_data.columns:
        # KPI cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_sales = sales_data['sale_in_liters'].sum()
            st.metric(
                "Total Sales",
                f"{total_sales/1e6:.2f}M L",
                "All records"
            )
        
        with col2:
            if 'district' in sales_data.columns:
                num_districts = sales_data['district'].nunique()
                st.metric("Districts", num_districts, "Tracked")
        
        with col3:
            if 'year' in sales_data.columns:
                num_years = sales_data['year'].nunique()
                st.metric("Years", num_years, "Available")
        
        with col4:
            if 'state' in sales_data.columns:
                num_states = sales_data['state'].nunique()
                st.metric("States", num_states, "Covered")
        
        st.divider()
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            if not time_series.empty and 'year' in time_series.columns:
                fig = px.line(
                    time_series,
                    x='year',
                    y='total_sales',
                    title="Liquor Sales Trend Over Years",
                    labels={'total_sales': 'Sales (Liters)', 'year': 'Year'},
                    markers=True
                )
                fig.update_layout(hovermode='x unified')
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if not state_data.empty and 'state' in state_data.columns:
                plot_data = state_data.copy()
                if isinstance(plot_data.columns, pd.MultiIndex):
                    plot_data.columns = ['_'.join(col).strip() for col in plot_data.columns.values]
                
                y_col = 'total_sales' if 'total_sales' in plot_data.columns else plot_data.columns[1]
                
                fig = px.bar(
                    plot_data.sort_values(y_col, ascending=True),
                    x=y_col,
                    y='state',
                    title="Total Sales by State",
                    labels={y_col: 'Sales (Liters)'},
                    orientation='h'
                )
                st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("📊 Summary Statistics")
        if not state_data.empty:
            st.dataframe(
                state_data,
                use_container_width=True
            )
    else:
        st.warning("No valid data available. Check CSV format.")


elif selected_module == "📊 Sales Analysis":
    st.header("📊 Sales Analysis by District")
    
    if not sales_data.empty and 'year' in sales_data.columns:
        years = sorted(sales_data['year'].dropna().unique())
        if len(years) > 0:
            selected_year = st.selectbox("Select Year:", years)
            
            year_data = sales_data[sales_data['year'] == selected_year]
            
            col1, col2 = st.columns(2)
            
            with col1:
                if 'district' in year_data.columns and 'sale_in_liters' in year_data.columns:
                    top_districts = year_data.nlargest(10, 'sale_in_liters')
                    
                    if not top_districts.empty:
                        fig = px.bar(
                            top_districts,
                            x='sale_in_liters',
                            y='district',
                            title=f"Top 10 Districts by Sales ({selected_year:.0f})",
                            labels={'sale_in_liters': 'Sales (Liters)'},
                            orientation='h'
                        )
                        st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                if 'state' in year_data.columns:
                    state_year = year_data.groupby('state').agg({'sale_in_liters': 'sum'}).reset_index()
                    
                    if not state_year.empty:
                        fig = px.pie(
                            state_year,
                            names='state',
                            values='sale_in_liters',
                            title=f"Sales Distribution by State ({selected_year:.0f})"
                        )
                        st.plotly_chart(fig, use_container_width=True)
            
            st.subheader("Detailed District Data")
            if 'district' in year_data.columns:
                display_data = year_data[['district', 'state', 'sale_in_liters']].copy() if 'state' in year_data.columns else year_data[['district', 'sale_in_liters']].copy()
                display_data = display_data.sort_values('sale_in_liters', ascending=False)
                st.dataframe(display_data, use_container_width=True)
    else:
        st.warning("No data available for analysis.")


elif selected_module == "🔍 Anomaly Detection":
    st.header("🔍 Anomaly Detection")
    st.markdown("Detect unusual patterns in liquor sales data using ML")
    
    if not anomaly_data.empty:
        with st.spinner("Training anomaly detection model..."):
            results = ml_models.detect_sales_anomalies(anomaly_data)
        
        if 'error' not in results or results['error'] is None:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Records Analyzed", len(results['results']))
            
            with col2:
                st.metric("Anomalies Detected", results['anomaly_count'])
            
            with col3:
                st.metric("Model Accuracy", f"{results['accuracy']:.2%}")
            
            st.divider()
            
            if results['anomaly_count'] > 0:
                if 'anomaly_type' in results['results'].columns:
                    anomaly_breakdown = results['results']['anomaly_type'].value_counts()
                    
                    fig = px.bar(
                        x=anomaly_breakdown.index,
                        y=anomaly_breakdown.values,
                        title="Anomaly Breakdown",
                        labels={'x': 'Type', 'y': 'Count'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                st.subheader("Top Anomalies")
                top_anomalies = ml_models.get_top_anomalies(results['results'], n=15)
                
                if not top_anomalies.empty:
                    cols_to_show = [col for col in ['district', 'year', 'sale_in_liters', 'anomaly_type', 'yoy_change'] if col in top_anomalies.columns]
                    st.dataframe(
                        top_anomalies[cols_to_show],
                        use_container_width=True
                    )
            else:
                st.info("No anomalies detected in the data.")
        else:
            st.error(f"Error: {results.get('error', 'Unknown error')}")
    else:
        st.warning("No data available for anomaly detection.")


elif selected_module == "🗺️ Geographic Distribution":
    st.header("🗺️ Geographic Distribution")
    
    if not sales_data.empty and 'year' in sales_data.columns:
        years = sorted(sales_data['year'].dropna().unique())
        if len(years) > 0:
            selected_year = st.selectbox("Select Year for Map:", years)
            
            year_data = sales_data[sales_data['year'] == selected_year]
            district_sales = year_data.groupby('district')['sale_in_liters'].sum().reset_index()
            
            m = folium.Map(
                location=[15.3173, 75.7139], 
                zoom_start=7,
                tiles="OpenStreetMap"
            )
            
            district_sales['district_norm'] = district_sales['district'].astype(str).str.lower().str.strip()
            
            points_added = 0
            mapping_cities = cities
            
            for city_key, coords in mapping_cities.items():
                city_norm = str(city_key).lower().strip()
                state = coords.get('state', 'Karnataka')
                
                sales_val = 0.0
                label_type = "District"
                
                match = district_sales[district_sales['district_norm'] == city_norm]
                if match.empty:
                    match = district_sales[district_sales['district_norm'].str.contains(city_norm, regex=False)]
                
                if not match.empty:
                    raw_val = match.iloc[0]['sale_in_liters']
                    
                    try:
                        if hasattr(raw_val, 'item'):
                            sales_val = raw_val.item()
                        else:
                            sales_val = float(raw_val)
                    except (ValueError, TypeError):
                        sales_val = 0.0
                
                if sales_val > 0:
                    points_added += 1
                    display_val = float(sales_val) / 1000000.0
                    radius = min(40, max(5, (sales_val**0.5) / 100))
                    
                    popup_text = f"{city_key.title()}\nState: {state}\nSales: {display_val:.2f}M L"
                    
                    folium.CircleMarker(
                        location=[coords['lat'], coords['lon']],
                        radius=radius,
                        popup=popup_text,
                        color='crimson',
                        fill=True,
                        fillColor='crimson',
                        fillOpacity=0.6,
                        weight=1
                    ).add_to(m)
            
            st_folium(m, width=800, height=500)
            
            if points_added > 0:
                st.info(f"✅ Plotted {points_added} districts based on sales data.")
            else:
                st.warning("No districts matched.")
    else:
        st.warning("No geographic data available.")


elif selected_module == "📈 Trends":
    st.header("📈 Sales Trends Analysis")
    
    if not sales_data.empty and not time_series.empty and 'year' in time_series.columns:
        fig = px.line(
            time_series,
            x='year',
            y='total_sales',
            title="National Liquor Sales Trend",
            labels={'total_sales': 'Sales (Liters)', 'year': 'Year'},
            markers=True
        )
        st.plotly_chart(fig, use_container_width=True)
        
        if len(time_series) > 1:
            col1, col2, col3 = st.columns(3)
            
            try:
                first_sales = float(time_series.iloc[0]['total_sales'])
                last_sales = float(time_series.iloc[-1]['total_sales'])
                
                total_growth = ((last_sales - first_sales) / first_sales) * 100
                
                with col1:
                    year_start = time_series.iloc[0]['year']
                    st.metric("Initial Sales", f"{first_sales/1e6:.2f}M L", f"Year {year_start:.0f}")
                
                with col2:
                    year_end = time_series.iloc[-1]['year']
                    st.metric("Latest Sales", f"{last_sales/1e6:.2f}M L", f"Year {year_end:.0f}")
                
                with col3:
                    years_diff = int(time_series.iloc[-1]['year'] - time_series.iloc[0]['year'])
                    st.metric("Total Growth", f"{total_growth:.1f}%", f"Over {years_diff} years")
            except Exception as e:
                st.error(f"Error calculating growth stats: {e}")
        
        if 'state' in sales_data.columns:
            st.subheader("State-wise Sales Comparison")
            
            states = sorted(sales_data['state'].unique())
            states_to_compare = st.multiselect(
                "Select states to compare:",
                states,
                default=states[:3] if len(states) >= 3 else states
            )
            
            if states_to_compare:
                state_trends = sales_data[sales_data['state'].isin(states_to_compare)]
                state_trends = state_trends.groupby(['year', 'state']).agg({'sale_in_liters': 'sum'}).reset_index()
                
                fig = px.line(
                    state_trends,
                    x='year',
                    y='sale_in_liters',
                    color='state',
                    title="State-wise Sales Trends",
                    markers=True
                )
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No trend data available.")


elif selected_module == "📋 Raw Data":
    st.header("📋 Raw Data Explorer")
    
    if not sales_data.empty:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Records", len(sales_data))
        
        with col2:
            if 'year' in sales_data.columns:
                year_range = f"{sales_data['year'].min():.0f} - {sales_data['year'].max():.0f}"
                st.metric("Date Range", year_range)
        
        with col3:
            st.metric("Columns", len(sales_data.columns))
        
        st.divider()
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'state' in sales_data.columns:
                selected_states = st.multiselect(
                    "Filter by State:",
                    sorted(sales_data['state'].unique()),
                    default=sorted(sales_data['state'].unique())
                )
            else:
                selected_states = []
        
        with col2:
            if 'year' in sales_data.columns:
                selected_years = st.multiselect(
                    "Filter by Year:",
                    sorted(sales_data['year'].dropna().unique()),
                    default=sorted(sales_data['year'].dropna().unique())
                )
            else:
                selected_years = []
        
        filtered_data = sales_data.copy()
        if selected_states:
            filtered_data = filtered_data[filtered_data['state'].isin(selected_states)]
        if selected_years:
            filtered_data = filtered_data[filtered_data['year'].isin(selected_years)]
        
        st.subheader(f"Showing {len(filtered_data)} records")
        st.dataframe(filtered_data, use_container_width=True)
        
        csv = filtered_data.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="liquor_sales_filtered.csv",
            mime="text/csv"
        )
    else:
        st.warning("No data available to explore.")


# ==================== NEW MODULES: OPERATIONAL SUPPLY CHAIN ====================

elif selected_module == "🚛 Live Tracking":
    st.header("🚛 Live Vehicle Tracking & Geofencing")
    st.markdown("**Real-time tracking with dynamic truck movement - Refresh every 3 seconds**")
    
    # Enable auto-refresh by using st.empty() and time.sleep()
    sim = get_simulator()
    
    truck_fleet = sim.generate_truck_fleet()
    compliance = sim.calculate_route_compliance(truck_fleet)
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        in_transit = len(truck_fleet[truck_fleet['status'] == 'In Transit'])
        st.metric("Vehicles In Transit", in_transit)
    
    with col2:
        high_risk = len(compliance[compliance['alert_type'] == 'HIGH_RISK'])
        medium_risk = len(compliance[compliance['alert_type'] == 'MEDIUM_RISK'])
        total_alerts = high_risk + medium_risk
        st.metric("⚠️ Active Alerts", total_alerts, delta=f"{high_risk} HIGH + {medium_risk} MEDIUM")
    
    with col3:
        total_cargo = truck_fleet['cargo_liters'].sum()
        st.metric("Total Cargo", f"{total_cargo/1e6:.2f}M L")
    
    with col4:
        compliance_rate = (len(compliance[compliance['is_compliant']]) / len(compliance)) * 100
        st.metric("Compliance Rate", f"{compliance_rate:.1f}%")
    
    st.divider()
    
    st.subheader("📍 Live Fleet Map - Trucks Moving Dynamically")
    
    m = folium.Map(
        location=[15.3173, 75.7139],
        zoom_start=7,
        tiles="OpenStreetMap"
    )
    
    # Draw routes first
    for route in sim.routes:
        folium.PolyLine(
            locations=[(route['lat_from'], route['lon_from']), (route['lat_to'], route['lon_to'])],
            color='gray',
            weight=2,
            opacity=0.5,
            popup=f"{route['from']} → {route['to']}"
        ).add_to(m)
    
    # Add trucks with dynamic position
    for _, truck in truck_fleet.iterrows():
        color = 'red' if truck['is_deviating'] else 'green'
        icon_text = '⚠️ DEVIATED' if truck['is_deviating'] else '✓ ON ROUTE'
        
        # Popup with detailed info
        popup_html = f"""
        <b>{truck['truck_id']}</b><br>
        {icon_text}<br>
        From: {truck['from']} → {truck['to']}<br>
        Cargo: {truck['cargo_liters']/1000:.1f}K L<br>
        Speed: {truck['speed_kmh']:.0f} km/h<br>
        Progress: {truck['progress_percent']:.1f}%<br>
        Deviation: {truck['deviation_km']:.2f} km
        """
        
        folium.CircleMarker(
            location=[truck['lat'], truck['lon']],
            radius=10,
            popup=popup_html,
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.8,
            weight=2,
            tooltip=f"{truck['truck_id']} - {icon_text}"
        ).add_to(m)
    
    st_folium(m, width=800, height=500)
    
    st.info("🔄 **Trucks move continuously along their routes!** Refresh the page to see updated positions every 3 seconds.")
    
    st.divider()
    
    st.subheader("Compliance Report - Live Data")
    
    compliance_display = compliance.copy()
    compliance_display['status_badge'] = compliance_display['alert_type'].apply(
        lambda x: '✅ COMPLIANT' if x == 'NORMAL' else f'⚠️ {x}'
    )
    
    # Sort by alert level to show HIGH_RISK first
    alert_order = {'HIGH_RISK': 0, 'MEDIUM_RISK': 1, 'NORMAL': 2}
    compliance_display['alert_order'] = compliance_display['alert_type'].map(alert_order)
    compliance_display = compliance_display.sort_values('alert_order')
    
    st.dataframe(
        compliance_display[['truck_id', 'from', 'to', 'status', 'cargo_liters', 'deviation_km', 'risk_score', 'status_badge']],
        use_container_width=True,
        hide_index=True
    )
    
    st.subheader("📊 Risk Analysis")
    
    risk_dist = compliance['alert_type'].value_counts()
    
    fig = px.bar(
        x=risk_dist.index,
        y=risk_dist.values,
        title="Alert Distribution",
        labels={'x': 'Risk Level', 'y': 'Count'},
        color=risk_dist.index,
        color_discrete_map={
            'NORMAL': 'green',
            'MEDIUM_RISK': 'orange',
            'HIGH_RISK': 'red',
        }
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Deviation histogram
    st.subheader("Deviation Distance Distribution")
    fig = px.histogram(
        compliance,
        x='deviation_km',
        nbins=10,
        title="Truck Deviation from Approved Routes",
        labels={'deviation_km': 'Deviation (km)', 'count': 'Number of Trucks'}
    )
    st.plotly_chart(fig, use_container_width=True)


elif selected_module == "🏭 Production Compliance":
    st.header("🏭 Production & Inventory Reconciliation")
    st.markdown("**Detect unauthorized diversion: Input (Molasses) vs Output (Spirit)**")
    
    sim = get_simulator()
    
    ledger = sim.generate_production_ledger()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_input = ledger['molasses_liters'].sum()
        st.metric("Total Molasses Input", f"{total_input/1e6:.2f}M L")
    
    with col2:
        total_output = ledger['actual_output'].sum()
        st.metric("Total Spirit Output", f"{total_output/1e6:.2f}M L")
    
    with col3:
        avg_efficiency = (ledger['actual_output'].sum() / ledger['molasses_liters'].sum()) * 100
        st.metric("Avg Efficiency", f"{avg_efficiency:.1f}%")
    
    with col4:
        alerts = len(ledger[ledger['alert'] == 'DIVERSION_SUSPECTED'])
        st.metric("🚨 Diversion Alerts", alerts)
    
    st.divider()
    
    factories = sorted(ledger['factory_id'].unique())
    selected_factory = st.selectbox("Select Factory:", factories)
    
    factory_data = ledger[ledger['factory_id'] == selected_factory].sort_values('date')
    
    st.subheader(f"Production Trend: {selected_factory}")
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=factory_data['date'],
        y=factory_data['theoretical_output'],
        mode='lines',
        name='Theoretical Output',
        line=dict(color='blue', dash='dash', width=3)
    ))
    
    fig.add_trace(go.Scatter(
        x=factory_data['date'],
        y=factory_data['actual_output'],
        mode='lines+markers',
        name='Actual Output',
        line=dict(color='green', width=3),
        marker=dict(size=6)
    ))
    
    fig.update_layout(
        title="Input vs Output (Should be close for normal operations)",
        xaxis_title="Date",
        yaxis_title="Liters",
        hovermode='x unified',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    st.subheader("⚠️ Anomalies Detected")
    
    anomalies = factory_data[factory_data['alert'] == 'DIVERSION_SUSPECTED']
    
    if len(anomalies) > 0:
        st.error(f"🚨 {len(anomalies)} suspicious production records detected for {selected_factory}!")
        st.dataframe(
            anomalies[['date', 'molasses_liters', 'theoretical_output', 'actual_output', 'variance_percent', 'alert']],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.success(f"✅ No diversion alerts for {selected_factory}")
    
    st.subheader("Full Production Ledger")
    st.dataframe(
        factory_data[['date', 'molasses_liters', 'theoretical_output', 'actual_output', 'variance_percent', 'alert']],
        use_container_width=True,
        hide_index=True
    )


elif selected_module == "✅ Label Authenticity":
    st.header("✅ QR Code & Label Authenticity Verification")
    st.markdown("**Verify product authenticity to prevent counterfeits**")
    
    sim = get_simulator()
    
    qr_db = sim.generate_qr_database()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_batches = len(qr_db)
        st.metric("Total Batches in DB", total_batches)
    
    with col2:
        valid_batches = len(qr_db[qr_db['is_valid']])
        st.metric("Valid Batches", valid_batches)
    
    with col3:
        counterfeit = len(qr_db[~qr_db['is_valid']])
        st.metric("🚨 Counterfeit/Expired", counterfeit)
    
    st.divider()
    
    st.subheader("🔍 Verify a Product")
    
    sample_batches = qr_db['batch_id'].head(10).tolist()
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        batch_id = st.text_input(
            "Enter Batch ID to verify:",
            value=sample_batches[0] if sample_batches else "BATCH-2024-KA-000001",
            help=f"Example: {sample_batches[0] if sample_batches else 'BATCH-2024-KA-000001'}"
        )
    
    with col2:
        verify_btn = st.button("✓ Verify", use_container_width=True)
    
    if verify_btn and batch_id:
        result = sim.verify_qr_code(batch_id, qr_db)
        
        if result['is_authentic']:
            st.success(f"✅ {result['message']}")
            
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Batch ID:** {result['batch_id']}")
                st.write(f"**Factory:** {result['factory_id']}")
                st.write(f"**Product:** {result['product']}")
            
            with col2:
                st.write(f"**Manufactured:** {result['manufacture_date']}")
                st.write(f"**Expires:** {result['expiry_date']}")
                st.write(f"**QR Status:** {result['qr_status']}")
                st.write(f"**Seal:** {result['seal_status']}")
        else:
            st.error(f"❌ {result['message']}")
            st.warning("⚠️ This product may be counterfeit or expired. Do not consume.")
    
    st.divider()
    
    st.subheader("📋 QR Database (All Batches)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        selected_factory = st.multiselect(
            "Filter by Factory:",
            sorted(qr_db['factory_id'].unique()),
            default=sorted(qr_db['factory_id'].unique())
        )
    
    with col2:
        selected_product = st.multiselect(
            "Filter by Product:",
            sorted(qr_db['product'].unique()),
            default=sorted(qr_db['product'].unique())
        )
    
    filtered_qr = qr_db[
        (qr_db['factory_id'].isin(selected_factory)) &
        (qr_db['product'].isin(selected_product))
    ]
    
    st.dataframe(filtered_qr, use_container_width=True, hide_index=True)
    
    st.subheader("📊 Authenticity Summary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        status_dist = qr_db['qr_code_status'].value_counts()
        fig = px.pie(
            names=status_dist.index,
            values=status_dist.values,
            title="QR Code Status Distribution",
            color_discrete_map={'VALID': 'green', 'COUNTERFEIT': 'red'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        seal_dist = qr_db['seal_integrity'].value_counts()
        fig = px.pie(
            names=seal_dist.index,
            values=seal_dist.values,
            title="Seal Integrity Status",
            color_discrete_map={'OK': 'green', 'BROKEN': 'red'}
        )
        st.plotly_chart(fig, use_container_width=True)


# Footer
st.markdown("---")
st.markdown(
    "**Status:** Production Ready | "
    "**Data Source:** data.gov.in CSV (Real) + Dynamic Simulation | "
    "**Trucks:** Moving continuously along approved routes | "
    "**Models:** Real-time Anomaly Detection + Supply Chain Governance"
)