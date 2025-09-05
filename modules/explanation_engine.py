from typing import Dict, List, Any
import random

class ExplanationEngine:
    def __init__(self):
        # Explanation templates for different score components
        self.explanation_templates = {
            'sugar_content': {
                'excellent': "Excellent! This product has very low sugar content, well within WHO recommendations.",
                'good': "Good sugar content. This product is within healthy limits for sugar intake.",
                'moderate': "Moderate sugar content. Consider this when planning your daily sugar intake.",
                'poor': "High sugar content! This exceeds WHO recommendations for daily sugar intake.",
                'very_poor': "Very high sugar content! This product contains excessive amounts of sugar."
            },
            'sodium_content': {
                'excellent': "Excellent! Very low sodium content, great for heart health.",
                'good': "Good sodium levels. This product is within healthy limits.",
                'moderate': "Moderate sodium content. Monitor your daily sodium intake.",
                'poor': "High sodium content! This exceeds WHO recommendations for daily sodium intake.",
                'very_poor': "Very high sodium content! This product contains excessive sodium."
            },
            'saturated_fat': {
                'excellent': "Excellent! Very low saturated fat content, great for cardiovascular health.",
                'good': "Good saturated fat levels. This product is within healthy limits.",
                'moderate': "Moderate saturated fat content. Consider this in your daily fat intake.",
                'poor': "High saturated fat content! This exceeds WHO recommendations.",
                'very_poor': "Very high saturated fat content! This product contains excessive saturated fat."
            },
            'trans_fat': {
                'excellent': "Excellent! No trans fats detected, which is ideal for health.",
                'good': "Good! Minimal trans fat content.",
                'moderate': "Contains some trans fats. Consider limiting consumption.",
                'poor': "High trans fat content! This is concerning for heart health.",
                'very_poor': "Very high trans fat content! This product contains dangerous levels of trans fats."
            },
            'fiber_content': {
                'excellent': "Excellent! High fiber content, great for digestive health and satiety.",
                'good': "Good fiber content. This contributes positively to your daily fiber intake.",
                'moderate': "Moderate fiber content. Every bit helps with daily fiber goals.",
                'poor': "Low fiber content. Consider adding more fiber-rich foods to your diet.",
                'very_poor': "Very low fiber content. This product provides minimal fiber benefits."
            },
            'protein_content': {
                'excellent': "Excellent! High protein content, great for muscle health and satiety.",
                'good': "Good protein content. This contributes well to your daily protein needs.",
                'moderate': "Moderate protein content. A decent source of protein.",
                'poor': "Low protein content. Consider other protein sources for your daily needs.",
                'very_poor': "Very low protein content. This product provides minimal protein."
            },
            'additives_count': {
                'excellent': "Excellent! Very few additives, indicating a more natural product.",
                'good': "Good! Minimal use of food additives.",
                'moderate': "Moderate number of additives. Generally acceptable for processed foods.",
                'poor': "High number of additives. Consider choosing products with fewer additives.",
                'very_poor': "Very high number of additives! This product contains many artificial ingredients."
            },
            'preservatives': {
                'excellent': "Excellent! No preservatives detected, indicating a fresher product.",
                'good': "Good! Minimal use of preservatives.",
                'moderate': "Contains some preservatives, which is common in packaged foods.",
                'poor': "High preservative content. Consider fresher alternatives when possible.",
                'very_poor': "Very high preservative content! This product contains many preservatives."
            },
            'artificial_colors': {
                'excellent': "Excellent! No artificial colors detected, indicating natural coloring.",
                'good': "Good! Minimal use of artificial colors.",
                'moderate': "Contains some artificial colors, which is common in processed foods.",
                'poor': "High artificial color content. Consider more natural alternatives.",
                'very_poor': "Very high artificial color content! This product contains many artificial colors."
            },
            'natural_ratio': {
                'excellent': "Excellent! High ratio of natural ingredients, indicating a wholesome product.",
                'good': "Good! Mostly natural ingredients with minimal processing.",
                'moderate': "Moderate natural ingredient ratio. A mix of natural and processed ingredients.",
                'poor': "Low natural ingredient ratio. This product is heavily processed.",
                'very_poor': "Very low natural ingredient ratio! This product is highly processed."
            },
            'artificial_sweeteners': {
                'excellent': "Excellent! No artificial sweeteners detected, using natural sweeteners only.",
                'good': "Good! Minimal use of artificial sweeteners.",
                'moderate': "Contains some artificial sweeteners, which is common in diet products.",
                'poor': "High artificial sweetener content. Consider natural sweetener alternatives.",
                'very_poor': "Very high artificial sweetener content! This product contains many artificial sweeteners."
            }
        }
        
        # Recommendations for improvement
        self.recommendations = {
            'sugar_content': [
                "Choose products with less than 10g sugar per 100g",
                "Look for products sweetened with natural ingredients",
                "Consider fresh fruits instead of sugary snacks"
            ],
            'sodium_content': [
                "Choose products with less than 400mg sodium per 100g",
                "Look for low-sodium or no-salt-added versions",
                "Season food with herbs and spices instead of salt"
            ],
            'saturated_fat': [
                "Choose products with less than 5g saturated fat per 100g",
                "Look for products with healthy fats like olive oil",
                "Consider plant-based alternatives"
            ],
            'trans_fat': [
                "Avoid products with trans fats completely",
                "Check ingredient lists for 'partially hydrogenated oils'",
                "Choose products with natural fats"
            ],
            'fiber_content': [
                "Choose whole grain products when possible",
                "Look for products with added fiber",
                "Include fresh vegetables and fruits in your diet"
            ],
            'protein_content': [
                "Choose products with at least 10g protein per 100g",
                "Look for complete protein sources",
                "Consider plant-based protein options"
            ],
            'additives_count': [
                "Choose products with fewer ingredients",
                "Look for organic or natural versions",
                "Prepare fresh foods when possible"
            ],
            'preservatives': [
                "Choose fresh or minimally processed foods",
                "Look for products with natural preservatives",
                "Check expiration dates and consume quickly"
            ],
            'artificial_colors': [
                "Choose products with natural coloring",
                "Look for organic or natural versions",
                "Avoid products with many artificial colors"
            ],
            'natural_ratio': [
                "Choose products with recognizable ingredients",
                "Look for organic or natural versions",
                "Prepare foods from scratch when possible"
            ],
            'artificial_sweeteners': [
                "Choose products with natural sweeteners",
                "Look for unsweetened versions",
                "Use natural sweeteners like honey or maple syrup"
            ]
        }
    
    def generate_explanations(self, score_result: Dict[str, Any], normalized_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive explanations for the health score"""
        try:
            explanations = {}
            score_components = score_result.get('score_components', {})
            
            # Generate explanations for each score component
            for component, score_info in score_components.items():
                explanation = self._generate_component_explanation(component, score_info, normalized_data)
                explanations[component] = explanation
            
            # Add overall summary
            explanations['overall'] = self._generate_overall_explanation(score_result, normalized_data)
            
            return explanations
            
        except Exception as e:
            return {
                'overall': {
                    'title': 'Explanation Error',
                    'explanation': f'Failed to generate explanations: {str(e)}',
                    'score_impact': 0
                }
            }
    
    def _generate_component_explanation(self, component: str, score_info: Dict[str, Any], normalized_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate explanation for a specific score component"""
        value = score_info['value']
        score_impact = score_info['score_impact']
        
        # Determine explanation level based on score impact
        if score_impact >= 15:
            level = 'excellent'
        elif score_impact >= 5:
            level = 'good'
        elif score_impact >= -5:
            level = 'moderate'
        elif score_impact >= -15:
            level = 'poor'
        else:
            level = 'very_poor'
        
        # Get explanation template
        explanation_text = self.explanation_templates.get(component, {}).get(level, 
            f"This component scored {score_impact} points based on the value {value}.")
        
        # Get recommendations
        recommendations = self.recommendations.get(component, [])
        
        # Generate title
        title = self._generate_component_title(component, score_impact)
        
        return {
            'title': title,
            'explanation': explanation_text,
            'score_impact': score_impact,
            'value': value,
            'recommendations': recommendations,
            'source': score_info.get('source', 'Unknown'),
            'level': level
        }
    
    def _generate_component_title(self, component: str, score_impact: int) -> str:
        """Generate a title for a score component"""
        titles = {
            'sugar_content': 'Sugar Content',
            'sodium_content': 'Sodium Content',
            'saturated_fat': 'Saturated Fat',
            'trans_fat': 'Trans Fat',
            'fiber_content': 'Fiber Content',
            'protein_content': 'Protein Content',
            'additives_count': 'Food Additives',
            'preservatives': 'Preservatives',
            'artificial_colors': 'Artificial Colors',
            'natural_ratio': 'Natural Ingredients',
            'artificial_sweeteners': 'Artificial Sweeteners'
        }
        
        base_title = titles.get(component, component.replace('_', ' ').title())
        
        if score_impact > 0:
            return f"✅ {base_title}"
        elif score_impact < 0:
            return f"⚠️ {base_title}"
        else:
            return f"ℹ️ {base_title}"
    
    def _generate_overall_explanation(self, score_result: Dict[str, Any], normalized_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate overall explanation for the health score"""
        score = score_result['score']
        band = score_result['band']
        
        # Generate overall explanation based on score band
        if band == 'Excellent':
            explanation = f"This product scores {score}/100, which is excellent! It meets most health guidelines and contains beneficial nutrients with minimal harmful components."
            recommendations = [
                "This is a great choice for regular consumption",
                "Consider this product as part of a balanced diet",
                "Share this healthy option with family and friends"
            ]
        elif band == 'Moderate':
            explanation = f"This product scores {score}/100, which is moderate. It has some positive aspects but also areas for improvement. Consider your overall diet when consuming this product."
            recommendations = [
                "Enjoy in moderation as part of a balanced diet",
                "Consider healthier alternatives when possible",
                "Balance with other nutritious foods"
            ]
        else:  # Poor
            explanation = f"This product scores {score}/100, which is poor. It contains several components that exceed health recommendations. Consider limiting consumption or finding healthier alternatives."
            recommendations = [
                "Limit consumption of this product",
                "Look for healthier alternatives",
                "Consider making homemade versions with better ingredients",
                "Use this product sparingly in your diet"
            ]
        
        return {
            'title': f'Overall Health Score: {score}/100 ({band})',
            'explanation': explanation,
            'score_impact': score_result.get('score_impact', 0),
            'recommendations': recommendations,
            'band': band,
            'score': score
        }
    
    def get_health_tips(self) -> List[str]:
        """Get general health tips for better food choices"""
        return [
            "Choose whole, unprocessed foods whenever possible",
            "Read nutrition labels and ingredient lists carefully",
            "Look for products with fewer ingredients",
            "Choose products with natural colors and flavors",
            "Limit foods high in sugar, sodium, and saturated fat",
            "Include plenty of fiber and protein in your diet",
            "Avoid products with trans fats",
            "Choose organic or natural versions when available",
            "Prepare meals from scratch when possible",
            "Stay hydrated with water instead of sugary drinks"
        ]
