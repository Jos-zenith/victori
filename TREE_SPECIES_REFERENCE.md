# Tree Species Reference & Carbon Offset Calculations

## Overview

Different tree species have different wood densities, which affect their carbon storage capacity. This guide provides reference values for common tree species and example calculations.

## How Wood Density Affects CO₂ Offset

The Chave equation uses wood density (ρ) as a critical parameter:
$$AGB = 0.0919 \times (\rho \times DBH^2 \times H)^{0.906}$$

**Higher wood density = Greater carbon storage capacity**

For example, a 30cm Teak tree stores 50% more carbon than the same Pine tree:
- **Pine (ρ=0.50)**: 175 kg AGB → 49 kg/month CO₂
- **Teak (ρ=0.80)**: 280 kg AGB → 79 kg/month CO₂

## Common Tree Species by Region

### Tropical Species
| Species | Wood Density | Monthly CO₂ (30cm, 20m) | Use | Region |
|---------|:----------:|:-----:|----|----|
| Mango | 0.72 | 56 kg | Fruit tree | SE Asia, India |
| Coconut | 0.59 | 45 kg | Tropical | SE Asia |
| Teak | 0.80 | 62 kg | Timber | SE Asia, India |
| Mahogany | 0.69 | 54 kg | Timber | Tropical America |
| Rubber | 0.51 | 39 kg | Latex | SE Asia |
| Ebony | 0.95 | 74 kg | Premium | Africa, SE Asia |

### Temperate Species
| Species | Wood Density | Monthly CO₂ (30cm, 20m) | Use | Region |
|---------|:----------:|:-----:|----|----|
| Oak | 0.75 | 58 kg | Hardwood | Europe, N. America |
| Birch | 0.67 | 52 kg | Timber | N. Europe, Asia |
| Pine | 0.50 | 38 kg | Softwood | N. Hemisphere |
| Spruce | 0.42 | 32 kg | Softwood | N. Europe, Asia |
| Beech | 0.72 | 56 kg | Hardwood | Europe |
| Ash | 0.70 | 54 kg | Tool handles | Europe, N. America |

### Tropical Hardwoods
| Species | Wood Density | Monthly CO₂ (30cm, 20m) | Notes |
|---------|:----------:|:-----:|-------|
| Ipe | 0.98 | 76 kg | Very dense, rot-resistant |
| Cumaru | 0.91 | 71 kg | Golden heartwood |
| Jarrah | 0.90 | 70 kg | Australian hardwood |
| Rosewood | 0.85 | 66 kg | Fine furniture |
| Balsa | 0.15 | 11 kg | Light, fast-growing |

## Calculation Examples

### Example 1: Mango Tree
**Scenario**: Tropical mango tree, mature with fruit-bearing height

```
Input:
- Species: Mango Tree
- DBH: 35 cm
- Height: 22 m
- Wood Density: 0.72 g/cm³

Calculation:
AGB = 0.0919 × (0.72 × 35² × 22)^0.906
AGB = 0.0919 × (192,510)^0.906
AGB ≈ 358 kg

Carbon = 358 × 0.47 ≈ 168 kg
CO₂ Annual = 168 × 3.67 ≈ 616 kg/year
CO₂ Monthly ≈ 51 kg/month
Credits ≈ 62 (1 credit = 10kg CO₂)

Result: High carbon storage for tropical climate
```

### Example 2: Pine Tree (Commercial Timber)
**Scenario**: Young pine in managed forest

```
Input:
- Species: Pine Tree
- DBH: 25 cm
- Height: 18 m
- Wood Density: 0.50 g/cm³

Calculation:
AGB = 0.0919 × (0.50 × 25² × 18)^0.906
AGB = 0.0919 × (56,250)^0.906
AGB ≈ 161 kg

Carbon = 161 × 0.47 ≈ 75.7 kg
CO₂ Annual = 75.7 × 3.67 ≈ 277 kg/year
CO₂ Monthly ≈ 23 kg/month
Credits ≈ 28

Result: Moderate carbon storage, fast-growing
```

### Example 3: Ebony Tree (Rare/Dense)
**Scenario**: Ancient ebony tree with maximum density

```
Input:
- Species: Ebony Tree
- DBH: 40 cm
- Height: 25 m
- Wood Density: 0.95 g/cm³

Calculation:
AGB = 0.0919 × (0.95 × 40² × 25)^0.906
AGB = 0.0919 × (380,000)^0.906
AGB ≈ 543 kg

Carbon = 543 × 0.47 ≈ 255 kg
CO₂ Annual = 255 × 3.67 ≈ 936 kg/year
CO₂ Monthly ≈ 78 kg/month
Credits ≈ 94

Result: Exceptional carbon storage for premium wood
```

## Testing Local Calculations

### Using Python Script
```bash
# Test Mango tree
python victori/functions/test_chave.py --dbh 35 --height 22 --species mango

# Test Pine tree
python victori/functions/test_chave.py --dbh 25 --height 18 --species pine

# Test with custom density
python victori/functions/test_chave.py --dbh 40 --height 25 --density 0.95

# List all available species
python victori/functions/test_chave.py --list-species

# Get JSON output for integration
python victori/functions/test_chave.py --dbh 30 --height 20 --json
```

### Expected Output
```
============================================================
CHAVE ALLOMETRIC EQUATION - CALCULATION RESULTS
============================================================

INPUT PARAMETERS:
  Diameter at Breast Height (DBH): 30 cm
  Tree Height: 20 m
  Wood Density: 0.72 g/cm³

CALCULATION STEPS:
  1. AGB = 0.0919 × (0.72 × 30² × 20)^0.906
     AGB = 253.15 kg

  2. Carbon = AGB × 0.47 (47% of dry biomass)
     Carbon = 119.0 kg

  3. CO₂ = Carbon × 3.67 (molecular weight conversion)
     CO₂ Annual = 436.7 kg

RESULTS:
  Annual CO₂ Offset: 436.7 kg/year
  Monthly CO₂ Offset: 36.4 kg/month
  Carbon Credits: 43.7 (1 credit = 10kg CO₂)

============================================================
```

## Wood Density by Category

### Very Light (< 0.40 g/cm³)
- Balsa: 0.15
- Kapok: 0.35
- *Fast-growing, quick CO₂ sequestration in early years*

### Light (0.40 - 0.60 g/cm³)
- Pine: 0.50
- Spruce: 0.42
- Rubber: 0.51
- *Commercial softwoods, moderate carbon storage*

### Medium (0.60 - 0.75 g/cm³)
- Birch: 0.67
- Ash: 0.70
- Beech: 0.72
- Mango: 0.72
- *Hardwoods with balanced carbon storage*

### Heavy (0.75 - 0.90 g/cm³)
- Oak: 0.75
- Rosewood: 0.85
- Jarrah: 0.90
- Teak: 0.80
- *Premium hardwoods, excellent carbon storage*

### Very Heavy (> 0.90 g/cm³)
- Ebony: 0.95
- Cumaru: 0.91
- Ipe: 0.98
- *Rare/luxury woods, maximum carbon density*

## Regional Carbon Offset Strategies

### Tropical Regions (High CO₂ Sequestration)
**Recommended Species**: Mango, Teak, Mahogany
- **Advantage**: High wood density + fast growth
- **Monthly per tree (30cm, 20m)**: 50-62 kg CO₂
- **Best for**: Large-scale carbon credit programs

### Temperate Regions (Moderate CO₂)
**Recommended Species**: Oak, Birch, Ash
- **Advantage**: Slower growth but sustained storage
- **Monthly per tree (30cm, 20m)**: 52-58 kg CO₂
- **Best for**: Long-term reforestation

### Boreal Regions (Low CO₂)
**Recommended Species**: Pine, Spruce
- **Advantage**: Fast growth, wide distribution
- **Monthly per tree (30cm, 20m)**: 32-38 kg CO₂
- **Best for**: Climate adaptation

## Using Species Data in Dashboard

When identifying trees with the ESP32-CAM:

1. **ML Model identifies species** → Returns species name + confidence
2. **Dashboard looks up wood density** → From tree reference data
3. **Applies correct density in Chave equation** → More accurate CO₂
4. **Stores species in metadata** → For future calculations

```javascript
const speciesDatabase = {
  'Mango Tree': { density: 0.72 },
  'Coconut Tree': { density: 0.59 },
  'Oak Tree': { density: 0.75 },
  'Pine Tree': { density: 0.50 },
  // ... more species
}

const getDensityForSpecies = (species) => {
  return speciesDatabase[species]?.density || 0.60 // default
}
```

## Monthly Carbon Credit Summary

For trees at different sizes with common species:

### Small Tree (20cm DBH, 15m height)
| Species | Monthly CO₂ | Annual CO₂ | Credits |
|---------|:----------:|:--------:|:-------:|
| Pine | 11 kg | 136 kg | 14 |
| Oak | 16 kg | 196 kg | 20 |
| Mango | 18 kg | 214 kg | 21 |
| Teak | 19 kg | 231 kg | 23 |

### Medium Tree (30cm DBH, 20m height)
| Species | Monthly CO₂ | Annual CO₂ | Credits |
|---------|:----------:|:--------:|:-------:|
| Pine | 23 kg | 276 kg | 28 |
| Oak | 32 kg | 391 kg | 39 |
| Mango | 36 kg | 437 kg | 44 |
| Teak | 39 kg | 474 kg | 47 |

### Large Tree (40cm DBH, 25m height)
| Species | Monthly CO₂ | Annual CO₂ | Credits |
|---------|:----------:|:--------:|:-------:|
| Pine | 35 kg | 425 kg | 43 |
| Oak | 49 kg | 595 kg | 60 |
| Mango | 56 kg | 675 kg | 68 |
| Teak | 60 kg | 729 kg | 73 |

## Integration with ESP32 Setup

When your ESP32 captures a tree image:

1. Sends image to `/upload-tree-image` endpoint
2. ML model analyzes and returns species
3. Species name stored in `metadata.tree_species`
4. Dashboard retrieves wood density for species
5. Chave equation uses density-specific value
6. More accurate CO₂ calculation displayed

This allows the calculator to adapt to local tree species automatically!
