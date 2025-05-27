import tkinter as tk
from tkinter import ttk
import win32print
import win32api
from pathlib import Path
from PIL import Image, ImageDraw, ImageTk
import os
import json
import signal
import sys

class BaseWindow(tk.Tk):
    _active_window = None  # Fenêtre active actuellement
    
    def __init__(self, title="Fenêtre", width=1200, height=800):
        # Vérifier si une fenêtre est déjà active
        if BaseWindow._active_window is not None:
            try:
                BaseWindow._active_window.destroy()
            except:
                pass
                
        super().__init__()
        
        # Enregistrer cette fenêtre comme active
        BaseWindow._active_window = self
        
        # Configuration de la fenêtre
        self.title(title)
        self.geometry(f"{width}x{height}")
        
        # Centrer la fenêtre
        self.center_window()
        
        # Style pour les champs modifiés
        self.style = ttk.Style()
        self.style.configure("Modified.TEntry", fieldbackground="#E0E0E0")  # Gris clair
        self.style.configure("Modified.TCombobox", fieldbackground="#E0E0E0")  # Gris clair
        
        # Variables pour suivre les modifications
        self.modified_fields = {}
        self.original_values = {}
        
        # État de la fenêtre
        self.window_state = {
            'geometry': self.geometry(),
            'title': self.title()
        }
        
        # Créer le layout de base
        self._create_base_layout()
        
        # Gérer la fermeture de la fenêtre
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        
    def _create_base_layout(self):
        """Crée le layout de base avec zone centrale et boutons."""
        # Frame principal
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Zone centrale
        self.center_frame = ttk.Frame(self.main_frame)
        self.center_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Boutons d'action en bas
        self.action_frame = ttk.Frame(self)
        self.action_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Créer les boutons par défaut
        self.create_action_buttons()
        
    def _on_closing(self):
        """Gère la fermeture de la fenêtre."""
        try:
            # Réinitialiser la fenêtre active
            if BaseWindow._active_window == self:
                BaseWindow._active_window = None
                
            # Fermer la fenêtre
            self.destroy()
        except Exception as e:
            print(f"Erreur lors de la fermeture : {e}")
            self.destroy()
            
    def create_action_buttons(self):
        """Crée les boutons d'action par défaut."""
        self.print_btn = self.create_print_button(self.action_frame, None)
        self.print_btn.pack(side=tk.LEFT, padx=5)
        
        self.save_btn = ttk.Button(self.action_frame, text="Enregistrer", command=None, state='normal')
        self.save_btn.pack(side=tk.LEFT, padx=5)
        
        self.cancel_btn = ttk.Button(self.action_frame, text="Annuler", command=self.destroy)
        self.cancel_btn.pack(side=tk.LEFT, padx=5)
        
    def center_window(self):
        """Centre la fenêtre sur l'écran."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
    def create_editable_field(self, parent, **kwargs):
        """Crée un champ éditable avec suivi des modifications."""
        entry = ttk.Entry(parent, **kwargs)
        entry.bind('<KeyRelease>', lambda e: self._on_field_modified(e.widget))
        entry.bind('<FocusOut>', lambda e: self._on_field_lost_focus(e.widget))
        return entry
        
    def create_editable_combobox(self, parent, values=None, **kwargs):
        """Crée une combobox éditable avec suivi des modifications et tooltip."""
        combo = ttk.Combobox(parent, values=values, **kwargs)
        combo.bind('<KeyRelease>', lambda e: self._on_field_modified(e.widget))
        combo.bind('<FocusOut>', lambda e: self._on_field_lost_focus(e.widget))
        
        # Ajouter le tooltip
        def show_tooltip(event):
            if combo.winfo_width() < combo.winfo_reqwidth():
                tooltip = tk.Toplevel(self)
                tooltip.wm_overrideredirect(True)
                tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
                label = ttk.Label(tooltip, text=combo.get(), background="#ffffe0", relief='solid', borderwidth=1)
                label.pack()
                
                def hide_tooltip(event):
                    tooltip.destroy()
                    
                combo.bind('<Leave>', hide_tooltip, add='+')
                combo.bind('<Key>', hide_tooltip, add='+')
                
        combo.bind('<Enter>', show_tooltip)
        return combo
        
    def _on_field_modified(self, widget):
        """Gère la modification d'un champ."""
        try:
            if widget not in self.original_values:
                self.original_values[widget] = widget.get()
                
            if widget.get() != self.original_values[widget]:
                widget.configure(style="Modified.TEntry" if isinstance(widget, ttk.Entry) else "Modified.TCombobox")
                self.modified_fields[widget] = True
            else:
                widget.configure(style="TEntry" if isinstance(widget, ttk.Entry) else "TCombobox")
                self.modified_fields[widget] = False
        except Exception as e:
            print(f"Erreur lors de la modification du champ : {e}")
            
    def _on_field_lost_focus(self, widget):
        """Gère la perte de focus d'un champ."""
        try:
            if widget in self.modified_fields and not self.modified_fields[widget]:
                widget.configure(style="TEntry" if isinstance(widget, ttk.Entry) else "TCombobox")
        except Exception as e:
            print(f"Erreur lors de la perte de focus : {e}")
            
    def print_document(self, pdf_path):
        """Imprime le document avec l'imprimante par défaut."""
        try:
            win32api.ShellExecute(
                0,
                "print",
                str(pdf_path),
                '/d:"%s"' % win32print.GetDefaultPrinter(),
                ".",
                0
            )
            return True
        except Exception as e:
            print(f"Erreur lors de l'impression : {e}")
            return False
            
    def create_print_button(self, parent, command):
        """Crée un bouton d'impression."""
        return ttk.Button(parent, text="Imprimer", command=command)

class BaseWindowCRM(BaseWindow):
    def __init__(self, title="Fenêtre", width=1200, height=800):
        super().__init__(title, width, height)
        
        # Charger les icônes
        self._load_icons()
        
        # Variables pour les articles
        self.items = []
        
        # Ajouter le bandeau gauche
        self._create_left_panel()
        
    def _load_icons(self):
        """Charge les icônes pour les boutons d'action."""
        icon_size = (16, 16)
        icons_path = Path("merchand/data/icons")
        icons_path.mkdir(parents=True, exist_ok=True)
        
        # Créer les icônes si elles n'existent pas
        if not (icons_path / "edit.png").exists():
            self._create_default_icons(icons_path)
            
        # Charger les icônes
        self.delete_icon = ImageTk.PhotoImage(Image.open(icons_path / "delete.png").resize(icon_size))
        
    def _create_default_icons(self, icons_path):
        """Crée des icônes par défaut si elles n'existent pas."""
        # Icône suppression (poubelle)
        delete_img = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
        draw = ImageDraw.Draw(delete_img)
        # Poubelle
        draw.rectangle([(8, 8), (24, 24)], fill='red')
        draw.rectangle([(4, 4), (28, 8)], fill='red')
        draw.line([(12, 12), (20, 12)], fill='white', width=2)
        draw.line([(12, 16), (20, 16)], fill='white', width=2)
        delete_img.save(icons_path / "delete.png")
        
    def _create_left_panel(self):
        """Crée le bandeau gauche pour les informations CRM."""
        # Bandeau gauche
        self.left_frame = ttk.Frame(self.main_frame)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # Réorganiser les frames
        self.center_frame.pack_forget()
        self.center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def create_treeview(self, parent, columns, **kwargs):
        """Crée une grille avec alternance de couleurs et lignes visibles."""
        tree = ttk.Treeview(parent, columns=columns, show="headings", **kwargs)
        
        # Configurer les colonnes
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)  # Largeur par défaut
            
        # Alterner les couleurs des lignes
        tree.tag_configure('oddrow', background='#F0F0F0')
        tree.tag_configure('evenrow', background='white')
        
        # Ajouter les lignes avec alternance de couleurs
        def _on_insert(event):
            for i, item in enumerate(tree.get_children()):
                tags = tree.item(item)['tags']
                if not tags:
                    tags = ('oddrow' if i % 2 else 'evenrow',)
                tree.item(item, tags=tags)
                
        tree.bind('<<TreeviewOpen>>', _on_insert)
        tree.bind('<<TreeviewClose>>', _on_insert)
        
        return tree
        
    def create_price_field(self, parent, **kwargs):
        """Crée un champ de prix en lecture seule."""
        price_entry = ttk.Entry(parent, state='readonly', **kwargs)
        return price_entry
        
    def update_price_field(self, price_field, price):
        """Met à jour un champ de prix."""
        price_field.config(state='normal')
        price_field.delete(0, tk.END)
        price_field.insert(0, f"{price:.2f} €")
        price_field.config(state='readonly')
        
    def create_quantity_combobox(self, parent, **kwargs):
        """Crée une combobox pour la quantité (1-5)."""
        combo = ttk.Combobox(parent, values=[str(i) for i in range(1, 6)], state='readonly', width=5, **kwargs)
        combo.set('1')  # Valeur par défaut
        return combo
        
    def create_discount_combobox(self, parent, **kwargs):
        """Crée une combobox pour la réduction."""
        combo = ttk.Combobox(parent, values=[str(i) for i in range(0, 101, 10)], state='readonly', width=5, **kwargs)
        combo.set('0')  # Valeur par défaut
        return combo
        
    def calculate_item_totals(self, base_price, quantity, discount_percent):
        """Calcule les totaux pour un article."""
        price = float(base_price) * (1 - discount_percent / 100)
        subtotal = price * quantity
        vat = subtotal * 0.20
        total = subtotal + vat
        return price, subtotal, vat, total
        
    def format_currency(self, amount):
        """Formate un montant en devise."""
        return f"{amount:.2f} €"
        
    def add_item(self, item_data):
        """Ajoute un article à la liste."""
        self.items.append(item_data)
        return item_data
        
    def delete_item(self, index):
        """Supprime un article et redessine la grille."""
        if 0 <= index < len(self.items):
            self.items.pop(index)
            return True
        return False

class BaseWindowDataGrid(BaseWindowCRM):
    def __init__(self, title="Fenêtre", width=1200, height=800):
        super().__init__(title, width, height)
        
        # Style pour la grille
        self.style.configure("Alternate.Treeview", background="#F0F0F0")  # Gris clair
        self.style.configure("Treeview", rowheight=25)  # Hauteur des lignes
        self.style.configure("Treeview.Heading", font=('Helvetica', 10, 'bold'))
        
    def create_treeview(self, parent, columns, **kwargs):
        """Crée une grille avec alternance de couleurs et lignes visibles."""
        tree = super().create_treeview(parent, columns, **kwargs)
        
        # Ajouter le menu contextuel
        def show_context_menu(event):
            item = tree.identify_row(event.y)
            if item:
                tree.selection_set(item)
                menu = tk.Menu(self, tearoff=0)
                menu.add_command(label="Supprimer", image=self.delete_icon, compound=tk.LEFT,
                               command=lambda: self._delete_item(tree, item))
                menu.post(event.x_root, event.y_root)
                
        tree.bind('<Button-3>', show_context_menu)
        
        return tree
        
    def _delete_item(self, tree, item):
        """Supprime un article et redessine la grille."""
        index = tree.index(item)
        if self.delete_item(index):
            # Supprimer tous les éléments
            for item in tree.get_children():
                tree.delete(item)
                
            # Redessiner la grille
            for i, item_data in enumerate(self.items):
                price, subtotal, vat, total = self.calculate_item_totals(
                    item_data['base_price'],
                    item_data['quantity'],
                    item_data['discount_percent']
                )
                
                tree.insert("", "end", values=(
                    item_data['product_id'],  # Code produit
                    item_data['name'],
                    item_data['duration'],
                    self.format_currency(item_data['base_price']),
                    item_data['quantity'],
                    f"{item_data['discount_percent']}%",
                    self.format_currency(subtotal),
                    self.format_currency(vat),
                    self.format_currency(total)
                ), tags=('oddrow' if i % 2 else 'evenrow',)) 