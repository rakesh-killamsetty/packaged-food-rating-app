# FoodScore – Detailed Project Documentation

## 1) Mission and Objectives

### Mission
Empower people to make healthier packaged‑food choices by turning real‑world labels/barcodes into accurate, medical‑grade insights that are easy to understand.

### Objectives
- Extract trustworthy information from product images (barcodes, nutrition labels, ingredients)
- Analyze health impact using evidence‑based guidance and output a single health score (0–100)
- Provide transparent risks, contraindications, and recommendations with concise explanations
- Deliver a modern, responsive, themeable UI with scan history
- Fail gracefully (OCR‑only) and enhance accuracy when Gemini is available

## 2) Problem Statement and Why This Matters
Food labels are dense and inconsistent. Consumers need a clear, trustworthy signal. FoodScore reads the label, normalizes it, applies clinical nutrition rules, and (optionally) enriches the result with LLM‑assisted medical analysis to surface a dependable score with context.

## 3) High‑Level System Overview

```
User → React App → FastAPI Backend → { OCR, Barcode Lookup, Normalizer }
                                      ↘ Gemini Medical Analysis (if API key set)
                                        → Scoring Engine → JSON result → UI
```

- React (Vite) handles image upload, manual input, and renders results
- FastAPI orchestrates OCR, barcode detection, optional Gemini analysis, and scoring
- OCR uses EasyOCR/PyTesseract + OpenCV + Pyzbar (EAN/UPC)
- Gemini (if enabled) returns structured medical analysis merged into the final result
- History is stored in the browser (localStorage)

## 4) Detailed Data Flow
1) Input: image upload or manual barcode/name
2) Backend processing:
   - Barcode detection → `pyzbar` on OpenCV image
   - OCR → EasyOCR/PyTesseract; regex parses calories, protein, sugars, fats, sodium, etc.
   - Normalization → per‑100g/ml when feasible; standardized ingredient list
   - Gemini (optional) → JSON: medical_health_score, key_concerns, nutrient_risks, contraindications, recommendations
   - Scoring engine → merges nutrition + LLM insights → final score + band + explanations
3) Output: JSON with product_name, brand, nutrition{}, ingredients[], score, band, concerns, recommendations, evidence
4) Frontend: renders score ring, nutrient bars, risks, recs, evidence, and history

## 5) Tech Stack and Rationale

### Frontend
- React + TypeScript (component model, type safety)
- Vite (fast dev server and HMR)
- Tailwind CSS (rapid theming and design consistency)
- Framer Motion / React‑Three‑Fiber (polished interactions/3D)

Why: Excellent DX + responsive UX; straightforward theming and animations.

### Backend
- FastAPI (typed, fast, auto OpenAPI docs)
- OCR: EasyOCR + PyTesseract + OpenCV (mature stack, works offline)
- Barcode: Pyzbar (reliable EAN/UPC)
- Gemini API (google‑generativeai) for medical‑grade interpretation when available
- Simple local LLM fallback to avoid hard failures

Why: Python’s OCR/CV/LLM ecosystem is strong; FastAPI keeps modules clean and testable.

### References / Data Sources
- WHO/FAO dietary guidance and macronutrient thresholds
- FDA Daily Values and labeling guidance
- OpenFoodFacts API for barcode lookups
- (Planned) USDA FoodData Central for verified nutrient baselines

## 6) Scoring Philosophy (Summary)
- Normalize values to per‑100g/ml where feasible
- Penalize excessive added sugars, sodium, trans fats; flag high saturated fat
- Reward fiber and protein density; prefer shorter, simpler ingredient lists
- Incorporate LLM‑flagged risks (e.g., high sodium → hypertension risk) into explanations and banding
- Output bands: Poor, Moderate, Good, Excellent

## 7) Key API Endpoints
- `POST /analyze-image` – OCR + barcode flow (no Gemini required)
- `POST /analyze-image-gemini` – Uses Gemini when `GEMINI_API_KEY` is set
- `GET /health` – Service health and active model info

OpenAPI docs: `http://localhost:8000/docs`.

## 8) Running the Project

Prerequisites: Node.js 18+, Python 3.10+, Google Gemini API key

Backend
```powershell
pip install -r backend_requirements.txt
$env:GEMINI_API_KEY="YOUR_GEMINI_KEY"   # set in the same shell
python backend_api.py                    # http://localhost:8000
```

Frontend
```bash
cd foodscore-react
npm install
npm run dev   # use the printed Vite URL (commonly http://localhost:3000 or http://localhost:5173)
```

## 9) Usage Tips
- Use clear, well‑lit images; center barcode or crop to nutrition label
- If OCR misses fields, reduce glare and improve contrast; try again
- You can also enter a barcode or product name manually in the UI

## 10) Troubleshooting
- Only sample data appears → ensure `GEMINI_API_KEY` is set in the same shell that runs `backend_api.py`
- CORS errors → backend allows ports 3000 and 5173; run Vite on one of these
- 404 via curl on Vite → open in a browser (SPA routes are client‑side)
- Slow model loads → prefer Gemini; local fallback can be slower/limited

## 11) Security & Privacy
- No accounts in MVP; scan history is stored locally in the browser
- Never commit API keys; use environment variables

## 12) Roadmap
- Personalization (age/conditions) for contraindication emphasis
- USDA integration for verified nutrient lookups
- Batch scanning and PWA/offline mode
- Clinician mode with exportable reports

## 13) Directory Layout (Current)
```
foodscore-react/
  src/
    components/
    contexts/
    services/
    App.tsx
backend_api.py
modules/
backend_requirements.txt
README.md
DOCS.md
```

