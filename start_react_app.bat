@echo off
echo 🚀 Starting FoodScore React App...
echo.
echo 📦 Installing dependencies...
cd foodscore-react
call npm install
echo.
echo 🌐 Starting development server...
echo 📱 React app will be available at: http://localhost:3000
echo 🔗 Make sure the backend API is running on: http://localhost:8000
echo.
call npm run dev
