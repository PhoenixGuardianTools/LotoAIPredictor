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
    'QLineEdit': 'tk.Entry',
    'QTextEdit': 'tk.Text',
    'QCheckBox': 'tk.Checkbutton',
    'QRadioButton': 'tk.Radiobutton',
    'QVBoxLayout': '# Remplacer par pack() ou grid()',
    'QHBoxLayout': '# Remplacer par pack() ou grid()',
    'QMessageBox': 'messagebox',
}

def convert_file(filepath):
    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    # Remplacement des imports PyQt6
    content = re.sub(
        r'from PyQt6\.QtWidgets import [^\n]+',
        'import tkinter as tk\nfrom tkinter import ttk, messagebox',
        content
    )
    content = re.sub(r'from PyQt6 import QtCore[^\n]*', '', content)
    content = re.sub(r'from PyQt6 import QtGui[^\n]*', '', content)
    content = re.sub(r'import PyQt6[^\n]*', '', content)

    # Remplacement des widgets PyQt6 par Tkinter
    for pyqt, tk in PYQT_TO_TK.items():
        content = re.sub(rf'\b{pyqt}\b', tk, content)

    # Ajout d'un commentaire en haut du fichier
    content = "# Conversion automatique PyQt6 -> Tkinter : vérifiez manuellement les layouts et signaux !\n" + content

    # Sauvegarde du fichier converti
    backup_path = filepath + ".bak"
    if not os.path.exists(backup_path):
        os.rename(filepath, backup_path)
    else:
        print(f"Attention : {backup_path} existe déjà, il ne sera pas écrasé.")
        return  # On ne modifie pas le fichier si le backup existe déjà
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
                        try:
                            convert_file(filepath)
                        except Exception as e:
                            print(f"Erreur sur {filepath} : {e}")

if __name__ == "__main__":
    convert_project("APP/ui/tabs")  # Mets ici le dossier à convertir