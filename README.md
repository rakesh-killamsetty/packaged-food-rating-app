# FoodScore - Health Rating Platform

A modern React-based web application that provides instant health scores for packaged foods using medical-grade analysis backed by WHO, FDA, and peer-reviewed research.

## 🚀 Features

- **Medical-Grade Analysis**: Scoring based on WHO, FDA guidelines and peer-reviewed research
- **Instant Insights**: Get your health score in seconds with clear explanations
- **Multiple Input Methods**: 
  - Barcode scanning from images
  - Manual barcode entry
  - Product name search
- **Beautiful UI**: Modern dark/light theme with 3D animations
- **Scan History**: Track your previous scans and health scores
- **Real-time Analysis**: Powered by advanced AI and medical databases

## 🛠️ Tech Stack

### Frontend
- **React 19** with TypeScript
- **Vite** for fast development and building
- **Tailwind CSS** for styling
- **Framer Motion** for animations
- **Three.js** for 3D effects
- **Radix UI** for accessible components

### Backend
- **FastAPI** for the API server
- **Python** modules for:
  - OCR processing (EasyOCR)
  - Barcode lookup (OpenFoodFacts API)
  - LLM text extraction (OpenAI, Anthropic)
  - Medical nutrition analysis
  - Health scoring engine

## 📦 Installation

### Prerequisites
- Node.js 18+ 
- Python 3.8+
- npm or yarn

### Frontend Setup
```bash
cd foodscore-react
npm install
npm run dev
```

### Backend Setup
```bash
# Install Python dependencies
pip install -r backend_requirements.txt

# Start the FastAPI server
python backend_api.py
```

## 🚀 Quick Start

1. **Start the React app**:
   ```bash
   cd foodscore-react
   npm run dev
   ```

2. **Start the backend API**:
   ```bash
   python backend_api.py
   ```

3. **Open your browser** to `http://localhost:3000`

## 📱 Usage

1. **Upload an image** of a barcode or food label
2. **Or manually enter** a barcode number or product name
3. **Get instant results** with:
   - Health score (0-100)
   - Detailed nutrition breakdown
   - Medical recommendations
   - Evidence-based explanations

## 🎨 Themes

The application supports both dark and light themes with a toggle button in the navigation bar.

## 📊 Health Scoring

Health scores are calculated using:
- **WHO guidelines** for nutrition
- **FDA recommendations** for food safety
- **Medical research** for ingredient analysis
- **Peer-reviewed studies** for health impacts

## 🔧 Development

### Project Structure
```
foodscore-react/
├── src/
│   ├── components/     # React components
│   ├── contexts/       # React contexts
│   ├── services/       # API services
│   └── App.tsx         # Main app component
├── modules/            # Python backend modules
├── backend_api.py      # FastAPI server
└── README.md
```

### Available Scripts
- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support or questions, please open an issue in the repository.

---

**Made with ❤️ for healthier food choices**
