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
        self.routes = [
            {'from': 'Bengaluru', 'to': 'Mysore', 'distance': 140, 'lat_from': 12.9716, 'lon_from': 77.5946, 'lat_to': 12.2958, 'lon_to': 76.6394},
            {'from': 'Bengaluru', 'to': 'Tumkur', 'distance': 70, 'lat_from': 12.9716, 'lon_from': 77.5946, 'lat_to': 13.3392, 'lon_to': 77.1017},
            {'from': 'Bengaluru', 'to': 'Hassan', 'distance': 187, 'lat_from': 12.9716, 'lon_from': 77.5946, 'lat_to': 13.0033, 'lon_to': 76.1004},
            {'from': 'Bengaluru', 'to': 'Mangalore', 'distance': 350, 'lat_from': 12.9716, 'lon_from': 77.5946, 'lat_to': 12.9141, 'lon_to': 74.8560},
            {'from': 'Hubli', 'to': 'Belgaum', 'distance': 110, 'lat_from': 15.3647, 'lon_from': 75.1240, 'lat_to': 15.8497, 'lon_to': 74.4977},
        ]
    
    # ==================== 🚛 LOGISTICS & GEOFENCING ====================
    
    @st.cache_data(ttl=60)  # Cache for 60 seconds to allow smooth updates
    def generate_truck_fleet(_self):
        """Generate a fleet of trucks with dynamic positions along routes"""
        trucks = []
        
        for i in range(_self.num_trucks):
            route = _self.routes[i % len(_self.routes)]
            
            # Time-based progress: Each truck moves continuously along its route
            # Use current time to calculate position (smooth animation)
            current_time = datetime.now()
            time_seconds = current_time.hour * 3600 + current_time.minute * 60 + current_time.second
            
            # Each truck completes a round trip in ~4 hours (14400 seconds)
            # This creates continuous movement
            cycle_time = time_seconds % 14400
            
            # Progress 0-1 along the route (goes 0->1->0 for round trip)
            if cycle_time < 7200:  # First half: 0 to 1
                progress = cycle_time / 7200.0
            else:  # Second half: 1 to 0 (return journey)
                progress = (14400 - cycle_time) / 7200.0
            
            # Calculate interpolated position along the route
            current_lat = route['lat_from'] + (route['lat_to'] - route['lat_from']) * progress
            current_lon = route['lon_from'] + (route['lon_to'] - route['lon_from']) * progress
            
            # Calculate deviation: Some trucks deviate slightly from route
            # Deviation creates a random jitter perpendicular to route
            is_deviating = np.random.random() < 0.15  # 15% chance of deviation
            
            if is_deviating:
                # Deviation perpendicular to route (creates left/right deviation)
                deviation_lat = np.random.normal(0, 0.08)  # Larger deviation
                deviation_lon = np.random.normal(0, 0.08)
                current_lat += deviation_lat
                current_lon += deviation_lon
                deviation_km = np.sqrt((deviation_lat * 111)**2 + (deviation_lon * 111 * np.cos(np.radians(current_lat)))**2)
            else:
                deviation_km = 0.0
            
            # Calculate speed based on progress
            # Truck speeds up in middle of journey, slows near destinations
            speed_base = 80 if np.random.random() > 0.3 else 0
            if progress < 0.1 or progress > 0.9:
                speed_variation = speed_base * 0.6  # Slower at start/end
            else:
                speed_variation = speed_base  # Normal speed in middle
            
            truck = {
                'truck_id': f'TRK-KA-{i+1:04d}',
                'status': 'In Transit' if speed_variation > 0 else 'Parked',
                'from': route['from'],
                'to': route['to'],
                'lat': current_lat,
                'lon': current_lon,
                'speed_kmh': speed_variation,
                'cargo_liters': np.random.randint(5000, 25000),
                'progress_percent': progress * 100,
                'deviation_km': deviation_km,
                'is_deviating': is_deviating,
                'last_ping': datetime.now() - timedelta(seconds=np.random.randint(5, 30)),
                'route_index': i % len(_self.routes),
            }
            trucks.append(truck)
        
        logger.info(f"✓ Generated {len(trucks)} trucks at time {current_time.strftime('%H:%M:%S')}")
        return pd.DataFrame(trucks)
    
    @st.cache_data(ttl=60)
    def calculate_route_compliance(_self, truck_df):
        """Calculate which trucks deviate from approved routes"""
        results = []
        
        deviating_count = 0
        
        for _, truck in truck_df.iterrows():
            # Deviation threshold: >10km is suspicious
            is_compliant = truck['deviation_km'] < 10
            
            # Risk calculation: Higher deviation = higher risk
            risk_score = min(100, (truck['deviation_km'] / 20) * 100)
            
            # Alert classification
            alert_type = 'NORMAL'
            if truck['is_deviating'] and truck['deviation_km'] > 15:
                alert_type = 'HIGH_RISK'
                deviating_count += 1
            elif truck['is_deviating'] and truck['deviation_km'] > 10:
                alert_type = 'MEDIUM_RISK'
                deviating_count += 1
            
            results.append({
                'truck_id': truck['truck_id'],
                'is_compliant': is_compliant,
                'deviation_km': float(truck['deviation_km']),
                'risk_score': float(risk_score),
                'alert_type': alert_type,
                'status': truck['status'],
                'cargo_liters': int(truck['cargo_liters']),
                'speed_kmh': float(truck['speed_kmh']),
                'from': truck['from'],
                'to': truck['to'],
                'progress_percent': float(truck['progress_percent']),
            })
        
        logger.info(f"✓ Calculated compliance: {deviating_count} trucks with alerts")
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
            
            batch_id = f"BATCH-2024-{factory.split('_')[1]}-{i+1:06d}"
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
        
        record = match.iloc[0]
        
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