import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import streamlit as st
import logging

logger = logging.getLogger(__name__)

class RealMLModels:
    """ML models for real supply chain data"""
    
    def __init__(self):
        self.anomaly_model = None
        self.anomaly_scaler = None
    
    def detect_sales_anomalies(self, sales_df):
        """Detect anomalies in real liquor sales data"""
        
        logger.info("Training anomaly detection model...")
        
        if sales_df.empty:
            return {
                'model': None,
                'results': pd.DataFrame(),
                'accuracy': 0,
                'anomaly_count': 0,
                'error': 'No data available'
            }
        
        # Prepare features for anomaly detection
        if 'sale_in_liters' not in sales_df.columns:
            return {
                'model': None,
                'results': sales_df,
                'accuracy': 0,
                'anomaly_count': 0,
                'error': 'Missing sale_in_liters column'
            }
        
        features_df = sales_df[['sale_in_liters']].fillna(0)
        
        if len(features_df) < 2:
            return {
                'model': None,
                'results': sales_df,
                'accuracy': 0,
                'anomaly_count': 0,
                'error': 'Insufficient data'
            }
        
        # Standardize features
        self.anomaly_scaler = StandardScaler()
        features_scaled = self.anomaly_scaler.fit_transform(features_df)
        
        # Train Isolation Forest
        contamination_rate = min(0.1, max(0.01, 1 / len(features_df)))
        self.anomaly_model = IsolationForest(contamination=contamination_rate, random_state=42)
        anomalies = self.anomaly_model.fit_predict(features_scaled)
        
        # Add predictions
        sales_df_copy = sales_df.copy()
        sales_df_copy['is_anomaly'] = anomalies
        sales_df_copy['anomaly_score'] = self.anomaly_model.score_samples(features_scaled)
        
        # Classify anomaly type
        sales_df_copy['anomaly_type'] = 'NORMAL'
        
        mean_sale = sales_df_copy['sale_in_liters'].mean()
        std_sale = sales_df_copy['sale_in_liters'].std()
        
        if std_sale > 0:
            sales_df_copy.loc[
                (sales_df_copy['is_anomaly'] == -1) & (sales_df_copy['sale_in_liters'] > mean_sale + 2*std_sale),
                'anomaly_type'
            ] = 'SPIKE'
            
            sales_df_copy.loc[
                (sales_df_copy['is_anomaly'] == -1) & (sales_df_copy['sale_in_liters'] < mean_sale - 2*std_sale),
                'anomaly_type'
            ] = 'DROP'
        
        anomaly_count = len(sales_df_copy[sales_df_copy['is_anomaly'] == -1])
        accuracy = 1 - (anomaly_count / max(len(sales_df_copy), 1))
        
        logger.info(f"✓ Anomalies detected: {anomaly_count}, Accuracy: {accuracy:.2%}")
        
        return {
            'model': self.anomaly_model,
            'results': sales_df_copy,
            'accuracy': accuracy,
            'anomaly_count': anomaly_count
        }
    
    def get_top_anomalies(self, results_df, n=10):
        """Get top anomalies"""
        
        if 'is_anomaly' not in results_df.columns:
            return pd.DataFrame()
        
        anomalies = results_df[results_df['is_anomaly'] == -1]
        
        if anomalies.empty:
            return pd.DataFrame()
        
        mean_val = results_df['sale_in_liters'].mean()
        anomalies = anomalies.copy()
        anomalies['deviation'] = abs(anomalies['sale_in_liters'] - mean_val)
        
        return anomalies.nlargest(n, 'deviation')

@st.cache_resource
def get_ml_models():
    return RealMLModels()

ml_models = get_ml_models()
