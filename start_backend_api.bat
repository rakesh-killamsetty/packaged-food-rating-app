@echo off
echo 🚀 Starting FoodScore Backend API...
echo.
echo 📦 Installing dependencies...
pip install -r backend_requirements.txt
echo.
echo 🌐 Starting API server...
echo 📡 API will be available at: http://localhost:8000
echo 📚 API Documentation: http://localhost:8000/docs
echo.
python backend_api.py
