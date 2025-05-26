@echo off
setlocal EnableDelayedExpansion

:: === CHEMIN SIGNSIGNTOOL ===
set SIGNTOOL_PATH="C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x64\signtool.exe"
set MSI_FILE=LotoAIPredictor_v1.0.1.msi

:: === VÉRIFICATION DE SIGNSIGNTOOL.EXE ===
if not exist %SIGNTOOL_PATH% (
    echo ❌ ERREUR : signtool.exe introuvable :
    echo %SIGNTOOL_PATH%
    echo Vérifie le chemin ou installe le Windows SDK.
    pause
    exit /b 1
)

:: === DEMANDER LE CHEMIN VERS LE CERTIFICAT ===
set /p CERT_FILE=📁 Entrez le chemin complet vers le certificat (.pfx) : 

if not exist "!CERT_FILE!" (
    echo ❌ ERREUR : Le certificat "!CERT_FILE!" est introuvable.
    pause
    exit /b 1
)

:: === VÉRIFICATION DU FICHIER MSI ===
if not exist "%MSI_FILE%" (
    echo ❌ ERREUR : Le fichier MSI %MSI_FILE% est introuvable.
    pause
    exit /b 1
)

:: === DEMANDER LE MOT DE PASSE ===
set /p CERT_PASSWORD=🔐 Entrez le mot de passe du certificat : 

:: === SIGNATURE ===
echo 🖋️ Signature de %MSI_FILE% en cours avec :
echo Certificat : !CERT_FILE!
%SIGNTOOL_PATH% sign ^
  /f "!CERT_FILE!" ^
  /p "!CERT_PASSWORD!" ^
  /tr http://timestamp.digicert.com ^
  /td sha256 ^
  /fd sha256 ^
  "%MSI_FILE%"

if %ERRORLEVEL% NEQ 0 (
    echo ❌ La signature a échoué. Vérifie le mot de passe, le certificat, ou le fichier MSI.
    pause
    exit /b 1
)

echo ✅ Signature réussie !
pause
