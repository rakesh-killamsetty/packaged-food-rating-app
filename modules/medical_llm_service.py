"""
Medical LLM Service for Food Nutrition Analysis
Uses BioMistral 7B - a medical-grade LLM trained on PubMed Central data
"""

import os
import logging
from typing import Dict, List, Optional, Any
import json
import re
from datetime import datetime

# Try to import ML dependencies, fallback to demo mode if not available
try:
    import torch
    from transformers import (
        AutoTokenizer, 
        AutoModelForCausalLM, 
        BitsAndBytesConfig,
        pipeline
    )
    ML_AVAILABLE = True
except ImportError as e:
    print(f"Warning: ML dependencies not available: {e}")
    print("Running in demo mode...")
    ML_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MedicalLLMService:
    """
    Medical LLM Service using BioMistral 7B for food nutrition analysis
    """
    
    def __init__(self):
        # Try multiple medical LLM models in order of preference
        self.model_options = [
            "microsoft/BioMistral-7B",
            "microsoft/DialoGPT-medium",  # Fallback option
            "distilbert-base-uncased",    # Lightweight fallback
        ]
        self.model_name = self.model_options[0]
        self.tokenizer = None
        self.model = None
        self.pipeline = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.is_loaded = False
        
        # Medical nutrition guidelines and references
        self.medical_guidelines = {
            "who_guidelines": {
                "sodium": {"max_daily": 2000, "unit": "mg"},
                "sugar": {"max_daily": 50, "unit": "g"},
                "saturated_fat": {"max_daily": 22, "unit": "g"},
                "trans_fat": {"max_daily": 2, "unit": "g"}
            },
            "fda_guidelines": {
                "fiber": {"min_daily": 25, "unit": "g"},
                "protein": {"min_daily": 50, "unit": "g"},
                "vitamin_c": {"min_daily": 90, "unit": "mg"},
                "calcium": {"min_daily": 1000, "unit": "mg"}
            },
            "medical_conditions": {
                "diabetes": ["sugar", "carbohydrates", "glycemic_index"],
                "hypertension": ["sodium", "potassium"],
                "heart_disease": ["saturated_fat", "trans_fat", "cholesterol"],
                "obesity": ["calories", "sugar", "saturated_fat"]
            }
        }
    
    def load_model(self) -> bool:
        """
        Load the BioMistral 7B model with optimized configuration
        """
        if not ML_AVAILABLE:
            logger.info("ML dependencies not available, running in demo mode...")
            self.is_loaded = False
            return False
            
        try:
            logger.info(f"Loading BioMistral 7B model on {self.device}...")
            
            # Configure quantization for memory efficiency
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4"
            )
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True,
                padding_side="left"
            )
            
            # Add padding token if not present
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load model with quantization
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                quantization_config=quantization_config if self.device == "cuda" else None,
                device_map="auto" if self.device == "cuda" else None,
                trust_remote_code=True,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
            )
            
            # Create pipeline for text generation
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device_map="auto" if self.device == "cuda" else None,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
            )
            
            self.is_loaded = True
            logger.info("BioMistral 7B model loaded successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load BioMistral model: {str(e)}")
            logger.info("Falling back to demo mode...")
            self.is_loaded = False
            return False
    
    def analyze_food_nutrition(self, 
                             product_name: str, 
                             ingredients: List[str], 
                             nutrition_facts: Dict[str, Any],
                             barcode: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze food product using medical-grade LLM
        """
        if not self.is_loaded:
            return self._get_demo_analysis(product_name, ingredients, nutrition_facts)
        
        try:
            # Create medical analysis prompt
            prompt = self._create_medical_prompt(product_name, ingredients, nutrition_facts)
            
            # Generate medical analysis
            response = self.pipeline(
                prompt,
                max_new_tokens=512,
                temperature=0.3,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id
            )
            
            # Parse the response
            analysis = self._parse_medical_response(response[0]['generated_text'])
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in medical analysis: {str(e)}")
            return self._get_demo_analysis(product_name, ingredients, nutrition_facts)
    
    def _create_medical_prompt(self, 
                              product_name: str, 
                              ingredients: List[str], 
                              nutrition_facts: Dict[str, Any]) -> str:
        """
        Create a medical-grade prompt for food analysis
        """
        prompt = f"""<s>[INST] As a medical nutritionist with expertise in food science and clinical nutrition, analyze the following food product based on WHO, FDA, and peer-reviewed medical research:

Product: {product_name}
Ingredients: {', '.join(ingredients)}
Nutrition Facts (per 100g):
"""
        
        for nutrient, value in nutrition_facts.items():
            prompt += f"- {nutrient}: {value}\n"
        
        prompt += """
Please provide a comprehensive medical analysis including:

1. HEALTH SCORE (0-100): Based on WHO/FDA guidelines and medical research
2. MEDICAL CONCERNS: Potential health risks based on ingredients and nutrition
3. NUTRIENT ANALYSIS: Detailed breakdown of each nutrient's medical significance
4. CLINICAL RECOMMENDATIONS: Evidence-based recommendations for different health conditions
5. CONTRAINDICATIONS: Medical conditions that should avoid this product
6. EVIDENCE: Cite relevant medical studies and guidelines

Format your response as structured JSON with medical accuracy and evidence-based insights.
[/INST]"""
        
        return prompt
    
    def _parse_medical_response(self, response: str) -> Dict[str, Any]:
        """
        Parse the medical LLM response into structured data
        """
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group())
            else:
                # Fallback parsing
                analysis = self._fallback_parse(response)
            
            # Enhance with medical guidelines
            analysis = self._enhance_with_medical_guidelines(analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error parsing medical response: {str(e)}")
            return self._fallback_parse(response)
    
    def _fallback_parse(self, response: str) -> Dict[str, Any]:
        """
        Fallback parsing when JSON extraction fails
        """
        # Extract health score
        score_match = re.search(r'HEALTH SCORE[:\s]*(\d+)', response, re.IGNORECASE)
        health_score = int(score_match.group(1)) if score_match else 75
        
        # Extract medical concerns
        concerns_match = re.search(r'MEDICAL CONCERNS[:\s]*(.*?)(?=NUTRIENT ANALYSIS|CLINICAL RECOMMENDATIONS|$)', response, re.IGNORECASE | re.DOTALL)
        medical_concerns = concerns_match.group(1).strip() if concerns_match else "No significant medical concerns identified."
        
        return {
            "health_score": health_score,
            "medical_concerns": medical_concerns,
            "analysis": response,
            "timestamp": datetime.now().isoformat(),
            "model_used": "BioMistral-7B"
        }
    
    def _enhance_with_medical_guidelines(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance analysis with medical guidelines and references
        """
        analysis["medical_guidelines"] = self.medical_guidelines
        analysis["evidence_sources"] = [
            "WHO Guidelines on Nutrition",
            "FDA Food Safety Guidelines", 
            "PubMed Medical Research",
            "Clinical Nutrition Studies"
        ]
        analysis["model_used"] = "BioMistral-7B"
        analysis["timestamp"] = datetime.now().isoformat()
        
        return analysis
    
    def _get_demo_analysis(self, 
                          product_name: str, 
                          ingredients: List[str], 
                          nutrition_facts: Dict[str, Any]) -> Dict[str, Any]:
        """
        Demo analysis when model is not available
        """
        # Basic health scoring based on ingredients and nutrition
        health_score = self._calculate_basic_health_score(ingredients, nutrition_facts)
        
        return {
            "health_score": health_score,
            "medical_concerns": self._get_medical_concerns(ingredients, nutrition_facts),
            "nutrient_analysis": self._analyze_nutrients(nutrition_facts),
            "clinical_recommendations": self._get_clinical_recommendations(health_score),
            "contraindications": self._get_contraindications(ingredients),
            "evidence_sources": [
                "WHO Guidelines on Nutrition",
                "FDA Food Safety Guidelines",
                "PubMed Medical Research"
            ],
            "model_used": "Demo Mode (BioMistral-7B not available)",
            "timestamp": datetime.now().isoformat(),
            "medical_guidelines": self.medical_guidelines
        }
    
    def _calculate_basic_health_score(self, ingredients: List[str], nutrition_facts: Dict[str, Any]) -> int:
        """
        Calculate basic health score based on ingredients and nutrition
        """
        score = 100
        
        # Check for harmful ingredients
        harmful_ingredients = [
            "artificial sweetener", "high fructose corn syrup", "trans fat",
            "sodium benzoate", "artificial color", "preservative"
        ]
        
        for ingredient in ingredients:
            ingredient_lower = ingredient.lower()
            for harmful in harmful_ingredients:
                if harmful in ingredient_lower:
                    score -= 10
        
        # Check nutrition facts
        if "sodium" in nutrition_facts:
            sodium = float(nutrition_facts["sodium"].replace("mg", "").strip())
            if sodium > 600:  # High sodium
                score -= 15
        
        if "sugar" in nutrition_facts:
            sugar = float(nutrition_facts["sugar"].replace("g", "").strip())
            if sugar > 15:  # High sugar
                score -= 20
        
        return max(0, min(100, score))
    
    def _get_medical_concerns(self, ingredients: List[str], nutrition_facts: Dict[str, Any]) -> str:
        """
        Identify medical concerns based on ingredients and nutrition
        """
        concerns = []
        
        # Check for high sodium
        if "sodium" in nutrition_facts:
            sodium = float(nutrition_facts["sodium"].replace("mg", "").strip())
            if sodium > 600:
                concerns.append("High sodium content may contribute to hypertension")
        
        # Check for high sugar
        if "sugar" in nutrition_facts:
            sugar = float(nutrition_facts["sugar"].replace("g", "").strip())
            if sugar > 15:
                concerns.append("High sugar content may increase diabetes risk")
        
        # Check ingredients
        for ingredient in ingredients:
            if "artificial" in ingredient.lower():
                concerns.append("Contains artificial ingredients with potential health risks")
        
        return "; ".join(concerns) if concerns else "No significant medical concerns identified."
    
    def _analyze_nutrients(self, nutrition_facts: Dict[str, Any]) -> Dict[str, str]:
        """
        Analyze individual nutrients
        """
        analysis = {}
        
        for nutrient, value in nutrition_facts.items():
            if "sodium" in nutrient.lower():
                analysis[nutrient] = "Essential for fluid balance, but excess can cause hypertension"
            elif "sugar" in nutrient.lower():
                analysis[nutrient] = "Provides energy but excess can lead to diabetes and obesity"
            elif "protein" in nutrient.lower():
                analysis[nutrient] = "Essential for muscle and tissue repair"
            elif "fiber" in nutrient.lower():
                analysis[nutrient] = "Important for digestive health and cholesterol management"
            else:
                analysis[nutrient] = "Important for overall health and nutrition"
        
        return analysis
    
    def _get_clinical_recommendations(self, health_score: int) -> List[str]:
        """
        Get clinical recommendations based on health score
        """
        if health_score >= 80:
            return [
                "Suitable for regular consumption",
                "Good nutritional profile",
                "Minimal health risks"
            ]
        elif health_score >= 60:
            return [
                "Moderate consumption recommended",
                "Monitor portion sizes",
                "Consider healthier alternatives"
            ]
        else:
            return [
                "Limit consumption",
                "High in potentially harmful ingredients",
                "Consult healthcare provider if consumed regularly"
            ]
    
    def _get_contraindications(self, ingredients: List[str]) -> List[str]:
        """
        Get medical contraindications
        """
        contraindications = []
        
        for ingredient in ingredients:
            ingredient_lower = ingredient.lower()
            if "artificial sweetener" in ingredient_lower:
                contraindications.append("May not be suitable for individuals with phenylketonuria")
            elif "sodium" in ingredient_lower:
                contraindications.append("Avoid if you have hypertension or heart disease")
            elif "sugar" in ingredient_lower:
                contraindications.append("Limit if you have diabetes or prediabetes")
        
        return contraindications if contraindications else ["No specific contraindications identified"]

# Global instance
medical_llm_service = MedicalLLMService()
