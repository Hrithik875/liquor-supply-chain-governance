import pandas as pd
import numpy as np
import logging
import streamlit as st
import re
from config import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealDataFetcher:
    """Load and process REAL CSV data from data.gov.in"""
    
    @st.cache_data(ttl=CACHE_DURATION)
    def fetch_liquor_sales_data(_self):
        """Load real liquor sales CSV data with robust encoding handling"""
        try:
            if not check_data_file():
                logger.error(f"Data file '{DATA_FILE}' not found!")
                return pd.DataFrame()
            
            logger.info(f"Loading real data from {DATA_FILE}...")
            
            # Try different encodings
            encodings = ['utf-8', 'cp1252', 'iso-8859-1', 'windows-1252']
            for encoding in encodings:
                try:
                    df = pd.read_csv(DATA_FILE, encoding=encoding)
                    logger.info(f"✓ Loaded {len(df)} records with {encoding}")
                    return df
                except UnicodeDecodeError:
                    continue
            
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error loading CSV: {e}")
            return pd.DataFrame()
    
    @st.cache_data(ttl=CACHE_DURATION)
    def get_processed_sales_data(_self):
        """Process and standardize the loaded CSV data"""
        df = _self.fetch_liquor_sales_data()
        if df.empty: return pd.DataFrame()
        
        try:
            # 1. Standardize column names
            df.columns = [str(col).lower().strip() for col in df.columns]
            
            # 2. Identify ID columns (Metadata)
            id_vars = []
            possible_ids = ['sl no', 'division', 'district', 'state', 'state code', 'state name']
            
            for col in df.columns:
                if col in possible_ids:
                    id_vars.append(col)
            
            # 3. Identify Value columns (Years)
            # We look for columns that look like years (e.g. "2015-16" or "sale...2015-16")
            year_pattern = re.compile(r'(\d{4}-\d{2}|\d{4})')
            value_vars = []
            rename_map = {}
            
            for col in df.columns:
                if col in id_vars: continue
                if 'growth' in col: continue  # Skip growth columns
                
                # Check if column contains a year
                match = year_pattern.search(col)
                if match:
                    year_str = match.group(1)
                    rename_map[col] = year_str  # Rename "sale...2015-16" to "2015-16"
                    value_vars.append(year_str)
            
            # Apply renaming
            df = df.rename(columns=rename_map)
            
            # 4. Melt the DataFrame (Wide -> Long format)
            if value_vars:
                # Keep only ID columns and Year columns
                cols_to_keep = id_vars + value_vars
                df = df[cols_to_keep]
                
                df = df.melt(
                    id_vars=id_vars, 
                    value_vars=value_vars, 
                    var_name='year', 
                    value_name='sale_in_liters'
                )
                logger.info("✓ Melted wide-format data into long-format")
            else:
                # Fallback if no years found (unlikely based on your logs)
                logger.warning("No year columns found, using raw data")
            
            # 5. Clean Data
            # Clean Sales: Remove non-numeric characters
            if 'sale_in_liters' in df.columns:
                df['sale_in_liters'] = df['sale_in_liters'].astype(str).str.replace(r'[^\d.]', '', regex=True)
                df['sale_in_liters'] = pd.to_numeric(df['sale_in_liters'], errors='coerce').fillna(0)
            
            # Clean Year: Extract just the starting year (2015-16 -> 2015)
            if 'year' in df.columns:
                df['year'] = df['year'].astype(str).str.extract(r'(\d{4})').astype(float)
            
            # Standardize 'district' column name
            if 'district' not in df.columns:
                for col in df.columns:
                    if 'district' in col:
                        df = df.rename(columns={col: 'district'})
                        break

            # Add State if missing (Your data is from Karnataka OGD)
            if 'state' not in df.columns:
                df['state'] = 'Karnataka'

            return df
            
        except Exception as e:
            logger.error(f"Error processing data: {e}")
            return df
            
    @st.cache_data(ttl=CACHE_DURATION)
    def get_anomaly_detection_data(_self):
        df = _self.get_processed_sales_data()
        if df.empty: return pd.DataFrame()
        
        try:
            agg_data = df.groupby(['district', 'year']).agg({'sale_in_liters': 'sum'}).reset_index()
            agg_data = agg_data.sort_values(['district', 'year'])
            agg_data['yoy_change'] = agg_data.groupby('district')['sale_in_liters'].pct_change() * 100
            
            agg_data['is_anomaly'] = agg_data['yoy_change'].abs() > 30
            agg_data['anomaly_type'] = 'NORMAL'
            agg_data.loc[agg_data['yoy_change'] > 30, 'anomaly_type'] = 'SPIKE'
            agg_data.loc[agg_data['yoy_change'] < -30, 'anomaly_type'] = 'DROP'
            
            return agg_data
        except Exception:
            return pd.DataFrame()

    @st.cache_data(ttl=CACHE_DURATION)
    def get_state_level_data(_self):
        df = _self.get_processed_sales_data()
        if df.empty: return pd.DataFrame()
        
        # Aggregate
        state_data = df.groupby('state').agg({'sale_in_liters': ['sum', 'mean', 'max']}).reset_index()
        
        # Flatten MultiIndex columns
        state_data.columns = ['state', 'total_sales', 'avg_sales', 'max_sales']
        return state_data


    @st.cache_data(ttl=CACHE_DURATION)
    def get_time_series_data(_self):
        df = _self.get_processed_sales_data()
        if df.empty: return pd.DataFrame()
        ts = df.groupby('year')['sale_in_liters'].sum().reset_index()
        ts.columns = ['year', 'total_sales']
        return ts.sort_values('year')

    def get_city_mapping(self):
        return CITIES

@st.cache_resource
def get_data_fetcher():
    return RealDataFetcher()
