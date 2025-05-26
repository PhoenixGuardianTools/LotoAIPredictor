import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import json
from core.database import check_fdj_status, update_fdj_data
from core.reports import ReportGenerator
from core.export import export_to_excel, export_to_pdf
from ui.tabs.ascii_display import display_ascii_report
from ui.tabs.visualization_report import visualize_report

class ReportsTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_ui()
        self.report_generator = ReportGenerator()
        
    def setup_ui(self):
        """Configure l'interface utilisateur de l'onglet Rapports."""
        # Frame principal
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame supérieur pour les contrôles
        control_frame = ttk.LabelFrame(main_frame, text="Contrôles")
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Sélection du jeu
        ttk.Label(control_frame, text="Jeu:").grid(row=0, column=0, padx=5, pady=5)
        self.game_var = tk.StringVar(value="Loto")
        game_combo = ttk.Combobox(control_frame, textvariable=self.game_var, 
                                 values=["Loto", "EuroDreams", "Euromillions"])
        game_combo.grid(row=0, column=1, padx=5, pady=5)
        
        # Type de rapport
        ttk.Label(control_frame, text="Type:").grid(row=0, column=2, padx=5, pady=5)
        self.report_type_var = tk.StringVar(value="daily")
        report_type_combo = ttk.Combobox(control_frame, textvariable=self.report_type_var,
                                       values=["daily", "weekly", "monthly", "custom"])
        report_type_combo.grid(row=0, column=3, padx=5, pady=5)
        
        # Période personnalisée
        self.date_frame = ttk.Frame(control_frame)
        self.date_frame.grid(row=1, column=0, columnspan=4, padx=5, pady=5)
        
        ttk.Label(self.date_frame, text="Du:").pack(side=tk.LEFT, padx=5)
        self.start_date = ttk.Entry(self.date_frame, width=10)
        self.start_date.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(self.date_frame, text="Au:").pack(side=tk.LEFT, padx=5)
        self.end_date = ttk.Entry(self.date_frame, width=10)
        self.end_date.pack(side=tk.LEFT, padx=5)
        
        # Bouton de mise à jour FDJ
        self.update_fdj_btn = ttk.Button(control_frame, text="Mettre à jour FDJ",
                                       command=self.update_fdj)
        self.update_fdj_btn.grid(row=0, column=4, padx=5, pady=5)
        
        # Frame pour l'affichage du rapport
        report_frame = ttk.LabelFrame(main_frame, text="Rapport")
        report_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Zone de texte pour le rapport ASCII
        self.report_text = tk.Text(report_frame, wrap=tk.WORD, height=20)
        self.report_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame pour les boutons d'action
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Boutons d'export
        ttk.Button(action_frame, text="Exporter Excel",
                  command=self.export_excel).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Exporter PDF",
                  command=self.export_pdf).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Actualiser",
                  command=self.refresh_report).pack(side=tk.LEFT, padx=5)
        
        # Initialisation
        self.refresh_report()
        self.check_fdj_status()
    
    def check_fdj_status(self):
        """Vérifie le statut de la base FDJ et met à jour l'interface."""
        status = check_fdj_status(self.game_var.get())
        if status['is_up_to_date']:
            self.update_fdj_btn.configure(state='disabled')
        else:
            self.update_fdj_btn.configure(state='normal')
    
    def update_fdj(self):
        """Met à jour les données FDJ."""
        try:
            update_fdj_data(self.game_var.get())
            messagebox.showinfo("Succès", "Base de données mise à jour avec succès!")
            self.check_fdj_status()
            self.refresh_report()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la mise à jour: {str(e)}")
    
    def refresh_report(self):
        """Rafraîchit l'affichage du rapport."""
        try:
            # Génération du rapport
            if self.report_type_var.get() == "custom":
                # TODO: Implémenter la génération de rapport personnalisé
                pass
            else:
                report = self.report_generator.generate_daily_report(self.game_var.get())
            
            # Affichage ASCII
            self.report_text.delete(1.0, tk.END)
            display_ascii_report(report, self.report_type_var.get())
            
            # Mise à jour du statut FDJ
            self.check_fdj_status()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la génération du rapport: {str(e)}")
    
    def export_excel(self):
        """Exporte le rapport au format Excel."""
        try:
            # Demander le chemin de sauvegarde
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                initialfile=f"{self.game_var.get()}_{datetime.now().strftime('%Y%m%d')}.xlsx"
            )
            
            if file_path:
                # Générer le rapport
                if self.report_type_var.get() == "custom":
                    # TODO: Implémenter la génération de rapport personnalisé
                    pass
                else:
                    report = self.report_generator.generate_daily_report(self.game_var.get())
                
                # Exporter en Excel
                export_to_excel(report, self.report_type_var.get(), file_path)
                messagebox.showinfo("Succès", "Rapport exporté avec succès!")
        
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'export Excel: {str(e)}")
    
    def export_pdf(self):
        """Exporte le rapport au format PDF."""
        try:
            # Demander le chemin de sauvegarde
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                initialfile=f"{self.game_var.get()}_{datetime.now().strftime('%Y%m%d')}.pdf"
            )
            
            if file_path:
                # Générer le rapport
                if self.report_type_var.get() == "custom":
                    # TODO: Implémenter la génération de rapport personnalisé
                    pass
                else:
                    report = self.report_generator.generate_daily_report(self.game_var.get())
                
                # Exporter en PDF
                export_to_pdf(report, self.report_type_var.get(), file_path)
                messagebox.showinfo("Succès", "Rapport exporté avec succès!")
        
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'export PDF: {str(e)}") 