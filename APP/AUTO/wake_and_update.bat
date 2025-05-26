@echo off
echo [AUTO] Tentative Wake-on-LAN...
:: Exemple : envoyer un paquet magique Wake-on-LAN si sur réseau
:: wakeonlan 00:11:22:33:44:55

timeout /t 30
echo [AUTO] Mise à jour automatique des tirages...
python AUTO/auto_update.py
pause
