# Script de conversion PyQt6 -> Tkinter (conversion basique)
import os
import re

PYQT_TO_TK = {
    'QWidget': 'tk.Frame',
    'QPushButton': 'tk.Button',
    'QLabel': 'tk.Label',
    'QListWidget': 'tk.Listbox',
    'QComboBox': 'ttk.Combobox',
    'QSpinBox': 'tk.Spinbox',
    'QVBoxLayout': '# Remplacer par pack() ou grid()',
    'QHBoxLayout': '# Remplacer par pack() ou grid()',
    # Ajoute d'autres mappings si besoin
}

def convert_file(filepath):
    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    # Remplacement des imports
    content = re.sub(r'from PyQt6\.QtWidgets import [^\n]+', 'import tkinter as tk\nfrom tkinter import ttk', content)
    content = re.sub(r'from PyQt6 import QtCore[^\n]*', '', content)
    content = re.sub(r'from PyQt6 import QtGui[^\n]*', '', content)

    # Remplacement des widgets
    for pyqt, tk in PYQT_TO_TK.items():
        content = re.sub(rf'\b{pyqt}\b', tk, content)

    # Sauvegarde du fichier converti
    backup_path = filepath + ".bak"
    os.rename(filepath, backup_path)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Converti : {filepath} (sauvegarde : {backup_path})")

def convert_project(root_dir):
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith(".py"):
                filepath = os.path.join(dirpath, filename)
                with open(filepath, encoding="utf-8") as f:
                    if "PyQt6" in f.read():
                        convert_file(filepath)

if __name__ == "__main__":
    convert_project("APP/ui")  # Mets ici le dossier à convertir