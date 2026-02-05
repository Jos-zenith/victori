#!/usr/bin/env python3
"""
Chave Allometric Equation Test Utility

This script allows you to test carbon offset calculations locally
before deploying to the ESP32 and dashboard.

Usage:
    python test_chave.py
    
    Or with custom values:
    python test_chave.py --dbh 30 --height 20 --density 0.60
"""

import argparse
import json
from typing import Dict, Tuple


class ChaveCalculator:
    """Calculate Above Ground Biomass (AGB) using Chave equation."""
    
    # Default wood density for tropical trees (g/cm³)
    DEFAULT_WOOD_DENSITY = 0.60
    
    # Carbon content of dry biomass (fraction)
    CARBON_FRACTION = 0.47
    
    # CO2 to carbon conversion factor
    CO2_TO_CARBON = 3.67
    
    # Months per year for monthly rate calculation
    MONTHS_PER_YEAR = 12
    
    @staticmethod
    def calculate_agb(dbh: float, height: float, wood_density: float = DEFAULT_WOOD_DENSITY) -> float:
        """
        Calculate Above Ground Biomass using Chave equation.
        
        AGB = 0.0919 × (ρ × DBH² × H)^0.906
        
        Args:
            dbh: Diameter at Breast Height (cm)
            height: Tree height (m)
            wood_density: Wood density (g/cm³), default 0.60
            
        Returns:
            Above Ground Biomass (kg)
        """
        if dbh <= 0:
            raise ValueError("DBH must be > 0")
        if height <= 0:
            raise ValueError("Height must be > 0")
        if wood_density <= 0:
            raise ValueError("Wood density must be > 0")
            
        # Chave coefficient
        coeff = 0.0919
        
        # Calculate the power term
        power_term = wood_density * (dbh ** 2) * height
        
        # Apply exponent
        agb = coeff * (power_term ** 0.906)
        
        return agb
    
    @staticmethod
    def calculate_carbon(agb: float) -> float:
        """
        Calculate carbon content from biomass.
        
        Carbon = AGB × 0.47 (carbon is ~47% of dry biomass)
        
        Args:
            agb: Above Ground Biomass (kg)
            
        Returns:
            Carbon content (kg)
        """
        return agb * ChaveCalculator.CARBON_FRACTION
    
    @staticmethod
    def calculate_co2_annual(carbon: float) -> float:
        """
        Convert carbon to CO2 equivalent (annual).
        
        CO2 = Carbon × 3.67 (molecular weight conversion)
        
        Args:
            carbon: Carbon content (kg)
            
        Returns:
            Annual CO2 offset (kg)
        """
        return carbon * ChaveCalculator.CO2_TO_CARBON
    
    @staticmethod
    def calculate_co2_monthly(co2_annual: float) -> float:
        """
        Calculate monthly CO2 offset from annual.
        
        Args:
            co2_annual: Annual CO2 offset (kg)
            
        Returns:
            Monthly CO2 offset (kg)
        """
        return co2_annual / ChaveCalculator.MONTHS_PER_YEAR
    
    @classmethod
    def full_calculation(
        cls,
        dbh: float,
        height: float,
        wood_density: float = DEFAULT_WOOD_DENSITY
    ) -> Dict[str, float]:
        """
        Perform complete Chave calculation pipeline.
        
        Args:
            dbh: Diameter at Breast Height (cm)
            height: Tree height (m)
            wood_density: Wood density (g/cm³)
            
        Returns:
            Dictionary with all calculated values
        """
        agb = cls.calculate_agb(dbh, height, wood_density)
        carbon = cls.calculate_carbon(agb)
        co2_annual = cls.calculate_co2_annual(carbon)
        co2_monthly = cls.calculate_co2_monthly(co2_annual)
        
        return {
            'input': {
                'dbh_cm': dbh,
                'height_m': height,
                'wood_density': wood_density,
            },
            'calculation': {
                'agb_kg': round(agb, 2),
                'carbon_kg': round(carbon, 2),
                'co2_annual_kg': round(co2_annual, 2),
                'co2_monthly_kg': round(co2_monthly, 2),
                'carbon_credits': round(co2_annual / 10, 1),  # 1 credit = 10kg CO2
            }
        }


class TreeSpecies:
    """Reference wood density values for common tree species."""
    
    SPECIES_DATA = {
        'mango': {'density': 0.72, 'name': 'Mango Tree'},
        'coconut': {'density': 0.59, 'name': 'Coconut Tree'},
        'oak': {'density': 0.75, 'name': 'Oak Tree'},
        'pine': {'density': 0.50, 'name': 'Pine Tree'},
        'teak': {'density': 0.80, 'name': 'Teak Tree'},
        'mahogany': {'density': 0.69, 'name': 'Mahogany Tree'},
        'birch': {'density': 0.67, 'name': 'Birch Tree'},
        'default': {'density': 0.60, 'name': 'Generic Tropical Tree'},
    }
    
    @classmethod
    def get_density(cls, species: str) -> float:
        """Get wood density for a tree species."""
        species_lower = species.lower()
        return cls.SPECIES_DATA.get(species_lower, cls.SPECIES_DATA['default'])['density']
    
    @classmethod
    def list_species(cls) -> None:
        """Print all available tree species with densities."""
        print("\nAvailable Tree Species (with wood density):\n")
        for key, data in cls.SPECIES_DATA.items():
            if key != 'default':
                print(f"  {key:12} - {data['name']:20} (density: {data['density']} g/cm³)")
        print(f"  {'default':12} - {cls.SPECIES_DATA['default']['name']:20} (density: {cls.SPECIES_DATA['default']['density']} g/cm³)")


def print_results(results: Dict) -> None:
    """Pretty print calculation results."""
    print("\n" + "="*60)
    print("CHAVE ALLOMETRIC EQUATION - CALCULATION RESULTS")
    print("="*60)
    
    inp = results['input']
    calc = results['calculation']
    
    print(f"\nINPUT PARAMETERS:")
    print(f"  Diameter at Breast Height (DBH): {inp['dbh_cm']} cm")
    print(f"  Tree Height: {inp['height_m']} m")
    print(f"  Wood Density: {inp['wood_density']} g/cm³")
    
    print(f"\nCALCULATION STEPS:")
    print(f"  1. AGB = 0.0919 × ({inp['wood_density']} × {inp['dbh_cm']}² × {inp['height_m']})^0.906")
    print(f"     AGB = {calc['agb_kg']} kg")
    print(f"\n  2. Carbon = AGB × 0.47 (47% of dry biomass)")
    print(f"     Carbon = {calc['carbon_kg']} kg")
    print(f"\n  3. CO₂ = Carbon × 3.67 (molecular weight conversion)")
    print(f"     CO₂ Annual = {calc['co2_annual_kg']} kg")
    print(f"\nRESULTS:")
    print(f"  Annual CO₂ Offset: {calc['co2_annual_kg']} kg/year")
    print(f"  Monthly CO₂ Offset: {calc['co2_monthly_kg']} kg/month")
    print(f"  Carbon Credits: {calc['carbon_credits']} (1 credit = 10kg CO₂)")
    print("\n" + "="*60)
    
    # Return as JSON for programmatic use
    return json.dumps(results, indent=2)


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description='Chave Allometric Equation Calculator for Tree Carbon Offset',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_chave.py --dbh 30 --height 20
  python test_chave.py --dbh 25.5 --height 18 --species mango
  python test_chave.py --list-species
        """
    )
    
    parser.add_argument('--dbh', type=float, default=30,
                        help='Diameter at Breast Height in cm (default: 30)')
    parser.add_argument('--height', type=float, default=20,
                        help='Tree height in meters (default: 20)')
    parser.add_argument('--species', type=str, default='default',
                        help='Tree species for wood density lookup (default: default)')
    parser.add_argument('--density', type=float, default=None,
                        help='Override wood density (g/cm³)')
    parser.add_argument('--list-species', action='store_true',
                        help='List available tree species')
    parser.add_argument('--json', action='store_true',
                        help='Output results as JSON')
    
    args = parser.parse_args()
    
    # Handle list species
    if args.list_species:
        TreeSpecies.list_species()
        return
    
    # Get wood density
    if args.density is not None:
        wood_density = args.density
    else:
        wood_density = TreeSpecies.get_density(args.species)
    
    # Calculate
    try:
        results = ChaveCalculator.full_calculation(args.dbh, args.height, wood_density)
        
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print_results(results)
            
    except ValueError as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
