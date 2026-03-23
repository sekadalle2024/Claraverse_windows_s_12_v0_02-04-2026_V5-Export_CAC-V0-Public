@echo off
setlocal
echo ============================================================
echo 🚀 CLARAVERSE - DEPLOIEMENT EN UN CLIC SUR NETLIFY
echo ============================================================
echo.
echo Ce script va :
echo 1. Nettoyer l'ancien build
echo 2. Compiler la nouvelle version (production)
echo 3. Envoyer les fichiers sur Netlify
echo.
echo Appuyez sur une touche pour commencer...
pause > nul

cd /d "%~dp0deploiement-netlify"
powershell -ExecutionPolicy Bypass -File .\deploy.ps1 -Message "Mise a jour manuelle (One-Click)"

if %ERRORLEVEL% equ 0 (
    echo.
    echo ✅ DEPLOIEMENT TERMINE AVEC SUCCES !
    echo Votre site est a jour.
) else (
    echo.
    echo ❌ UNE ERREUR EST SURVENUE DURANT LE DEPLOIEMENT.
    echo Veuillez verifier la connexion internet et l'authentification Netlify.
)

echo.
echo Appuyez sur une touche pour fermer cette fenetre...
pause > nul
