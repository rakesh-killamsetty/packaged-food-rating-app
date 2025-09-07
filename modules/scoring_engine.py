from typing import Dict, List, Any, Tuple
import math

# Try to import medical LLM service, fallback gracefully if not available
try:
    from .medical_llm_service import medical_llm_service
    MEDICAL_LLM_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Medical LLM service not available: {e}")
    medical_llm_service = None
    MEDICAL_LLM_AVAILABLE = False

class HealthScoringEngine:
    def __init__(self):
        # WHO, FDA, and FSSAI guidelines for health scoring
        self.scoring_rules = {
            # Sugar content (per 100g) - WHO recommends <10% of daily energy intake
            'sugar_content': {
                'thresholds': [(5, 0), (10, -10), (15, -20), (20, -30)],
                'max_penalty': -30,
                'source': 'WHO Guidelines',
                'description': 'Sugar content per 100g'
            },
            
            # Sodium content (per 100g) - WHO recommends <2g sodium per day
            'sodium_content': {
                'thresholds': [(200, 0), (400, -10), (600, -20), (800, -30)],
                'max_penalty': -30,
                'source': 'WHO Guidelines',
                'description': 'Sodium content per 100g (mg)'
            },
            
            # Saturated fat (per 100g) - WHO recommends <10% of daily energy intake
            'saturated_fat': {
                'thresholds': [(2, 0), (5, -10), (10, -20), (15, -30)],
                'max_penalty': -30,
                'source': 'WHO Guidelines',
                'description': 'Saturated fat per 100g'
            },
            
            # Trans fat (per 100g) - Should be minimal
            'trans_fat': {
                'thresholds': [(0.5, -10), (1, -20), (2, -30)],
                'max_penalty': -30,
                'source': 'FDA Guidelines',
                'description': 'Trans fat per 100g'
            },
            
            # Fiber content (per 100g) - Positive scoring
            'fiber_content': {
                'thresholds': [(2, 5), (3, 10), (5, 15), (8, 20)],
                'max_bonus': 20,
                'source': 'WHO Guidelines',
                'description': 'Dietary fiber per 100g'
            },
            
            # Protein content (per 100g) - Positive scoring
            'protein_content': {
                'thresholds': [(5, 5), (10, 10), (15, 15), (20, 20)],
                'max_bonus': 20,
                'source': 'FSSAI Guidelines',
                'description': 'Protein per 100g'
            },
            
            # Additives count - Penalty for high number
            'additives_count': {
                'thresholds': [(3, -5), (5, -10), (8, -15), (10, -20)],
                'max_penalty': -20,
                'source': 'FSSAI Guidelines',
                'description': 'Number of food additives'
            },
            
            # Preservatives - Penalty
            'preservatives': {
                'thresholds': [(1, -5), (2, -10), (3, -15)],
                'max_penalty': -15,
                'source': 'FDA Guidelines',
                'description': 'Preservatives present'
            },
            
            # Artificial colors - Penalty
            'artificial_colors': {
                'thresholds': [(1, -5), (2, -10), (3, -15)],
                'max_penalty': -15,
                'source': 'FDA Guidelines',
                'description': 'Artificial colors present'
            },
            
            # Natural ingredients ratio - Bonus
            'natural_ratio': {
                'thresholds': [(0.3, 5), (0.5, 10), (0.7, 15), (0.9, 20)],
                'max_bonus': 20,
                'source': 'FSSAI Guidelines',
                'description': 'Ratio of natural ingredients'
            },
            
            # Artificial sweeteners - Penalty
            'artificial_sweeteners': {
                'thresholds': [(1, -8), (2, -15)],
                'max_penalty': -15,
                'source': 'FDA Guidelines',
                'description': 'Artificial sweeteners present'
            }
        }
    
    def calculate_score(self, normalized_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate health score based on normalized product data with medical LLM enhancement"""
        try:
            nutrition = normalized_data.get('nutrition', {})
            ingredients = normalized_data.get('ingredients', [])
            product_name = normalized_data.get('product_name', 'Unknown Product')
            
            # Get medical LLM analysis for enhanced scoring
            medical_analysis = self._get_medical_analysis(product_name, ingredients, nutrition)
            
            # Initialize score components
            score_components = {}
            total_score = 50  # Start with neutral score
            triggered_rules = []
            
            # Calculate nutrition-based scores
            nutrition_scores = self._calculate_nutrition_scores(nutrition)
            score_components.update(nutrition_scores)
            
            # Calculate ingredient-based scores
            ingredient_scores = self._calculate_ingredient_scores(normalized_data)
            score_components.update(ingredient_scores)
            
            # Apply medical LLM insights to scoring
            medical_scores = self._apply_medical_insights(medical_analysis, normalized_data)
            score_components.update(medical_scores)
            
            # Calculate total score
            for component, score_info in score_components.items():
                score_change = score_info['score_impact']
                total_score += score_change
                triggered_rules.append(score_info)
            
            # Ensure score is within 0-100 range
            total_score = max(0, min(100, total_score))
            
            # Determine health band
            band = self._determine_health_band(total_score)
            
            return {
                'score': round(total_score),
                'band': band,
                'score_components': score_components,
                'triggered_rules': triggered_rules,
                'max_possible_score': 100,
                'min_possible_score': 0,
                'score_impact': total_score - 50,
                'medical_analysis': medical_analysis,
                'medical_enhanced': True
            }
            
        except Exception as e:
            return {
                'score': 0,
                'band': 'Poor',
                'error': f"Scoring failed: {str(e)}",
                'score_components': {},
                'triggered_rules': [],
                'medical_enhanced': False
            }
    
    def _calculate_nutrition_scores(self, nutrition: Dict[str, float]) -> Dict[str, Any]:
        """Calculate scores based on nutrition data"""
        scores = {}
        
        # Sugar content scoring
        sugar = nutrition.get('sugar', 0)
        sugar_score = self._apply_rule('sugar_content', sugar)
        if sugar_score['score_impact'] != 0:
            scores['sugar_content'] = sugar_score
        
        # Sodium content scoring
        sodium = nutrition.get('sodium', 0)
        sodium_score = self._apply_rule('sodium_content', sodium)
        if sodium_score['score_impact'] != 0:
            scores['sodium_content'] = sodium_score
        
        # Saturated fat scoring
        saturated_fat = nutrition.get('saturated_fat', 0)
        saturated_fat_score = self._apply_rule('saturated_fat', saturated_fat)
        if saturated_fat_score['score_impact'] != 0:
            scores['saturated_fat'] = saturated_fat_score
        
        # Trans fat scoring
        trans_fat = nutrition.get('trans_fat', 0)
        trans_fat_score = self._apply_rule('trans_fat', trans_fat)
        if trans_fat_score['score_impact'] != 0:
            scores['trans_fat'] = trans_fat_score
        
        # Fiber content scoring (positive)
        fiber = nutrition.get('fiber', 0)
        fiber_score = self._apply_rule('fiber_content', fiber)
        if fiber_score['score_impact'] != 0:
            scores['fiber_content'] = fiber_score
        
        # Protein content scoring (positive)
        protein = nutrition.get('protein', 0)
        protein_score = self._apply_rule('protein_content', protein)
        if protein_score['score_impact'] != 0:
            scores['protein_content'] = protein_score
        
        return scores
    
    def _calculate_ingredient_scores(self, normalized_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate scores based on ingredient analysis"""
        scores = {}
        
        # Additives count scoring
        additives = normalized_data.get('additives', [])
        additives_count = len(additives)
        additives_score = self._apply_rule('additives_count', additives_count)
        if additives_score['score_impact'] != 0:
            scores['additives_count'] = additives_score
        
        # Preservatives scoring
        preservatives = normalized_data.get('preservatives', [])
        preservatives_count = len(preservatives)
        preservatives_score = self._apply_rule('preservatives', preservatives_count)
        if preservatives_score['score_impact'] != 0:
            scores['preservatives'] = preservatives_score
        
        # Artificial colors scoring
        artificial_colors = normalized_data.get('artificial_colors', [])
        colors_count = len(artificial_colors)
        colors_score = self._apply_rule('artificial_colors', colors_count)
        if colors_score['score_impact'] != 0:
            scores['artificial_colors'] = colors_score
        
        # Natural ratio scoring (positive)
        natural_ratio = normalized_data.get('natural_ratio', 0)
        natural_score = self._apply_rule('natural_ratio', natural_ratio)
        if natural_score['score_impact'] != 0:
            scores['natural_ratio'] = natural_score
        
        # Artificial sweeteners scoring
        artificial_sweeteners = normalized_data.get('artificial_sweeteners', [])
        sweeteners_count = len(artificial_sweeteners)
        sweeteners_score = self._apply_rule('artificial_sweeteners', sweeteners_count)
        if sweeteners_score['score_impact'] != 0:
            scores['artificial_sweeteners'] = sweeteners_score
        
        return scores
    
    def _apply_rule(self, rule_name: str, value: float) -> Dict[str, Any]:
        """Apply a specific scoring rule to a value"""
        if rule_name not in self.scoring_rules:
            return {'score_impact': 0, 'rule_name': rule_name, 'value': value}
        
        rule = self.scoring_rules[rule_name]
        thresholds = rule['thresholds']
        
        # Find the appropriate threshold
        score_impact = 0
        for threshold_value, impact in thresholds:
            if value >= threshold_value:
                score_impact = impact
            else:
                break
        
        return {
            'rule_name': rule_name,
            'value': value,
            'score_impact': score_impact,
            'description': rule['description'],
            'source': rule['source'],
            'thresholds': thresholds
        }
    
    def _determine_health_band(self, score: int) -> str:
        """Determine health band based on score"""
        if score >= 80:
            return "Excellent"
        elif score >= 60:
            return "Moderate"
        else:
            return "Poor"
    
    def get_scoring_rules(self) -> Dict[str, Any]:
        """Get all scoring rules for transparency"""
        return self.scoring_rules
    
    def explain_score_component(self, component: str, value: float) -> str:
        """Generate explanation for a specific score component"""
        if component not in self.scoring_rules:
            return f"No scoring rule found for {component}"
        
        rule = self.scoring_rules[component]
        score_info = self._apply_rule(component, value)
        
        if score_info['score_impact'] > 0:
            return f"Good {rule['description']}: {value} (bonus: +{score_info['score_impact']} points)"
        elif score_info['score_impact'] < 0:
            return f"High {rule['description']}: {value} (penalty: {score_info['score_impact']} points)"
        else:
            return f"Moderate {rule['description']}: {value} (no impact on score)"
    
    def _get_medical_analysis(self, product_name: str, ingredients: List[str], nutrition: Dict[str, float]) -> Dict[str, Any]:
        """Get medical analysis from BioMistral LLM"""
        if not MEDICAL_LLM_AVAILABLE or not medical_llm_service:
            return {'error': 'Medical LLM service not available'}
            
        try:
            # Convert nutrition values to strings for medical LLM
            nutrition_str = {}
            for key, value in nutrition.items():
                if isinstance(value, (int, float)):
                    if 'sodium' in key.lower():
                        nutrition_str[key] = f"{value}mg"
                    elif 'sugar' in key.lower() or 'fat' in key.lower() or 'protein' in key.lower() or 'fiber' in key.lower():
                        nutrition_str[key] = f"{value}g"
                    else:
                        nutrition_str[key] = f"{value}"
                else:
                    nutrition_str[key] = str(value)
            
            return medical_llm_service.analyze_food_nutrition(
                product_name=product_name,
                ingredients=ingredients,
                nutrition_facts=nutrition_str
            )
        except Exception as e:
            return {'error': f'Medical analysis failed: {str(e)}'}
    
    def _apply_medical_insights(self, medical_analysis: Dict[str, Any], normalized_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply medical LLM insights to scoring"""
        medical_scores = {}
        
        try:
            # Extract health score from medical analysis
            medical_health_score = medical_analysis.get('health_score', 75)
            
            # Calculate medical score impact (difference from baseline)
            medical_impact = (medical_health_score - 75) * 0.3  # Scale medical score impact
            
            medical_scores['medical_llm_analysis'] = {
                'rule_name': 'medical_llm_analysis',
                'value': medical_health_score,
                'score_impact': round(medical_impact),
                'description': 'Medical LLM health assessment',
                'source': 'BioMistral-7B Medical Model',
                'medical_concerns': medical_analysis.get('medical_concerns', ''),
                'clinical_recommendations': medical_analysis.get('clinical_recommendations', [])
            }
            
            # Apply medical contraindications penalty
            contraindications = medical_analysis.get('contraindications', [])
            if contraindications:
                contraindication_penalty = -len(contraindications) * 5
                medical_scores['medical_contraindications'] = {
                    'rule_name': 'medical_contraindications',
                    'value': len(contraindications),
                    'score_impact': contraindication_penalty,
                    'description': 'Medical contraindications identified',
                    'source': 'BioMistral-7B Medical Model',
                    'contraindications': contraindications
                }
            
            # Apply nutrient analysis insights
            nutrient_analysis = medical_analysis.get('nutrient_analysis', {})
            if nutrient_analysis:
                # Check for high-risk nutrients
                high_risk_penalty = 0
                for nutrient, analysis in nutrient_analysis.items():
                    if any(risk_word in analysis.lower() for risk_word in ['high', 'excess', 'risk', 'concern']):
                        high_risk_penalty -= 3
                
                if high_risk_penalty < 0:
                    medical_scores['medical_nutrient_risks'] = {
                        'rule_name': 'medical_nutrient_risks',
                        'value': abs(high_risk_penalty),
                        'score_impact': high_risk_penalty,
                        'description': 'High-risk nutrients identified by medical analysis',
                        'source': 'BioMistral-7B Medical Model',
                        'nutrient_analysis': nutrient_analysis
                    }
            
        except Exception as e:
            medical_scores['medical_analysis_error'] = {
                'rule_name': 'medical_analysis_error',
                'value': 0,
                'score_impact': 0,
                'description': f'Medical analysis error: {str(e)}',
                'source': 'BioMistral-7B Medical Model'
            }
        
        return medical_scores
