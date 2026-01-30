import os
from pathlib import Path
import glob

# Auto-detect CSV file
def find_csv_file():
    csv_files = glob.glob("*.csv")
    if csv_files: return csv_files[0]
    return "liquor_sales_data.csv"

DATA_FILE = find_csv_file()
DATA_FILE_PATH = Path(DATA_FILE)

def check_data_file():
    return DATA_FILE_PATH.exists()

CACHE_DURATION = 3600

# UPDATED: Mapping Cities/Districts to Coordinates
# Keys are lowercase to match district names in your CSV
CITIES = {
    # Karnataka Districts
    'bangalore': {'lat': 12.9716, 'lon': 77.5946, 'state': 'Karnataka'},
    'bengaluru': {'lat': 12.9716, 'lon': 77.5946, 'state': 'Karnataka'},
    'bangalore urban': {'lat': 12.9716, 'lon': 77.5946, 'state': 'Karnataka'},
    'bangalore rural': {'lat': 13.2847, 'lon': 77.5712, 'state': 'Karnataka'},
    'mysore': {'lat': 12.2958, 'lon': 76.6394, 'state': 'Karnataka'},
    'mysuru': {'lat': 12.2958, 'lon': 76.6394, 'state': 'Karnataka'},
    'belgaum': {'lat': 15.8497, 'lon': 74.4977, 'state': 'Karnataka'},
    'belagavi': {'lat': 15.8497, 'lon': 74.4977, 'state': 'Karnataka'},
    'hubli': {'lat': 15.3647, 'lon': 75.1240, 'state': 'Karnataka'},
    'dharwad': {'lat': 15.4589, 'lon': 75.0078, 'state': 'Karnataka'},
    'mangalore': {'lat': 12.9141, 'lon': 74.8560, 'state': 'Karnataka'},
    'dakshina kannada': {'lat': 12.9141, 'lon': 74.8560, 'state': 'Karnataka'},
    'udupi': {'lat': 13.3409, 'lon': 74.7421, 'state': 'Karnataka'},
    'hassan': {'lat': 13.0033, 'lon': 76.1004, 'state': 'Karnataka'},
    'shivamogga': {'lat': 13.9299, 'lon': 75.5681, 'state': 'Karnataka'},
    'shimoga': {'lat': 13.9299, 'lon': 75.5681, 'state': 'Karnataka'},
    'tumkur': {'lat': 13.3392, 'lon': 77.1017, 'state': 'Karnataka'},
    'tumakuru': {'lat': 13.3392, 'lon': 77.1017, 'state': 'Karnataka'},
    'bellary': {'lat': 15.1394, 'lon': 76.9214, 'state': 'Karnataka'},
    'ballari': {'lat': 15.1394, 'lon': 76.9214, 'state': 'Karnataka'},
    'vijayapura': {'lat': 16.8302, 'lon': 75.7100, 'state': 'Karnataka'},
    'bijapur': {'lat': 16.8302, 'lon': 75.7100, 'state': 'Karnataka'},
    'kalaburagi': {'lat': 17.3297, 'lon': 76.8343, 'state': 'Karnataka'},
    'gulbarga': {'lat': 17.3297, 'lon': 76.8343, 'state': 'Karnataka'},
    
    # Other States (Just in case)
    'visakhapatnam': {'lat': 17.6869, 'lon': 83.2185, 'state': 'Andhra Pradesh'},
    'hyderabad': {'lat': 17.3850, 'lon': 78.4867, 'state': 'Telangana'},
    'pune': {'lat': 18.5204, 'lon': 73.8567, 'state': 'Maharashtra'},
    'mumbai': {'lat': 19.0760, 'lon': 72.8777, 'state': 'Maharashtra'},
    'chennai': {'lat': 13.0827, 'lon': 80.2707, 'state': 'Tamil Nadu'},
}
