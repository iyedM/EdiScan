@echo off
REM === Script pour lancer EdiScan automatiquement ===

REM 1. Aller dans le dossier du projet
cd /d "%~dp0"

REM 2. Activer l'environnement virtuel
call ediscan-env\Scripts\activate.bat

REM 3. Créer le dossier uploads si non existant
if not exist uploads (
    mkdir uploads
)

REM 4. Lancer Flask
python server\app.py

REM 5. Optionnel: ouvrir le navigateur automatiquement (décommente si tu veux)
REM start http://127.0.0.1:5000

pause
