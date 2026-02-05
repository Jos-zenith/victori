"""
Tree Identification Module for HCCMS
Uses pre-trained ResNet50 model from BarkVisionAI dataset to identify tree species
"""

import torch
from torchvision import models, transforms
from PIL import Image
import numpy as np
import logging
from typing import Dict, Tuple, Optional, Any
import urllib.request
import io

logger = logging.getLogger(__name__)

# Tree species class mapping (from BarkVisionAI dataset - 13 classes)
SPECIES_CLASSES = {
    0: "Aesculus indica",
    1: "Buchanania lanzan",
    2: "Cedrus deodara",
    3: "Eucalyptus globulus",
    4: "Madhuca longifolia",
    5: "Mangifera sylvatica",
    6: "Phyllanthus emblica",
    7: "Pinus roxburghii",
    8: "Quercus leucotrichophora",
    9: "Rhododendron arboreum",
    10: "Senegalia catechu",
    11: "Shorea robusta",
    12: "Taxus baccata"
}

# Species to carbon absorption mapping (kg CO2/month)
SPECIES_CARBON_RATES = {
    "Aesculus indica": 2.2,
    "Buchanania lanzan": 1.9,
    "Cedrus deodara": 2.3,
    "Eucalyptus globulus": 2.8,
    "Madhuca longifolia": 2.1,
    "Mangifera sylvatica": 2.0,
    "Phyllanthus emblica": 1.8,
    "Pinus roxburghii": 1.8,
    "Quercus leucotrichophora": 2.4,
    "Rhododendron arboreum": 2.0,
    "Senegalia catechu": 1.7,
    "Shorea robusta": 2.5,
    "Taxus baccata": 2.1
}


class TreeIdentifier:
    """
    ResNet50-based tree species identifier trained on BarkVisionAI dataset.
    Identifies tree species from bark images and provides carbon absorption estimates.
    """
    
    def __init__(self, model_path: str = 'best_resnet50.pth'):
        """
        Initialize the tree identifier with pre-trained ResNet50 model.
        
        Args:
            model_path: Path to the PyTorch model weights file
        """
        self.device = torch.device('cpu')
        self.model = None
        self.model_path = model_path
        self.transform = None
        self._initialize_model()
    
    def _initialize_model(self) -> None:
        """Load and configure the ResNet50 model"""
        try:
            # Create ResNet50 architecture
            self.model = models.resnet50(pretrained=False)
            
            # Modify final layer for 13 tree species classes
            num_features = self.model.fc.in_features
            self.model.fc = torch.nn.Linear(num_features, 13)
            
            # Load trained weights
            self.model.load_state_dict(
                torch.load(self.model_path, map_location=self.device),
                strict=True
            )
            
            self.model.to(self.device)
            self.model.eval()
            
            # Set up image preprocessing pipeline
            self.transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225]
                )
            ])
            
            logger.info("Tree identifier model loaded successfully")
        
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            self.model = None
            raise
    
    def identify(self, image_source: str) -> Dict[str, Any]:
        """
        Identify tree species from a bark image.
        
        Args:
            image_source: Path to image file OR URL
        
        Returns:
            {
                "success": bool,
                "species": str,
                "confidence": float (0-1),
                "class_id": int,
                "carbon_rate_kg_per_month": float,
                "error": str (if failed)
            }
        """
        try:
            if not self.model:
                return {
                    "success": False,
                    "species": None,
                    "confidence": 0.0,
                    "error": "Model not loaded"
                }
            
            # Load image
            img = self._load_image(image_source)
            if img is None:
                return {
                    "success": False,
                    "species": None,
                    "confidence": 0.0,
                    "error": "Failed to load image"
                }
            
            # Preprocess image
            if self.transform is None:
                return {
                    "success": False,
                    "species": None,
                    "confidence": 0.0,
                    "error": "Transform not initialized"
                }
            
            img_tensor = self.transform(img)
            if not isinstance(img_tensor, torch.Tensor):
                img_tensor = torch.tensor(img_tensor)
            img_tensor = img_tensor.unsqueeze(0).to(self.device)
            
            # Run inference
            with torch.no_grad():
                output = self.model(img_tensor)
                probabilities = torch.softmax(output, dim=1)
                confidence, predicted_idx = torch.max(probabilities, 1)
            
            # Get species name
            species = SPECIES_CLASSES.get(int(predicted_idx.item()), "Unknown")
            carbon_rate = SPECIES_CARBON_RATES.get(species, 2.0)
            
            return {
                "success": True,
                "species": species,
                "confidence": float(confidence.item()),
                "class_id": int(predicted_idx.item()),
                "carbon_rate_kg_per_month": carbon_rate,
                "error": None
            }
        
        except Exception as e:
            logger.error(f"Error during inference: {str(e)}")
            return {
                "success": False,
                "species": None,
                "confidence": 0.0,
                "class_id": None,
                "carbon_rate_kg_per_month": 0.0,
                "error": str(e)
            }
    
    def _load_image(self, image_source: str) -> Optional[Image.Image]:
        """
        Load image from either file path or URL.
        
        Args:
            image_source: File path or URL to image
        
        Returns:
            PIL Image object or None if failed
        """
        try:
            if image_source.startswith('http://') or image_source.startswith('https://'):
                # Load from URL
                with urllib.request.urlopen(image_source, timeout=10) as response:
                    img_data = response.read()
                img = Image.open(io.BytesIO(img_data))
            else:
                # Load from file path
                img = Image.open(image_source)
            
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            return img
        
        except Exception as e:
            logger.error(f"Error loading image: {str(e)}")
            return None
    
    def get_confidence_level(self, confidence: float) -> str:
        """
        Categorize confidence score into human-readable level.
        
        Args:
            confidence: Confidence score (0-1)
        
        Returns:
            Confidence level string
        """
        if confidence >= 0.9:
            return "very_high"
        elif confidence >= 0.7:
            return "high"
        elif confidence >= 0.5:
            return "medium"
        elif confidence >= 0.3:
            return "low"
        else:
            return "very_low"


# ============================================================================
# VGG16-BASED TREE IDENTIFIER (BarkVisionAI trained on Coconut/Mango trees)
# ============================================================================

class VGG16TreeIdentifier:
    """
    VGG16-based tree species identifier trained on BarkVisionAI dataset.
    Specialized for Coconut Tree and Mango Tree identification with high accuracy.
    """
    
    def __init__(self, model_path: str = 'best_VGG16.pth'):
        """
        Initialize the VGG16 tree identifier.
        
        Args:
            model_path: Path to the PyTorch model weights file
        """
        self.device = torch.device('cpu')
        self.model = None
        self.model_path = model_path
        self.transform = None
        self.class_names = {0: "Coconut Tree", 1: "Mango Tree"}
        self._initialize_model()
    
    def _initialize_model(self) -> None:
        """Load and configure the VGG16 model"""
        try:
            # Create VGG16 architecture
            self.model = models.vgg16(pretrained=False)
            
            # Modify final layer for 2 tree species classes (Coconut & Mango)
            num_features = self.model.classifier[-1].in_features
            self.model.classifier[-1] = torch.nn.Linear(num_features, 2)
            
            # Load trained weights
            self.model.load_state_dict(
                torch.load(self.model_path, map_location=self.device),
                strict=True
            )
            
            self.model.to(self.device)
            self.model.eval()
            
            # Set up image preprocessing pipeline
            self.transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.RandomHorizontalFlip(),
            ])
            
            logger.info("VGG16 tree identifier model loaded successfully")
        
        except Exception as e:
            logger.error(f"Failed to load VGG16 model: {str(e)}")
            self.model = None
            raise
    
    def identify(self, image_source: str) -> Dict[str, Any]:
        """
        Identify tree species from a bark image.
        
        Args:
            image_source: Path to image file OR URL
        
        Returns:
            {
                "success": bool,
                "species": str,
                "confidence": float (0-1),
                "class_id": int,
                "carbon_rate_kg_per_month": float,
                "error": str (if failed)
            }
        """
        try:
            if not self.model:
                return {
                    "success": False,
                    "species": None,
                    "confidence": 0.0,
                    "error": "Model not loaded"
                }
            
            # Load image
            img = self._load_image(image_source)
            if img is None:
                return {
                    "success": False,
                    "species": None,
                    "confidence": 0.0,
                    "error": "Failed to load image"
                }
            
            # Preprocess image
            if self.transform is None:
                return {
                    "success": False,
                    "species": None,
                    "confidence": 0.0,
                    "error": "Transform not initialized"
                }
            
            img_tensor = self.transform(img)
            if not isinstance(img_tensor, torch.Tensor):
                img_tensor = torch.tensor(img_tensor)
            img_tensor = img_tensor.unsqueeze(0).to(self.device)
            
            # Run inference
            with torch.no_grad():
                output = self.model(img_tensor)
                probabilities = torch.softmax(output, dim=1)
                confidence, predicted_idx = torch.max(probabilities, 1)
            
            # Get species name
            species = self.class_names.get(int(predicted_idx.item()), "Unknown")
            carbon_rate = 2.5 if species == "Coconut Tree" else 1.8
            
            return {
                "success": True,
                "species": species,
                "confidence": float(confidence.item()),
                "class_id": int(predicted_idx.item()),
                "carbon_rate_kg_per_month": carbon_rate,
                "error": None
            }
        
        except Exception as e:
            logger.error(f"Error during VGG16 inference: {str(e)}")
            return {
                "success": False,
                "species": None,
                "confidence": 0.0,
                "class_id": None,
                "carbon_rate_kg_per_month": 0.0,
                "error": str(e)
            }
    
    def _load_image(self, image_source: str) -> Optional[Image.Image]:
        """
        Load image from either file path or URL.
        
        Args:
            image_source: File path or URL to image
        
        Returns:
            PIL Image object or None if failed
        """
        try:
            if image_source.startswith('http://') or image_source.startswith('https://'):
                with urllib.request.urlopen(image_source, timeout=10) as response:
                    img_data = response.read()
                img = Image.open(io.BytesIO(img_data))
            else:
                img = Image.open(image_source)
            
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            return img
        
        except Exception as e:
            logger.error(f"Error loading image: {str(e)}")
            return None
    
    def get_confidence_level(self, confidence: float) -> str:
        """
        Categorize confidence score into human-readable level.
        
        Args:
            confidence: Confidence score (0-1)
        
        Returns:
            Confidence level string
        """
        if confidence >= 0.9:
            return "Very High"
        elif confidence >= 0.7:
            return "High"
        elif confidence >= 0.5:
            return "Medium"
        else:
            return "Low"


# Global instances (lazy-loaded)
_resnet50_instance = None
_vgg16_instance = None

def get_identifier(model_type: str = 'resnet50') -> TreeIdentifier:
    """
    Get or create global tree identifier instance.
    
    Args:
        model_type: 'resnet50' (13 species) or 'vgg16' (Coconut/Mango)
    
    Returns:
        Tree identifier instance
    """
    global _resnet50_instance
    if model_type == 'resnet50':
        if _resnet50_instance is None:
            _resnet50_instance = TreeIdentifier('best_resnet50.pth')
        return _resnet50_instance
    else:
        raise ValueError(f"Unknown model type: {model_type}")

def get_vgg16_identifier() -> VGG16TreeIdentifier:
    """Get or create global VGG16 tree identifier instance (Coconut/Mango specialist)"""
    global _vgg16_instance
    if _vgg16_instance is None:
        _vgg16_instance = VGG16TreeIdentifier('best_VGG16.pth')
    return _vgg16_instance
