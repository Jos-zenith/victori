/*
  # Add Tree Measurement Columns to Sensor Readings
  
  Adds columns to store tree-specific measurements from ESP32:
  - tree_dbh: Diameter at Breast Height in cm
  - tree_height: Tree height in meters
  - co2_emitted_ppm: CO2 emitted by cars in ppm
  - co2_absorbed_ppm: CO2 absorbed by trees in ppm
  - o2_released_ppm: O2 released by trees in ppm
*/

-- Add tree measurement columns to sensor_readings
ALTER TABLE sensor_readings
ADD COLUMN IF NOT EXISTS tree_dbh NUMERIC(6,2) CHECK (tree_dbh >= 0),
ADD COLUMN IF NOT EXISTS tree_height NUMERIC(6,2) CHECK (tree_height >= 0),
ADD COLUMN IF NOT EXISTS co2_emitted_ppm NUMERIC(7,2),
ADD COLUMN IF NOT EXISTS co2_absorbed_ppm NUMERIC(7,2),
ADD COLUMN IF NOT EXISTS o2_released_ppm NUMERIC(7,2);

-- Add index for tree measurements to speed up biomass calculations
CREATE INDEX IF NOT EXISTS idx_sensor_readings_tree_measurements 
  ON sensor_readings(device_id, tree_dbh, tree_height, timestamp DESC);

-- Create view for tree biomass analysis
CREATE OR REPLACE VIEW tree_biomass_analysis AS
SELECT 
  sr.id,
  sr.device_id,
  sr.user_id,
  sr.timestamp,
  sr.tree_dbh,
  sr.tree_height,
  sr.temperature,
  sr.humidity,
  sr.light_intensity,
  sr.co2_emitted_ppm,
  sr.co2_absorbed_ppm,
  sr.o2_released_ppm,
  -- Chave equation estimation (simplified)
  CASE 
    WHEN sr.tree_dbh > 0 AND sr.tree_height > 0 THEN
      ROUND((0.0919 * POWER(0.60 * sr.tree_dbh * sr.tree_dbh * sr.tree_height, 0.906))::numeric, 2)
    ELSE NULL
  END as estimated_agb_kg,
  -- Carbon content (47% of dry biomass)
  CASE 
    WHEN sr.tree_dbh > 0 AND sr.tree_height > 0 THEN
      ROUND((0.0919 * POWER(0.60 * sr.tree_dbh * sr.tree_dbh * sr.tree_height, 0.906) * 0.47)::numeric, 2)
    ELSE NULL
  END as estimated_carbon_kg,
  -- CO2 equivalent (carbon * 3.67)
  CASE 
    WHEN sr.tree_dbh > 0 AND sr.tree_height > 0 THEN
      ROUND((0.0919 * POWER(0.60 * sr.tree_dbh * sr.tree_dbh * sr.tree_height, 0.906) * 0.47 * 3.67)::numeric, 2)
    ELSE NULL
  END as estimated_co2_eq_kg
FROM sensor_readings sr;

COMMENT ON VIEW tree_biomass_analysis IS 'Estimates tree biomass and carbon sequestration using Chave allometric equation';

-- Create materialized view for daily aggregates (for performance)
CREATE MATERIALIZED VIEW IF NOT EXISTS daily_tree_carbon_credits AS
SELECT 
  DATE(sr.timestamp) as date,
  sr.device_id,
  sr.user_id,
  COUNT(*) as reading_count,
  ROUND(AVG(sr.temperature)::numeric, 2) as avg_temperature,
  ROUND(AVG(sr.humidity)::numeric, 2) as avg_humidity,
  ROUND(AVG(sr.light_intensity)::numeric, 2) as avg_light_intensity,
  ROUND(AVG(sr.tree_dbh)::numeric, 2) as avg_dbh,
  ROUND(AVG(sr.tree_height)::numeric, 2) as avg_height,
  ROUND(AVG(sr.co2_absorbed_ppm)::numeric, 2) as avg_co2_absorbed,
  ROUND(AVG(sr.o2_released_ppm)::numeric, 2) as avg_o2_released,
  -- Daily carbon credit (sum of CO2 absorption)
  ROUND(SUM(CASE 
    WHEN sr.tree_dbh > 0 AND sr.tree_height > 0 THEN
      (0.0919 * POWER(0.60 * sr.tree_dbh * sr.tree_dbh * sr.tree_height, 0.906) * 0.47 * 3.67 / 24)
    ELSE 0
  END)::numeric, 2) as daily_co2_offset_kg
FROM sensor_readings sr
WHERE sr.processed = true
GROUP BY DATE(sr.timestamp), sr.device_id, sr.user_id;

COMMENT ON MATERIALIZED VIEW daily_tree_carbon_credits IS 'Daily aggregated carbon credit calculations from tree measurements';

-- Create index for fast queries on the materialized view
CREATE INDEX IF NOT EXISTS idx_daily_tree_carbon_credits_user 
  ON daily_tree_carbon_credits(user_id, date DESC);

-- Grant permissions
ALTER TABLE sensor_readings ENABLE ROW LEVEL SECURITY;
