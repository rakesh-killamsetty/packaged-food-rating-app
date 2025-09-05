// API service for connecting to Python backend
const API_BASE_URL = 'http://localhost:8501/api';

export interface NutritionData {
  calories: number;
  protein: number;
  total_fat: number;
  saturated_fat: number;
  trans_fat: number;
  cholesterol: number;
  sodium: number;
  total_carbohydrate: number;
  dietary_fiber: number;
  total_sugars: number;
  added_sugars: number;
  calcium: number;
  iron: number;
  potassium: number;
}

export interface ScanResult {
  id?: string;
  timestamp?: string;
  product_name: string;
  brand: string;
  barcode: string;
  nutrition: NutritionData;
  ingredients: string[];
  serving_size: string;
  source: string;
  score: number;
  band: string;
  explanations: string[];
  recommendations: string[];
  evidence: string[];
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

class ApiService {
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return { success: true, data };
    } catch (error) {
      console.error('API request failed:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred',
      };
    }
  }

  // Analyze image using AI
  async analyzeImage(imageFile: File): Promise<ApiResponse<ScanResult>> {
    const formData = new FormData();
    formData.append('image', imageFile);

    try {
      const response = await fetch(`${API_BASE_URL}/analyze-image`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return { success: true, data };
    } catch (error) {
      console.error('Image analysis failed:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Image analysis failed',
      };
    }
  }

  // Search by barcode
  async searchByBarcode(barcode: string): Promise<ApiResponse<ScanResult>> {
    return this.request<ScanResult>(`/search-barcode/${barcode}`);
  }

  // Search by product name
  async searchByName(name: string): Promise<ApiResponse<ScanResult>> {
    return this.request<ScanResult>(`/search-name`, {
      method: 'POST',
      body: JSON.stringify({ name }),
    });
  }

  // Get health score for nutrition data
  async getHealthScore(nutrition: NutritionData): Promise<ApiResponse<{
    score: number;
    band: string;
    explanations: string[];
    recommendations: string[];
  }>> {
    return this.request<{
      score: number;
      band: string;
      explanations: string[];
      recommendations: string[];
    }>('/health-score', {
      method: 'POST',
      body: JSON.stringify({ nutrition }),
    });
  }

  // Get product history
  async getHistory(): Promise<ApiResponse<ScanResult[]>> {
    return this.request<ScanResult[]>('/history');
  }

  // Save scan result
  async saveScanResult(result: ScanResult): Promise<ApiResponse<void>> {
    return this.request<void>('/save-result', {
      method: 'POST',
      body: JSON.stringify(result),
    });
  }

  // Get nutrition guidelines
  async getGuidelines(): Promise<ApiResponse<{
    sugar: { max: number; unit: string };
    sodium: { max: number; unit: string };
    saturated_fat: { max: number; unit: string };
    fiber: { min: number; unit: string };
  }>> {
    return this.request<{
      sugar: { max: number; unit: string };
      sodium: { max: number; unit: string };
      saturated_fat: { max: number; unit: string };
      fiber: { min: number; unit: string };
    }>('/guidelines');
  }
}

export const apiService = new ApiService();

// Mock data for development when backend is not available
export const mockScanResult: ScanResult = {
  product_name: "Coca Cola Classic",
  brand: "The Coca-Cola Company",
  barcode: "5449000000996",
  nutrition: {
    calories: 42.0,
    protein: 0.0,
    total_fat: 0.0,
    saturated_fat: 0.0,
    trans_fat: 0.0,
    cholesterol: 0.0,
    sodium: 1.0,
    total_carbohydrate: 10.6,
    dietary_fiber: 0.0,
    total_sugars: 10.6,
    added_sugars: 10.6,
    calcium: 0.0,
    iron: 0.0,
    potassium: 0.0
  },
  ingredients: [
    "Carbonated Water",
    "Sugar",
    "Caramel Color",
    "Phosphoric Acid",
    "Natural Flavors",
    "Caffeine"
  ],
  serving_size: "100ml",
  source: "OpenFoodFacts",
  score: 25,
  band: "Poor",
  explanations: [
    "High sugar content (10.6g per 100ml) exceeds WHO recommendations",
    "No nutritional value - empty calories",
    "Contains phosphoric acid which may affect bone health"
  ],
  recommendations: [
    "Consider water or unsweetened alternatives",
    "Limit consumption to occasional treats",
    "Be aware of sugar content in other foods"
  ],
  evidence: [
    "WHO Guidelines on Sugar Intake",
    "FDA Nutrition Facts Panel",
    "Peer-reviewed studies on sugar consumption"
  ]
};

// Enhanced mock data with variety
export const mockProducts: Record<string, ScanResult> = {
  "5449000000996": mockScanResult,
  "3017620422003": {
    product_name: "Nutella Hazelnut Spread",
    brand: "Ferrero",
    barcode: "3017620422003",
    nutrition: {
      calories: 546.0,
      protein: 7.3,
      total_fat: 30.0,
      saturated_fat: 18.0,
      trans_fat: 0.0,
      cholesterol: 0.0,
      sodium: 0.1,
      total_carbohydrate: 59.4,
      dietary_fiber: 3.4,
      total_sugars: 47.0,
      added_sugars: 47.0,
      calcium: 0.0,
      iron: 0.0,
      potassium: 0.0
    },
    ingredients: [
      "Sugar",
      "Palm Oil",
      "Hazelnuts",
      "Cocoa Powder",
      "Skimmed Milk Powder",
      "Lecithin",
      "Vanillin"
    ],
    serving_size: "100g",
    source: "OpenFoodFacts",
    score: 35,
    band: "Poor",
    explanations: [
      "Very high sugar content (47g per 100g) - over 3x WHO recommendation",
      "High saturated fat from palm oil (18g per 100g)",
      "Contains processed ingredients and additives"
    ],
    recommendations: [
      "Use sparingly as an occasional treat",
      "Consider natural nut butters as alternatives",
      "Check portion sizes carefully"
    ],
    evidence: [
      "WHO Guidelines on Sugar Intake",
      "FDA Nutrition Facts Panel",
      "Studies on palm oil health effects"
    ]
  },
  "1234567890123": {
    product_name: "Whole Grain Bread",
    brand: "Nature's Own",
    barcode: "1234567890123",
    nutrition: {
      calories: 247.0,
      protein: 13.4,
      total_fat: 4.2,
      saturated_fat: 0.9,
      trans_fat: 0.0,
      cholesterol: 0.0,
      sodium: 681.0,
      total_carbohydrate: 41.0,
      dietary_fiber: 7.0,
      total_sugars: 5.0,
      added_sugars: 2.0,
      calcium: 100.0,
      iron: 2.5,
      potassium: 200.0
    },
    ingredients: [
      "Whole Wheat Flour",
      "Water",
      "Yeast",
      "Salt",
      "Sugar",
      "Vegetable Oil",
      "Preservative"
    ],
    serving_size: "100g",
    source: "OpenFoodFacts",
    score: 75,
    band: "Good",
    explanations: [
      "Good fiber content (7g per 100g) supports digestive health",
      "Low sugar content (5g per 100g) with minimal added sugars",
      "Made with whole grains providing essential nutrients"
    ],
    recommendations: [
      "Excellent choice for daily consumption",
      "Good source of fiber and protein",
      "Consider portion control due to sodium content"
    ],
    evidence: [
      "WHO Guidelines on Fiber Intake",
      "FDA Nutrition Facts Panel",
      "Studies on whole grain benefits"
    ]
  },
  "9876543210987": {
    product_name: "Greek Yogurt",
    brand: "Chobani",
    barcode: "9876543210987",
    nutrition: {
      calories: 59.0,
      protein: 10.0,
      total_fat: 0.4,
      saturated_fat: 0.2,
      trans_fat: 0.0,
      cholesterol: 0.0,
      sodium: 36.0,
      total_carbohydrate: 3.6,
      dietary_fiber: 0.0,
      total_sugars: 3.6,
      added_sugars: 0.0,
      calcium: 110.0,
      iron: 0.0,
      potassium: 141.0
    },
    ingredients: [
      "Cultured Pasteurized Nonfat Milk",
      "Live Active Cultures",
      "Pectin",
      "Natural Flavors"
    ],
    serving_size: "100g",
    source: "OpenFoodFacts",
    score: 85,
    band: "Excellent",
    explanations: [
      "High protein content (10g per 100g) supports muscle health",
      "Low sugar content with no added sugars",
      "Rich in probiotics and calcium"
    ],
    recommendations: [
      "Excellent choice for daily consumption",
      "Great source of protein and probiotics",
      "Perfect for breakfast or snacks"
    ],
    evidence: [
      "FDA Nutrition Facts Panel",
      "Studies on probiotic benefits",
      "Research on protein requirements"
    ]
  }
};

// Function to get random product for variety
export const getRandomMockProduct = (): ScanResult => {
  const products = Object.values(mockProducts);
  return products[Math.floor(Math.random() * products.length)];
};
