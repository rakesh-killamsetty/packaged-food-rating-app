# 🍎 FoodScore - React Frontend

A stunning, modern React application for medical-grade food analysis with beautiful dark theme, 3D animations, and mesmerizing UI effects.

## ✨ Features

### 🎨 **Stunning UI/UX**
- **Dark Theme**: Beautiful dark theme with glass morphism effects
- **3D Animations**: Framer Motion powered animations and 3D effects
- **Responsive Design**: Mobile-first responsive design
- **Interactive Elements**: Hover effects, transitions, and micro-interactions

### 🔬 **Medical-Grade Analysis**
- **AI-Powered Scanner**: Upload images or use camera for food analysis
- **Health Score Visualization**: Interactive circular progress rings
- **Nutrition Dashboard**: Comprehensive nutrition facts display
- **Real-time Recommendations**: Evidence-based health recommendations

### 🚀 **Advanced Features**
- **Drag & Drop**: Intuitive file upload with drag and drop
- **3D Background**: Three.js powered floating orbs background
- **Particle System**: Animated particle effects
- **Glass Morphism**: Modern glass-like UI components
- **Gradient Animations**: Dynamic gradient text and backgrounds

## 🛠️ Tech Stack

- **Frontend**: React 19 + TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **Animations**: Framer Motion
- **3D Graphics**: Three.js + React Three Fiber
- **Icons**: Lucide React
- **UI Components**: Radix UI
- **Backend**: FastAPI (Python)

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ 
- npm or yarn
- Python 3.8+ (for backend)

### Installation

1. **Clone and navigate to the React app:**
   ```bash
   cd foodscore-react
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```

4. **Start the backend API (in another terminal):**
   ```bash
   # From the main project directory
   pip install -r backend_requirements.txt
   python backend_api.py
   ```

5. **Open your browser:**
   - React App: http://localhost:3000
   - API Docs: http://localhost:8000/docs

### Using Startup Scripts

**Windows:**
```bash
start_dev.bat
```

**Linux/macOS:**
```bash
chmod +x start_dev.sh
./start_dev.sh
```

## 📁 Project Structure

```
foodscore-react/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── AdvancedScanner.tsx
│   │   ├── HealthScoreRing.tsx
│   │   ├── NutritionBar.tsx
│   │   └── AnimatedCard.tsx
│   ├── services/            # API services
│   │   └── api.ts
│   ├── App.tsx              # Main application
│   ├── main.tsx            # Entry point
│   └── index.css           # Global styles
├── public/                  # Static assets
├── package.json
├── tailwind.config.js      # Tailwind configuration
├── vite.config.ts          # Vite configuration
└── README.md
```

## 🎨 Design System

### Colors
- **Primary**: Green (#22c55e) - Health and nature
- **Accent**: Blue (#0ea5e9) - Trust and technology
- **Dark**: Slate (#0f172a to #334155) - Professional dark theme
- **Gradients**: Dynamic gradients for visual appeal

### Typography
- **Display**: Poppins - Headings and titles
- **Body**: Inter - Body text and UI elements

### Animations
- **Floating**: Smooth floating animations
- **Hover**: Scale and glow effects
- **Transitions**: Smooth page transitions
- **3D Effects**: Card rotations and depth

## 🔧 Available Scripts

```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build
npm run lint         # Run ESLint
```

## 🌟 Key Components

### AdvancedScanner
- Drag & drop file upload
- Camera integration
- Real-time analysis feedback
- Comprehensive results display

### HealthScoreRing
- Animated circular progress
- Color-coded health scores
- Smooth transitions
- Responsive sizing

### NutritionBar
- Animated progress bars
- Color-coded nutrition levels
- Smooth fill animations
- Responsive design

## 🔌 API Integration

The React app connects to a FastAPI backend providing:
- Image analysis endpoints
- Barcode lookup
- Health score calculation
- Nutrition data processing

### API Endpoints
- `POST /analyze-image` - Analyze uploaded food images
- `GET /search-barcode/{barcode}` - Search by barcode
- `POST /search-name` - Search by product name
- `POST /health-score` - Calculate health scores
- `GET /history` - Get scan history

## 🎯 Features in Detail

### 1. **Hero Section**
- Animated text with typewriter effect
- 3D floating orbs background
- Particle system animation
- Call-to-action buttons with hover effects

### 2. **Feature Cards**
- 3D hover effects
- Gradient backgrounds
- Smooth animations
- Responsive grid layout

### 3. **Scanner Interface**
- Drag & drop file upload
- Real-time scanning feedback
- Comprehensive results display
- Mobile-optimized interface

### 4. **Health Visualization**
- Interactive score rings
- Animated nutrition bars
- Color-coded indicators
- Smooth transitions

## 🚀 Performance

- **Vite**: Lightning-fast development and builds
- **Code Splitting**: Automatic code splitting for optimal loading
- **Tree Shaking**: Dead code elimination
- **Optimized Assets**: Compressed images and assets
- **Lazy Loading**: Components loaded on demand

## 📱 Mobile Support

- **Responsive Design**: Works on all screen sizes
- **Touch Gestures**: Optimized for mobile interaction
- **Performance**: Optimized for mobile devices
- **PWA Ready**: Can be installed as a PWA

## 🎨 Customization

### Theme Customization
Edit `src/index.css` to customize:
- Color schemes
- Animation timings
- Glass morphism effects
- Gradient combinations

### Component Styling
All components use Tailwind CSS classes and can be easily customized by modifying the className props.

## 🔧 Development

### Adding New Components
1. Create component in `src/components/`
2. Export from component file
3. Import in `App.tsx` or parent component
4. Use with proper TypeScript types

### API Integration
1. Add new endpoints in `src/services/api.ts`
2. Define TypeScript interfaces
3. Use in components with proper error handling
4. Add loading states and error boundaries

## 🐛 Troubleshooting

### Common Issues

1. **Port already in use:**
   ```bash
   # Kill process on port 3000
   npx kill-port 3000
   ```

2. **Dependencies not installing:**
   ```bash
   # Clear cache and reinstall
   rm -rf node_modules package-lock.json
   npm install
   ```

3. **Backend connection issues:**
   - Ensure backend is running on port 8000
   - Check CORS settings in backend
   - Verify API endpoints are accessible

## 📄 License

This project is part of the FoodScore medical food analysis platform.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For support and questions:
- Check the documentation
- Review the API documentation at `/docs`
- Open an issue on GitHub

---

**Built with ❤️ for better nutrition awareness**