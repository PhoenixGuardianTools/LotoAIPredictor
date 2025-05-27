import os
import sys
import subprocess
import venv
from pathlib import Path
import site
import platform

def print_section(title):
    """Affiche une section avec un titre."""
    print("\n" + "="*50)
    print(f" {title} ".center(50, "="))
    print("="*50 + "\n")

def get_python_path():
    """Retourne le chemin de l'exécutable Python."""
    return sys.executable

def get_pip_path():
    """Retourne le chemin de pip."""
    return os.path.join(os.path.dirname(sys.executable), "Scripts", "pip.exe")

def create_virtual_env():
    """Crée un environnement virtuel s'il n'existe pas."""
    venv_path = Path("venv")
    if not venv_path.exists():
        print_section("Création de l'environnement virtuel")
        venv.create(venv_path, with_pip=True)
        print("Environnement virtuel créé avec succès.")
    return venv_path

def get_venv_python():
    """Retourne le chemin de Python dans l'environnement virtuel."""
    if platform.system() == "Windows":
        return Path("venv/Scripts/python.exe")
    return Path("venv/bin/python")

def get_venv_pip():
    """Retourne le chemin de pip dans l'environnement virtuel."""
    if platform.system() == "Windows":
        return Path("venv/Scripts/pip.exe")
    return Path("venv/bin/pip")

def install_requirements():
    """Installe les dépendances depuis requirements.txt."""
    print_section("Installation des dépendances")
    pip_path = get_venv_pip()
    
    # Liste des dépendances à installer
    dependencies = [
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0",
        "pandas>=2.0.0",
        "matplotlib",
        "openpyxl",
        "xlsxwriter",
        "cryptography>=41.0.0",
        "schedule>=1.1.0",
        "pyotp",
        "flask",
        "numpy",
        "scikit-learn",
        "ephem",
        "stripe>=12.1.0",
        "wmi>=1.5.1",
        "paypalrestsdk>=1.13.1",
        "qrcode[pil]==8.2.0",
        "jinja2>=3.1.2",
        "pdfkit==1.0.0",
        "reportlab>=4.0.0",
        "Pillow>=10.0.0",
        "pywin32",
        "selenium>=4.0.0",
        "webdriver-manager>=3.8.0",
        "ntplib>=0.4.0",
        "openai>=1.0.0"
    ]
    
    try:
        for dep in dependencies:
            print(f"Installation de {dep}...")
            subprocess.run([str(pip_path), "install", dep], check=True)
        print("Dépendances installées avec succès.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'installation des dépendances: {e}")
        return False

def verify_installation():
    """Vérifie que toutes les dépendances sont correctement installées."""
    print_section("Vérification de l'installation")
    python_path = get_venv_python()
    
    # Liste des modules critiques à vérifier
    critical_modules = [
        "tkinter",
        "PIL",
        "pandas",
        "matplotlib",
        "schedule",
        "requests",
        "beautifulsoup4",
        "pywin32",
        "numpy",
        "flask",
        "cryptography"
    ]
    
    for module in critical_modules:
        try:
            subprocess.run([str(python_path), "-c", f"import {module}"], 
                         check=True, 
                         capture_output=True)
            print(f"✓ {module} est correctement installé")
        except subprocess.CalledProcessError:
            print(f"✗ {module} n'est pas installé correctement")
            return False
    
    return True

def setup_environment():
    """Configure l'environnement de développement."""
    print_section("Configuration de l'environnement")
    
    # Afficher les informations système
    print(f"Système d'exploitation: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version}")
    print(f"Chemin Python: {get_python_path()}")
    print(f"Chemin pip: {get_pip_path()}")
    
    # Créer l'environnement virtuel
    venv_path = create_virtual_env()
    print(f"Environnement virtuel: {venv_path.absolute()}")
    
    # Installer les dépendances
    if not install_requirements():
        print("Erreur lors de l'installation des dépendances.")
        return False
    
    # Vérifier l'installation
    if not verify_installation():
        print("Erreur lors de la vérification de l'installation.")
        return False
    
    print_section("Configuration terminée")
    print("Pour activer l'environnement virtuel:")
    if platform.system() == "Windows":
        print("    .\\venv\\Scripts\\activate")
    else:
        print("    source venv/bin/activate")
    
    return True

if __name__ == "__main__":
    if setup_environment():
        print("\nL'environnement est prêt à être utilisé!")
    else:
        print("\nDes erreurs sont survenues lors de la configuration.")
        sys.exit(1)
