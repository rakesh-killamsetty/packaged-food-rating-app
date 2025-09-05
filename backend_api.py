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

# Add the modules directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

try:
    from modules.medical_nutrition_api import MedicalNutritionAPI
    from modules.llm_text_extractor import LLMTextExtractor
    from modules.normalizer import DataNormalizer
    from modules.scoring_engine import HealthScoringEngine
    from modules.explanation_engine import ExplanationEngine
    from modules.database import DatabaseManager
except ImportError as e:
    print(f"Warning: Could not import modules: {e}")
    print("Running in demo mode...")

# Initialize FastAPI app
app = FastAPI(
    title="FoodScore API",
    description="Medical-grade food analysis API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
try:
    medical_api = MedicalNutritionAPI()
    llm_extractor = LLMTextExtractor()
    normalizer = DataNormalizer()
    scoring_engine = HealthScoringEngine()
    explanation_engine = ExplanationEngine()
    db_manager = DatabaseManager()
except Exception as e:
    print(f"Warning: Could not initialize services: {e}")
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
    return {"status": "healthy", "services": {
        "medical_api": medical_api is not None,
        "llm_extractor": llm_extractor is not None,
        "normalizer": normalizer is not None,
        "scoring_engine": scoring_engine is not None,
        "explanation_engine": explanation_engine is not None,
        "database": db_manager is not None
    }}

@app.post("/analyze-image")
async def analyze_image(image: UploadFile = File(...)):
    """Analyze uploaded food image"""
    try:
        # For demo purposes, return a mock result
        # In production, this would use the actual image analysis
        demo_product = DEMO_PRODUCTS["5449000000996"]
        result = create_demo_result(demo_product)
        
        return JSONResponse(content=result)
    except Exception as e:
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

if __name__ == "__main__":
    print("🚀 Starting FoodScore API Server...")
    print("📡 API will be available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔗 CORS enabled for: http://localhost:3000")
    
    uvicorn.run(
        "backend_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
