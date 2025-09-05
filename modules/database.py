import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Any

class DatabaseManager:
    def __init__(self, db_path: str = "food_rating.db"):
        self.db_path = db_path
    
    def initialize_database(self):
        """Initialize the SQLite database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create analysis history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL,
                barcode TEXT,
                raw_data TEXT,
                normalized_data TEXT,
                score INTEGER,
                band TEXT,
                score_impact INTEGER,
                explanations TEXT,
                ingredients_count INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create scoring rules table for audit trail
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scoring_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rule_name TEXT NOT NULL,
                rule_description TEXT,
                threshold_value REAL,
                score_impact INTEGER,
                source TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert default scoring rules
        self._insert_default_rules(cursor)
        
        conn.commit()
        conn.close()
    
    def _insert_default_rules(self, cursor):
        """Insert default scoring rules based on WHO, FDA, FSSAI guidelines"""
        rules = [
            ("sugar_content", "Sugar content per 100g", 10.0, -20, "WHO Guidelines"),
            ("sodium_content", "Sodium content per 100g", 400.0, -15, "WHO Guidelines"),
            ("saturated_fat", "Saturated fat per 100g", 5.0, -10, "WHO Guidelines"),
            ("trans_fat", "Trans fat per 100g", 1.0, -25, "FDA Guidelines"),
            ("fiber_content", "Fiber content per 100g", 3.0, 15, "WHO Guidelines"),
            ("protein_content", "Protein content per 100g", 10.0, 10, "FSSAI Guidelines"),
            ("additives_count", "Number of additives", 5.0, -5, "FSSAI Guidelines"),
            ("preservatives", "Preservatives present", 1.0, -10, "FDA Guidelines"),
            ("artificial_colors", "Artificial colors present", 1.0, -8, "FDA Guidelines"),
            ("natural_ingredients", "Natural ingredients ratio", 0.7, 20, "FSSAI Guidelines")
        ]
        
        cursor.execute('SELECT COUNT(*) FROM scoring_rules')
        if cursor.fetchone()[0] == 0:
            cursor.executemany('''
                INSERT INTO scoring_rules (rule_name, rule_description, threshold_value, score_impact, source)
                VALUES (?, ?, ?, ?, ?)
            ''', rules)
    
    def save_analysis(self, raw_data: Dict, normalized_data: Dict, score_result: Dict, explanations: Dict):
        """Save analysis results to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Extract product name
        product_name = raw_data.get('product_name', 'Unknown Product')
        barcode = raw_data.get('barcode', '')
        
        # Count ingredients
        ingredients_count = len(normalized_data.get('ingredients', []))
        
        cursor.execute('''
            INSERT INTO analysis_history 
            (product_name, barcode, raw_data, normalized_data, score, band, score_impact, explanations, ingredients_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            product_name,
            barcode,
            json.dumps(raw_data),
            json.dumps(normalized_data),
            score_result['score'],
            score_result['band'],
            score_result.get('score_impact', 0),
            json.dumps(explanations),
            ingredients_count
        ))
        
        conn.commit()
        conn.close()
    
    def get_analysis_history(self, limit: int = 50) -> List[Dict]:
        """Retrieve analysis history from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT product_name, barcode, score, band, score_impact, ingredients_count, timestamp
            FROM analysis_history
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'product_name': row[0],
                'barcode': row[1],
                'score': row[2],
                'band': row[3],
                'score_impact': row[4],
                'ingredients_count': row[5],
                'timestamp': row[6]
            })
        
        conn.close()
        return results
    
    def get_scoring_rules(self) -> List[Dict]:
        """Get all scoring rules for transparency"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT rule_name, rule_description, threshold_value, score_impact, source
            FROM scoring_rules
            ORDER BY rule_name
        ''')
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'rule_name': row[0],
                'rule_description': row[1],
                'threshold_value': row[2],
                'score_impact': row[3],
                'source': row[4]
            })
        
        conn.close()
        return results
