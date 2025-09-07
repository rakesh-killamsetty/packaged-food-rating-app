"""
Simple Medical LLM Service for Food Nutrition Analysis
Uses a more accessible model for medical-grade analysis
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

class SimpleMedicalLLMService:
    """
    Simple Medical LLM Service for food nutrition analysis
    Uses accessible models that work without authentication
    """
    
    def __init__(self):
        # Use more accessible models
        self.model_options = [
            "microsoft/DialoGPT-medium",  # Conversational model
            "distilgpt2",                 # Lightweight GPT-2
            "gpt2",                       # Standard GPT-2
        ]
        self.model_name = self.model_options[0]
        self.tokenizer = None
        self.model = None
        self.pipeline = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.is_loaded = False
        
        # Medical nutrition guidelines
        self.medical_guidelines = {
            "who_guidelines": {
                "sodium": {"max_daily": 2000, "unit": "mg"},
                "sugar": {"max_daily": 50, "unit": "g"},
                "saturated_fat": {"max_daily": 22, "unit": "g"},
                "trans_fat": {"max_daily": 2, "unit": "g"},
            },
            "fda_guidelines": {
                "calories": {"high": 400, "unit": "kcal"},
                "sodium": {"high": 600, "unit": "mg"},
                "sugar": {"high": 12, "unit": "g"},
            },
            "fssai_guidelines": {
                "sodium": {"max_daily": 2000, "unit": "mg"},
                "sugar": {"max_daily": 50, "unit": "g"},
                "saturated_fat": {"max_daily": 22, "unit": "g"},
            }
        }
    
    def load_model(self) -> bool:
        """
        Load a medical LLM model
        """
        if not ML_AVAILABLE:
            logger.info("ML dependencies not available, using demo mode")
            return False
            
        for model_name in self.model_options:
            try:
                logger.info(f"Loading {model_name} on {self.device}...")
                
                # Load tokenizer
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                
                # Add padding token if not present
                if self.tokenizer.pad_token is None:
                    self.tokenizer.pad_token = self.tokenizer.eos_token
                
                # Load model
                self.model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    torch_dtype=torch.float32
                )
                
                # Create pipeline
                self.pipeline = pipeline(
                    "text-generation",
                    model=self.model,
                    tokenizer=self.tokenizer,
                    max_length=256,
                    do_sample=True,
                    temperature=0.7,
                    top_p=0.9,
                    pad_token_id=self.tokenizer.eos_token_id
                )
                
                self.model_name = model_name
                self.is_loaded = True
                logger.info(f"✅ {model_name} loaded successfully!")
                return True
                
            except Exception as e:
                logger.warning(f"Failed to load {model_name}: {e}")
                continue
        
        logger.error("All model loading attempts failed")
        logger.info("Falling back to demo mode...")
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
            return self._demo_analysis(product_name, ingredients, nutrition_facts, barcode)
        
        try:
            # Create medical analysis prompt
            prompt = self._create_medical_prompt(product_name, ingredients, nutrition_facts, barcode)
            
            # Generate analysis using LLM
            response = self.pipeline(
                prompt,
                max_length=len(prompt.split()) + 200,
                num_return_sequences=1,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            # Extract analysis from response
            analysis_text = response[0]['generated_text']
            analysis_text = analysis_text.replace(prompt, "").strip()
            
            # Parse the analysis
            return self._parse_medical_analysis(analysis_text, nutrition_facts)
            
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            return self._demo_analysis(product_name, ingredients, nutrition_facts, barcode)
    
    def _create_medical_prompt(self, product_name: str, ingredients: List[str], 
                             nutrition_facts: Dict[str, Any], barcode: Optional[str] = None) -> str:
        """Create a medical analysis prompt"""
        
        # Format nutrition facts
        nutrition_str = "\n".join([f"{k}: {v}" for k, v in nutrition_facts.items() if v is not None])
        
        prompt = f"""
MEDICAL NUTRITION ANALYSIS

Product: {product_name}
Ingredients: {', '.join(ingredients)}
Nutrition Facts (per 100g):
{nutrition_str}

Please provide a medical-grade analysis including:
1. Health Score (0-100)
2. Key Health Concerns
3. Nutrient Risks
4. Medical Recommendations
5. Contraindications

Analysis:
"""
        return prompt.strip()
    
    def _parse_medical_analysis(self, analysis_text: str, nutrition_facts: Dict[str, Any]) -> Dict[str, Any]:
        """Parse LLM analysis into structured format"""
        
        # Extract health score
        health_score = 70  # Default
        score_match = re.search(r'health score[:\s]*(\d+)', analysis_text.lower())
        if score_match:
            health_score = int(score_match.group(1))
        
        # Extract key concerns
        concerns = []
        if "high sodium" in analysis_text.lower():
            concerns.append("High sodium content may increase blood pressure risk")
        if "high sugar" in analysis_text.lower():
            concerns.append("High sugar content may contribute to diabetes risk")
        if "saturated fat" in analysis_text.lower():
            concerns.append("Saturated fat content may affect cardiovascular health")
        
        # Extract recommendations
        recommendations = []
        if "reduce" in analysis_text.lower():
            recommendations.append("Consider reducing portion size")
        if "balance" in analysis_text.lower():
            recommendations.append("Balance with other nutritious foods")
        
        return {
            "medical_health_score": health_score,
            "key_concerns": concerns,
            "nutrient_risks": self._assess_nutrient_risks(nutrition_facts),
            "medical_recommendations": recommendations,
            "contraindications": self._get_contraindications(nutrition_facts),
            "analysis_source": f"Medical LLM ({self.model_name})",
            "analysis_timestamp": datetime.now().isoformat(),
            "raw_analysis": analysis_text
        }
    
    def _assess_nutrient_risks(self, nutrition_facts: Dict[str, Any]) -> List[str]:
        """Assess nutrient risks based on medical guidelines"""
        risks = []
        
        # Check sodium
        sodium = nutrition_facts.get('sodium', 0)
        if sodium > 600:  # High sodium threshold
            risks.append(f"High sodium content ({sodium}mg) exceeds recommended limits")
        
        # Check sugar
        sugar = nutrition_facts.get('total_sugars', 0)
        if sugar > 12:  # High sugar threshold
            risks.append(f"High sugar content ({sugar}g) may contribute to health risks")
        
        # Check saturated fat
        sat_fat = nutrition_facts.get('saturated_fat', 0)
        if sat_fat > 5:  # High saturated fat threshold
            risks.append(f"High saturated fat content ({sat_fat}g) may affect heart health")
        
        return risks
    
    def _get_contraindications(self, nutrition_facts: Dict[str, Any]) -> List[str]:
        """Get medical contraindications"""
        contraindications = []
        
        # High sodium contraindications
        sodium = nutrition_facts.get('sodium', 0)
        if sodium > 600:
            contraindications.append("Not recommended for individuals with hypertension")
        
        # High sugar contraindications
        sugar = nutrition_facts.get('total_sugars', 0)
        if sugar > 12:
            contraindications.append("Not recommended for individuals with diabetes")
        
        return contraindications
    
    def _demo_analysis(self, product_name: str, ingredients: List[str], 
                      nutrition_facts: Dict[str, Any], barcode: Optional[str] = None) -> Dict[str, Any]:
        """Demo analysis when LLM is not available"""
        
        # Calculate basic health score
        health_score = self._calculate_demo_health_score(nutrition_facts)
        
        # Assess risks
        risks = self._assess_nutrient_risks(nutrition_facts)
        
        # Get contraindications
        contraindications = self._get_contraindications(nutrition_facts)
        
        return {
            "medical_health_score": health_score,
            "key_concerns": risks[:3],  # Top 3 concerns
            "nutrient_risks": risks,
            "medical_recommendations": [
                "Consult with healthcare provider for personalized advice",
                "Consider portion control for optimal health",
                "Balance with other nutritious foods"
            ],
            "contraindications": contraindications,
            "analysis_source": "Medical Guidelines (Demo Mode)",
            "analysis_timestamp": datetime.now().isoformat(),
            "raw_analysis": f"Demo analysis for {product_name} based on medical guidelines"
        }
    
    def _calculate_demo_health_score(self, nutrition_facts: Dict[str, Any]) -> int:
        """Calculate health score based on nutrition facts"""
        score = 100
        
        # Deduct points for high values
        sodium = nutrition_facts.get('sodium', 0)
        if sodium > 600:
            score -= min(30, (sodium - 600) // 10)
        
        sugar = nutrition_facts.get('total_sugars', 0)
        if sugar > 12:
            score -= min(25, (sugar - 12) * 2)
        
        sat_fat = nutrition_facts.get('saturated_fat', 0)
        if sat_fat > 5:
            score -= min(20, (sat_fat - 5) * 3)
        
        return max(0, score)

# Create global instance
simple_medical_llm_service = SimpleMedicalLLMService()
