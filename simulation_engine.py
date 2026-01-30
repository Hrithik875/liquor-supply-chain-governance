import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SupplyChainSimulator:
    """Simulate real-world supply chain operations: GPS tracking, production, QR codes"""
    
    def __init__(self, num_trucks=15, num_batches=50):
        self.num_trucks = num_trucks
        self.num_batches = num_batches
        np.random.seed(42)
    
    # ==================== 🚛 LOGISTICS & GEOFENCING ====================
    
    @st.cache_data(ttl=3600)
    def generate_truck_fleet(_self):
        """Generate a fleet of trucks with routes"""
        trucks = []
        
        routes = [
            {'from': 'Bengaluru', 'to': 'Mysore', 'distance': 140, 'lat_from': 12.9716, 'lon_from': 77.5946, 'lat_to': 12.2958, 'lon_to': 76.6394},
            {'from': 'Bengaluru', 'to': 'Tumkur', 'distance': 70, 'lat_from': 12.9716, 'lon_from': 77.5946, 'lat_to': 13.3392, 'lon_to': 77.1017},
            {'from': 'Bengaluru', 'to': 'Hassan', 'distance': 187, 'lat_from': 12.9716, 'lon_from': 77.5946, 'lat_to': 13.0033, 'lon_to': 76.1004},
            {'from': 'Bengaluru', 'to': 'Mangalore', 'distance': 350, 'lat_from': 12.9716, 'lon_from': 77.5946, 'lat_to': 12.9141, 'lon_to': 74.8560},
            {'from': 'Hubli', 'to': 'Belgaum', 'distance': 110, 'lat_from': 15.3647, 'lon_from': 75.1240, 'lat_to': 15.8497, 'lon_to': 74.4977},
        ]
        
        for i in range(_self.num_trucks):
            route = routes[i % len(routes)]
            
            # Current position (0-100% along the route)
            progress = np.random.uniform(0, 1)
            current_lat = route['lat_from'] + (route['lat_to'] - route['lat_from']) * progress
            current_lon = route['lon_from'] + (route['lon_to'] - route['lon_from']) * progress
            
            # Simulate deviations (some trucks go off-route)
            is_deviating = np.random.random() < 0.15  # 15% chance of deviation
            
            if is_deviating:
                current_lat += np.random.normal(0, 0.05)
                current_lon += np.random.normal(0, 0.05)
            
            truck = {
                'truck_id': f'TRK-KA-{i+1:04d}',
                'status': 'In Transit' if np.random.random() > 0.2 else 'Idle',
                'from': route['from'],
                'to': route['to'],
                'lat': current_lat,
                'lon': current_lon,
                'speed_kmh': np.random.uniform(40, 90) if np.random.random() > 0.3 else 0,
                'cargo_liters': np.random.randint(5000, 25000),
                'progress_percent': progress * 100,
                'deviation_km': np.random.uniform(0, 15) if is_deviating else 0,
                'is_deviating': is_deviating,
                'last_ping': datetime.now() - timedelta(minutes=np.random.randint(1, 120)),
            }
            trucks.append(truck)
        
        logger.info(f"✓ Generated {len(trucks)} trucks")
        return pd.DataFrame(trucks)
    
    @st.cache_data(ttl=3600)
    def calculate_route_compliance(_self, truck_df):
        """Calculate which trucks deviate from approved routes"""
        results = []
        
        for _, truck in truck_df.iterrows():
            # Deviation threshold: >10km is suspicious
            is_compliant = truck['deviation_km'] < 10
            
            risk_score = min(100, (truck['deviation_km'] / 20) * 100)
            
            alert_type = 'NORMAL'
            if truck['is_deviating'] and truck['deviation_km'] > 15:
                alert_type = 'HIGH_RISK'
            elif truck['is_deviating'] and truck['deviation_km'] > 10:
                alert_type = 'MEDIUM_RISK'
            
            results.append({
                'truck_id': truck['truck_id'],
                'is_compliant': is_compliant,
                'deviation_km': truck['deviation_km'],
                'risk_score': risk_score,
                'alert_type': alert_type,
                'status': truck['status'],
                'cargo_liters': truck['cargo_liters'],
                'speed_kmh': truck['speed_kmh'],
            })
        
        logger.info(f"✓ Calculated compliance for {len(results)} trucks")
        return pd.DataFrame(results)
    
    # ==================== 🏭 PRODUCTION & INVENTORY ====================
    
    @st.cache_data(ttl=3600)
    def generate_production_ledger(_self):
        """Generate Input (Molasses) vs Output (Spirit) ledger"""
        ledger = []
        
        factories = ['Factory_BLR_001', 'Factory_BLR_002', 'Factory_HUB_001', 'Factory_MYS_001']
        
        for factory in factories:
            for day in range(30):  # Last 30 days
                date = (datetime.now() - timedelta(days=30-day)).date()
                
                # Input: Molasses (in cartons, 1 carton = ~1000L)
                molasses_cartons = np.random.randint(50, 200)
                molasses_liters = molasses_cartons * 1000
                
                # Processing: 1L Molasses → ~0.8L Spirit (realistic fermentation loss)
                theoretical_output = molasses_liters * 0.8
                
                # Actual Output: Should match theoretical ± waste
                waste_percent = np.random.uniform(2, 8)  # 2-8% waste
                waste_liters = theoretical_output * (waste_percent / 100)
                
                # Add anomalies: Some factories divert (output << theoretical)
                if np.random.random() < 0.05:  # 5% chance of diversion
                    actual_output = theoretical_output * np.random.uniform(0.4, 0.7)  # Only 40-70% output!
                    alert = 'DIVERSION_SUSPECTED'
                else:
                    actual_output = theoretical_output - waste_liters
                    alert = 'NORMAL'
                
                balance = actual_output - waste_liters
                
                ledger.append({
                    'factory_id': factory,
                    'date': date,
                    'molasses_liters': molasses_liters,
                    'theoretical_output': theoretical_output,
                    'waste_liters': waste_liters,
                    'actual_output': actual_output,
                    'balance': balance,
                    'alert': alert,
                    'variance_percent': ((actual_output - theoretical_output) / theoretical_output) * 100,
                })
        
        logger.info(f"✓ Generated production ledger with {len(ledger)} records")
        return pd.DataFrame(ledger)
    
    # ==================== 🔍 PRODUCT AUTHENTICITY ====================
    
    @st.cache_data(ttl=3600)
    def generate_qr_database(_self):
        """Generate database of valid QR codes / batch IDs"""
        batches = []
        
        factories = ['Factory_BLR_001', 'Factory_BLR_002', 'Factory_HUB_001', 'Factory_MYS_001']
        products = ['PREMIUM_WHISKY', 'STANDARD_RUM', 'VODKA_CLEAR', 'BRANDY_RESERVE']
        
        for i in range(_self.num_batches):
            factory = np.random.choice(factories)
            product = np.random.choice(products)
            
            batch_id = f"BATCH-2024-{factory.split('_')}-{i+1:06d}"
            manufacture_date = datetime.now() - timedelta(days=np.random.randint(1, 180))
            expiry_date = manufacture_date + timedelta(days=365*5)  # 5-year shelf life
            
            batch = {
                'batch_id': batch_id,
                'factory_id': factory,
                'product': product,
                'manufacture_date': manufacture_date.date(),
                'expiry_date': expiry_date.date(),
                'quantity_cases': np.random.randint(100, 5000),
                'is_valid': np.random.random() > 0.05,  # 95% valid
                'qr_code_status': 'VALID' if np.random.random() > 0.05 else 'COUNTERFEIT',
                'seal_integrity': 'OK' if np.random.random() > 0.03 else 'BROKEN',
            }
            batches.append(batch)
        
        logger.info(f"✓ Generated {len(batches)} QR batch records")
        return pd.DataFrame(batches)
    
    def verify_qr_code(self, batch_id, qr_database):
        """Verify if a QR code/batch ID is authentic"""
        match = qr_database[qr_database['batch_id'] == batch_id]
        
        if match.empty:
            return {
                'found': False,
                'status': 'NOT_FOUND',
                'message': f'Batch ID {batch_id} not found in database. ⚠️ POSSIBLE COUNTERFEIT',
                'is_authentic': False,
            }
        
        record = match.iloc
        
        is_authentic = (
            record['is_valid'] and 
            record['qr_code_status'] == 'VALID' and 
            record['seal_integrity'] == 'OK' and
            record['expiry_date'] > datetime.now().date()
        )
        
        return {
            'found': True,
            'status': 'AUTHENTIC' if is_authentic else 'COUNTERFEIT_OR_EXPIRED',
            'batch_id': batch_id,
            'factory_id': record['factory_id'],
            'product': record['product'],
            'manufacture_date': record['manufacture_date'],
            'expiry_date': record['expiry_date'],
            'qr_status': record['qr_code_status'],
            'seal_status': record['seal_integrity'],
            'is_authentic': is_authentic,
            'message': f"✅ AUTHENTIC - {record['product']}" if is_authentic else "❌ COUNTERFEIT OR EXPIRED",
        }

@st.cache_resource
def get_simulator():
    return SupplyChainSimulator()

simulator = get_simulator()
