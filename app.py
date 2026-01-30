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
        ["🏠 Dashboard", "📊 Sales Analysis", "🔍 Anomaly Detection", "🗺️ Geographic Distribution", "📈 Trends", "📋 Raw Data"]
    )
    
    st.divider()
    
    st.subheader("📊 Data Status")
    st.success("✅ Real CSV data from data.gov.in")
    st.success("✅ No API keys needed")
    st.success("✅ No generated data")
    st.success("✅ Production Ready")
    
    st.divider()
    
    st.subheader("About")
    st.caption("AI-Enabled Liquor Supply Chain Governance\n\nReal-time anomaly detection using actual government datasets.")


# Main title
st.title("🏭 AI-Enabled Liquor Supply Chain Governance")
st.markdown("Real-time monitoring with actual government data from data.gov.in")


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
                # Ensure we have flat columns for plotting
                plot_data = state_data.copy()
                if isinstance(plot_data.columns, pd.MultiIndex):
                    plot_data.columns = ['_'.join(col).strip() for col in plot_data.columns.values]
                
                # Use the correct column name based on data structure
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
        # Filter by year
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
            
            # Filter data for selected year
            year_data = sales_data[sales_data['year'] == selected_year]
            
            # Aggregate by District
            district_sales = year_data.groupby('district')['sale_in_liters'].sum().reset_index()
            
            # Create folium map centered on Karnataka
            m = folium.Map(
                location=[15.3173, 75.7139], 
                zoom_start=7,
                tiles="OpenStreetMap"
            )
            
            # Normalize district names for matching
            district_sales['district_norm'] = district_sales['district'].astype(str).str.lower().str.strip()
            
            points_added = 0
            
            # Use cities dict from config
            mapping_cities = cities
            
            for city_key, coords in mapping_cities.items():
                city_norm = str(city_key).lower().strip()
                state = coords.get('state', 'Karnataka')
                
                sales_val = 0.0
                label_type = "District"
                
                # Try to find a match
                match = district_sales[district_sales['district_norm'] == city_norm]
                if match.empty:
                    match = district_sales[district_sales['district_norm'].str.contains(city_norm, regex=False)]
                
                if not match.empty:
                    # FIX: Safely extract scalar value
                    raw_val = match.iloc[0]['sale_in_liters']
                    
                    # Convert to standard Python float, handling numpy types
                    try:
                        if hasattr(raw_val, 'item'):
                            sales_val = raw_val.item()
                        else:
                            sales_val = float(raw_val)
                    except (ValueError, TypeError):
                        sales_val = 0.0
                
                if sales_val > 0:
                    points_added += 1
                    
                    # Calculate display value as a native float
                    display_val = float(sales_val) / 1000000.0
                    
                    # Calculate radius
                    radius = min(40, max(5, (sales_val**0.5) / 100))
                    
                    # FIX: Use safe variables in f-string
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
                st.warning("No districts matched. Check if city names in config.py match CSV district names.")
    else:
        st.warning("No geographic data available.")


elif selected_module == "📈 Trends":
    st.header("📈 Sales Trends Analysis")
    
    if not sales_data.empty and not time_series.empty and 'year' in time_series.columns:
        # Overall trend
        fig = px.line(
            time_series,
            x='year',
            y='total_sales',
            title="National Liquor Sales Trend",
            labels={'total_sales': 'Sales (Liters)', 'year': 'Year'},
            markers=True
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Growth statistics
        if len(time_series) > 1:
            col1, col2, col3 = st.columns(3)
            
            # FIX: Use .iloc properly for position-based indexing
            try:
                first_sales = time_series.iloc[0]['total_sales']
                last_sales = time_series.iloc[-1]['total_sales']
                
                # Convert to float to avoid numpy issues
                first_sales = float(first_sales)
                last_sales = float(last_sales)
                
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
        
        # State-wise trends
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
        
        # Filter options
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
        
        # Apply filters
        filtered_data = sales_data.copy()
        if selected_states:
            filtered_data = filtered_data[filtered_data['state'].isin(selected_states)]
        if selected_years:
            filtered_data = filtered_data[filtered_data['year'].isin(selected_years)]
        
        st.subheader(f"Showing {len(filtered_data)} records")
        st.dataframe(filtered_data, use_container_width=True)
        
        # Download button
        csv = filtered_data.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="liquor_sales_filtered.csv",
            mime="text/csv"
        )
    else:
        st.warning("No data available to explore.")


# Footer
st.markdown("---")
st.markdown(
    "**Status:** Production Ready | "
    "**Data Source:** data.gov.in CSV | "
    "**Dataset:** District Wise And Year Wise Sale Of Indian Made Liquor (2015-2021) | "
    "**Models:** Real-time Anomaly Detection"
)
