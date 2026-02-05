import { createClient } from '@supabase/supabase-js'

// Get environment variables
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || ''
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || ''

if (!supabaseUrl || !supabaseAnonKey) {
  console.error('Missing Supabase environment variables')
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

// Database types
export interface User {
  id: string
  email: string
  full_name: string
  phone?: string
  account_type: 'individual' | 'organization'
  carbon_tier: 'bronze' | 'silver' | 'gold' | 'platinum'
  created_at: string
  updated_at: string
  is_active: boolean
}

export interface Device {
  id: string
  user_id: string
  name: string
  device_type: 'esp32' | 'arduino' | 'other'
  firmware_version?: string
  serial_number?: string
  status: 'active' | 'inactive' | 'error' | 'maintenance'
  api_key: string
  last_heartbeat?: string
  battery_level: number
  timezone: string
  created_at: string
  updated_at: string
}

export interface SensorReading {
  id: string
  device_id: string
  user_id: string
  temperature: number
  humidity: number
  soil_moisture: number
  light_intensity: number
  pressure?: number
  co2_level?: number
  battery: number
  rssi: number
  timestamp: string
  received_at: string
  processed: boolean
}

export interface TreeIdentification {
  id: string
  device_id: string
  user_id: string
  species: string
  confidence: number
  confidence_level: 'very_high' | 'high' | 'medium' | 'low' | 'very_low'
  class_id?: number
  carbon_rate_kg_per_month: number
  image_url?: string
  location?: { latitude: number; longitude: number }
  identified_at: string
  model_version?: string
  processing_time_ms?: number
}

export interface DailySummary {
  id: string
  device_id: string
  user_id: string
  date: string
  reading_count: number
  temperature_min?: number
  temperature_max?: number
  temperature_avg?: number
  humidity_min?: number
  humidity_max?: number
  humidity_avg?: number
  soil_moisture_min?: number
  soil_moisture_max?: number
  soil_moisture_avg?: number
  light_intensity_min?: number
  light_intensity_max?: number
  light_intensity_avg?: number
  carbon_change_kg: number
  trees_identified: number
  device_status?: string
  created_at: string
}

export interface CarbonCredit {
  id: string
  user_id: string
  device_id?: string
  year: number
  month: number
  month_key: string
  carbon_absorbed_kg: number
  carbon_sequestration_rate: number
  credits_earned: number
  credit_value_usd: number
  verification_status: 'pending' | 'verified' | 'disputed'
  created_at: string
  updated_at: string
}
