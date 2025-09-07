#!/usr/bin/env python3
"""
FastAPI Backend for FoodScore React App
Provides REST API endpoints for the medical food analysis platform
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
import sys
import json
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from datetime import datetime

# Add the modules directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

try:
    from modules.medical_nutrition_api import MedicalNutritionAPI
    from modules.llm_text_extractor import LLMTextExtractor
    from modules.normalizer import DataNormalizer
    from modules.scoring_engine import HealthScoringEngine
    from modules.explanation_engine import ExplanationEngine
    from modules.database import DatabaseManager
    from modules.medical_llm_service import medical_llm_service
    from modules.simple_medical_llm import simple_medical_llm_service
    from modules.gemini_service import gemini_medical_service
    MODULES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import modules: {e}")
    print("Running in demo mode...")
    MODULES_AVAILABLE = False

# Initialize FastAPI app
app = FastAPI(
    title="FoodScore API",
    description="Medical-grade food analysis API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
if MODULES_AVAILABLE:
    try:
        medical_api = MedicalNutritionAPI()
        llm_extractor = LLMTextExtractor()
        normalizer = DataNormalizer()
        scoring_engine = HealthScoringEngine()
        explanation_engine = ExplanationEngine()
        db_manager = DatabaseManager()
        
        # Initialize medical LLM service
        print("🩺 Initializing Medical LLM...")
        # Try simple medical LLM first
        simple_llm_loaded = simple_medical_llm_service.load_model()
        if simple_llm_loaded:
            print("✅ Simple Medical LLM loaded successfully!")
        else:
            print("⚠️ Simple Medical LLM failed, trying BioMistral...")
            medical_llm_loaded = medical_llm_service.load_model()
            if medical_llm_loaded:
                print("✅ BioMistral Medical LLM loaded successfully!")
            else:
                print("⚠️ All Medical LLMs failed, using demo mode")
        
        # Initialize Gemini service
        print("🤖 Initializing Gemini Medical Service...")
        gemini_loaded = gemini_medical_service.load_model()
        if gemini_loaded:
            print("✅ Gemini Medical Service loaded successfully!")
        else:
            print("⚠️ Gemini not available, using local LLM")
            
    except Exception as e:
        print(f"Warning: Could not initialize services: {e}")
        medical_api = None
        llm_extractor = None
        normalizer = None
        scoring_engine = None
        explanation_engine = None
        db_manager = None
else:
    print("Running in demo mode - modules not available")
    medical_api = None
    llm_extractor = None
    normalizer = None
    scoring_engine = None
    explanation_engine = None
    db_manager = None

# Pydantic models
class SearchRequest(BaseModel):
    name: str

class HealthScoreRequest(BaseModel):
    nutrition: Dict[str, float]

class ScanResult(BaseModel):
    product_name: str
    brand: str
    barcode: str
    nutrition: Dict[str, float]
    ingredients: List[str]
    serving_size: str
    source: str
    score: int
    band: str
    explanations: List[str]
    recommendations: List[str]
    evidence: List[str]

# Demo data
DEMO_PRODUCTS = {
    "5449000000996": {
        "product_name": "Coca Cola Classic",
        "brand": "The Coca-Cola Company",
        "barcode": "5449000000996",
        "nutrition": {
            "calories": 42.0,
            "protein": 0.0,
            "total_fat": 0.0,
            "saturated_fat": 0.0,
            "trans_fat": 0.0,
            "cholesterol": 0.0,
            "sodium": 1.0,
            "total_carbohydrate": 10.6,
            "dietary_fiber": 0.0,
            "total_sugars": 10.6,
            "added_sugars": 10.6,
            "calcium": 0.0,
            "iron": 0.0,
            "potassium": 0.0
        },
        "ingredients": [
            "Carbonated Water",
            "Sugar",
            "Caramel Color",
            "Phosphoric Acid",
            "Natural Flavors",
            "Caffeine"
        ],
        "serving_size": "100ml",
        "source": "Demo Data"
    },
    "3017620422003": {
        "product_name": "Nutella Hazelnut Spread",
        "brand": "Ferrero",
        "barcode": "3017620422003",
        "nutrition": {
            "calories": 546.0,
            "protein": 7.3,
            "total_fat": 30.0,
            "saturated_fat": 18.0,
            "trans_fat": 0.0,
            "cholesterol": 0.0,
            "sodium": 0.1,
            "total_carbohydrate": 59.4,
            "dietary_fiber": 3.4,
            "total_sugars": 47.0,
            "added_sugars": 47.0,
            "calcium": 0.0,
            "iron": 0.0,
            "potassium": 0.0
        },
        "ingredients": [
            "Sugar",
            "Palm Oil",
            "Hazelnuts",
            "Cocoa Powder",
            "Skimmed Milk Powder",
            "Lecithin",
            "Vanillin"
        ],
        "serving_size": "100g",
        "source": "Demo Data"
    }
}

def extract_barcode_from_image(image) -> str:
    """Extract barcode from image using computer vision"""
    try:
        import cv2
        import numpy as np
        from pyzbar import pyzbar
        
        # Convert PIL image to OpenCV format
        opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Detect barcodes
        barcodes = pyzbar.decode(opencv_image)
        
        for barcode in barcodes:
            barcode_data = barcode.data.decode('utf-8')
            barcode_type = barcode.type
            print(f"Found {barcode_type} barcode: {barcode_data}")
            return barcode_data
            
        return None
    except ImportError:
        print("⚠️ pyzbar not available, trying alternative method")
        return None
    except Exception as e:
        print(f"⚠️ Barcode extraction error: {e}")
        return None

def extract_text_from_image(image) -> str:
    """Extract text from image using OCR"""
    try:
        import easyocr
        import numpy as np
        
        # Convert PIL image to numpy array
        image_array = np.array(image)
        
        # Initialize EasyOCR reader
        reader = easyocr.Reader(['en'])
        
        # Extract text
        results = reader.readtext(image_array)
        
        # Combine all text
        full_text = ' '.join([result[1] for result in results])
        return full_text
        
    except ImportError:
        print("⚠️ EasyOCR not available, trying pytesseract")
        try:
            import pytesseract
            
            # Use pytesseract as fallback
            text = pytesseract.image_to_string(image)
            return text
        except ImportError:
            print("⚠️ OCR libraries not available")
            return ""
    except Exception as e:
        print(f"⚠️ OCR error: {e}")
        # Try pytesseract as fallback
        try:
            import pytesseract
            text = pytesseract.image_to_string(image)
            return text
        except:
            return ""

def extract_barcode_from_text(text: str) -> str:
    """Extract barcode from OCR text using regex"""
    import re
    
    # Look for barcode patterns in various formats
    patterns = [
        r'barcode\s*:?\s*(\d{12,13})',  # "Barcode: 5449000000996"
        r'\b(\d{13})\b',  # 13-digit barcodes (EAN-13)
        r'\b(\d{12})\b',  # 12-digit barcodes (UPC-A)
        r'(\d{12,13})',   # Any 12-13 digit number
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            # Return the first valid barcode found
            barcode = matches[0] if isinstance(matches[0], str) else matches[0]
            if len(barcode) >= 12:  # Valid barcode length
                return barcode
    
    return None

def extract_nutrition_from_ocr_text(text: str) -> Dict[str, float]:
    """Extract nutrition data from OCR text"""
    import re
    
    nutrition = {}
    text_lower = text.lower()
    
    # Extract energy/calories (handle both kcal and calories)
    energy_patterns = [
        r'energy\s*:?\s*(\d+(?:\.\d+)?)\s*kcal',
        r'calories?\s*:?\s*(\d+(?:\.\d+)?)',
        r'(\d+(?:\.\d+)?)\s*kcal'
    ]
    for pattern in energy_patterns:
        match = re.search(pattern, text_lower)
        if match:
            nutrition['calories'] = float(match.group(1))
            break
    
    # Extract protein
    protein_match = re.search(r'protein\s*:?\s*(\d+(?:\.\d+)?)\s*g', text_lower)
    if protein_match:
        nutrition['protein'] = float(protein_match.group(1))
    
    # Extract carbohydrates
    carb_match = re.search(r'carbohydrate\s*:?\s*(\d+(?:\.\d+)?)\s*g', text_lower)
    if carb_match:
        nutrition['total_carbohydrate'] = float(carb_match.group(1))
    
    # Extract sugar
    sugar_match = re.search(r'sugar\s*:?\s*(\d+(?:\.\d+)?)\s*g', text_lower)
    if sugar_match:
        nutrition['total_sugars'] = float(sugar_match.group(1))
    
    # Extract sodium
    sodium_match = re.search(r'sodium\s*:?\s*(\d+(?:\.\d+)?)\s*mg', text_lower)
    if sodium_match:
        nutrition['sodium'] = float(sodium_match.group(1))
    
    # Extract total fat
    total_fat_match = re.search(r'total\s*fat\s*:?\s*(\d+(?:\.\d+)?)\s*g', text_lower)
    if total_fat_match:
        nutrition['total_fat'] = float(total_fat_match.group(1))
    
    # Extract saturated fat
    sat_fat_match = re.search(r'saturated\s*fat\s*:?\s*(\d+(?:\.\d+)?)\s*g', text_lower)
    if sat_fat_match:
        nutrition['saturated_fat'] = float(sat_fat_match.group(1))
    
    # Extract polyunsaturated fat
    poly_fat_match = re.search(r'poly\s*unsaturated\s*fat\s*:?\s*(\d+(?:\.\d+)?)\s*g', text_lower)
    if poly_fat_match:
        nutrition['polyunsaturated_fat'] = float(poly_fat_match.group(1))
    
    # Extract monounsaturated fat
    mono_fat_match = re.search(r'mono\s*unsaturated\s*fat\s*:?\s*(\d+(?:\.\d+)?)\s*g', text_lower)
    if mono_fat_match:
        nutrition['monounsaturated_fat'] = float(mono_fat_match.group(1))
    
    # Extract trans fat
    trans_fat_match = re.search(r'trans\s*fat\s*:?\s*(\d+(?:\.\d+)?)\s*g', text_lower)
    if trans_fat_match:
        nutrition['trans_fat'] = float(trans_fat_match.group(1))
    
    # Extract cholesterol
    cholesterol_match = re.search(r'cholesterol\s*:?\s*(\d+(?:\.\d+)?)\s*mg', text_lower)
    if cholesterol_match:
        nutrition['cholesterol'] = float(cholesterol_match.group(1))
    
    # Extract dietary fiber
    fiber_match = re.search(r'dietary\s*fiber\s*:?\s*(\d+(?:\.\d+)?)\s*g', text_lower)
    if fiber_match:
        nutrition['dietary_fiber'] = float(fiber_match.group(1))
    
    # Extract vitamins
    vit_a_match = re.search(r'vitamin\s*a\s*:?\s*(\d+(?:\.\d+)?)\s*mcg', text_lower)
    if vit_a_match:
        nutrition['vitamin_a'] = float(vit_a_match.group(1))
    
    vit_d_match = re.search(r'vitamin\s*d\s*:?\s*(\d+(?:\.\d+)?)\s*mcg', text_lower)
    if vit_d_match:
        nutrition['vitamin_d'] = float(vit_d_match.group(1))
    
    return nutrition

def extract_product_name_from_text(text: str) -> str:
    """Extract product name from OCR text"""
    import re
    
    # Look for common product name patterns
    patterns = [
        r'([A-Z][A-Z\s]+(?:OIL|BREAD|COLA|COKE|NUTELLA|MILK|YOGURT|CHEESE|BUTTER|FLOUR|RICE|PASTA|SNACKS?|COOKIES?|CRACKERS?|CEREAL|JUICE|DRINK|WATER|TEA|COFFEE|SUGAR|SALT|SPICE|SAUCE|KETCHUP|MAYO|MUSTARD|VINEGAR|HONEY|JAM|JELLY|SYRUP|CHOCOLATE|CANDY|GUM|CHIPS?|NUTS?|SEEDS?|BEANS?|LENTILS?|GRAINS?|FLOUR|PASTA|NOODLES?|SOUP|STOCK|BROTH|POWDER|MIX|BLEND|SPREAD|DIP|DRESSING|MARINADE|RUB|SEASONING|HERBS?|SPICES?|EXTRACT|ESSENCE|FLAVOR|FLAVOUR))',
        r'([A-Z][A-Z\s]+(?:REFINED|VIRGIN|EXTRA|PURE|ORGANIC|NATURAL|FRESH|FROZEN|DRIED|DEHYDRATED|CONCENTRATED|PASTEURIZED|HOMOGENIZED|FORTIFIED|ENRICHED|LIGHT|LITE|DIET|SUGAR-FREE|FAT-FREE|LOW-FAT|LOW-SODIUM|GLUTEN-FREE|DAIRY-FREE|VEGAN|VEGETARIAN|KOSHER|HALAL))',
        r'([A-Z][A-Z\s]+(?:SUNFLOWER|OLIVE|COCONUT|PALM|CANOLA|SOYBEAN|CORN|PEANUT|SESAME|WALNUT|ALMOND|HAZELNUT|PISTACHIO|CASHEW|MACADAMIA|PECAN|BRAZIL|PINE|CHIA|FLAX|HEMP|AVOCADO|GRAPESEED|SAFFLOWER|RICE|BRAN|WHEAT|GERM|FLAXSEED|SESAME|PUMPKIN|SUNFLOWER))',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        if matches:
            # Return the longest match (most likely to be the product name)
            return max(matches, key=len).strip()
    
    # If no pattern matches, try to find words in ALL CAPS
    all_caps_words = re.findall(r'\b[A-Z]{2,}\b', text)
    if all_caps_words:
        # Filter out common non-product words
        filtered_words = [word for word in all_caps_words if word not in ['NUTRITION', 'FACTS', 'INGREDIENTS', 'SERVING', 'SIZE', 'CALORIES', 'ENERGY', 'PROTEIN', 'CARBOHYDRATE', 'FAT', 'SODIUM', 'SUGAR', 'FIBER', 'VITAMIN', 'MINERAL', 'BATCH', 'MADE', 'PACKED', 'BEST', 'BEFORE', 'MADE', 'IN', 'USA', 'INDIA', 'CHINA', 'ITALY', 'FRANCE', 'GERMANY', 'SPAIN', 'MEXICO', 'CANADA', 'AUSTRALIA', 'BRAZIL', 'JAPAN', 'KOREA', 'THAILAND', 'MALAYSIA', 'SINGAPORE', 'HONG', 'KONG', 'TAIWAN', 'PHILIPPINES', 'INDONESIA', 'VIETNAM', 'BANGLADESH', 'PAKISTAN', 'SRI', 'LANKA', 'NEPAL', 'BHUTAN', 'MYANMAR', 'CAMBODIA', 'LAOS', 'BRUNEI', 'TIMOR', 'LESTE', 'MALDIVES', 'AFGHANISTAN', 'IRAN', 'IRAQ', 'ISRAEL', 'JORDAN', 'LEBANON', 'SYRIA', 'TURKEY', 'EGYPT', 'LIBYA', 'TUNISIA', 'ALGERIA', 'MOROCCO', 'SUDAN', 'ETHIOPIA', 'KENYA', 'UGANDA', 'TANZANIA', 'SOUTH', 'AFRICA', 'NIGERIA', 'GHANA', 'SENEGAL', 'MALI', 'BURKINA', 'FASO', 'NIGER', 'CHAD', 'CAMEROON', 'GABON', 'CONGO', 'ANGOLA', 'ZAMBIA', 'ZIMBABWE', 'BOTSWANA', 'NAMIBIA', 'LESOTHO', 'SWAZILAND', 'MADAGASCAR', 'MAURITIUS', 'SEYCHELLES', 'COMOROS', 'DJIBOUTI', 'SOMALIA', 'ERITREA', 'BURUNDI', 'RWANDA', 'CENTRAL', 'AFRICAN', 'REPUBLIC', 'DEMOCRATIC', 'REPUBLIC', 'OF', 'THE', 'CONGO', 'EQUATORIAL', 'GUINEA', 'SAO', 'TOME', 'AND', 'PRINCIPE', 'CAPE', 'VERDE', 'GUINEA-BISSAU', 'SIERRA', 'LEONE', 'LIBERIA', 'IVORY', 'COAST', 'TOGO', 'BENIN', 'GAMBIA', 'GUINEA', 'BISSAU', 'SENEGAL', 'MAURITANIA', 'MOROCCO', 'ALGERIA', 'TUNISIA', 'LIBYA', 'EGYPT', 'SUDAN', 'ETHIOPIA', 'ERITREA', 'DJIBOUTI', 'SOMALIA', 'KENYA', 'UGANDA', 'TANZANIA', 'RWANDA', 'BURUNDI', 'DEMOCRATIC', 'REPUBLIC', 'OF', 'THE', 'CONGO', 'CENTRAL', 'AFRICAN', 'REPUBLIC', 'CHAD', 'CAMEROON', 'EQUATORIAL', 'GUINEA', 'GABON', 'SAO', 'TOME', 'AND', 'PRINCIPE', 'ANGOLA', 'ZAMBIA', 'MALAWI', 'MADAGASCAR', 'MAURITIUS', 'SEYCHELLES', 'COMOROS', 'MAYOTTE', 'REUNION', 'ZIMBABWE', 'BOTSWANA', 'NAMIBIA', 'SOUTH', 'AFRICA', 'LESOTHO', 'SWAZILAND', 'MADAGASCAR', 'MAURITIUS', 'SEYCHELLES', 'COMOROS', 'MAYOTTE', 'REUNION']]
        if filtered_words:
            return ' '.join(filtered_words[:3])  # Take first 3 words
    
    return "Product Detected from Image"

def match_product_by_name(text: str) -> Dict[str, Any]:
    """Match product by name in OCR text and extract nutrition data"""
    text_lower = text.lower()
    
    # Extract product name from OCR text
    product_name = extract_product_name_from_text(text)
    
    # Extract nutrition data from OCR text
    nutrition_data = extract_nutrition_from_ocr_text(text)
    
    # Check for known products and create result with OCR data
    if "coca" in text_lower or "cola" in text_lower:
        # Use OCR data if available, otherwise use demo data
        base_product = DEMO_PRODUCTS["5449000000996"].copy()
        if nutrition_data:
            base_product["nutrition"].update(nutrition_data)
            base_product["extracted_text"] = text
        return base_product
        
    elif "nutella" in text_lower:
        base_product = DEMO_PRODUCTS["3017620422003"].copy()
        if nutrition_data:
            base_product["nutrition"].update(nutrition_data)
            base_product["extracted_text"] = text
        return base_product
        
    elif "bread" in text_lower or "whole grain" in text_lower:
        base_product = {
            "product_name": "Whole Grain Bread",
            "brand": "Detected from Image",
            "barcode": "",
            "nutrition": {
                "calories": 247.0,
                "protein": 13.4,
                "total_fat": 4.2,
                "saturated_fat": 0.9,
                "trans_fat": 0.0,
                "cholesterol": 0.0,
                "sodium": 681.0,
                "total_carbohydrate": 41.0,
                "dietary_fiber": 7.0,
                "total_sugars": 5.0,
                "added_sugars": 2.0,
                "calcium": 100.0,
                "iron": 2.5,
                "potassium": 200.0
            },
            "ingredients": [
                "Whole Wheat Flour",
                "Water",
                "Yeast",
                "Salt",
                "Sugar",
                "Vegetable Oil"
            ],
            "serving_size": "100g",
            "source": "OCR Detection"
        }
        if nutrition_data:
            base_product["nutrition"].update(nutrition_data)
            base_product["extracted_text"] = text
        return base_product
    
    # For any other product, create a result with extracted product name and nutrition data
    if nutrition_data or product_name != "Product Detected from Image":
        return {
            "product_name": product_name,
            "brand": "Detected from Image",
            "barcode": "",
            "nutrition": nutrition_data if nutrition_data else {
                "calories": 0.0,
                "protein": 0.0,
                "total_fat": 0.0,
                "saturated_fat": 0.0,
                "trans_fat": 0.0,
                "cholesterol": 0.0,
                "sodium": 0.0,
                "total_carbohydrate": 0.0,
                "dietary_fiber": 0.0,
                "total_sugars": 0.0,
                "added_sugars": 0.0,
                "calcium": 0.0,
                "iron": 0.0,
                "potassium": 0.0
            },
            "ingredients": ["Ingredients not fully extracted"],
            "serving_size": "100g",
            "source": "OCR Detection",
            "extracted_text": text
        }
    
    return None

def create_generic_result_from_image(image) -> Dict[str, Any]:
    """Create a generic result when no specific product is detected"""
    return {
        "product_name": "Unknown Product (Image Analysis)",
        "brand": "Detected from Image",
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
        "ingredients": [
            "Water",
            "Wheat Flour",
            "Sugar",
            "Vegetable Oil",
            "Salt",
            "Yeast",
            "Natural Flavors"
        ],
        "serving_size": "100g",
        "source": "Image Analysis Fallback"
    }

def create_llm_analysis_result(product_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a result using LLM medical analysis"""
    try:
        print(f"🔍 Creating LLM analysis for: {product_data.get('product_name', 'Unknown')}")
        print(f"🔍 MODULES_AVAILABLE: {MODULES_AVAILABLE}")
        print(f"🔍 LLM loaded: {simple_medical_llm_service.is_loaded if MODULES_AVAILABLE else 'N/A'}")
        
        # Use LLM for medical analysis if available
        if MODULES_AVAILABLE and simple_medical_llm_service.is_loaded:
            print("🧠 Using Medical LLM for analysis...")
            medical_analysis = simple_medical_llm_service.analyze_food_nutrition(
                product_name=product_data["product_name"],
                ingredients=product_data["ingredients"],
                nutrition_facts=product_data["nutrition"],
                barcode=product_data.get("barcode")
            )
            print(f"🧠 LLM analysis result: {medical_analysis.get('analysis_source', 'Unknown')}")
            
            return {
                "product_name": product_data["product_name"],
                "brand": product_data["brand"],
                "barcode": product_data["barcode"],
                "nutrition": product_data["nutrition"],
                "ingredients": product_data["ingredients"],
                "serving_size": product_data["serving_size"],
                "score": medical_analysis.get("medical_health_score", 70),
                "explanation": f"Medical-grade analysis: {medical_analysis.get('raw_analysis', 'Analysis completed')}",
                "recommendations": medical_analysis.get("medical_recommendations", [
                    "Consult with healthcare provider for personalized advice",
                    "Consider portion control for optimal health",
                    "Balance with other nutritious foods"
                ]),
                "medical_concerns": medical_analysis.get("key_concerns", []),
                "nutrient_risks": medical_analysis.get("nutrient_risks", []),
                "contraindications": medical_analysis.get("contraindications", []),
                "source": medical_analysis.get("analysis_source", "Medical LLM Analysis"),
                "timestamp": medical_analysis.get("analysis_timestamp", datetime.now().isoformat())
            }
        else:
            # Fallback to basic analysis
            return create_demo_result(product_data)
    except Exception as e:
        print(f"⚠️ LLM analysis failed: {e}")
        return create_demo_result(product_data)

def create_demo_result(product_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a complete demo result with scoring"""
    # Calculate health score (simplified)
    nutrition = product_data["nutrition"]
    sugar = nutrition.get("total_sugars", 0)
    sodium = nutrition.get("sodium", 0)
    saturated_fat = nutrition.get("saturated_fat", 0)
    fiber = nutrition.get("dietary_fiber", 0)
    
    # Simple scoring algorithm
    score = 100
    if sugar > 15:
        score -= 30
    elif sugar > 10:
        score -= 20
    elif sugar > 5:
        score -= 10
    
    if sodium > 400:
        score -= 25
    elif sodium > 200:
        score -= 15
    
    if saturated_fat > 5:
        score -= 20
    elif saturated_fat > 2:
        score -= 10
    
    if fiber < 3:
        score -= 15
    elif fiber < 1:
        score -= 25
    
    score = max(0, min(100, score))
    
    # Determine band
    if score >= 80:
        band = "Excellent"
    elif score >= 60:
        band = "Good"
    elif score >= 40:
        band = "Moderate"
    else:
        band = "Poor"
    
    # Generate explanations and recommendations
    explanations = []
    recommendations = []
    evidence = ["WHO Guidelines", "FDA Nutrition Facts", "Medical Research"]
    
    if sugar > 10:
        explanations.append(f"High sugar content ({sugar}g per 100g) exceeds WHO recommendations")
        recommendations.append("Consider low-sugar alternatives")
    
    if sodium > 200:
        explanations.append(f"High sodium content ({sodium}mg per 100g) may affect blood pressure")
        recommendations.append("Limit sodium intake for heart health")
    
    if saturated_fat > 5:
        explanations.append(f"High saturated fat ({saturated_fat}g per 100g) may increase heart disease risk")
        recommendations.append("Choose products with less saturated fat")
    
    if fiber < 3:
        explanations.append(f"Low fiber content ({fiber}g per 100g) - fiber supports digestive health")
        recommendations.append("Include more fiber-rich foods in your diet")
    
    return {
        **product_data,
        "score": score,
        "band": band,
        "explanations": explanations,
        "recommendations": recommendations,
        "evidence": evidence
    }

@app.get("/")
async def root():
    return {"message": "FoodScore API is running!", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    llm_status = False
    llm_model = "Demo Mode"
    
    if MODULES_AVAILABLE:
        if simple_medical_llm_service.is_loaded:
            llm_status = True
            llm_model = f"Simple Medical LLM ({simple_medical_llm_service.model_name})"
        elif medical_llm_service.is_loaded:
            llm_status = True
            llm_model = f"BioMistral ({medical_llm_service.model_name})"
    
    return {"status": "healthy", "services": {
        "medical_api": medical_api is not None,
        "llm_extractor": llm_extractor is not None,
        "normalizer": normalizer is not None,
        "scoring_engine": scoring_engine is not None,
        "explanation_engine": explanation_engine is not None,
        "database": db_manager is not None,
        "medical_llm": llm_status,
        "medical_llm_model": llm_model
    }}

@app.post("/analyze-image-gemini")
async def analyze_image_gemini(image: UploadFile = File(...)):
    """Analyze uploaded food image using Gemini API for medical-grade analysis"""
    try:
        # Read the uploaded image
        image_data = await image.read()
        
        if MODULES_AVAILABLE and gemini_medical_service.is_loaded:
            print("🤖 Using Gemini for medical analysis...")
            analysis = gemini_medical_service.analyze_food_image(image_data)
            
            # Convert to expected format
            result = {
                "product_name": analysis.get("product_name", "Unknown Product"),
                "brand": analysis.get("brand", "Unknown Brand"),
                "barcode": analysis.get("barcode", ""),
                "nutrition": analysis.get("nutrition", {}),
                "ingredients": analysis.get("ingredients", []),
                "serving_size": analysis.get("serving_size", "100g"),
                "score": analysis.get("medical_health_score", 70),
                "band": "Excellent" if analysis.get("medical_health_score", 70) >= 80 else 
                       "Good" if analysis.get("medical_health_score", 70) >= 60 else
                       "Moderate" if analysis.get("medical_health_score", 70) >= 40 else "Poor",
                "explanations": analysis.get("key_concerns", []),
                "recommendations": analysis.get("medical_recommendations", []),
                "evidence": ["WHO Guidelines", "FDA Recommendations", "Medical Research"],
                "source": analysis.get("analysis_source", "Gemini Medical Analysis"),
                "timestamp": analysis.get("analysis_timestamp", datetime.now().isoformat()),
                "analysis_method": "gemini_medical_analysis",
                "medical_concerns": analysis.get("key_concerns", []),
                "nutrient_risks": analysis.get("nutrient_risks", []),
                "contraindications": analysis.get("contraindications", [])
            }
            
            return JSONResponse(content=result)
        else:
            # Fallback to regular analysis
            return await analyze_image(image)
            
    except Exception as e:
        print(f"❌ Gemini analysis failed: {e}")
        return JSONResponse(
            content={"error": f"Analysis failed: {str(e)}"},
            status_code=500
        )

@app.post("/analyze-image")
async def analyze_image(image: UploadFile = File(...)):
    """Analyze uploaded food image with OCR and barcode detection"""
    try:
        # Read the uploaded image
        image_data = await image.read()
        
        # Convert to PIL Image
        from PIL import Image
        import io
        pil_image = Image.open(io.BytesIO(image_data))
        
        # Try to extract barcode first
        barcode = None
        try:
            barcode = extract_barcode_from_image(pil_image)
            if barcode:
                print(f"🔍 Barcode detected: {barcode}")
                # Search for product by barcode
                if barcode in DEMO_PRODUCTS:
                    product_data = DEMO_PRODUCTS[barcode]
                    result = create_llm_analysis_result(product_data)
                    result["detected_barcode"] = barcode
                    result["analysis_method"] = "barcode_detection"
                    return JSONResponse(content=result)
        except Exception as e:
            print(f"⚠️ Barcode detection failed: {e}")
        
        # If no barcode found, try OCR
        try:
            ocr_result = extract_text_from_image(pil_image)
            print(f"📝 OCR extracted text: {ocr_result[:200]}...")
            
            # Try to find barcode in OCR text
            barcode_from_ocr = extract_barcode_from_text(ocr_result)
            if barcode_from_ocr:
                print(f"🔍 Barcode found in OCR text: {barcode_from_ocr}")
                if barcode_from_ocr in DEMO_PRODUCTS:
                    product_data = DEMO_PRODUCTS[barcode_from_ocr]
                    result = create_llm_analysis_result(product_data)
                    result["detected_barcode"] = barcode_from_ocr
                    result["analysis_method"] = "ocr_barcode_detection"
                    return JSONResponse(content=result)
                else:
                    # Barcode found but not in demo products, still use it
                    print(f"⚠️ Barcode {barcode_from_ocr} not in demo products, using OCR analysis")
            
            # Try to match product by name in OCR text
            product_match = match_product_by_name(ocr_result)
            if product_match:
                print(f"🔍 Product match found: {product_match.get('product_name', 'Unknown')}")
                print(f"🔍 Product source: {product_match.get('source', 'Unknown')}")
                result = create_llm_analysis_result(product_match)
                print(f"🔍 Final result source: {result.get('source', 'Unknown')}")
                result["analysis_method"] = "ocr_name_matching"
                result["extracted_text"] = ocr_result
                # Include detected barcode if found
                if barcode_from_ocr:
                    result["detected_barcode"] = barcode_from_ocr
                return JSONResponse(content=result)
                
        except Exception as e:
            print(f"⚠️ OCR failed: {e}")
        
        # If all else fails, return a generic result based on image analysis
        generic_result = create_generic_result_from_image(pil_image)
        generic_result["analysis_method"] = "image_analysis_fallback"
        return JSONResponse(content=generic_result)
        
    except Exception as e:
        print(f"❌ Image analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Image analysis failed: {str(e)}")

@app.get("/search-barcode/{barcode}")
async def search_by_barcode(barcode: str):
    """Search for product by barcode"""
    try:
        if barcode in DEMO_PRODUCTS:
            product_data = DEMO_PRODUCTS[barcode]
            result = create_demo_result(product_data)
            return JSONResponse(content=result)
        else:
            # Return a generic demo product
            generic_product = {
                "product_name": f"Product {barcode}",
                "brand": "Unknown Brand",
                "barcode": barcode,
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
                "ingredients": [
                    "Water",
                    "Wheat Flour",
                    "Sugar",
                    "Vegetable Oil",
                    "Salt",
                    "Yeast",
                    "Natural Flavors"
                ],
                "serving_size": "100g",
                "source": "Demo Data"
            }
            result = create_demo_result(generic_product)
            return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Barcode search failed: {str(e)}")

@app.post("/search-name")
async def search_by_name(request: SearchRequest):
    """Search for product by name"""
    try:
        name_lower = request.name.lower()
        
        # Check for known products
        if "coca" in name_lower or "cola" in name_lower:
            product_data = DEMO_PRODUCTS["5449000000996"]
        elif "nutella" in name_lower:
            product_data = DEMO_PRODUCTS["3017620422003"]
        elif "bread" in name_lower:
            product_data = {
                "product_name": f"Whole Grain Bread - {request.name}",
                "brand": "Demo Brand",
                "barcode": "",
                "nutrition": {
                    "calories": 247.0,
                    "protein": 13.4,
                    "total_fat": 4.2,
                    "saturated_fat": 0.9,
                    "trans_fat": 0.0,
                    "cholesterol": 0.0,
                    "sodium": 681.0,
                    "total_carbohydrate": 41.0,
                    "dietary_fiber": 7.0,
                    "total_sugars": 5.0,
                    "added_sugars": 2.0,
                    "calcium": 100.0,
                    "iron": 2.5,
                    "potassium": 200.0
                },
                "ingredients": [
                    "Whole Wheat Flour",
                    "Water",
                    "Yeast",
                    "Salt",
                    "Sugar",
                    "Vegetable Oil",
                    "Preservative"
                ],
                "serving_size": "100g",
                "source": "Demo Data"
            }
        else:
            # Generic product
            product_data = {
                "product_name": f"Demo Product - {request.name}",
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
                "ingredients": [
                    "Water",
                    "Wheat Flour",
                    "Sugar",
                    "Vegetable Oil",
                    "Salt",
                    "Yeast",
                    "Natural Flavors"
                ],
                "serving_size": "100g",
                "source": "Demo Data"
            }
        
        result = create_demo_result(product_data)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Name search failed: {str(e)}")

@app.post("/health-score")
async def get_health_score(request: HealthScoreRequest):
    """Calculate health score for nutrition data"""
    try:
        nutrition = request.nutrition
        sugar = nutrition.get("total_sugars", 0)
        sodium = nutrition.get("sodium", 0)
        saturated_fat = nutrition.get("saturated_fat", 0)
        fiber = nutrition.get("dietary_fiber", 0)
        
        # Calculate score
        score = 100
        if sugar > 15:
            score -= 30
        elif sugar > 10:
            score -= 20
        elif sugar > 5:
            score -= 10
        
        if sodium > 400:
            score -= 25
        elif sodium > 200:
            score -= 15
        
        if saturated_fat > 5:
            score -= 20
        elif saturated_fat > 2:
            score -= 10
        
        if fiber < 3:
            score -= 15
        elif fiber < 1:
            score -= 25
        
        score = max(0, min(100, score))
        
        # Determine band
        if score >= 80:
            band = "Excellent"
        elif score >= 60:
            band = "Good"
        elif score >= 40:
            band = "Moderate"
        else:
            band = "Poor"
        
        # Generate explanations and recommendations
        explanations = []
        recommendations = []
        
        if sugar > 10:
            explanations.append(f"High sugar content ({sugar}g per 100g) exceeds WHO recommendations")
            recommendations.append("Consider low-sugar alternatives")
        
        if sodium > 200:
            explanations.append(f"High sodium content ({sodium}mg per 100g) may affect blood pressure")
            recommendations.append("Limit sodium intake for heart health")
        
        if saturated_fat > 5:
            explanations.append(f"High saturated fat ({saturated_fat}g per 100g) may increase heart disease risk")
            recommendations.append("Choose products with less saturated fat")
        
        if fiber < 3:
            explanations.append(f"Low fiber content ({fiber}g per 100g) - fiber supports digestive health")
            recommendations.append("Include more fiber-rich foods in your diet")
        
        return JSONResponse(content={
            "score": score,
            "band": band,
            "explanations": explanations,
            "recommendations": recommendations
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health score calculation failed: {str(e)}")

@app.get("/history")
async def get_history():
    """Get scan history"""
    try:
        # Return empty history for demo
        return JSONResponse(content=[])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")

@app.post("/save-result")
async def save_scan_result(result: ScanResult):
    """Save scan result to history"""
    try:
        # In production, this would save to database
        return JSONResponse(content={"message": "Result saved successfully"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save result: {str(e)}")

@app.get("/guidelines")
async def get_guidelines():
    """Get nutrition guidelines"""
    try:
        return JSONResponse(content={
            "sugar": {"max": 10, "unit": "g per 100g"},
            "sodium": {"max": 400, "unit": "mg per 100g"},
            "saturated_fat": {"max": 5, "unit": "g per 100g"},
            "fiber": {"min": 3, "unit": "g per 100g"}
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get guidelines: {str(e)}")

@app.post("/medical-analysis")
async def get_medical_analysis(request: dict):
    """Get medical-grade analysis using BioMistral LLM"""
    try:
        product_name = request.get("product_name", "Unknown Product")
        ingredients = request.get("ingredients", [])
        nutrition_facts = request.get("nutrition_facts", {})
        barcode = request.get("barcode", None)
        
        # Use medical LLM for analysis
        if 'medical_llm_service' in globals() and medical_llm_service.is_loaded:
            analysis = medical_llm_service.analyze_food_nutrition(
                product_name=product_name,
                ingredients=ingredients,
                nutrition_facts=nutrition_facts,
                barcode=barcode
            )
        else:
            # Fallback to demo analysis
            analysis = {
                "health_score": 75,
                "medical_concerns": "Demo mode - medical LLM not available",
                "nutrient_analysis": {},
                "clinical_recommendations": ["Consult healthcare provider for medical advice"],
                "contraindications": [],
                "evidence_sources": ["Demo Mode"],
                "model_used": "Demo Mode (BioMistral-7B not available)",
                "timestamp": "2024-01-01T00:00:00Z"
            }
        
        return JSONResponse(content=analysis)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Medical analysis failed: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting FoodScore API Server...")
    print("📡 API will be available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔗 CORS enabled for: http://localhost:3000, http://localhost:5173")
    
    uvicorn.run(
        "backend_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
