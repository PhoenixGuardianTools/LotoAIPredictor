@echo off
echo [1/3] Export des fichiers JSON...
python export_web_data.py

echo [2/3] Commit des changements...
cd web
git add .
git commit -m "🔄 MAJ auto des stats web"
git push origin main
cd ..

echo [3/3] Publication terminée ✅
pause
