import re
from typing import Dict, List, Any
import json

class DataNormalizer:
    def __init__(self):
        # Ingredient standardization mapping
        self.ingredient_mapping = {
            # Sugars
            'sugar': 'sugar',
            'cane sugar': 'sugar',
            'brown sugar': 'sugar',
            'white sugar': 'sugar',
            'fructose': 'sugar',
            'glucose': 'sugar',
            'sucrose': 'sugar',
            'high fructose corn syrup': 'sugar',
            'hfcs': 'sugar',
            'corn syrup': 'sugar',
            'honey': 'sugar',
            'maple syrup': 'sugar',
            'agave': 'sugar',
            'maltose': 'sugar',
            'dextrose': 'sugar',
            
            # Fats
            'palm oil': 'palm oil',
            'vegetable oil': 'vegetable oil',
            'canola oil': 'canola oil',
            'sunflower oil': 'sunflower oil',
            'coconut oil': 'coconut oil',
            'olive oil': 'olive oil',
            'butter': 'butter',
            'lard': 'lard',
            'shortening': 'shortening',
            
            # Preservatives and additives
            'sodium benzoate': 'preservative',
            'potassium sorbate': 'preservative',
            'calcium propionate': 'preservative',
            'bht': 'preservative',
            'bha': 'preservative',
            'sodium nitrite': 'preservative',
            'sodium nitrate': 'preservative',
            
            # Artificial colors
            'red 40': 'artificial color',
            'yellow 5': 'artificial color',
            'yellow 6': 'artificial color',
            'blue 1': 'artificial color',
            'blue 2': 'artificial color',
            'green 3': 'artificial color',
            'red 3': 'artificial color',
            'tartrazine': 'artificial color',
            'sunset yellow': 'artificial color',
            'allura red': 'artificial color',
            
            # Flavor enhancers
            'monosodium glutamate': 'msg',
            'msg': 'msg',
            'disodium inosinate': 'flavor enhancer',
            'disodium guanylate': 'flavor enhancer',
            
            # Sweeteners
            'aspartame': 'artificial sweetener',
            'sucralose': 'artificial sweetener',
            'saccharin': 'artificial sweetener',
            'acesulfame k': 'artificial sweetener',
            'stevia': 'natural sweetener',
            'xylitol': 'sugar alcohol',
            'sorbitol': 'sugar alcohol',
            'mannitol': 'sugar alcohol',
            
            # Natural ingredients
            'water': 'water',
            'salt': 'salt',
            'sea salt': 'salt',
            'kosher salt': 'salt',
            'flour': 'flour',
            'wheat flour': 'flour',
            'whole wheat flour': 'whole grain',
            'rice flour': 'flour',
            'corn flour': 'flour',
            'milk': 'milk',
            'whole milk': 'milk',
            'skim milk': 'milk',
            'eggs': 'eggs',
            'egg whites': 'eggs',
            'egg yolks': 'eggs'
        }
        
        # Unit conversion factors (to per 100g/ml)
        self.unit_conversions = {
            'g': 1.0,
            'gram': 1.0,
            'grams': 1.0,
            'kg': 1000.0,
            'kilogram': 1000.0,
            'mg': 0.001,
            'milligram': 0.001,
            'ml': 1.0,
            'milliliter': 1.0,
            'l': 1000.0,
            'liter': 1000.0,
            'oz': 28.35,  # ounces to grams
            'ounce': 28.35,
            'ounces': 28.35,
            'lb': 453.59,  # pounds to grams
            'pound': 453.59,
            'pounds': 453.59,
            'cup': 240.0,  # cup to ml (approximate)
            'cups': 240.0,
            'tbsp': 15.0,  # tablespoon to ml
            'tablespoon': 15.0,
            'tablespoons': 15.0,
            'tsp': 5.0,  # teaspoon to ml
            'teaspoon': 5.0,
            'teaspoons': 5.0
        }
    
    def normalize_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize raw product data into standardized format"""
        try:
            normalized = {
                'product_name': self._normalize_product_name(raw_data.get('product_name', '')),
                'barcode': raw_data.get('barcode', ''),
                'brand': raw_data.get('brand', ''),
                'categories': raw_data.get('categories', ''),
                'nutrition': self._normalize_nutrition(raw_data.get('nutrition', {})),
                'ingredients': self._normalize_ingredients(raw_data.get('ingredients', [])),
                'serving_size': self._normalize_serving_size(raw_data.get('serving_size', '')),
                'source': raw_data.get('source', 'unknown'),
                'raw_data': raw_data
            }
            
            # Calculate additional metrics
            normalized['additives'] = self._identify_additives(normalized['ingredients'])
            normalized['natural_ratio'] = self._calculate_natural_ratio(normalized['ingredients'])
            normalized['preservatives'] = self._identify_preservatives(normalized['ingredients'])
            normalized['artificial_colors'] = self._identify_artificial_colors(normalized['ingredients'])
            normalized['artificial_sweeteners'] = self._identify_artificial_sweeteners(normalized['ingredients'])
            
            return normalized
            
        except Exception as e:
            return {
                'error': f"Normalization failed: {str(e)}",
                'product_name': raw_data.get('product_name', 'Unknown Product'),
                'nutrition': {},
                'ingredients': [],
                'additives': [],
                'natural_ratio': 0.0,
                'source': 'error'
            }
    
    def _normalize_product_name(self, name: str) -> str:
        """Clean and normalize product name"""
        if not name or name == 'Unknown Product':
            return 'Unknown Product'
        
        # Remove extra whitespace and special characters
        cleaned = re.sub(r'\s+', ' ', name.strip())
        cleaned = re.sub(r'[^\w\s\-&]', '', cleaned)
        
        return cleaned
    
    def _normalize_nutrition(self, nutrition: Dict[str, float]) -> Dict[str, float]:
        """Normalize nutrition data to per 100g/ml standard"""
        normalized_nutrition = {}
        
        for nutrient, value in nutrition.items():
            if isinstance(value, (int, float)) and value >= 0:
                # Ensure values are reasonable (not too high)
                if value > 10000:  # Likely per serving, not per 100g
                    value = value / 10  # Rough conversion
                
                normalized_nutrition[nutrient] = round(float(value), 2)
        
        return normalized_nutrition
    
    def _normalize_ingredients(self, ingredients: List[str]) -> List[str]:
        """Normalize and standardize ingredient names"""
        normalized_ingredients = []
        
        for ingredient in ingredients:
            if not ingredient or len(ingredient.strip()) < 2:
                continue
            
            # Clean ingredient name
            cleaned = ingredient.strip().lower()
            cleaned = re.sub(r'[^\w\s\-]', '', cleaned)
            cleaned = re.sub(r'\s+', ' ', cleaned)
            
            # Standardize using mapping
            standardized = self.ingredient_mapping.get(cleaned, cleaned)
            
            if standardized not in normalized_ingredients:
                normalized_ingredients.append(standardized)
        
        return normalized_ingredients
    
    def _normalize_serving_size(self, serving_size: str) -> str:
        """Normalize serving size information"""
        if not serving_size or serving_size == 'Unknown':
            return 'Unknown'
        
        # Clean up serving size text
        cleaned = re.sub(r'\s+', ' ', serving_size.strip())
        return cleaned
    
    def _identify_additives(self, ingredients: List[str]) -> List[str]:
        """Identify food additives in ingredients list"""
        additives = []
        
        # E-number patterns
        e_number_pattern = r'e\d{3}[a-z]?'
        
        # Common additive keywords
        additive_keywords = [
            'preservative', 'artificial', 'synthetic', 'stabilizer', 'emulsifier',
            'thickener', 'gelling agent', 'anti-caking agent', 'flavor enhancer',
            'msg', 'monosodium glutamate', 'bht', 'bha', 'sodium benzoate',
            'potassium sorbate', 'calcium propionate', 'sodium nitrite',
            'sodium nitrate', 'tartrazine', 'sunset yellow', 'allura red',
            'aspartame', 'sucralose', 'saccharin', 'acesulfame'
        ]
        
        for ingredient in ingredients:
            ingredient_lower = ingredient.lower()
            
            # Check for E-numbers
            if re.search(e_number_pattern, ingredient_lower):
                additives.append(ingredient)
            # Check for additive keywords
            elif any(keyword in ingredient_lower for keyword in additive_keywords):
                additives.append(ingredient)
        
        return additives
    
    def _identify_preservatives(self, ingredients: List[str]) -> List[str]:
        """Identify preservatives specifically"""
        preservatives = []
        
        preservative_keywords = [
            'sodium benzoate', 'potassium sorbate', 'calcium propionate',
            'bht', 'bha', 'sodium nitrite', 'sodium nitrate',
            'sodium sulfite', 'sodium bisulfite', 'sodium metabisulfite',
            'calcium sorbate', 'sorbic acid', 'benzoic acid'
        ]
        
        for ingredient in ingredients:
            ingredient_lower = ingredient.lower()
            if any(pres in ingredient_lower for pres in preservative_keywords):
                preservatives.append(ingredient)
        
        return preservatives
    
    def _identify_artificial_colors(self, ingredients: List[str]) -> List[str]:
        """Identify artificial colors"""
        colors = []
        
        color_keywords = [
            'red 40', 'yellow 5', 'yellow 6', 'blue 1', 'blue 2',
            'green 3', 'red 3', 'tartrazine', 'sunset yellow',
            'allura red', 'brilliant blue', 'indigo carmine',
            'artificial color', 'fd&c', 'lake'
        ]
        
        for ingredient in ingredients:
            ingredient_lower = ingredient.lower()
            if any(color in ingredient_lower for color in color_keywords):
                colors.append(ingredient)
        
        return colors
    
    def _identify_artificial_sweeteners(self, ingredients: List[str]) -> List[str]:
        """Identify artificial sweeteners"""
        sweeteners = []
        
        sweetener_keywords = [
            'aspartame', 'sucralose', 'saccharin', 'acesulfame k',
            'acesulfame potassium', 'neotame', 'advantame'
        ]
        
        for ingredient in ingredients:
            ingredient_lower = ingredient.lower()
            if any(sweet in ingredient_lower for sweet in sweetener_keywords):
                sweeteners.append(ingredient)
        
        return sweeteners
    
    def _calculate_natural_ratio(self, ingredients: List[str]) -> float:
        """Calculate ratio of natural ingredients to total ingredients"""
        if not ingredients:
            return 0.0
        
        natural_keywords = [
            'water', 'salt', 'flour', 'milk', 'eggs', 'butter', 'oil',
            'sugar', 'honey', 'vanilla', 'cocoa', 'chocolate', 'fruit',
            'vegetable', 'herb', 'spice', 'natural', 'organic'
        ]
        
        natural_count = 0
        for ingredient in ingredients:
            ingredient_lower = ingredient.lower()
            if any(natural in ingredient_lower for natural in natural_keywords):
                natural_count += 1
        
        return round(natural_count / len(ingredients), 2)
