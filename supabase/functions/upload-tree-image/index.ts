import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from 'jsr:@supabase/supabase-js@2';

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Client-Info, Apikey",
};

interface ImageUploadRequest {
  device_id: string;
  api_key: string;
  image_base64: string;  // Base64 encoded image from ESP32 CAM
  species?: string;
  dbh?: number;  // Diameter at Breast Height in cm
  height?: number;  // Tree height in meters
  location?: {
    latitude: number;
    longitude: number;
  };
  timestamp?: string;
}

interface TreeAnalysisResult {
  species: string;
  confidence: number;
  confidence_level: string;
  carbon_kg_monthly: number;
  carbon_tonnes_yearly: number;
  image_url: string;
  identified_at: string;
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
    const data: ImageUploadRequest = await req.json();

    // Validate required fields
    if (!data.device_id || !data.api_key || !data.image_base64) {
      return new Response(
        JSON.stringify({ error: "device_id, api_key, and image_base64 are required" }),
        {
          status: 400,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        }
      );
    }

    // Validate device and API key
    const { data: device, error: deviceError } = await supabase
      .from('devices')
      .select('user_id, sensors')
      .eq('id', data.device_id)
      .eq('api_key', data.api_key)
      .eq('status', 'active')
      .maybeSingle();

    if (deviceError || !device) {
      await supabase.from('activity_logs').insert({
        user_id: null,
        action: 'image_upload',
        device_id: data.device_id,
        status: 'error',
        error_message: 'Device authentication failed',
      });

      return new Response(
        JSON.stringify({ error: "Device authentication failed" }),
        {
          status: 401,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        }
      );
    }

    // Convert base64 to binary
    const imageData = Uint8Array.from(
      atob(data.image_base64),
      c => c.charCodeAt(0)
    );

    // Create unique filename with timestamp
    const timestamp = new Date().toISOString();
    const fileName = `tree-images/${data.device_id}/${Date.now()}-${Math.random().toString(36).substr(2, 9)}.jpg`;

    // Upload image to Supabase Storage
    const { data: uploadData, error: uploadError } = await supabase
      .storage
      .from('tree-captures')
      .upload(fileName, imageData, {
        contentType: 'image/jpeg',
        upsert: false,
      });

    if (uploadError) {
      console.error('Upload error:', uploadError);
      return new Response(
        JSON.stringify({ error: "Failed to upload image" }),
        {
          status: 500,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        }
      );
    }

    // Get public URL for the image
    const { data: urlData } = supabase
      .storage
      .from('tree-captures')
      .getPublicUrl(fileName);

    const imageUrl = urlData.publicUrl;

    // Call ML inference endpoint to identify tree
    const inferenceResponse = await fetch('http://localhost:5000/predict', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        image_url: imageUrl,
        image_base64: data.image_base64,
      }),
    }).catch(() => null);

    let analysisResult: TreeAnalysisResult | null = null;
    let mlError = null;

    if (inferenceResponse?.ok) {
      const mlResult = await inferenceResponse.json();
      
      // Calculate confidence level
      const confValue = mlResult.confidence;
      let confidenceLevel = 'medium';
      if (confValue >= 0.9) confidenceLevel = 'very_high';
      else if (confValue >= 0.8) confidenceLevel = 'high';
      else if (confValue >= 0.6) confidenceLevel = 'medium';
      else if (confValue >= 0.4) confidenceLevel = 'low';
      else confidenceLevel = 'very_low';

      // Calculate carbon based on Chave equation if DBH provided
      let carbonMonthly = 2.0;  // Default fallback
      let carbonYearly = 24.0;

      if (data.dbh && data.dbh > 0) {
        // Chave equation approximation for monthly carbon
        // AGB_kg ≈ 0.0919 × (ρ × DBH² × H)^0.906
        // Assuming default parameters, monthly CO2 ≈ AGB / 50
        const estimatedAGB = 0.0919 * Math.pow(
          0.60 * data.dbh * data.dbh * (data.height || 20),
          0.906
        );
        carbonMonthly = estimatedAGB * 0.47 * 3.67 / 12;  // Convert to monthly CO2
        carbonYearly = carbonMonthly * 12;
      }

      analysisResult = {
        species: mlResult.species,
        confidence: Math.round(confValue * 100),
        confidence_level: confidenceLevel,
        carbon_kg_monthly: Math.round(carbonMonthly * 100) / 100,
        carbon_tonnes_yearly: Math.round(carbonYearly / 1000 * 100) / 100,
        image_url: imageUrl,
        identified_at: timestamp,
      };
    } else {
      mlError = 'ML inference service unavailable - using species from ESP32';
    }

    // Store tree identification in database
    const { data: identification, error: identError } = await supabase
      .from('tree_identifications')
      .insert({
        device_id: data.device_id,
        user_id: device.user_id,
        species: analysisResult?.species || data.species || 'Unknown',
        confidence: analysisResult ? analysisResult.confidence / 100 : null,
        confidence_level: analysisResult?.confidence_level || null,
        carbon_rate_kg_per_month: analysisResult?.carbon_kg_monthly || 2.0,
        image_url: imageUrl,
        location: data.location || null,
        identified_at: timestamp,
        model_version: analysisResult ? 'resnet50' : null,
      })
      .select()
      .single();

    if (identError) {
      console.error('Database error:', identError);
      return new Response(
        JSON.stringify({ error: "Failed to store identification" }),
        {
          status: 500,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        }
      );
    }

    // Log successful upload
    await supabase.from('activity_logs').insert({
      user_id: device.user_id,
      action: 'image_upload',
      device_id: data.device_id,
      status: 'success',
      metadata: {
        image_url: imageUrl,
        species: analysisResult?.species,
        confidence: analysisResult?.confidence,
      },
    });

    return new Response(
      JSON.stringify({
        success: true,
        message: "Image uploaded and analyzed successfully",
        identification_id: identification.id,
        analysis: analysisResult || {
          species: data.species || 'Unknown',
          confidence: 0,
          confidence_level: 'low',
          carbon_kg_monthly: 2.0,
          carbon_tonnes_yearly: 0.024,
          image_url: imageUrl,
          identified_at: timestamp,
        },
        ml_error: mlError,
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
