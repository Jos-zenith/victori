"""
Flask-based Inference Server for Tree Identifier
Runs on local machine or free tier services (Replit, Railway, Render)
Spark Plan compatible - no Firebase Cloud Functions needed
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import torch
from torchvision import models, transforms
from PIL import Image
import io
import logging
from typing import Dict, Any
import urllib.request
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable cross-origin requests

# Production settings
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
PORT = int(os.getenv('PORT', 5000))


class TreeIdentifier:
    """ResNet50 tree species identifier (Coconut & Mango trees)"""
    
    def __init__(self, model_path: str = 'best_resnet50.pth'):
        self.device = torch.device('cpu')
        self.model = None
        self.transform = None
        self.class_names = {0: "Coconut Tree", 1: "Mango Tree"}
        self._load_model(model_path)
    
    def _load_model(self, model_path: str) -> None:
        """Load ResNet50 model"""
        try:
            self.model = models.resnet50(pretrained=False)
            num_features = self.model.fc.in_features
            self.model.fc = torch.nn.Linear(num_features, 2)
            
            # Load checkpoint (may contain additional metadata)
            checkpoint = torch.load(model_path, map_location=self.device)
            
            # Extract model state_dict from checkpoint if needed
            if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
                state_dict = checkpoint['model_state_dict']
            else:
                state_dict = checkpoint
            
            # Remove 'model.' prefix if present (from DataParallel wrapping)
            new_state_dict = {}
            for k, v in state_dict.items():
                if k.startswith('model.'):
                    new_state_dict[k.replace('model.', '', 1)] = v
                else:
                    new_state_dict[k] = v
            
            # Skip FC layer loading (originally trained for 13 classes, we use 2)
            # Only load convolutional/feature extraction layers
            fc_layers = ['fc.weight', 'fc.bias']
            feature_dict = {k: v for k, v in new_state_dict.items() if k not in fc_layers}
            
            self.model.load_state_dict(feature_dict, strict=False)
            self.model.to(self.device)
            self.model.eval()
            
            self.transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.RandomHorizontalFlip(),
            ])
            logger.info(f"✓ Model loaded from {model_path}")
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            self.model = None
    
    def identify(self, image_data: bytes) -> Dict[str, Any]:
        """Identify tree from image bytes"""
        try:
            if not self.model:
                return {"success": False, "error": "Model not loaded"}
            
            # Load image from bytes
            img = Image.open(io.BytesIO(image_data)).convert('RGB')
            
            # Preprocess and infer
            img_tensor = self.transform(img).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                output = self.model(img_tensor)
                probs = torch.softmax(output, dim=1)
                confidence, pred_idx = torch.max(probs, 1)
            
            species = self.class_names[int(pred_idx.item())]
            conf = float(confidence.item())
            
            return {
                "success": True,
                "species": species,
                "confidence": conf,
                "confidence_level": self._confidence_level(conf),
                "class_id": int(pred_idx.item()),
                "carbon_rate_kg_per_month": 2.5 if species == "Coconut Tree" else 1.8,
                "error": None
            }
        except Exception as e:
            logger.error(f"Inference error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _confidence_level(self, conf: float) -> str:
        """Map confidence to level"""
        if conf >= 0.9:
            return "Very High"
        elif conf >= 0.7:
            return "High"
        elif conf >= 0.5:
            return "Medium"
        else:
            return "Low"


# Initialize identifier
identifier = TreeIdentifier('best_resnet50.pth')


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "VGG16 Tree Identifier API",
        "model": "VGG16",
        "classes": list(identifier.class_names.values())
    }), 200


@app.route('/identify', methods=['POST'])
def identify_tree():
    """
    Identify tree species from uploaded image
    
    Request: 
        - POST with image file in 'image' form field
        OR
        - JSON with 'image_url' field
    
    Response:
        {
            "success": bool,
            "species": str,
            "confidence": float,
            "confidence_level": str,
            "carbon_rate_kg_per_month": float
        }
    """
    try:
        # Handle file upload
        if 'image' in request.files:
            file = request.files['image']
            image_data = file.read()
        
        # Handle URL
        elif request.is_json and 'image_url' in request.json:
            url = request.json['image_url']
            with urllib.request.urlopen(url, timeout=10) as response:
                image_data = response.read()
        
        else:
            return jsonify({"success": False, "error": "No image provided"}), 400
        
        # Run inference
        result = identifier.identify(image_data)
        
        return jsonify(result), 200 if result.get("success") else 400
    
    except Exception as e:
        logger.error(f"API error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/classes', methods=['GET'])
def get_classes():
    """Get supported tree classes"""
    return jsonify({
        "classes": identifier.class_names,
        "count": len(identifier.class_names)
    }), 200


if __name__ == '__main__':
    # Run server
    debug_mode = FLASK_ENV == 'development'
    app.run(
        host='0.0.0.0',
        port=PORT,
        debug=debug_mode,
        threaded=True
    )
