import subprocess
import sys
import pkg_resources

def install_requirements():
    print("🔍 Vérification des dépendances...")
    
    # Lire les dépendances requises
    with open('requirements.txt', 'r') as f:
        required = {line.split('>=')[0].strip() for line in f if line.strip()}
    
    # Vérifier les packages installés
    installed = {pkg.key for pkg in pkg_resources.working_set}
    
    # Trouver les packages manquants
    missing = required - installed
    
    if missing:
        print(f"📦 Installation des packages manquants : {', '.join(missing)}")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', *missing])
        print("✅ Installation terminée !")
    else:
        print("✅ Toutes les dépendances sont déjà installées !")

if __name__ == "__main__":
    install_requirements() 