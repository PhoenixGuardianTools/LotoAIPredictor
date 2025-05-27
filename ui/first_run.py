import tkinter as tk
from tkinter import ttk
import re
from core.config_manager import ConfigManager

class FirstRunDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Configuration initiale")
        self.geometry("800x600")
        
        self.config_manager = ConfigManager()
        self.create_widgets()
        
        # Empêcher la fermeture de la fenêtre
        self.protocol("WM_DELETE_WINDOW", lambda: None)
    
    def create_widgets(self):
        """Crée les widgets de l'interface."""
        # Notebook pour les différentes étapes
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Onglets
        self.create_personal_info_tab()
        self.create_address_tab()
        self.create_email_tab()
        self.create_options_tab()
        
        # Boutons de navigation
        self.create_navigation_buttons()
    
    def create_personal_info_tab(self):
        """Crée l'onglet des informations personnelles."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Informations personnelles")
        
        # Civilité
        ttk.Label(tab, text="Civilité:").grid(row=0, column=0, padx=5, pady=5)
        self.civilite = ttk.Combobox(tab, values=["Monsieur", "Madame", "Mademoiselle"])
        self.civilite.grid(row=0, column=1, padx=5, pady=5)
        
        # Nom
        ttk.Label(tab, text="Nom:").grid(row=1, column=0, padx=5, pady=5)
        self.nom = ttk.Entry(tab)
        self.nom.grid(row=1, column=1, padx=5, pady=5)
        
        # Prénom
        ttk.Label(tab, text="Prénom:").grid(row=2, column=0, padx=5, pady=5)
        self.prenom = ttk.Entry(tab)
        self.prenom.grid(row=2, column=1, padx=5, pady=5)
        
        # Surnom
        ttk.Label(tab, text="Surnom:").grid(row=3, column=0, padx=5, pady=5)
        self.surnom = ttk.Entry(tab)
        self.surnom.grid(row=3, column=1, padx=5, pady=5)
        
        # Téléphone
        ttk.Label(tab, text="Téléphone:").grid(row=4, column=0, padx=5, pady=5)
        self.telephone = ttk.Entry(tab)
        self.telephone.grid(row=4, column=1, padx=5, pady=5)
        self.telephone.bind('<KeyRelease>', self.format_phone)
    
    def create_address_tab(self):
        """Crée l'onglet de l'adresse."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Adresse")
        
        # Type de voie
        ttk.Label(tab, text="Type de voie:").grid(row=0, column=0, padx=5, pady=5)
        self.type_voie = ttk.Combobox(tab, values=["Rue", "Avenue", "Boulevard", "Place", "Cours", "Chemin", "Hameau", "Lieu-dit"])
        self.type_voie.grid(row=0, column=1, padx=5, pady=5)
        
        # Numéro
        ttk.Label(tab, text="Numéro:").grid(row=1, column=0, padx=5, pady=5)
        num_frame = ttk.Frame(tab)
        num_frame.grid(row=1, column=1, padx=5, pady=5)
        self.numero = ttk.Entry(num_frame, width=5)
        self.numero.pack(side="left")
        self.bis_ter = ttk.Combobox(num_frame, values=["", "bis", "ter"], width=3)
        self.bis_ter.pack(side="left", padx=5)
        
        # Voie
        ttk.Label(tab, text="Voie:").grid(row=2, column=0, padx=5, pady=5)
        self.voie = ttk.Entry(tab)
        self.voie.grid(row=2, column=1, padx=5, pady=5)
        self.voie.bind('<KeyRelease>', self.search_address)
        
        # Complément
        ttk.Label(tab, text="Complément:").grid(row=3, column=0, padx=5, pady=5)
        self.complement = ttk.Entry(tab)
        self.complement.grid(row=3, column=1, padx=5, pady=5)
        ttk.Label(tab, text="(Bâtiment, étage...)").grid(row=3, column=2, padx=5, pady=5)
        
        # Code postal
        ttk.Label(tab, text="Code postal:").grid(row=4, column=0, padx=5, pady=5)
        self.code_postal = ttk.Entry(tab)
        self.code_postal.grid(row=4, column=1, padx=5, pady=5)
        self.code_postal.bind('<KeyRelease>', self.search_postal_code)
        
        # Ville
        ttk.Label(tab, text="Ville:").grid(row=5, column=0, padx=5, pady=5)
        self.ville = ttk.Entry(tab)
        self.ville.grid(row=5, column=1, padx=5, pady=5)
    
    def create_email_tab(self):
        """Crée l'onglet de configuration email."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Email")
        
        # Email
        ttk.Label(tab, text="Email:").grid(row=0, column=0, padx=5, pady=5)
        self.email = ttk.Entry(tab)
        self.email.grid(row=0, column=1, padx=5, pady=5)
        
        # Serveur SMTP
        ttk.Label(tab, text="Serveur SMTP:").grid(row=1, column=0, padx=5, pady=5)
        self.smtp = ttk.Combobox(tab)
        self.smtp.grid(row=1, column=1, padx=5, pady=5)
        self.smtp.bind('<<ComboboxSelected>>', self.update_smtp_port)
        
        # Port SMTP
        ttk.Label(tab, text="Port:").grid(row=2, column=0, padx=5, pady=5)
        self.port = ttk.Entry(tab, state='readonly')
        self.port.grid(row=2, column=1, padx=5, pady=5)
        
        # Chargement des configurations SMTP
        smtp_configs = self.config_manager.get_smtp_configs()
        self.smtp['values'] = [config[0] for config in smtp_configs]
    
    def create_options_tab(self):
        """Crée l'onglet des options."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Options")
        
        # Newsletter
        self.newsletter = tk.BooleanVar(value=True)
        ttk.Checkbutton(tab, text="S'inscrire à la newsletter", variable=self.newsletter).grid(row=0, column=0, padx=5, pady=5)
        
        # Code parrain
        ttk.Label(tab, text="Code parrain:").grid(row=1, column=0, padx=5, pady=5)
        self.code_parrain = ttk.Entry(tab)
        self.code_parrain.grid(row=1, column=1, padx=5, pady=5)
    
    def create_navigation_buttons(self):
        """Crée les boutons de navigation."""
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(btn_frame, text="Précédent", command=self.previous_tab).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Suivant", command=self.next_tab).pack(side="right", padx=5)
    
    def format_phone(self, event):
        """Formate le numéro de téléphone."""
        phone = self.telephone.get().replace(" ", "")
        if phone.startswith("0"):
            phone = "+33" + phone[1:]
        self.telephone.delete(0, tk.END)
        self.telephone.insert(0, phone)
    
    def search_address(self, event):
        """Recherche une adresse."""
        query = self.voie.get()
        if len(query) >= 3:
            results = self.config_manager.search_address(query)
            # TODO: Afficher les résultats dans une liste déroulante
    
    def search_postal_code(self, event):
        """Recherche une ville par code postal."""
        code = self.code_postal.get()
        if len(code) >= 2:
            results = self.config_manager.search_postal_code(code)
            if results:
                self.ville.delete(0, tk.END)
                self.ville.insert(0, results[0][1])
    
    def update_smtp_port(self, event):
        """Met à jour le port SMTP selon le serveur choisi."""
        smtp_configs = self.config_manager.get_smtp_configs()
        selected = self.smtp.get()
        for config in smtp_configs:
            if config[0] == selected:
                self.port.configure(state='normal')
                self.port.delete(0, tk.END)
                self.port.insert(0, str(config[2]))
                self.port.configure(state='readonly')
                break
    
    def previous_tab(self):
        """Passe à l'onglet précédent."""
        current = self.notebook.index(self.notebook.select())
        if current > 0:
            self.notebook.select(current - 1)
    
    def next_tab(self):
        """Passe à l'onglet suivant ou valide la configuration."""
        current = self.notebook.index(self.notebook.select())
        if current < self.notebook.index('end') - 1:
            self.notebook.select(current + 1)
        else:
            self.validate_config()
    
    def validate_config(self):
        """Valide la configuration."""
        # Vérification des champs obligatoires
        if not all([self.nom.get(), self.prenom.get(), self.email.get()]):
            tk.messagebox.showerror("Erreur", "Veuillez remplir tous les champs obligatoires")
            return
        
        # Création de la configuration
        user_data = {
            'type': 'client',
            'nom': self.nom.get(),
            'prenom': self.prenom.get(),
            'surnom': self.surnom.get(),
            'email': self.email.get(),
            'civilite': self.civilite.get(),
            'telephone': self.telephone.get(),
            'newsletter': self.newsletter.get(),
            'code_parrain': self.code_parrain.get(),
            'adresse': {
                'type_voie': self.type_voie.get(),
                'numero': self.numero.get(),
                'bis_ter': self.bis_ter.get(),
                'voie': self.voie.get(),
                'complement': self.complement.get(),
                'code_postal': self.code_postal.get(),
                'ville': self.ville.get()
            },
            'email_config': {
                'server': self.smtp.get(),
                'port': self.port.get()
            }
        }
        
        # Création de la configuration
        success, message = self.config_manager.create_user_config(user_data)
        if success:
            tk.messagebox.showinfo("Succès", message)
            self.destroy()
        else:
            tk.messagebox.showerror("Erreur", message) 