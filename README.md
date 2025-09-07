# FoodScore – Medical‑grade Packaged Food Rating

FoodScore is a React + FastAPI application that converts barcodes/labels into a health score with clear medical explanations. OCR + barcode detection extract data from images, then Gemini performs medical analysis, and a scoring engine produces the final score with evidence and recommendations.

## ✨ Features

- **Gemini medical analysis** for products (image → nutrition/ingredients → risks/recommendations)
- **OCR + barcode detection**: EasyOCR/PyTesseract + OpenCV + Pyzbar
- **Multiple inputs**: upload image, enter barcode, or product name
- **Accurate scoring** using WHO/FDA style thresholds and nutrient limits
- **Modern UI**: Dark/light themes, animations, history of scans

## 🧱 Tech Stack

- Frontend: React + TypeScript, Vite, Tailwind CSS, Framer Motion, React‑Three‑Fiber
- Backend: FastAPI (Python), EasyOCR/PyTesseract, OpenCV, Pyzbar, Google Gemini API
- Data sources: OpenFoodFacts, (planned) USDA FoodData Central

## 🗺️ Architecture (high level)

1. User uploads photo or enters barcode/name in the React app
2. Backend extracts barcode + OCR text → normalizes nutrition + ingredients
3. Gemini analyzes medical suitability and risks → returns structured JSON
4. Scoring engine merges OCR/nutrition with LLM insights → health score
5. Frontend renders score ring, nutrients, concerns, recommendations, history

## ✅ Prerequisites

- Node.js 18+
- Python 3.10+ (recommended)
- A Google Gemini API key

## ⚙️ Setup

1) Install backend dependencies
```bash
pip install -r backend_requirements.txt
```

2) Set Gemini API key (PowerShell on Windows)
```powershell
$env:GEMINI_API_KEY="YOUR_GEMINI_KEY"
```
Keep this terminal open – environment variables are per‑shell.

3) Start backend (FastAPI)
```bash
python backend_api.py
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

4) Install frontend and run Vite dev server
```bash
cd foodscore-react
npm install
npm run dev 
# App: http://localhost:3000
```

## 🚀 How to Use

1. Open http://localhost:3000
2. Upload a barcode/label/product image, or enter barcode/product name
3. Review: score, nutrient bars, medical concerns, recommendations, evidence
4. Toggle theme and view your scan history

## 🔒 Environment & Ports

- Backend runs at `http://localhost:3000`
- Frontend runs at `http://localhost:3000`
- CORS is enabled for  3000 

If the frontend can’t connect, ensure you started the backend shell with `GEMINI_API_KEY` set, and that the frontend is on 5173. Use the same PC/local network.

## 🧪 Troubleshooting

- Frontend shows mock/sample data: confirm `GEMINI_API_KEY` is set in the same terminal that starts `backend_api.py`
- 404 when curling 5173: open the URL in a browser (Vite dev server serves the SPA path)
- Barcode not detected: ensure clear, well‑lit image with the barcode fully visible
- OCR misses text: crop to the nutrition label region and retry

## 📚 References

- WHO/FAO diet and nutrition guidance
- FDA guidance on nutrition labeling and daily values
- OpenFoodFacts API
- Google Generative AI (Gemini) – model API

## 📂 Project Structure
```
foodscore-react/
  src/
    components/
    contexts/
    services/
    App.tsx
backend_api.py            # FastAPI server and endpoints
modules/                  # OCR, LLM, scoring, helpers
backend_requirements.txt
README.md
```

## 📝 Scripts

- Frontend: `npm run dev -- --port 3000`
- Backend: `python backend_api.py`

---

Made with ❤️ to help you choose healthier packaged foods.
