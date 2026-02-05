"""
Utility functions for HCCMS - Simple helper script to initialize Firestore with carbon rates
"""

import firebase_admin
from firebase_admin import firestore
from google.cloud.firestore import SERVER_TIMESTAMP

def init_firestore_reference_data():
    """
    Initialize Firestore with reference data for carbon calculations
    Run this once after setting up your Firebase project
    
    Usage:
        python init_firestore.py
    """
    
    # Initialize Firebase (assumes you have GOOGLE_APPLICATION_CREDENTIALS set)
    if not firebase_admin._apps:
        firebase_admin.initialize_app()
    
    db = firestore.client()
    
    print("Initializing Firestore reference data...")
    
    # Initialize carbon rates
    carbon_rates = {
        "tree_carbon_absorption": {
            "Shorea robusta": {
                "kg_per_month": 2.5,
                "common_name": "Sal tree",
                "region": "Indian subcontinent"
            },
            "Pinus roxburghii": {
                "kg_per_month": 1.8,
                "common_name": "Chir Pine",
                "region": "Himalayas"
            },
            "Madhuca longifolia": {
                "kg_per_month": 2.1,
                "common_name": "Mahua tree",
                "region": "Central India"
            },
            "Buchanania lanzan": {
                "kg_per_month": 1.9,
                "common_name": "Charoli",
                "region": "Central India"
            },
            "Cedrus deodara": {
                "kg_per_month": 2.3,
                "common_name": "Deodar Cedar",
                "region": "Himalayas"
            },
            "default": {
                "kg_per_month": 2.0,
                "common_name": "Generic tree"
            }
        },
        "vehicle_emissions": {
            "average_car_co2_per_mile": 0.41,
            "average_car_co2_per_km": 0.255,
            "average_car_mpg": 24.7,
            "average_car_l_per_100km": 9.8
        },
        "credit_conversion": {
            "carbon_kg_per_credit": 1.0,
            "credit_usd_value": 15.00,
            "credit_cad_value": 20.00,
            "credit_inr_value": 1250.00
        },
        "environmental_factors": {
            "temperature_optimal_min_c": 15,
            "temperature_optimal_max_c": 30,
            "soil_moisture_optimal_min": 50,
            "soil_moisture_optimal_max": 85,
            "light_intensity_optimal_min": 40
        },
        "last_updated": SERVER_TIMESTAMP,
        "source": "EPA 2024, IPCC Guidelines, BarkVisionAI Dataset"
    }
    
    db.collection("carbon_rates").document("default").set(carbon_rates)
    print("✓ Carbon rates initialized")
    
    return True

if __name__ == "__main__":
    try:
        init_firestore_reference_data()
        print("\n✓ Firestore initialization complete!")
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
