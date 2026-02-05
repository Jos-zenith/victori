/*
  # HCCMS Database Schema - Initial Migration
  
  ## Overview
  Creates complete database structure for Household Carbon Credit Monitoring System
  
  ## New Tables
  1. **users** - User accounts and profiles
  2. **devices** - Registered IoT devices (ESP32/Arduino)
  3. **sensor_readings** - Raw sensor data from devices
  4. **tree_identifications** - ML-identified tree species
  5. **daily_summaries** - Aggregated daily metrics
  6. **carbon_credits** - Monthly carbon calculations
  7. **carbon_rates** - Reference data for calculations
  8. **activity_logs** - System audit trail
  
  ## Security
  - RLS enabled on all tables
  - Policies for authenticated users only
  - Device-specific access controls
*/

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ==================== USERS TABLE ====================
CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email TEXT UNIQUE NOT NULL,
  full_name TEXT NOT NULL,
  phone TEXT,
  address JSONB DEFAULT '{}'::jsonb,
  account_type TEXT DEFAULT 'individual' CHECK (account_type IN ('individual', 'organization')),
  carbon_tier TEXT DEFAULT 'bronze' CHECK (carbon_tier IN ('bronze', 'silver', 'gold', 'platinum')),
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now(),
  is_active BOOLEAN DEFAULT true
);

ALTER TABLE users ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can read own profile"
  ON users FOR SELECT
  TO authenticated
  USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
  ON users FOR UPDATE
  TO authenticated
  USING (auth.uid() = id)
  WITH CHECK (auth.uid() = id);

-- ==================== DEVICES TABLE ====================
CREATE TABLE IF NOT EXISTS devices (
  id TEXT PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  device_type TEXT DEFAULT 'esp32' CHECK (device_type IN ('esp32', 'arduino', 'other')),
  firmware_version TEXT,
  serial_number TEXT UNIQUE,
  location JSONB DEFAULT '{}'::jsonb,
  sensors JSONB DEFAULT '{}'::jsonb,
  status TEXT DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'error', 'maintenance')),
  api_key TEXT NOT NULL,
  last_heartbeat TIMESTAMPTZ,
  battery_level INTEGER DEFAULT 100 CHECK (battery_level >= 0 AND battery_level <= 100),
  timezone TEXT DEFAULT 'UTC',
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

ALTER TABLE devices ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own devices"
  ON devices FOR SELECT
  TO authenticated
  USING (user_id = auth.uid());

CREATE POLICY "Users can manage own devices"
  ON devices FOR ALL
  TO authenticated
  USING (user_id = auth.uid())
  WITH CHECK (user_id = auth.uid());

-- ==================== SENSOR READINGS TABLE ====================
CREATE TABLE IF NOT EXISTS sensor_readings (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  device_id TEXT NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  temperature NUMERIC(5,2),
  humidity NUMERIC(5,2) CHECK (humidity >= 0 AND humidity <= 100),
  soil_moisture NUMERIC(5,2) CHECK (soil_moisture >= 0 AND soil_moisture <= 100),
  light_intensity NUMERIC(5,2) CHECK (light_intensity >= 0 AND light_intensity <= 100),
  pressure NUMERIC(6,2),
  co2_level NUMERIC(6,2),
  battery INTEGER CHECK (battery >= 0 AND battery <= 100),
  rssi INTEGER,
  timestamp TIMESTAMPTZ DEFAULT now(),
  received_at TIMESTAMPTZ DEFAULT now(),
  processed BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT now()
);

ALTER TABLE sensor_readings ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own sensor readings"
  ON sensor_readings FOR SELECT
  TO authenticated
  USING (user_id = auth.uid());

CREATE POLICY "Devices can insert readings"
  ON sensor_readings FOR INSERT
  TO authenticated
  WITH CHECK (user_id = auth.uid());

-- Create index for time-series queries
CREATE INDEX IF NOT EXISTS idx_sensor_readings_device_timestamp 
  ON sensor_readings(device_id, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_sensor_readings_user_timestamp 
  ON sensor_readings(user_id, timestamp DESC);

-- ==================== TREE IDENTIFICATIONS TABLE ====================
CREATE TABLE IF NOT EXISTS tree_identifications (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  device_id TEXT NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  species TEXT NOT NULL,
  confidence NUMERIC(4,3) CHECK (confidence >= 0 AND confidence <= 1),
  confidence_level TEXT CHECK (confidence_level IN ('very_high', 'high', 'medium', 'low', 'very_low')),
  class_id INTEGER,
  carbon_rate_kg_per_month NUMERIC(6,2) DEFAULT 2.0,
  image_url TEXT,
  location JSONB,
  identified_at TIMESTAMPTZ DEFAULT now(),
  model_version TEXT,
  processing_time_ms INTEGER,
  created_at TIMESTAMPTZ DEFAULT now()
);

ALTER TABLE tree_identifications ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own tree identifications"
  ON tree_identifications FOR SELECT
  TO authenticated
  USING (user_id = auth.uid());

CREATE POLICY "Users can create tree identifications"
  ON tree_identifications FOR INSERT
  TO authenticated
  WITH CHECK (user_id = auth.uid());

-- ==================== DAILY SUMMARIES TABLE ====================
CREATE TABLE IF NOT EXISTS daily_summaries (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  device_id TEXT NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  date DATE NOT NULL,
  reading_count INTEGER DEFAULT 0,
  temperature_min NUMERIC(5,2),
  temperature_max NUMERIC(5,2),
  temperature_avg NUMERIC(5,2),
  humidity_min NUMERIC(5,2),
  humidity_max NUMERIC(5,2),
  humidity_avg NUMERIC(5,2),
  soil_moisture_min NUMERIC(5,2),
  soil_moisture_max NUMERIC(5,2),
  soil_moisture_avg NUMERIC(5,2),
  light_intensity_min NUMERIC(5,2),
  light_intensity_max NUMERIC(5,2),
  light_intensity_avg NUMERIC(5,2),
  carbon_change_kg NUMERIC(8,4) DEFAULT 0,
  trees_identified INTEGER DEFAULT 0,
  device_status TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(device_id, date)
);

ALTER TABLE daily_summaries ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own daily summaries"
  ON daily_summaries FOR SELECT
  TO authenticated
  USING (user_id = auth.uid());

CREATE INDEX IF NOT EXISTS idx_daily_summaries_device_date 
  ON daily_summaries(device_id, date DESC);

-- ==================== CARBON CREDITS TABLE ====================
CREATE TABLE IF NOT EXISTS carbon_credits (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  device_id TEXT REFERENCES devices(id) ON DELETE SET NULL,
  year INTEGER NOT NULL,
  month INTEGER NOT NULL CHECK (month >= 1 AND month <= 12),
  month_key TEXT NOT NULL,
  sensor_data_points INTEGER DEFAULT 0,
  avg_temperature NUMERIC(5,2),
  avg_humidity NUMERIC(5,2),
  avg_soil_moisture NUMERIC(5,2),
  tree_species TEXT[],
  carbon_absorbed_kg NUMERIC(10,4) DEFAULT 0,
  carbon_sequestration_rate NUMERIC(10,4) DEFAULT 0,
  vehicle_emissions_offset JSONB DEFAULT '{}'::jsonb,
  credits_earned NUMERIC(10,2) DEFAULT 0,
  credit_value_usd NUMERIC(10,2) DEFAULT 0,
  verification_status TEXT DEFAULT 'pending' CHECK (verification_status IN ('pending', 'verified', 'disputed')),
  calculation_method TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(user_id, month_key)
);

ALTER TABLE carbon_credits ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own carbon credits"
  ON carbon_credits FOR SELECT
  TO authenticated
  USING (user_id = auth.uid());

-- ==================== CARBON RATES TABLE (Reference Data) ====================
CREATE TABLE IF NOT EXISTS carbon_rates (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  tree_carbon_absorption JSONB NOT NULL DEFAULT '{}'::jsonb,
  vehicle_emissions JSONB DEFAULT '{}'::jsonb,
  credit_conversion JSONB DEFAULT '{}'::jsonb,
  environmental_factors JSONB DEFAULT '{}'::jsonb,
  last_updated TIMESTAMPTZ DEFAULT now(),
  source TEXT,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT now()
);

ALTER TABLE carbon_rates ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can read carbon rates"
  ON carbon_rates FOR SELECT
  TO authenticated
  USING (is_active = true);

-- Insert default carbon rates
INSERT INTO carbon_rates (tree_carbon_absorption, vehicle_emissions, credit_conversion, environmental_factors, source)
VALUES (
  '{"Shorea robusta": {"kg_per_month": 2.5, "common_name": "Sal tree"}, 
    "Pinus roxburghii": {"kg_per_month": 1.8, "common_name": "Chir Pine"},
    "Cedrus deodara": {"kg_per_month": 2.3, "common_name": "Deodar Cedar"},
    "Eucalyptus globulus": {"kg_per_month": 2.8, "common_name": "Blue gum"},
    "default": {"kg_per_month": 2.0}}'::jsonb,
  '{"average_car_co2_per_mile": 0.41, "average_car_co2_per_km": 0.255}'::jsonb,
  '{"carbon_kg_per_credit": 1.0, "credit_usd_value": 15.00}'::jsonb,
  '{"temperature_optimal_min_c": 15, "temperature_optimal_max_c": 30, 
    "soil_moisture_optimal_min": 50, "soil_moisture_optimal_max": 85}'::jsonb,
  'EPA 2024, IPCC Guidelines'
)
ON CONFLICT DO NOTHING;

-- ==================== ACTIVITY LOGS TABLE ====================
CREATE TABLE IF NOT EXISTS activity_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  action TEXT NOT NULL,
  device_id TEXT REFERENCES devices(id) ON DELETE SET NULL,
  status TEXT DEFAULT 'success' CHECK (status IN ('success', 'error', 'pending')),
  error_message TEXT,
  metadata JSONB DEFAULT '{}'::jsonb,
  ip_address INET,
  timestamp TIMESTAMPTZ DEFAULT now(),
  created_at TIMESTAMPTZ DEFAULT now()
);

ALTER TABLE activity_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own activity logs"
  ON activity_logs FOR SELECT
  TO authenticated
  USING (user_id = auth.uid());

CREATE INDEX IF NOT EXISTS idx_activity_logs_user_timestamp 
  ON activity_logs(user_id, timestamp DESC);

-- ==================== FUNCTIONS ====================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Add triggers for updated_at
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_users_updated_at') THEN
    CREATE TRIGGER update_users_updated_at
      BEFORE UPDATE ON users
      FOR EACH ROW
      EXECUTE FUNCTION update_updated_at_column();
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_devices_updated_at') THEN
    CREATE TRIGGER update_devices_updated_at
      BEFORE UPDATE ON devices
      FOR EACH ROW
      EXECUTE FUNCTION update_updated_at_column();
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_carbon_credits_updated_at') THEN
    CREATE TRIGGER update_carbon_credits_updated_at
      BEFORE UPDATE ON carbon_credits
      FOR EACH ROW
      EXECUTE FUNCTION update_updated_at_column();
  END IF;
END $$;