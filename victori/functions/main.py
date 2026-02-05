"""
HCCMS Cloud Functions - Backend for Household Carbon Credit Monitoring System
Handles sensor data reception, validation, processing, and storage in Firestore
"""

import functions_framework
from firebase_functions import https_fn, options
from firebase_functions.https_fn import Request, Response  # type: ignore
from firebase_admin import initialize_app, firestore, auth
from datetime import datetime, timezone
from typing import Dict, Any, Tuple, Optional
import logging
import json
from pydantic import BaseModel, ValidationError, Field

# Initialize Firebase Admin
initialize_app()
db = firestore.client()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global configuration
set_global_options = options.set_global_options
set_global_options(max_instances=10, memory=512)

# ==================== DATA MODELS ====================

class SensorReadingRequest(BaseModel):
    """Validates incoming sensor data from Arduino/ESP32"""
    device_id: str
    api_key: str  # Simple authentication
    temperature: float = Field(..., ge=-50, le=60)
    humidity: float = Field(..., ge=0, le=100)
    soil_moisture: float = Field(..., ge=0, le=100)
    light_intensity: float = Field(..., ge=0, le=100)
    pressure: Optional[float] = Field(default=None, ge=800, le=1200)
    co2_level: Optional[float] = Field(default=None, ge=300, le=2000)
    battery: float = Field(default=100, ge=0, le=100)
    rssi: int = Field(default=-100, ge=-120, le=0)

# ==================== AUTHENTICATION ====================

def validate_device_api_key(device_id: str, api_key: str) -> Tuple[bool, str]:
    """
    Validates device API key by checking against Firestore
    Returns: (is_valid, user_id)
    """
    try:
        device_doc = db.collection("devices").document(device_id).get()
        
        if not device_doc.exists():
            return False, "Device not found"
        
        device_data = device_doc.to_dict()
        
        # In production, use secure key hashing. For now, simple comparison
        if device_data.get("api_key") != api_key:
            return False, "Invalid API key"
        
        if device_data.get("status") != "active":
            return False, "Device is not active"
        
        return True, device_data.get("user_id")
    
    except Exception as e:
        logger.error(f"Auth validation error: {str(e)}")
        return False, str(e)

# ==================== CARBON CALCULATION ====================

def get_carbon_rates() -> Dict[str, Any]:
    """Fetches carbon conversion rates from Firestore"""
    try:
        rates_doc = db.collection("carbon_rates").document("default").get()
        if rates_doc.exists:
            return rates_doc.to_dict()
        
        # Return defaults if not found
        return {
            "tree_carbon_absorption": {
                "Shorea robusta": {"kg_per_month": 2.5},
                "Pinus roxburghii": {"kg_per_month": 1.8},
                "default": {"kg_per_month": 2.0}
            },
            "vehicle_emissions": {
                "average_car_co2_per_mile": 0.41
            }
        }
    except Exception as e:
        logger.error(f"Error fetching carbon rates: {str(e)}")
        return {}

def calculate_daily_carbon_contribution(
    avg_temperature: float,
    avg_soil_moisture: float,
    tree_species: str = "default"
) -> float:
    """
    Simplified carbon calculation based on environmental conditions
    In production, integrate with real ML model and tree health metrics
    
    Returns: kg CO2 equivalent absorbed
    """
    try:
        rates = get_carbon_rates()
        
        # Base absorption rate from tree species
        species_data = rates.get("tree_carbon_absorption", {})
        base_rate = species_data.get(tree_species, {}).get("kg_per_month", 2.0)
        
        # Normalize monthly rate to daily
        daily_base = base_rate / 30
        
        # Adjust for soil moisture (tree health proxy)
        moisture_factor = 0.5 + (avg_soil_moisture / 100) * 1.5  # 0.5x to 2.0x
        
        # Adjust for temperature (photosynthesis efficiency)
        # Optimal around 25°C
        if avg_temperature < 0 or avg_temperature > 45:
            temp_factor = 0.1
        elif 15 <= avg_temperature <= 30:
            temp_factor = 1.0
        else:
            temp_factor = 0.5
        
        daily_carbon = daily_base * moisture_factor * temp_factor
        
        return round(daily_carbon, 4)
    
    except Exception as e:
        logger.error(f"Carbon calculation error: {str(e)}")
        return 0.0

# ==================== CLOUD FUNCTIONS ====================

@https_fn.on_request(max_instances=20)
def receive_sensor_data(req: https_fn.Request) -> https_fn.Response:
    """
    HTTP endpoint: POST /receiveSensorData
    Receives sensor data from Arduino/ESP32, validates, and stores in Firestore
    
    Expected JSON payload:
    {
        "device_id": "device_001",
        "api_key": "secret_key_here",
        "temperature": 24.5,
        "humidity": 65.0,
        "soil_moisture": 75.0,
        "light_intensity": 85.0,
        "battery": 95,
        "rssi": -45
    }
    """
    
    # CORS headers
    if req.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type',
        }
        return Response('', status=204, headers=headers)
    
    headers = {'Access-Control-Allow-Origin': '*'}
    
    try:
        # Parse request JSON
        request_data = req.get_json()
        
        # Validate using Pydantic
        validated_data = SensorReadingRequest(**request_data)
        
        # Authenticate device
        is_valid, user_id = validate_device_api_key(validated_data.device_id, validated_data.api_key)
        
        if not is_valid:
            logger.warning(f"Auth failed for device: {validated_data.device_id}")
            log_activity(
                user_id="unknown",
                action="data_received",
                device_id=validated_data.device_id,
                status="error",
                error_message=f"Auth failed: {user_id}"
            )
            return Response(
                json.dumps({"error": "Authentication failed"}),
                status=401,
                headers=headers,
                mimetype="application/json"
            )
        
        # Prepare sensor reading document
        sensor_doc = {
            "device_id": validated_data.device_id,
            "user_id": user_id,
            "temperature": validated_data.temperature,
            "humidity": validated_data.humidity,
            "soil_moisture": validated_data.soil_moisture,
            "light_intensity": validated_data.light_intensity,
            "pressure": validated_data.pressure,
            "co2_level": validated_data.co2_level,
            "battery": validated_data.battery,
            "rssi": validated_data.rssi,
            "timestamp": firestore.SERVER_TIMESTAMP,
            "received_at": datetime.now(timezone.utc),
            "processed": False
        }
        
        # Write to Firestore
        # Using timestamp as document ID for natural sorting
        now = datetime.now(timezone.utc)
        doc_id = now.isoformat(timespec='milliseconds')
        
        db.collection("sensor_readings").document(validated_data.device_id).collection(
            "readings"
        ).document(doc_id).set(sensor_doc)
        
        # Update device last_heartbeat
        db.collection("devices").document(validated_data.device_id).update({
            "last_heartbeat": firestore.SERVER_TIMESTAMP,
            "status": "active"
        })
        
        # Log successful reception
        log_activity(
            user_id=user_id,
            action="data_received",
            device_id=validated_data.device_id,
            status="success"
        )
        
        logger.info(f"Sensor data received from {validated_data.device_id}")
        
        return Response(
            json.dumps({
                "success": True,
                "message": "Data received successfully",
                "doc_id": doc_id
            }),
            status=201,
            headers=headers,
            mimetype="application/json"
        )
    
    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}")
        return Response(
            json.dumps({
                "error": "Validation failed",
                "details": e.errors()
            }),
            status=400,
            headers=headers,
            mimetype="application/json"
        )
    
    except json.JSONDecodeError:
        logger.error("Invalid JSON in request")
        return Response(
            json.dumps({"error": "Invalid JSON"}),
            status=400,
            headers=headers,
            mimetype="application/json"
        )
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return Response(
            json.dumps({"error": f"Server error: {str(e)}"}),
            status=500,
            headers=headers,
            mimetype="application/json"
        )

@https_fn.on_request()
def calculate_daily_summary(req: Request) -> Response:
    """
    HTTP endpoint: POST /calculateDailySummary
    Aggregates sensor readings for a device on a given date and produces daily summary
    
    Expected JSON:
    {
        "device_id": "device_001",
        "date": "2026-02-05"
    }
    """
    
    headers = {'Access-Control-Allow-Origin': '*'}
    
    try:
        request_data = req.get_json()
        device_id = request_data.get("device_id")
        date_str = request_data.get("date", datetime.now(timezone.utc).strftime("%Y-%m-%d"))
        
        # Parse date
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        
        # Query readings for this device on this date
        query = (
            db.collection("sensor_readings")
            .document(device_id)
            .collection("readings")
            .order_by("timestamp")
            .stream()
        )
        
        readings = []
        for doc in query:
            reading_time = doc.get("timestamp")
            if reading_time and reading_time.date() == target_date:
                readings.append(doc.to_dict())
        
        if not readings:
            return Response(
                json.dumps({"error": "No readings found for this date"}),
                status=404,
                headers=headers,
                mimetype="application/json"
            )
        
        # Calculate aggregates
        temps = [r["temperature"] for r in readings]
        humidities = [r["humidity"] for r in readings]
        moistures = [r["soil_moisture"] for r in readings]
        lights = [r["light_intensity"] for r in readings]
        
        summary_doc = {
            "device_id": device_id,
            "date": date_str,
            "date_key": date_str,
            "reading_count": len(readings),
            "temperature": {
                "min": min(temps),
                "max": max(temps),
                "avg": sum(temps) / len(temps)
            },
            "humidity": {
                "min": min(humidities),
                "max": max(humidities),
                "avg": sum(humidities) / len(humidities)
            },
            "soil_moisture": {
                "min": min(moistures),
                "max": max(moistures),
                "avg": sum(moistures) / len(moistures)
            },
            "light_intensity": {
                "min": min(lights),
                "max": max(lights),
                "avg": sum(lights) / len(lights)
            },
            "carbon_change_kg": calculate_daily_carbon_contribution(
                avg_temperature=sum(temps) / len(temps),
                avg_soil_moisture=sum(moistures) / len(moistures)
            ),
            "created_at": firestore.SERVER_TIMESTAMP
        }
        
        # Write summary to Firestore
        db.collection("daily_summaries").document(device_id).collection(
            "summaries"
        ).document(date_str).set(summary_doc)
        
        logger.info(f"Daily summary created for {device_id} on {date_str}")
        
        return Response(
            json.dumps({
                "success": True,
                "message": "Daily summary calculated",
                "summary": summary_doc
            }),
            status=201,
            headers=headers,
            mimetype="application/json"
        )
    
    except Exception as e:
        logger.error(f"Error calculating daily summary: {str(e)}")
        return Response(
            json.dumps({"error": str(e)}),
            status=500,
            headers=headers,
            mimetype="application/json"
        )

@https_fn.on_request()
def get_device_summary(req: Request) -> Response:
    """
    HTTP endpoint: GET /getDeviceSummary?device_id=XXX&days=7
    Retrieves recent summary data for a device
    """
    
    headers = {'Access-Control-Allow-Origin': '*'}
    
    try:
        device_id = req.args.get("device_id")
        days = int(req.args.get("days", 7))
        
        if not device_id:
            return Response(
                json.dumps({"error": "device_id required"}),
                status=400,
                headers=headers,
                mimetype="application/json"
            )
        
        # Query daily summaries
        summaries = db.collection("daily_summaries").document(device_id).collection(
            "summaries"
        ).order_by("date_key", direction=firestore.Query.DESCENDING).limit(days).stream()
        
        results = []
        for doc in summaries:
            results.append({
                "date": doc.id,
                "data": doc.to_dict()
            })
        
        return Response(
            json.dumps({
                "success": True,
                "device_id": device_id,
                "summaries": results
            }),
            status=200,
            headers=headers,
            mimetype="application/json"
        )
    
    except Exception as e:
        logger.error(f"Error fetching device summary: {str(e)}")
        return Response(
            json.dumps({"error": str(e)}),
            status=500,
            headers=headers,
            mimetype="application/json"
        )

@https_fn.on_request()
def health_check(req: https_fn.Request) -> https_fn.Response:
    """Simple health check endpoint"""
    return Response(
        json.dumps({
            "status": "healthy",
            "service": "HCCMS Cloud Functions",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }),
        status=200,
        headers={'Access-Control-Allow-Origin': '*'},
        mimetype="application/json"
    )

@https_fn.on_request()
def identify_tree_species(req: https_fn.Request) -> https_fn.Response:
    """
    HTTP endpoint: POST /identifyTreeSpecies
    Identifies tree species from bark image using ResNet50 model
    
    Expected JSON:
    {
        "device_id": "device_001",
        "image_url": "https://example.com/image.jpg" OR "local/path/image.jpg",
        "location": {"latitude": 31.5, "longitude": 77.5}
    }
    
    Returns species, confidence, and carbon absorption rate
    """
    
    headers = {'Access-Control-Allow-Origin': '*'}
    
    try:
        data = req.get_json()
        device_id = data.get("device_id")
        image_url = data.get("image_url")
        location = data.get("location", {})
        
        if not device_id or not image_url:
            return Response(
                json.dumps({"error": "device_id and image_url are required"}),
                status=400,
                headers=headers,
                mimetype="application/json"
            )
        
        # Verify device exists
        device_doc = db.collection("devices").document(device_id).get()
        if not device_doc.exists():
            return Response(
                json.dumps({"error": "Device not found"}),
                status=404,
                headers=headers,
                mimetype="application/json"
            )
        
        device_data = device_doc.to_dict()
        user_id = device_data.get("user_id")
        
        # Load ML model and identify tree
        from ml_inference import get_identifier
        identifier = get_identifier()
        
        result = identifier.identify(image_url)
        
        if not result.get("success"):
            log_activity(
                user_id=user_id,
                action="tree_identification",
                device_id=device_id,
                status="error",
                error_message=result.get("error")
            )
            return Response(
                json.dumps({"error": result.get("error")}),
                status=400,
                headers=headers,
                mimetype="application/json"
            )
        
        # Store identification result in Firestore
        tree_doc = {
            "device_id": device_id,
            "user_id": user_id,
            "species": result.get("species"),
            "confidence": result.get("confidence"),
            "confidence_level": identifier.get_confidence_level(result.get("confidence")),
            "class_id": result.get("class_id"),
            "carbon_rate_kg_per_month": result.get("carbon_rate_kg_per_month"),
            "image_url": image_url,
            "location": location,
            "identified_at": firestore.SERVER_TIMESTAMP,
            "model_version": "ResNet50-BarkVisionAI",
            "processing_time_ms": 0
        }
        
        tree_id = db.collection("tree_identifications").add(tree_doc)[1].id
        
        log_activity(
            user_id=user_id,
            action="tree_identification",
            device_id=device_id,
            status="success",
            metadata={"tree_id": tree_id, "species": result.get("species")}
        )
        
        logger.info(f"Tree identified: {result.get('species')} for device {device_id}")
        
        return Response(
            json.dumps({
                "success": True,
                "tree_id": tree_id,
                "species": result.get("species"),
                "confidence": result.get("confidence"),
                "confidence_level": identifier.get_confidence_level(result.get("confidence")),
                "carbon_rate_kg_per_month": result.get("carbon_rate_kg_per_month"),
                "message": f"Tree identified as {result.get('species')} with {result.get('confidence'):.1%} confidence"
            }),
            status=201,
            headers=headers,
            mimetype="application/json"
        )
    
    except Exception as e:
        logger.error(f"Error identifying tree: {str(e)}")
        return Response(
            json.dumps({"error": f"Server error: {str(e)}"}),
            status=500,
            headers=headers,
            mimetype="application/json"
        )

# ==================== HELPER FUNCTIONS ====================

def log_activity(
    user_id: str,
    action: str,
    device_id: str = None,
    status: str = "success",
    error_message: Optional[str] = None,
    metadata: Dict = None
) -> None:
    """Log activity to Firestore for auditing"""
    try:
        activity = {
            "user_id": user_id,
            "action": action,
            "device_id": device_id,
            "status": status,
            "error_message": error_message,
            "timestamp": firestore.SERVER_TIMESTAMP,
            "metadata": metadata or {}
        }
        
        db.collection("activity_logs").add(activity)
    
    except Exception as e:
        logger.error(f"Error logging activity: {str(e)}")