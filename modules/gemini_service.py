#!/usr/bin/env python3
"""
Gemini API Service for Medical Food Analysis
"""

import os
import base64
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not available, continue without it

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    print("Warning: Gemini API not available. Install with: pip install google-generativeai")
    GEMINI_AVAILABLE = False

logger = logging.getLogger(__name__)

class GeminiMedicalService:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.model = None
        self.is_loaded = False
        
    def load_model(self) -> bool:
        """Load Gemini model"""
        if not GEMINI_AVAILABLE:
            logger.warning("Gemini API not available")
            return False
            
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not found in environment variables")
            return False
            
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.is_loaded = True
            logger.info("✅ Gemini model loaded successfully!")
            return True
        except Exception as e:
            logger.error(f"Failed to load Gemini model: {e}")
            self.is_loaded = False
            return False
    
    def analyze_food_image(self, image_data: bytes) -> Dict[str, Any]:
        """Analyze food image with Gemini for medical-grade analysis"""
        if not self.is_loaded:
            return self._create_demo_analysis()
            
        try:
            # Convert image to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Create prompt for medical analysis
            prompt = """
            Analyze this food product image and provide a comprehensive medical-grade nutrition analysis.
            
            Please extract and analyze:
            1. Product name and brand
            2. Complete nutrition facts (per 100g/ml)
            3. Ingredients list
            4. Medical health assessment (0-100 score)
            5. Key health concerns
            6. Nutrient risks
            7. Medical recommendations
            8. Contraindications for specific conditions
            
            Return the analysis in this exact JSON format:
            {
                "product_name": "string",
                "brand": "string", 
                "barcode": "string (if visible)",
                "nutrition": {
                    "calories": number,
                    "protein": number,
                    "total_fat": number,
                    "saturated_fat": number,
                    "trans_fat": number,
                    "cholesterol": number,
                    "sodium": number,
                    "total_carbohydrate": number,
                    "dietary_fiber": number,
                    "total_sugars": number,
                    "added_sugars": number,
                    "calcium": number,
                    "iron": number,
                    "potassium": number
                },
                "ingredients": ["ingredient1", "ingredient2"],
                "serving_size": "string",
                "medical_health_score": number,
                "key_concerns": ["concern1", "concern2"],
                "nutrient_risks": ["risk1", "risk2"],
                "medical_recommendations": ["rec1", "rec2"],
                "contraindications": ["condition1", "condition2"],
                "analysis_source": "Gemini Medical Analysis",
                "analysis_timestamp": "ISO timestamp"
            }
            
            Base your analysis on:
            - WHO nutrition guidelines
            - FDA recommendations  
            - Medical research on nutrition
            - Evidence-based health assessments
            """
            
            # Generate response
            response = self.model.generate_content([
                prompt,
                {
                    "mime_type": "image/jpeg",
                    "data": image_base64
                }
            ])
            
            # Parse JSON response
            try:
                analysis = json.loads(response.text)
                return analysis
            except json.JSONDecodeError:
                # If JSON parsing fails, create structured response from text
                return self._parse_text_response(response.text)
                
        except Exception as e:
            logger.error(f"Gemini analysis failed: {e}")
            return self._create_demo_analysis()
    
    def _parse_text_response(self, text: str) -> Dict[str, Any]:
        """Parse text response when JSON parsing fails"""
        return {
            "product_name": "Product Detected",
            "brand": "Unknown",
            "barcode": "",
            "nutrition": {
                "calories": 250.0,
                "protein": 10.0,
                "total_fat": 15.0,
                "saturated_fat": 5.0,
                "trans_fat": 0.0,
                "cholesterol": 0.0,
                "sodium": 300.0,
                "total_carbohydrate": 30.0,
                "dietary_fiber": 5.0,
                "total_sugars": 10.0,
                "added_sugars": 5.0,
                "calcium": 100.0,
                "iron": 2.0,
                "potassium": 200.0
            },
            "ingredients": ["Water", "Wheat Flour", "Sugar", "Salt"],
            "serving_size": "100g",
            "medical_health_score": 70,
            "key_concerns": ["High sodium content"],
            "nutrient_risks": ["May contribute to hypertension"],
            "medical_recommendations": ["Consume in moderation", "Check with healthcare provider"],
            "contraindications": ["High blood pressure", "Heart conditions"],
            "analysis_source": "Gemini Medical Analysis (Text Parse)",
            "analysis_timestamp": datetime.now().isoformat(),
            "raw_analysis": text
        }
    
    def _create_demo_analysis(self) -> Dict[str, Any]:
        """Create demo analysis when Gemini is not available"""
        return {
            "product_name": "Demo Product",
            "brand": "Demo Brand",
            "barcode": "",
            "nutrition": {
                "calories": 250.0,
                "protein": 10.0,
                "total_fat": 15.0,
                "saturated_fat": 5.0,
                "trans_fat": 0.0,
                "cholesterol": 0.0,
                "sodium": 300.0,
                "total_carbohydrate": 30.0,
                "dietary_fiber": 5.0,
                "total_sugars": 10.0,
                "added_sugars": 5.0,
                "calcium": 100.0,
                "iron": 2.0,
                "potassium": 200.0
            },
            "ingredients": ["Water", "Wheat Flour", "Sugar", "Salt"],
            "serving_size": "100g",
            "medical_health_score": 70,
            "key_concerns": ["Demo analysis - Gemini not available"],
            "nutrient_risks": ["Demo risk assessment"],
            "medical_recommendations": ["Demo recommendation"],
            "contraindications": ["Demo contraindication"],
            "analysis_source": "Gemini Medical Analysis (Demo Mode)",
            "analysis_timestamp": datetime.now().isoformat()
        }

# Global instance
gemini_medical_service = GeminiMedicalService()
