@echo off
echo 🚀 Starting InsureBot Voice Assistant...

echo.
echo 🌟 Starting System Initializer (Background Process)...
start "System Initializer" cmd /c "cd /d C:\Users\admin\OneDrive\Desktop\InsureBot && call rasa_env\Scripts\activate && python system_initializer.py"

echo ⚙️ Starting Rasa Actions...
timeout /t 3 /nobreak >nul
start "Rasa Actions" cmd /c "cd /d C:\Users\admin\OneDrive\Desktop\InsureBot && call rasa_env\Scripts\activate && rasa run actions --port 5055"

echo 🤖 Starting Rasa Server...
timeout /t 5 /nobreak >nul
start "Rasa Server" cmd /c "cd /d C:\Users\admin\OneDrive\Desktop\InsureBot && call rasa_env\Scripts\activate && rasa run --enable-api --cors \"*\" --port 5005"

echo 🌐 Starting Frontend...
timeout /t 8 /nobreak >nul
start "Frontend" cmd /c "cd /d C:\Users\admin\OneDrive\Desktop\InsureBot\frontend && npm run dev"

echo.
echo ✅ All services starting...
echo 🌟 System Initializer: http://localhost:8000
echo ⚙️ Actions Server: http://localhost:5055
echo 🤖 Rasa Server: http://localhost:5005
echo 🌐 Frontend: http://localhost:5173
echo.
echo 💡 The system will automatically initialize when you open the frontend!
echo.
pause
