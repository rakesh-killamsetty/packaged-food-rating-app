import cv2
import numpy as np
from PIL import Image
import easyocr
import re
from typing import Dict, List, Any

class OCRProcessor:
    def __init__(self):
        self.reader = easyocr.Reader(['en'])
        self.nutrition_patterns = {
            'calories': r'calories?\s*:?\s*(\d+(?:\.\d+)?)',
            'protein': r'protein\s*:?\s*(\d+(?:\.\d+)?)\s*g',
            'carbs': r'carbohydrates?\s*:?\s*(\d+(?:\.\d+)?)\s*g',
            'sugar': r'sugars?\s*:?\s*(\d+(?:\.\d+)?)\s*g',
            'fat': r'total\s*fat\s*:?\s*(\d+(?:\.\d+)?)\s*g',
            'saturated_fat': r'saturated\s*fat\s*:?\s*(\d+(?:\.\d+)?)\s*g',
            'trans_fat': r'trans\s*fat\s*:?\s*(\d+(?:\.\d+)?)\s*g',
            'sodium': r'sodium\s*:?\s*(\d+(?:\.\d+)?)\s*mg',
            'fiber': r'dietary\s*fiber\s*:?\s*(\d+(?:\.\d+)?)\s*g',
            'cholesterol': r'cholesterol\s*:?\s*(\d+(?:\.\d+)?)\s*mg'
        }
    
    def process_image(self, image: Image.Image) -> Dict[str, Any]:
        """Process uploaded image and extract nutrition/ingredient data"""
        try:
            # Convert PIL image to OpenCV format
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Preprocess image for better OCR
            processed_image = self._preprocess_image(cv_image)
            
            # Extract text using EasyOCR
            results = self.reader.readtext(processed_image)
            
            # Combine all text
            full_text = ' '.join([result[1] for result in results])
            
            # Extract nutrition information
            nutrition_data = self._extract_nutrition_data(full_text)
            
            # Extract ingredients
            ingredients = self._extract_ingredients(full_text)
            
            # Extract serving size
            serving_size = self._extract_serving_size(full_text)
            
            return {
                'product_name': self._extract_product_name(full_text),
                'raw_text': full_text,
                'nutrition': nutrition_data,
                'ingredients': ingredients,
                'serving_size': serving_size,
                'source': 'ocr'
            }
            
        except Exception as e:
            return {
                'error': f"OCR processing failed: {str(e)}",
                'product_name': 'Unknown Product',
                'nutrition': {},
                'ingredients': [],
                'serving_size': 'Unknown',
                'source': 'ocr'
            }
    
    def _preprocess_image(self, image):
        """Preprocess image for better OCR accuracy"""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        # Morphological operations to clean up
        kernel = np.ones((1, 1), np.uint8)
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        return cleaned
    
    def _extract_nutrition_data(self, text: str) -> Dict[str, float]:
        """Extract nutrition data from OCR text"""
        nutrition = {}
        text_lower = text.lower()
        
        for nutrient, pattern in self.nutrition_patterns.items():
            match = re.search(pattern, text_lower)
            if match:
                try:
                    value = float(match.group(1))
                    nutrition[nutrient] = value
                except ValueError:
                    continue
        
        return nutrition
    
    def _extract_ingredients(self, text: str) -> List[str]:
        """Extract ingredients list from OCR text"""
        # Look for common ingredient list patterns
        ingredient_patterns = [
            r'ingredients?\s*:?\s*(.*?)(?:\n|$)',
            r'contains?\s*:?\s*(.*?)(?:\n|$)',
            r'ingredients?\s*list\s*:?\s*(.*?)(?:\n|$)'
        ]
        
        ingredients = []
        text_lower = text.lower()
        
        for pattern in ingredient_patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE | re.DOTALL)
            if match:
                ingredient_text = match.group(1)
                # Split by common separators
                ingredient_list = re.split(r'[,;]\s*', ingredient_text)
                ingredients.extend([ing.strip() for ing in ingredient_list if ing.strip()])
                break
        
        # If no pattern found, try to extract from the end of the text
        if not ingredients:
            # Look for text that might be ingredients (contains common food terms)
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                if any(word in line.lower() for word in ['water', 'sugar', 'salt', 'flour', 'oil', 'milk']):
                    if ',' in line or ';' in line:
                        ingredient_list = re.split(r'[,;]\s*', line)
                        ingredients.extend([ing.strip() for ing in ingredient_list if ing.strip()])
        
        return ingredients[:20]  # Limit to first 20 ingredients
    
    def _extract_serving_size(self, text: str) -> str:
        """Extract serving size information"""
        serving_patterns = [
            r'serving\s*size\s*:?\s*([^,\n]+)',
            r'per\s*serving\s*:?\s*([^,\n]+)',
            r'size\s*:?\s*([^,\n]+)'
        ]
        
        text_lower = text.lower()
        for pattern in serving_patterns:
            match = re.search(pattern, text_lower)
            if match:
                return match.group(1).strip()
        
        return "Unknown"
    
    def _extract_product_name(self, text: str) -> str:
        """Extract product name from OCR text"""
        # Look for text that might be the product name (usually at the beginning)
        lines = text.split('\n')
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            if len(line) > 3 and not any(word in line.lower() for word in ['nutrition', 'ingredients', 'facts', 'serving']):
                return line
        
        return "Unknown Product"
