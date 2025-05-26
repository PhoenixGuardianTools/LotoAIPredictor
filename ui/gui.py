import tkinter as tk
from tkinter import ttk, messagebox
from core.insights import (
    generate_insight_report,
    store_custom_grid
)
from core.database import get_statistiques_grilles, get_grilles_jouees

from ui.tabs.tab_game import GameTab
from ui.tabs.tab_results import ResultsTab
from ui.tabs.tab_export import ExportTab
from ui.tabs.tab_about import AboutTab
from ui.tabs.tab_admin import AdminTab
from ui.tabs.tab_userguide import UserGuideTab
from ui.tabs.tab_support import SupportTab
from ui.tabs.tab_enterprise import EnterpriseTab

from LICENSE_ADMIN.license_checker import (
    is_admin_license,
    is_demo_mode,
    get_license_info,
    should_show_reminder,
    should_show_promo
)

class LotoAIPredictorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("LotoAI Predictor")
        self.root.geometry("1200x800")
        
        # Création des onglets
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=5)
        
        # Onglet Prédictions
        self.predictions_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.predictions_tab, text='Prédictions')
        self.setup_predictions_tab()
        
        # Onglet Statistiques
        self.stats_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_tab, text='Statistiques')
        self.setup_stats_tab()
        
        # Onglet Grilles Personnelles
        self.custom_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.custom_tab, text='Mes Grilles')
        self.setup_custom_tab()
        
        # Onglet Insights
        self.insights_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.insights_tab, text='Insights')
        self.setup_insights_tab()
    
    def setup_predictions_tab(self):
        """Configure l'onglet des prédictions."""
        # Sélection du jeu
        game_frame = ttk.LabelFrame(self.predictions_tab, text="Sélection du jeu")
        game_frame.pack(fill='x', padx=5, pady=5)
        
        self.game_var = tk.StringVar(value="Loto")
        games = ["Loto", "EuroDreams", "Euromillions"]
        for game in games:
            ttk.Radiobutton(game_frame, text=game, variable=self.game_var, value=game).pack(side='left', padx=5)
        
        # Affichage des prédictions
        pred_frame = ttk.LabelFrame(self.predictions_tab, text="Prédictions du jour")
        pred_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.pred_text = tk.Text(pred_frame, height=10, wrap='word')
        self.pred_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Boutons d'action
        btn_frame = ttk.Frame(self.predictions_tab)
        btn_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(btn_frame, text="Actualiser", command=self.refresh_predictions).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Jouer ces grilles", command=self.play_predictions).pack(side='left', padx=5)
    
    def setup_stats_tab(self):
        """Configure l'onglet des statistiques."""
        # Statistiques globales
        stats_frame = ttk.LabelFrame(self.stats_tab, text="Statistiques globales")
        stats_frame.pack(fill='x', padx=5, pady=5)
        
        self.stats_text = tk.Text(stats_frame, height=10, wrap='word')
        self.stats_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Graphiques
        graph_frame = ttk.LabelFrame(self.stats_tab, text="Évolution des gains")
        graph_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # TODO: Ajouter des graphiques matplotlib
    
    def setup_custom_tab(self):
        """Configure l'onglet des grilles personnelles."""
        # Saisie de grille
        input_frame = ttk.LabelFrame(self.custom_tab, text="Nouvelle grille")
        input_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(input_frame, text="Numéros:").pack(side='left', padx=5)
        self.numbers_entry = ttk.Entry(input_frame, width=30)
        self.numbers_entry.pack(side='left', padx=5)
        
        ttk.Label(input_frame, text="Spéciaux:").pack(side='left', padx=5)
        self.special_entry = ttk.Entry(input_frame, width=20)
        self.special_entry.pack(side='left', padx=5)
        
        ttk.Button(input_frame, text="Ajouter", command=self.add_custom_grid).pack(side='left', padx=5)
        
        # Liste des grilles
        list_frame = ttk.LabelFrame(self.custom_tab, text="Mes grilles")
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.grids_tree = ttk.Treeview(list_frame, columns=('date', 'numbers', 'special', 'gain'), show='headings')
        self.grids_tree.heading('date', text='Date')
        self.grids_tree.heading('numbers', text='Numéros')
        self.grids_tree.heading('special', text='Spéciaux')
        self.grids_tree.heading('gain', text='Gain')
        self.grids_tree.pack(fill='both', expand=True, padx=5, pady=5)
    
    def setup_insights_tab(self):
        """Configure l'onglet des insights."""
        # Insights généraux
        insights_frame = ttk.LabelFrame(self.insights_tab, text="Insights généraux")
        insights_frame.pack(fill='x', padx=5, pady=5)
        
        self.insights_text = tk.Text(insights_frame, height=10, wrap='word')
        self.insights_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Recommandations
        rec_frame = ttk.LabelFrame(self.insights_tab, text="Recommandations")
        rec_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.rec_text = tk.Text(rec_frame, height=10, wrap='word')
        self.rec_text.pack(fill='both', expand=True, padx=5, pady=5)
    
    def refresh_predictions(self):
        """Actualise les prédictions."""
        game = self.game_var.get()
        report = generate_daily_report()
        
        if game in report['jeux']:
            data = report['jeux'][game]
            self.pred_text.delete('1.0', tk.END)
            
            # Affichage des insights
            self.pred_text.insert(tk.END, "📊 Insights:\n")
            for rec in data['recommandations']:
                self.pred_text.insert(tk.END, f"{rec}\n")
            
            # Affichage des prédictions
            self.pred_text.insert(tk.END, "\n🎯 Grilles recommandées:\n")
            for i, pred in enumerate(data['predictions'], 1):
                self.pred_text.insert(tk.END, f"Grille {i}: {pred['numbers']} + {pred['special']}\n")
                self.pred_text.insert(tk.END, f"Score: {pred['score_tendance'] + pred['score_correlation'] + pred['score_sequence']}\n\n")
    
    def play_predictions(self):
        """Joue les grilles prédites."""
        if messagebox.askyesno("Confirmation", "Voulez-vous jouer ces grilles ?"):
            # TODO: Implémenter la logique de jeu
            messagebox.showinfo("Succès", "Grilles jouées avec succès !")
    
    def add_custom_grid(self):
        """Ajoute une grille personnelle."""
        try:
            numbers = [int(n) for n in self.numbers_entry.get().split(',')]
            special = [int(n) for n in self.special_entry.get().split(',')]
            
            grille = {
                'numbers': numbers,
                'special': special
            }
            
            store_custom_grid(self.game_var.get(), grille)
            messagebox.showinfo("Succès", "Grille ajoutée avec succès !")
            
            # Réinitialisation des champs
            self.numbers_entry.delete(0, tk.END)
            self.special_entry.delete(0, tk.END)
            
        except ValueError:
            messagebox.showerror("Erreur", "Format invalide. Utilisez des nombres séparés par des virgules.")

class AboutTab(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack(fill="both", expand=True)

        info = get_license_info()

        tk.Label(self, text="🧠 Logiciel : LotoAiPredictor", anchor="w", justify="left").pack(fill="x", padx=5, pady=2)
        tk.Label(self, text=f"🔐 Type de licence : {info['type']}", anchor="w", justify="left").pack(fill="x", padx=5, pady=2)
        tk.Label(self, text=f"📅 Expiration : {info['expiration']}", anchor="w", justify="left").pack(fill="x", padx=5, pady=2)
        tk.Label(self, text=f"⏳ Jours restants : {info['jours_restants']}", anchor="w", justify="left").pack(fill="x", padx=5, pady=2)

        if info['type'] == "demo":
            tk.Label(self, text=f"🎟️ Grilles restantes : {info['grilles_restantes']}", anchor="w", justify="left").pack(fill="x", padx=5, pady=2)

        # Ajout du bouton Quitter
        quit_button = tk.Button(self, text="Quitter", command=self.quit_application)
        quit_button.pack(pady=10)

    def quit_application(self):
        """Ferme proprement l'application."""
        self.master.destroy()

def launch_app(permissions=None):
    """Lance l'application."""
    root = tk.Tk()
    app = LotoAIPredictorGUI(root)
    
    # Ajout des onglets selon les permissions
    if permissions and permissions.get('is_admin'):
        app.notebook.add(AdminTab(app.notebook), text='Admin')
        app.notebook.add(EnterpriseTab(app.notebook), text='Entreprise')
    
    # Onglets communs
    app.notebook.add(SupportTab(app.notebook), text='Support')
    app.notebook.add(UserGuideTab(app.notebook), text='Guide')
    
    # Configuration de la fermeture propre lors du clic sur la X
    root.protocol("WM_DELETE_WINDOW", root.destroy)
    
    root.mainloop()
