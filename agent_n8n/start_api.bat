@echo off
REM Script de lancement de l'API n8n pour Windows
REM Auteur: desmedt.franck@iaproject.fr
REM Version: 1.0
REM Date: 03/06/2025

cd /d "%~dp0"

echo 🚀 Lancement de l'API Scraper n8n...
echo 📁 Répertoire: %CD%
echo.

REM Vérifier l'existence de l'environnement virtuel
if not exist "venv\Scripts\python.exe" (
    echo ❌ Environnement virtuel non trouvé!
    echo 📁 Cherché: %CD%\venv\Scripts\python.exe
    echo 🔧 Lancez d'abord: python install.py
    pause
    exit /b 1
)

REM Vérifier l'existence du script API
if not exist "api\api_scraper_pour_n8n.py" (
    echo ❌ Script API non trouvé!
    echo 📁 Cherché: %CD%\api\api_scraper_pour_n8n.py
    pause
    exit /b 1
)

echo 🐍 Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

echo 🎯 Lancement de l'API...
echo ========================================
python api\api_scraper_pour_n8n.py %*

echo.
echo 🏁 API arrêtée
pause