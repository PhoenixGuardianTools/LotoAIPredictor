@echo off
setlocal

:: === CONFIGURATION ===
set WIXBIN="C:\Program Files (x86)\WiX Toolset v3.11\bin"
set WXS=wix\LotoAIPredictor.wxs
set WIXOBJ=wix\LotoAIPredictor.wixobj
set MSI=LotoAIPredictor_v1.0.1.msi

:: === VÉRIFICATIONS DE BASE ===
if not exist %WXS% (
    echo ❌ Fichier .wxs introuvable : %WXS%
    pause
    exit /b 1
)

echo 🛠️ Compilation avec candle + light (WiX 3.11)...
%WIXBIN%\candle.exe %WXS% && %WIXBIN%\light.exe -ext WixUIExtension -ext WixUtilExtension %WIXOBJ% -o %MSI%

if %ERRORLEVEL% NEQ 0 (
    echo ❌ Échec de la compilation.
    pause
    exit /b 1
)

echo ✅ MSI généré : %MSI%
pause
