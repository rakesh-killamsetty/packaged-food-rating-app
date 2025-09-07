# PowerShell script to start backend with Gemini API
Write-Host "🤖 Starting Backend with Gemini API..." -ForegroundColor Green
Write-Host "Setting Gemini API Key..." -ForegroundColor Yellow
$env:GEMINI_API_KEY = "AIzaSyDwtJr0pj_oSWyiWON7EGEvZt0UmN-9QSI"
Write-Host "✅ API Key set!" -ForegroundColor Green
Write-Host "Starting FastAPI backend..." -ForegroundColor Yellow
python backend_api.py
