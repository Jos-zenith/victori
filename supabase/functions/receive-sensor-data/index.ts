import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from 'jsr:@supabase/supabase-js@2';

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Client-Info, Apikey",
};

interface SensorData {
  device_id: string;
  api_key: string;
  temperature: number;
  humidity: number;
  soil_moisture: number;
  light_intensity: number;
  pressure?: number;
  co2_level?: number;
  battery?: number;
  rssi?: number;
}

Deno.serve(async (req: Request) => {
  // Handle CORS preflight
  if (req.method === "OPTIONS") {
    return new Response(null, {
      status: 200,
      headers: corsHeaders,
    });
  }

  try {
    // Create Supabase client
    const supabaseUrl = Deno.env.get('SUPABASE_URL')!;
    const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;
    const supabase = createClient(supabaseUrl, supabaseKey);

    // Parse request body
    const data: SensorData = await req.json();

    // Validate required fields
    if (!data.device_id || !data.api_key) {
      return new Response(
        JSON.stringify({ error: "device_id and api_key are required" }),
        {
          status: 400,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        }
      );
    }

    // Validate device and API key
    const { data: device, error: deviceError } = await supabase
      .from('devices')
      .select('*')
      .eq('id', data.device_id)
      .eq('api_key', data.api_key)
      .eq('status', 'active')
      .maybeSingle();

    if (deviceError || !device) {
      // Log failed authentication attempt
      await supabase.from('activity_logs').insert({
        user_id: null,
        action: 'data_received',
        device_id: data.device_id,
        status: 'error',
        error_message: 'Authentication failed',
      });

      return new Response(
        JSON.stringify({ error: "Device authentication failed" }),
        {
          status: 401,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        }
      );
    }

    // Insert sensor reading
    const { data: reading, error: insertError } = await supabase
      .from('sensor_readings')
      .insert({
        device_id: data.device_id,
        user_id: device.user_id,
        temperature: data.temperature,
        humidity: data.humidity,
        soil_moisture: data.soil_moisture,
        light_intensity: data.light_intensity,
        pressure: data.pressure,
        co2_level: data.co2_level,
        battery: data.battery || 100,
        rssi: data.rssi || -100,
        timestamp: new Date().toISOString(),
        received_at: new Date().toISOString(),
        processed: false,
      })
      .select()
      .single();

    if (insertError) {
      console.error('Insert error:', insertError);
      return new Response(
        JSON.stringify({ error: "Failed to store sensor data" }),
        {
          status: 500,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        }
      );
    }

    // Update device last heartbeat
    await supabase
      .from('devices')
      .update({
        last_heartbeat: new Date().toISOString(),
        battery_level: data.battery || 100,
      })
      .eq('id', data.device_id);

    // Log successful reception
    await supabase.from('activity_logs').insert({
      user_id: device.user_id,
      action: 'data_received',
      device_id: data.device_id,
      status: 'success',
    });

    return new Response(
      JSON.stringify({
        success: true,
        message: "Sensor data received successfully",
        reading_id: reading.id,
      }),
      {
        status: 201,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      }
    );
  } catch (error) {
    console.error('Error:', error);
    return new Response(
      JSON.stringify({
        error: "Internal server error",
        details: error.message,
      }),
      {
        status: 500,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      }
    );
  }
});
