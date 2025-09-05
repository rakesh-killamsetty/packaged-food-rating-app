import requests
import json
from typing import Dict, List, Any, Optional

class BarcodeLookup:
    def __init__(self):
        self.openfoodfacts_base_url = "https://world.openfoodfacts.org/api/v0"
        self.timeout = 10
    
    def lookup_product(self, barcode: str) -> Dict[str, Any]:
        """Look up product information by barcode using OpenFoodFacts API"""
        try:
            # Clean barcode (remove non-numeric characters)
            clean_barcode = ''.join(filter(str.isdigit, barcode))
            
            if not clean_barcode:
                return self._create_error_response("Invalid barcode format")
            
            # Make API request
            url = f"{self.openfoodfacts_base_url}/product/{clean_barcode}.json"
            response = requests.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_openfoodfacts_response(data)
            else:
                return self._create_error_response(f"Product not found (HTTP {response.status_code})")
                
        except requests.exceptions.RequestException as e:
            return self._create_error_response(f"Network error: {str(e)}")
        except Exception as e:
            return self._create_error_response(f"Unexpected error: {str(e)}")
    
    def search_product(self, query: str) -> Dict[str, Any]:
        """Search for products by name using OpenFoodFacts API"""
        try:
            # Make search request
            url = f"{self.openfoodfacts_base_url}/cgi/search.pl"
            params = {
                'search_terms': query,
                'search_simple': 1,
                'action': 'process',
                'json': 1,
                'page_size': 5
            }
            
            response = requests.get(url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('products') and len(data['products']) > 0:
                    # Return the first (most relevant) product
                    return self._parse_openfoodfacts_response(data['products'][0])
                else:
                    return self._create_error_response("No products found")
            else:
                return self._create_error_response(f"Search failed (HTTP {response.status_code})")
                
        except requests.exceptions.RequestException as e:
            return self._create_error_response(f"Network error: {str(e)}")
        except Exception as e:
            return self._create_error_response(f"Unexpected error: {str(e)}")
    
    def _parse_openfoodfacts_response(self, data: Dict) -> Dict[str, Any]:
        """Parse OpenFoodFacts API response into standardized format"""
        try:
            # Extract basic product information
            product_name = data.get('product_name', 'Unknown Product')
            barcode = data.get('code', '')
            
            # Extract nutrition information
            nutrition = {}
            nutriments = data.get('nutriments', {})
            
            # Map OpenFoodFacts nutrition keys to our standard format
            nutrition_mapping = {
                'energy-kcal_100g': 'calories',
                'proteins_100g': 'protein',
                'carbohydrates_100g': 'carbs',
                'sugars_100g': 'sugar',
                'fat_100g': 'fat',
                'saturated-fat_100g': 'saturated_fat',
                'trans-fat_100g': 'trans_fat',
                'sodium_100g': 'sodium',
                'fiber_100g': 'fiber',
                'cholesterol_100g': 'cholesterol'
            }
            
            for off_key, our_key in nutrition_mapping.items():
                if off_key in nutriments:
                    nutrition[our_key] = float(nutriments[off_key])
            
            # Extract ingredients
            ingredients = []
            ingredients_text = data.get('ingredients_text', '')
            if ingredients_text:
                # Split by common separators and clean up
                ingredient_list = [ing.strip() for ing in ingredients_text.split(',')]
                ingredients = [ing for ing in ingredient_list if ing and len(ing) > 1]
            
            # Extract serving size
            serving_size = data.get('serving_size', 'Unknown')
            
            # Extract brand and category
            brand = data.get('brands', '')
            categories = data.get('categories', '')
            
            return {
                'product_name': product_name,
                'barcode': barcode,
                'brand': brand,
                'categories': categories,
                'nutrition': nutrition,
                'ingredients': ingredients,
                'serving_size': serving_size,
                'source': 'openfoodfacts',
                'raw_data': data
            }
            
        except Exception as e:
            return self._create_error_response(f"Failed to parse product data: {str(e)}")
    
    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """Create standardized error response"""
        return {
            'error': error_message,
            'product_name': 'Unknown Product',
            'barcode': '',
            'nutrition': {},
            'ingredients': [],
            'serving_size': 'Unknown',
            'source': 'error'
        }
    
    def get_product_categories(self) -> List[str]:
        """Get list of available product categories"""
        try:
            url = f"{self.openfoodfacts_base_url}/categories.json"
            response = requests.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                return [cat['name'] for cat in data.get('tags', [])]
            else:
                return []
                
        except Exception:
            return []
    
    def get_nutrition_grade_info(self, product_data: Dict) -> Dict[str, Any]:
        """Get nutrition grade information if available"""
        try:
            nutriscore = product_data.get('raw_data', {}).get('nutriscore_grade', '')
            nutrition_grades = product_data.get('raw_data', {}).get('nutrition_grades', '')
            
            return {
                'nutriscore_grade': nutriscore,
                'nutrition_grades': nutrition_grades,
                'has_grade': bool(nutriscore or nutrition_grades)
            }
        except Exception:
            return {'has_grade': False}
