import openai
import anthropic
import json
import re
from typing import Dict, List, Any, Optional
import os
from PIL import Image
import base64
import io

class LLMTextExtractor:
    """
    Advanced LLM-powered text extraction and analysis for food labels
    Uses OpenAI GPT-4 and Anthropic Claude for medical-grade accuracy
    """
    
    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        
        # Initialize API clients if keys are available
        if os.getenv('OPENAI_API_KEY'):
            self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        if os.getenv('ANTHROPIC_API_KEY'):
            self.anthropic_client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
    
    def extract_nutrition_from_image(self, image: Image.Image) -> Dict[str, Any]:
        """Extract nutrition information from food label image using LLM"""
        try:
            # Convert image to base64
            img_buffer = io.BytesIO()
            image.save(img_buffer, format='PNG')
            img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
            
            # Try OpenAI GPT-4 Vision first
            if self.openai_client:
                result = self._extract_with_openai_vision(img_base64)
                if result and not result.get('error'):
                    return result
            
            # Fallback to Anthropic Claude
            if self.anthropic_client:
                result = self._extract_with_anthropic_vision(img_base64)
                if result and not result.get('error'):
                    return result
            
            # Fallback to OCR if LLM fails
            return self._fallback_ocr_extraction(image)
            
        except Exception as e:
            # Always fallback to OCR if anything fails
            return self._fallback_ocr_extraction(image)
    
    def _extract_with_openai_vision(self, img_base64: str) -> Dict[str, Any]:
        """Extract nutrition using OpenAI GPT-4 Vision"""
        try:
            prompt = """
            Analyze this food label image and extract the following information in JSON format:
            
            {
                "product_name": "Product name",
                "serving_size": "Serving size with unit",
                "servings_per_container": "Number of servings per container",
                "nutrition_facts": {
                    "calories": number,
                    "total_fat": number,
                    "saturated_fat": number,
                    "trans_fat": number,
                    "cholesterol": number,
                    "sodium": number,
                    "total_carbohydrate": number,
                    "dietary_fiber": number,
                    "total_sugars": number,
                    "added_sugars": number,
                    "protein": number,
                    "vitamin_d": number,
                    "calcium": number,
                    "iron": number,
                    "potassium": number
                },
                "ingredients": ["ingredient1", "ingredient2", ...],
                "allergens": ["allergen1", "allergen2", ...],
                "certifications": ["organic", "non-gmo", ...],
                "health_claims": ["claim1", "claim2", ...]
            }
            
            Important:
            - Extract exact values as numbers (not strings)
            - Include units in serving_size
            - List all ingredients in order
            - Identify any allergens (milk, eggs, fish, shellfish, tree nuts, peanuts, wheat, soybeans)
            - Note any health claims or certifications
            - If a value is not visible, use null
            - Be extremely accurate with numbers and units
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{img_base64}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=2000,
                temperature=0.1
            )
            
            content = response.choices[0].message.content
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {'error': 'Could not parse JSON from OpenAI response'}
                
        except Exception as e:
            return {'error': f'OpenAI extraction failed: {str(e)}'}
    
    def _extract_with_anthropic_vision(self, img_base64: str) -> Dict[str, Any]:
        """Extract nutrition using Anthropic Claude"""
        try:
            prompt = """
            Analyze this food label image and extract the following information in JSON format:
            
            {
                "product_name": "Product name",
                "serving_size": "Serving size with unit",
                "servings_per_container": "Number of servings per container",
                "nutrition_facts": {
                    "calories": number,
                    "total_fat": number,
                    "saturated_fat": number,
                    "trans_fat": number,
                    "cholesterol": number,
                    "sodium": number,
                    "total_carbohydrate": number,
                    "dietary_fiber": number,
                    "total_sugars": number,
                    "added_sugars": number,
                    "protein": number,
                    "vitamin_d": number,
                    "calcium": number,
                    "iron": number,
                    "potassium": number
                },
                "ingredients": ["ingredient1", "ingredient2", ...],
                "allergens": ["allergen1", "allergen2", ...],
                "certifications": ["organic", "non-gmo", ...],
                "health_claims": ["claim1", "claim2", ...]
            }
            
            Important:
            - Extract exact values as numbers (not strings)
            - Include units in serving_size
            - List all ingredients in order
            - Identify any allergens (milk, eggs, fish, shellfish, tree nuts, peanuts, wheat, soybeans)
            - Note any health claims or certifications
            - If a value is not visible, use null
            - Be extremely accurate with numbers and units
            """
            
            response = self.anthropic_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=2000,
                temperature=0.1,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/png",
                                    "data": img_base64
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ]
            )
            
            content = response.content[0].text
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {'error': 'Could not parse JSON from Anthropic response'}
                
        except Exception as e:
            return {'error': f'Anthropic extraction failed: {str(e)}'}
    
    def _fallback_ocr_extraction(self, image: Image.Image) -> Dict[str, Any]:
        """Fallback OCR extraction if LLM fails"""
        try:
            import easyocr
            
            reader = easyocr.Reader(['en'])
            results = reader.readtext(image)
            
            # Combine all text
            full_text = ' '.join([result[1] for result in results])
            
            # Basic nutrition extraction using regex
            nutrition = self._extract_nutrition_regex(full_text)
            ingredients = self._extract_ingredients_regex(full_text)
            
            return {
                'product_name': self._extract_product_name_regex(full_text),
                'serving_size': self._extract_serving_size_regex(full_text),
                'nutrition_facts': nutrition,
                'ingredients': ingredients,
                'source': 'OCR Fallback'
            }
            
        except Exception as e:
            return {'error': f'OCR fallback failed: {str(e)}'}
    
    def _extract_nutrition_regex(self, text: str) -> Dict[str, float]:
        """Extract nutrition facts using regex patterns"""
        nutrition = {}
        text_lower = text.lower()
        
        patterns = {
            'calories': r'calories?\s*:?\s*(\d+(?:\.\d+)?)',
            'total_fat': r'total\s*fat\s*:?\s*(\d+(?:\.\d+)?)\s*g',
            'saturated_fat': r'saturated\s*fat\s*:?\s*(\d+(?:\.\d+)?)\s*g',
            'trans_fat': r'trans\s*fat\s*:?\s*(\d+(?:\.\d+)?)\s*g',
            'cholesterol': r'cholesterol\s*:?\s*(\d+(?:\.\d+)?)\s*mg',
            'sodium': r'sodium\s*:?\s*(\d+(?:\.\d+)?)\s*mg',
            'total_carbohydrate': r'total\s*carbohydrate\s*:?\s*(\d+(?:\.\d+)?)\s*g',
            'dietary_fiber': r'dietary\s*fiber\s*:?\s*(\d+(?:\.\d+)?)\s*g',
            'total_sugars': r'total\s*sugars?\s*:?\s*(\d+(?:\.\d+)?)\s*g',
            'added_sugars': r'added\s*sugars?\s*:?\s*(\d+(?:\.\d+)?)\s*g',
            'protein': r'protein\s*:?\s*(\d+(?:\.\d+)?)\s*g',
            'vitamin_d': r'vitamin\s*d\s*:?\s*(\d+(?:\.\d+)?)\s*mcg',
            'calcium': r'calcium\s*:?\s*(\d+(?:\.\d+)?)\s*mg',
            'iron': r'iron\s*:?\s*(\d+(?:\.\d+)?)\s*mg',
            'potassium': r'potassium\s*:?\s*(\d+(?:\.\d+)?)\s*mg'
        }
        
        for nutrient, pattern in patterns.items():
            match = re.search(pattern, text_lower)
            if match:
                try:
                    nutrition[nutrient] = float(match.group(1))
                except ValueError:
                    continue
        
        return nutrition
    
    def _extract_ingredients_regex(self, text: str) -> List[str]:
        """Extract ingredients list using regex"""
        ingredients = []
        
        # Look for ingredients section
        ingredient_patterns = [
            r'ingredients?\s*:?\s*(.*?)(?:\n|$)',
            r'contains?\s*:?\s*(.*?)(?:\n|$)',
            r'ingredients?\s*list\s*:?\s*(.*?)(?:\n|$)'
        ]
        
        for pattern in ingredient_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                ingredient_text = match.group(1)
                # Split by common separators
                ingredient_list = re.split(r'[,;]\s*', ingredient_text)
                ingredients.extend([ing.strip() for ing in ingredient_list if ing.strip()])
                break
        
        return ingredients[:20]  # Limit to first 20 ingredients
    
    def _extract_product_name_regex(self, text: str) -> str:
        """Extract product name using regex"""
        lines = text.split('\n')
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            if len(line) > 3 and not any(word in line.lower() for word in ['nutrition', 'ingredients', 'facts', 'serving']):
                return line
        return 'Unknown Product'
    
    def _extract_serving_size_regex(self, text: str) -> str:
        """Extract serving size using regex"""
        serving_patterns = [
            r'serving\s*size\s*:?\s*([^,\n]+)',
            r'per\s*serving\s*:?\s*([^,\n]+)',
            r'size\s*:?\s*([^,\n]+)'
        ]
        
        for pattern in serving_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return 'Unknown'
    
    def analyze_ingredients_with_llm(self, ingredients: List[str]) -> Dict[str, Any]:
        """Analyze ingredients using LLM for health insights"""
        if not self.openai_client and not self.anthropic_client:
            return {'error': 'No LLM API keys available'}
        
        try:
            ingredients_text = ', '.join(ingredients)
            
            prompt = f"""
            Analyze these food ingredients for health and safety:
            
            Ingredients: {ingredients_text}
            
            Provide analysis in JSON format:
            {{
                "additives": ["additive1", "additive2", ...],
                "preservatives": ["preservative1", "preservative2", ...],
                "artificial_colors": ["color1", "color2", ...],
                "artificial_flavors": ["flavor1", "flavor2", ...],
                "artificial_sweeteners": ["sweetener1", "sweetener2", ...],
                "natural_ingredients": ["ingredient1", "ingredient2", ...],
                "allergens": ["allergen1", "allergen2", ...],
                "health_concerns": ["concern1", "concern2", ...],
                "health_benefits": ["benefit1", "benefit2", ...],
                "processing_level": "minimal|moderate|high",
                "overall_assessment": "excellent|good|moderate|poor"
            }}
            
            Focus on:
            - Food additives and preservatives
            - Artificial ingredients
            - Natural vs processed ingredients
            - Potential allergens
            - Health implications
            - Processing level assessment
            """
            
            if self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1000,
                    temperature=0.1
                )
                content = response.choices[0].message.content
            else:
                response = self.anthropic_client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=1000,
                    temperature=0.1,
                    messages=[{"role": "user", "content": prompt}]
                )
                content = response.content[0].text
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {'error': 'Could not parse JSON from LLM response'}
                
        except Exception as e:
            return {'error': f'LLM ingredient analysis failed: {str(e)}'}
    
    def generate_health_insights(self, nutrition: Dict[str, float], ingredients_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive health insights using LLM"""
        if not self.openai_client and not self.anthropic_client:
            return {'error': 'No LLM API keys available'}
        
        try:
            prompt = f"""
            Generate comprehensive health insights based on this nutrition and ingredient data:
            
            Nutrition Facts (per 100g):
            {json.dumps(nutrition, indent=2)}
            
            Ingredient Analysis:
            {json.dumps(ingredients_analysis, indent=2)}
            
            Provide insights in JSON format:
            {{
                "overall_health_score": 0-100,
                "health_grade": "A+|A|B+|B|C+|C|D|F",
                "key_strengths": ["strength1", "strength2", ...],
                "key_concerns": ["concern1", "concern2", ...],
                "medical_recommendations": ["rec1", "rec2", ...],
                "target_audience": ["audience1", "audience2", ...],
                "dietary_suitability": {{
                    "diabetes_friendly": true/false,
                    "heart_healthy": true/false,
                    "weight_management": true/false,
                    "kidney_friendly": true/false,
                    "low_sodium": true/false,
                    "high_fiber": true/false,
                    "high_protein": true/false
                }},
                "nutrient_highlights": ["highlight1", "highlight2", ...],
                "improvement_suggestions": ["suggestion1", "suggestion2", ...]
            }}
            
            Base analysis on:
            - WHO nutrition guidelines
            - FDA recommendations
            - Medical research
            - Clinical evidence
            - Dietary guidelines
            """
            
            if self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1500,
                    temperature=0.1
                )
                content = response.choices[0].message.content
            else:
                response = self.anthropic_client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=1500,
                    temperature=0.1,
                    messages=[{"role": "user", "content": prompt}]
                )
                content = response.content[0].text
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {'error': 'Could not parse JSON from LLM response'}
                
        except Exception as e:
            return {'error': f'LLM health insights failed: {str(e)}'}
