"""
Chave Allometric Equation for Above-Ground Biomass (AGB) Estimation
Based on: Chave et al. (2014) - Improved pantropical tree aboveground biomass estimates from satellite data

This module provides functions to estimate tree biomass and convert to carbon credits
using the standard Chave equation, parameterized for different forest types.
"""

import math
import logging
from typing import Dict, Tuple, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class ForestType(Enum):
    """Forest type classification for Chave equation parameterization"""
    WET = "wet"  # Wet tropical forest
    MOIST = "moist"  # Moist tropical forest
    DRY = "dry"  # Dry tropical forest
    TEMPERATE = "temperate"  # Temperate forest


class ChaveCalculator:
    """
    Implements Chave allometric equation for tree AGB estimation.
    
    The Chave equation estimates above-ground biomass (AGB) in kg from:
    - Diameter at Breast Height (DBH) in cm
    - Tree height (H) in meters
    - Wood density (ρ) in g/cm³
    
    Formula: AGB = 0.0673 × (ρ × DBH²)^0.976  [wet tropical]
             AGB = 0.0919 × (ρ × DBH² × H)^0.906  [moist/dry tropical]
    """
    
    # Chave coefficients for different forest types
    CHAVE_COEFFICIENTS = {
        ForestType.WET: {"a": 0.0673, "b": 0.976},
        ForestType.MOIST: {"a": 0.0919, "b": 0.906},
        ForestType.DRY: {"a": 0.0919, "b": 0.906},
        ForestType.TEMPERATE: {"a": 0.0549, "b": 0.995},
    }
    
    # Wood density reference values (g/cm³) for common tropical species
    SPECIES_WOOD_DENSITY = {
        "Aesculus indica": 0.52,
        "Buchanania lanzan": 0.68,
        "Cedrus deodara": 0.55,
        "Eucalyptus globulus": 0.65,
        "Madhuca longifolia": 0.72,
        "Mangifera sylvatica": 0.62,
        "Phyllanthus emblica": 0.58,
        "Pinus roxburghii": 0.48,
        "Quercus leucotrichophora": 0.75,
        "Rhododendron arboreum": 0.55,
        "Senegalia catechu": 0.78,
        "Shorea robusta": 0.80,
        "Taxus baccata": 0.65,
        # Generic values for common trees
        "Mango Tree": 0.62,
        "Coconut Tree": 0.70,
        "Oak Tree": 0.75,
        "Teak Tree": 0.82,
        "Sal Tree": 0.80,
    }
    
    # Default wood density if species not found
    DEFAULT_WOOD_DENSITY = 0.60  # g/cm³
    
    # Carbon content in wood (approximately 50% of dry biomass)
    CARBON_FRACTION = 0.47
    
    # Conversion factor from carbon to CO2 (molecular weight ratio)
    CO2_CONVERSION_FACTOR = 44 / 12  # 3.67
    
    @classmethod
    def get_wood_density(cls, species: str) -> float:
        """
        Get wood density for a given tree species.
        
        Args:
            species: Tree species name
            
        Returns:
            Wood density in g/cm³
        """
        return cls.SPECIES_WOOD_DENSITY.get(species, cls.DEFAULT_WOOD_DENSITY)
    
    @classmethod
    def calculate_agb(
        cls,
        dbh: float,
        height: Optional[float] = None,
        wood_density: Optional[float] = None,
        species: Optional[str] = None,
        forest_type: ForestType = ForestType.MOIST,
    ) -> Dict[str, float]:
        """
        Calculate above-ground biomass (AGB) using Chave equation.
        
        Args:
            dbh: Diameter at Breast Height in cm (1.3m height)
            height: Tree height in meters (optional, improves accuracy)
            wood_density: Wood density in g/cm³ (optional)
            species: Tree species for automatic density lookup
            forest_type: Type of forest (affects equation parameters)
            
        Returns:
            Dictionary with:
                - agb_kg: Above-ground biomass in kg
                - carbon_kg: Carbon content in kg
                - co2_eq_kg: CO2 equivalent in kg
                - agb_tonnes: Above-ground biomass in tonnes
                - carbon_tonnes: Carbon in tonnes
                - co2_eq_tonnes: CO2 equivalent in tonnes
        """
        
        # Validate inputs
        if dbh <= 0:
            raise ValueError("DBH must be positive")
        if height is not None and height <= 0:
            raise ValueError("Height must be positive")
        
        # Determine wood density
        if wood_density is None:
            if species:
                wood_density = cls.get_wood_density(species)
            else:
                wood_density = cls.DEFAULT_WOOD_DENSITY
        
        # Get Chave coefficients for forest type
        coeff = cls.CHAVE_COEFFICIENTS[forest_type]
        
        try:
            # Calculate AGB using Chave equation
            if height is None:
                # Wet tropical forest: uses only DBH
                if forest_type == ForestType.WET:
                    # AGB = 0.0673 × (ρ × DBH²)^0.976
                    agb_kg = coeff["a"] * math.pow(wood_density * dbh ** 2, coeff["b"])
                else:
                    # For other types, estimate height from DBH (allometric relationship)
                    # H = 127.0 × (1 - exp(-0.0276 × DBH))^0.8706
                    height = 127.0 * math.pow(1 - math.exp(-0.0276 * dbh), 0.8706)
                    agb_kg = coeff["a"] * math.pow(wood_density * dbh ** 2 * height, coeff["b"])
            else:
                # AGB = 0.0919 × (ρ × DBH² × H)^0.906
                agb_kg = coeff["a"] * math.pow(wood_density * dbh ** 2 * height, coeff["b"])
            
            # Convert to carbon and CO2 equivalent
            carbon_kg = agb_kg * cls.CARBON_FRACTION
            co2_eq_kg = carbon_kg * cls.CO2_CONVERSION_FACTOR
            
            return {
                "agb_kg": round(agb_kg, 2),
                "carbon_kg": round(carbon_kg, 2),
                "co2_eq_kg": round(co2_eq_kg, 2),
                "agb_tonnes": round(agb_kg / 1000, 4),
                "carbon_tonnes": round(carbon_kg / 1000, 4),
                "co2_eq_tonnes": round(co2_eq_kg / 1000, 4),
            }
            
        except Exception as e:
            logger.error(f"Error calculating AGB: {str(e)}")
            raise
    
    @classmethod
    def calculate_carbon_sequestration_rate(
        cls,
        dbh: float,
        height: Optional[float] = None,
        wood_density: Optional[float] = None,
        species: Optional[str] = None,
        forest_type: ForestType = ForestType.MOIST,
        annual_growth_rate: float = 0.02,  # 2% annual increment
    ) -> Dict[str, float]:
        """
        Calculate annual carbon sequestration rate based on tree growth.
        
        Args:
            dbh: Current Diameter at Breast Height in cm
            height: Tree height in meters
            wood_density: Wood density in g/cm³
            species: Tree species
            forest_type: Type of forest
            annual_growth_rate: Annual DBH increment rate (default 2%)
            
        Returns:
            Dictionary with annual sequestration rates
        """
        
        # Current AGB
        current_agb = cls.calculate_agb(dbh, height, wood_density, species, forest_type)
        
        # Projected AGB after 1 year
        new_dbh = dbh * (1 + annual_growth_rate)
        projected_agb = cls.calculate_agb(new_dbh, height, wood_density, species, forest_type)
        
        # Calculate increments
        agb_increment = projected_agb["agb_kg"] - current_agb["agb_kg"]
        carbon_increment = projected_agb["carbon_kg"] - current_agb["carbon_kg"]
        co2_increment = projected_agb["co2_eq_kg"] - current_agb["co2_eq_kg"]
        
        return {
            "annual_agb_increment_kg": round(agb_increment, 2),
            "annual_carbon_sequestration_kg": round(carbon_increment, 2),
            "annual_co2_sequestration_kg": round(co2_increment, 2),
            "monthly_carbon_kg": round(carbon_increment / 12, 2),
            "monthly_co2_kg": round(co2_increment / 12, 2),
        }
    
    @classmethod
    def estimate_from_sensor_data(
        cls,
        temperature: float,
        humidity: float,
        light_intensity: float,
        co2_emitted: float,
        co2_absorbed: float,
        species: Optional[str] = None,
    ) -> Dict[str, float]:
        """
        Estimate tree biomass and carbon from environmental sensor data.
        This provides a simplified estimation without direct DBH measurement.
        
        Args:
            temperature: Temperature in Celsius
            humidity: Humidity percentage (0-100)
            light_intensity: Light intensity in µmol/m²/s
            co2_emitted: CO2 emitted by cars in ppm
            co2_absorbed: CO2 absorbed by trees in ppm
            species: Tree species (optional)
            
        Returns:
            Estimated carbon metrics based on environmental indicators
        """
        
        # Estimate tree health index (0-1) from environmental factors
        optimal_temp = 25  # Optimal temperature for most tropical trees
        temp_factor = 1 - abs(temperature - optimal_temp) / 40  # Penalty for deviation
        temp_factor = max(0, min(1, temp_factor))
        
        humidity_factor = 1 - abs(humidity - 70) / 50  # Optimal ~70%
        humidity_factor = max(0, min(1, humidity_factor))
        
        light_factor = 1 - abs(light_intensity - 800) / 1000  # Optimal ~800 µmol/m²/s
        light_factor = max(0, min(1, light_factor))
        
        # Health score combines environmental factors
        health_score = (temp_factor + humidity_factor + light_factor) / 3
        
        # CO2 sequestration potential (kg CO2/day) based on absorption rate
        base_sequestration = (co2_absorbed / 100) * 0.5  # Convert ppm to kg CO2/day
        adjusted_sequestration = base_sequestration * health_score
        
        # Get wood density for species
        wood_density = cls.get_wood_density(species or "")
        
        return {
            "health_score": round(health_score, 3),
            "temp_factor": round(temp_factor, 3),
            "humidity_factor": round(humidity_factor, 3),
            "light_factor": round(light_factor, 3),
            "daily_co2_sequestration_kg": round(adjusted_sequestration, 3),
            "monthly_co2_sequestration_kg": round(adjusted_sequestration * 30, 2),
            "annual_co2_sequestration_kg": round(adjusted_sequestration * 365, 2),
            "co2_offset_rate": round((co2_absorbed / (co2_emitted + 0.001)) * 100, 2),  # Percentage
        }


def estimate_dbh_from_trunk_image(image_width_px: float, real_width_cm: float) -> float:
    """
    Estimate DBH from trunk image analysis.
    Requires calibration with known reference object.
    
    Args:
        image_width_px: Trunk width in pixels from image
        real_width_cm: Known reference width in cm (e.g., from object in image)
        
    Returns:
        Estimated DBH in cm
    """
    if image_width_px <= 0 or real_width_cm <= 0:
        raise ValueError("Invalid image or reference measurements")
    
    # Calculate pixel-to-cm conversion
    px_per_cm = image_width_px / real_width_cm
    
    # Return as DBH estimate (assumes trunk width ≈ DBH)
    return real_width_cm


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    # Example 1: Calculate AGB for a Sal tree with known measurements
    result = ChaveCalculator.calculate_agb(
        dbh=45.0,  # 45 cm DBH
        height=25.0,  # 25 m height
        species="Shorea robusta",  # Sal tree
        forest_type=ForestType.MOIST,
    )
    print("Sal Tree (DBH=45cm, H=25m):")
    print(f"  AGB: {result['agb_kg']} kg ({result['agb_tonnes']} tonnes)")
    print(f"  CO2 Equivalent: {result['co2_eq_kg']} kg ({result['co2_eq_tonnes']} tonnes)")
    
    # Example 2: Calculate sequestration rate
    seq_rate = ChaveCalculator.calculate_carbon_sequestration_rate(
        dbh=45.0,
        height=25.0,
        species="Shorea robusta",
        forest_type=ForestType.MOIST,
    )
    print("\nAnnual Sequestration Rate:")
    print(f"  Monthly CO2: {seq_rate['monthly_co2_kg']} kg")
    print(f"  Annual CO2: {seq_rate['annual_co2_sequestration_kg']} kg")
    
    # Example 3: Estimate from sensor data
    sensor_est = ChaveCalculator.estimate_from_sensor_data(
        temperature=26.5,
        humidity=75.0,
        light_intensity=850.0,
        co2_emitted=420.0,
        co2_absorbed=35.0,
        species="Mango Tree",
    )
    print("\nSensor-Based Estimation:")
    print(f"  Health Score: {sensor_est['health_score']}")
    print(f"  Monthly CO2 Sequestration: {sensor_est['monthly_co2_sequestration_kg']} kg")
    print(f"  CO2 Offset Rate: {sensor_est['co2_offset_rate']}%")
