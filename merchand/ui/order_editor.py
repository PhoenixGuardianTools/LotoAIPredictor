import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
from pathlib import Path
from datetime import datetime, timedelta
from PIL import Image, ImageTk
import os
import webbrowser
import sqlite3
import sys

# Ajouter le répertoire parent au PYTHONPATH
current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent
sys.path.append(str(parent_dir))

from merchand.generate_order import OrderGenerator
from merchand.generate_invoice import InvoiceGenerator
from merchand.ui.base_window import BaseWindowDataGrid

class OrderEditor(BaseWindowDataGrid):
    def __init__(self):
        super().__init__(title="Éditeur de Bon de Commande", width=1400, height=900)
        
        self.order_generator = OrderGenerator()
        self.invoice_generator = InvoiceGenerator()
        
        self.current_order = None
        self.items = []
        self.clients_list = []
        self.selected_client_id = None
        
        # Charger les icônes
        self._load_icons()
        
        self._create_widgets()
        self._load_product_types()
        self._load_clients()
        
    def _load_icons(self):
        """Charge les icônes pour les boutons d'action."""
        icon_size = (16, 16)
        icons_path = Path("merchand/data/icons")
        icons_path.mkdir(parents=True, exist_ok=True)
        
        # Créer les icônes si elles n'existent pas
        if not (icons_path / "edit.png").exists():
            self._create_default_icons(icons_path)
            
        # Charger les icônes
        self.edit_icon = ImageTk.PhotoImage(Image.open(icons_path / "edit.png").resize(icon_size))
        self.validate_icon = ImageTk.PhotoImage(Image.open(icons_path / "validate.png").resize(icon_size))
        self.delete_icon = ImageTk.PhotoImage(Image.open(icons_path / "delete.png").resize(icon_size))
        self.view_icon = ImageTk.PhotoImage(Image.open(icons_path / "view.png").resize(icon_size))
        
    def _create_default_icons(self, icons_path):
        """Crée des icônes par défaut si elles n'existent pas."""
        from PIL import Image, ImageDraw
        
        # Icône édition (crayon)
        edit_img = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
        draw = ImageDraw.Draw(edit_img)
        draw.line([(5, 25), (25, 5)], fill='blue', width=2)
        draw.line([(25, 5), (27, 7)], fill='blue', width=2)
        edit_img.save(icons_path / "edit.png")
        
        # Icône validation (coche verte)
        validate_img = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
        draw = ImageDraw.Draw(validate_img)
        draw.line([(5, 15), (12, 22), (27, 7)], fill='green', width=2)
        validate_img.save(icons_path / "validate.png")
        
        # Icône suppression (croix rouge)
        delete_img = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
        draw = ImageDraw.Draw(delete_img)
        draw.line([(5, 5), (27, 27)], fill='red', width=2)
        draw.line([(5, 27), (27, 5)], fill='red', width=2)
        delete_img.save(icons_path / "delete.png")
        
        # Icône visualisation (œil)
        view_img = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
        draw = ImageDraw.Draw(view_img)
        draw.ellipse([(5, 10), (27, 22)], outline='black', width=2)
        draw.ellipse([(12, 14), (20, 18)], fill='black')
        view_img.save(icons_path / "view.png")
        
    def _create_widgets(self):
        # Frame gauche pour les informations client
        left_frame = ttk.LabelFrame(self.left_frame, text="Informations Client")
        left_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Combobox filtrante pour sélectionner un client
        ttk.Label(left_frame, text="Sélectionner un client :").pack(anchor=tk.W, padx=5, pady=2)
        self.client_combo_var = tk.StringVar()
        self.client_combo = self.create_editable_combobox(left_frame, textvariable=self.client_combo_var)
        self.client_combo.pack(fill=tk.X, padx=5, pady=2)
        self.client_combo.bind('<KeyRelease>', self._on_client_filter)
        self.client_combo.bind('<<ComboboxSelected>>', self._on_client_selected)
        
        # Champs client
        ttk.Label(left_frame, text="ID Client:").pack(anchor=tk.W, padx=5, pady=2)
        self.client_id_entry = ttk.Entry(left_frame, state='readonly')
        self.client_id_entry.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(left_frame, text="Nom:").pack(anchor=tk.W, padx=5, pady=2)
        self.client_name_entry = self.create_editable_field(left_frame)
        self.client_name_entry.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(left_frame, text="Email:").pack(anchor=tk.W, padx=5, pady=2)
        self.client_email_entry = self.create_editable_field(left_frame)
        self.client_email_entry.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(left_frame, text="Adresse:").pack(anchor=tk.W, padx=5, pady=2)
        self.client_address_entry = self.create_editable_field(left_frame)
        self.client_address_entry.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(left_frame, text="Code postal:").pack(anchor=tk.W, padx=5, pady=2)
        self.client_postal_code_entry = self.create_editable_field(left_frame)
        self.client_postal_code_entry.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(left_frame, text="Ville:").pack(anchor=tk.W, padx=5, pady=2)
        self.client_city_entry = self.create_editable_field(left_frame)
        self.client_city_entry.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(left_frame, text="Pays:").pack(anchor=tk.W, padx=5, pady=2)
        self.client_country_entry = self.create_editable_field(left_frame)
        self.client_country_entry.pack(fill=tk.X, padx=5, pady=2)
        
        # Bouton pour enregistrer les modifications du client
        self.save_client_btn = ttk.Button(left_frame, text="Enregistrer les modifications", command=self._save_client, state='disabled')
        self.save_client_btn.pack(fill=tk.X, padx=5, pady=10)
        
        # Frame droite pour les articles
        right_frame = ttk.LabelFrame(self.center_frame, text="Articles")
        right_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Sélection du produit
        product_frame = ttk.Frame(right_frame)
        product_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(product_frame, text="Type:").pack(side=tk.LEFT, padx=5)
        self.product_type_combo = ttk.Combobox(product_frame, state="readonly")
        self.product_type_combo.pack(side=tk.LEFT, padx=5)
        self.product_type_combo.bind('<<ComboboxSelected>>', self._on_product_type_selected)
        
        ttk.Label(product_frame, text="Produit:").pack(side=tk.LEFT, padx=5)
        self.product_combo = ttk.Combobox(product_frame, state="readonly")
        self.product_combo.pack(side=tk.LEFT, padx=5)
        self.product_combo.bind('<<ComboboxSelected>>', self._on_product_selected)
        
        ttk.Label(product_frame, text="Quantité:").pack(side=tk.LEFT, padx=5)
        self.quantity_combo = self.create_quantity_combobox(product_frame)
        self.quantity_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(product_frame, text="Prix unitaire:").pack(side=tk.LEFT, padx=5)
        self.price_entry = self.create_price_field(product_frame, width=10)
        self.price_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(product_frame, text="Réduction (%):").pack(side=tk.LEFT, padx=5)
        self.discount_combo = self.create_discount_combobox(product_frame)
        self.discount_combo.pack(side=tk.LEFT, padx=5)
        self.discount_combo.bind('<<ComboboxSelected>>', self._on_discount_changed)
        
        ttk.Button(product_frame, text="Ajouter", command=self._add_item).pack(side=tk.LEFT, padx=5)
        
        # Liste des articles avec icônes
        columns = ("product_id", "name", "duration", "price", "quantity", "discount", "subtotal", "vat", "total")
        self.items_tree = self.create_treeview(right_frame, columns)
        
        # Configurer les colonnes
        self.items_tree.heading("product_id", text="Code")
        self.items_tree.heading("name", text="Produit")
        self.items_tree.heading("duration", text="Durée")
        self.items_tree.heading("price", text="Prix unitaire")
        self.items_tree.heading("quantity", text="Quantité")
        self.items_tree.heading("discount", text="Réduction")
        self.items_tree.heading("subtotal", text="Sous-total")
        self.items_tree.heading("vat", text="TVA")
        self.items_tree.heading("total", text="Total")
        
        # Ajuster les largeurs des colonnes
        self.items_tree.column("product_id", width=100)
        self.items_tree.column("name", width=200)
        self.items_tree.column("duration", width=100)
        self.items_tree.column("price", width=100)
        self.items_tree.column("quantity", width=80)
        self.items_tree.column("discount", width=80)
        self.items_tree.column("subtotal", width=100)
        self.items_tree.column("vat", width=100)
        self.items_tree.column("total", width=100)
        
        self.items_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Ajouter les boutons d'action dans la première colonne
        self.items_tree.bind('<Double-1>', self._on_item_double_click)
        
        # Totaux par type de produit
        self.type_totals_frame = ttk.LabelFrame(right_frame, text="Totaux par type")
        self.type_totals_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Totaux généraux
        totals_frame = ttk.Frame(right_frame)
        totals_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(totals_frame, text="Sous-total:").pack(side=tk.LEFT, padx=5)
        self.subtotal_label = ttk.Label(totals_frame, text="0.00 €")
        self.subtotal_label.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(totals_frame, text="TVA (20%):").pack(side=tk.LEFT, padx=5)
        self.vat_label = ttk.Label(totals_frame, text="0.00 €")
        self.vat_label.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(totals_frame, text="Total:").pack(side=tk.LEFT, padx=5)
        self.total_label = ttk.Label(totals_frame, text="0.00 €")
        self.total_label.pack(side=tk.LEFT, padx=5)
        
        # Boutons d'action en bas
        self.print_btn.config(command=self._print_order)
        self.save_btn.config(command=self._generate_order)  # Le bouton Enregistrer génère le bon de commande
        self.cancel_btn.config(command=self._reset_grid)  # Le bouton Annuler réinitialise la grille
        
        # Ajouter les boutons spécifiques
        ttk.Button(self.action_frame, text="Générer", command=self._generate_order).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.action_frame, text="Envoyer", command=self._send_order).pack(side=tk.LEFT, padx=5)
        
    def _on_item_double_click(self, event):
        """Gère le double-clic sur un article."""
        item = self.items_tree.identify_row(event.y)
        if not item:
            return
            
        column = self.items_tree.identify_column(event.x)
        if column == "#1":  # Colonne des actions
            self._show_action_buttons(item, event.x, event.y)
            
    def _show_action_buttons(self, item, x, y):
        """Affiche les boutons d'action pour un article."""
        # Créer une fenêtre flottante pour les boutons
        popup = tk.Toplevel(self)
        popup.wm_overrideredirect(True)
        popup.wm_geometry(f"+{x}+{y}")
        
        # Ajouter les boutons
        ttk.Button(popup, image=self.edit_icon, command=lambda: self._edit_item(item, popup)).pack(side=tk.LEFT)
        ttk.Button(popup, image=self.validate_icon, command=lambda: self._validate_item(item, popup)).pack(side=tk.LEFT)
        ttk.Button(popup, image=self.delete_icon, command=lambda: self._delete_item(item, popup)).pack(side=tk.LEFT)
        ttk.Button(popup, image=self.view_icon, command=lambda: self._view_item(item, popup)).pack(side=tk.LEFT)
        
        # Fermer la popup quand on clique ailleurs
        def on_click_outside(event):
            popup.destroy()
            
        self.bind('<Button-1>', on_click_outside)
        
    def _delete_item(self, item, popup):
        """Supprime un article."""
        popup.destroy()
        index = self.items_tree.index(item)
        self.delete_item(index)
        self._update_items_tree()
        self._update_totals()
        
    def _update_items_tree(self):
        """Met à jour l'affichage des articles."""
        for item in self.items_tree.get_children():
            self.items_tree.delete(item)
            
        for i, item in enumerate(self.items):
            price, subtotal, vat, total = self.calculate_item_totals(
                item['base_price'],
                item['quantity'],
                item['discount_percent']
            )
            
            self.items_tree.insert("", "end", values=(
                item['product_id'],  # Code produit
                item['name'],
                item['duration'],
                self.format_currency(item['base_price']),
                item['quantity'],
                f"{item['discount_percent']}%",
                self.format_currency(subtotal),
                self.format_currency(vat),
                self.format_currency(total)
            ), tags=('oddrow' if i % 2 else 'evenrow',))
            
        self._update_type_totals()
        
    def _update_type_totals(self):
        """Met à jour les totaux par type de produit."""
        # Nettoyer le frame des totaux
        for widget in self.type_totals_frame.winfo_children():
            widget.destroy()
            
        # Calculer les totaux par type
        type_totals = {}
        for item in self.items:
            product_type = item['name'].split()[0]  # Premier mot du nom
            if product_type not in type_totals:
                type_totals[product_type] = 0
                
            price = float(item['base_price'])
            if 'discount_percent' in item:
                price = price * (1 - item['discount_percent'] / 100)
            type_totals[product_type] += price * item['quantity']
            
        # Afficher les totaux
        for product_type, total in type_totals.items():
            frame = ttk.Frame(self.type_totals_frame)
            frame.pack(fill=tk.X, padx=5, pady=2)
            ttk.Label(frame, text=f"{product_type}:").pack(side=tk.LEFT)
            ttk.Label(frame, text=f"{total:.2f} €").pack(side=tk.RIGHT)
            
    def _generate_order(self):
        """Génère le bon de commande et l'enregistre en base de données."""
        if not self._validate_data():
            return
            
        try:
            # Préparer les données
            order_data = self._prepare_order_data()
            
            # Générer le PDF
            pdf_path = self.order_generator.generate_order(order_data)
            if not pdf_path:
                messagebox.showerror("Erreur", "Erreur lors de la génération du PDF")
                return
                
            # Enregistrer en base de données
            db_path = Path("merchand/data/orders.db")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Créer la table si elle n'existe pas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    order_id TEXT PRIMARY KEY,
                    order_date TEXT,
                    due_date TEXT,
                    client_id TEXT,
                    total_amount REAL,
                    status TEXT,
                    pdf_path TEXT,
                    FOREIGN KEY (client_id) REFERENCES clients(client_id)
                )
            """)
            
            # Insérer la commande
            cursor.execute("""
                INSERT INTO orders (order_id, order_date, due_date, client_id, total_amount, status, pdf_path)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                order_data['order_number'],
                order_data['date'],
                order_data['due_date'],
                order_data['client']['id'],
                float(self.total_label.cget("text").replace(" €", "")),
                "En attente",
                str(pdf_path)
            ))
            
            # Créer la table des articles si elle n'existe pas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS order_items (
                    order_id TEXT,
                    product_id TEXT,
                    quantity INTEGER,
                    unit_price REAL,
                    discount_percent INTEGER,
                    total_price REAL,
                    FOREIGN KEY (order_id) REFERENCES orders(order_id),
                    FOREIGN KEY (product_id) REFERENCES products(product_id)
                )
            """)
            
            # Insérer les articles
            for item in self.items:
                price, subtotal, vat, total = self.calculate_item_totals(
                    item['base_price'],
                    item['quantity'],
                    item['discount_percent']
                )
                
                cursor.execute("""
                    INSERT INTO order_items (order_id, product_id, quantity, unit_price, discount_percent, total_price)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    order_data['order_number'],
                    item['product_id'],
                    item['quantity'],
                    item['base_price'],
                    item['discount_percent'],
                    total
                ))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Succès", "Bon de commande généré et enregistré avec succès")
            
            # Ouvrir le PDF
            os.startfile(pdf_path)
            
        except Exception as e:
            print(f"Erreur lors de la génération du bon de commande : {e}")
            messagebox.showerror("Erreur", f"Erreur lors de la génération du bon de commande : {e}")
            
    def _send_order(self):
        """Envoie le bon de commande par email."""
        if not self._validate_data():
            return
            
        order_data = self._prepare_order_data()
        pdf_path = self.order_generator.generate_order(order_data)
        
        if pdf_path:
            from merchand.generate_order import send_order_email
            send_order_email(
                to_email=order_data['client']['email'],
                pdf_path=Path(pdf_path),
                order_number=order_data['order_number']
            )
            
    def _prepare_order_data(self):
        """Prépare les données du bon de commande."""
        order_number = f"CMD{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Calculer les totaux
        subtotal = sum(float(item['base_price']) * item['quantity'] * (1 - item['discount_percent'] / 100) for item in self.items)
        vat = subtotal * 0.20
        total = subtotal + vat
        
        return {
            'order_number': order_number,
            'date': datetime.now().strftime("%Y-%m-%d"),
            'due_date': (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
            'client': {
                'id': self.client_id_entry.get(),
                'name': self.client_name_entry.get(),
                'email': self.client_email_entry.get(),
                'address': self.client_address_entry.get(),
                'postal_code': self.client_postal_code_entry.get(),
                'city': self.client_city_entry.get(),
                'country': self.client_country_entry.get()
            },
            'items': self.items,
            'subtotal': subtotal,
            'vat': vat,
            'total': total,
            'payment_method': "Virement bancaire",
            'payment_link': "https://phoenixproject.fr/payment",
            'promo_info': "Offre spéciale -20% sur les abonnements annuels"
        }
        
    def _load_product_types(self):
        """Charge les types de produits disponibles depuis la base de données."""
        try:
            db_path = Path("merchand/data/products.db")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Supprimer la table si elle existe pour repartir de zéro
            cursor.execute("DROP TABLE IF EXISTS products")
            
            # Créer la table products
            cursor.execute("""
                CREATE TABLE products (
                    product_id TEXT PRIMARY KEY,
                    product_type TEXT NOT NULL,
                    name TEXT NOT NULL,
                    duration TEXT,
                    price REAL NOT NULL,
                    description TEXT,
                    display_order INTEGER
                )
            """)
            
            # Insérer les données de test
            test_products = [
                ('LICENSE1W', 'License', 'License 1 Semaine', '1 semaine', 9.99, 'License hebdomadaire', 1),
                ('LICENSE1M', 'License', 'License 1 Mois', '1 mois', 29.99, 'License mensuelle', 2),                
                ('LICENSE3M', 'License', 'License 3 Mois', '3 mois', 79.99, 'License trimestrielle', 3), 
                ('LICENSE6M', 'License', 'License 6 Mois', '6 mois', 149.99, 'License semestrielle', 4),
                ('LICENSE1Y', 'License', 'License 1 An', '1 an', 299.99, 'License annuelle', 5),      
                ('SUPPORT1M', 'Support', 'Support 1 Mois', '1 mois', 49.99, 'Support mensuel', 6),
                ('SUPPORT3M', 'Support', 'Support 3 Mois', '3 mois', 129.99, 'Support trimestriel', 7),
                ('SUPPORT6M', 'Support', 'Support 6 Mois', '6 mois', 249.99, 'Support semestriel', 8),
                ('SUPPORT1Y', 'Support', 'Support 1 An', '1 an', 499.99, 'Support annuel', 9)
            ]
            cursor.executemany("""
                INSERT INTO products (product_id, product_type, name, duration, price, description, display_order)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, test_products)
            conn.commit()
            
            # Vérifier que les données ont été insérées
            cursor.execute("SELECT COUNT(*) FROM products")
            count = cursor.fetchone()[0]
            if count == 0:
                raise Exception("Aucun produit n'a été inséré dans la base de données")
            
            # Récupérer les types de produits uniques
            cursor.execute("SELECT DISTINCT product_type FROM products ORDER BY product_type")
            types = [row[0] for row in cursor.fetchall()]
            
            if not types:
                raise Exception("Aucun type de produit trouvé dans la base de données")
                
            conn.close()
            
            # Mettre à jour la combobox
            self.product_type_combo['values'] = types
            self.product_type_combo.set(types[0])
            self._on_product_type_selected(None)
            
        except Exception as e:
            print(f"Erreur lors du chargement des types de produits : {e}")
            messagebox.showerror("Erreur", f"Erreur lors du chargement des types de produits : {e}")
            # Créer un dossier data s'il n'existe pas
            data_dir = Path("merchand/data")
            data_dir.mkdir(parents=True, exist_ok=True)

    def _on_product_type_selected(self, event):
        """Charge les produits du type sélectionné depuis la base de données."""
        product_type = self.product_type_combo.get()
        if not product_type:
            return
            
        db_path = Path("merchand/data/products.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Récupérer les produits du type sélectionné
        cursor.execute("""
            SELECT product_id, name, duration, price 
            FROM products 
            WHERE product_type = ? 
            ORDER BY display_order
        """, (product_type,))
        products = cursor.fetchall()
        conn.close()
        
        # Mettre à jour la liste des produits
        self.product_combo['values'] = [f"{p[1]} ({p[2]})" for p in products]
        if products:
            self.product_combo.set(self.product_combo['values'][0])
            self._update_unit_price(products[0])

    def _on_product_selected(self, event):
        """Met à jour le prix unitaire quand un produit est sélectionné."""
        product_name = self.product_combo.get()
        if not product_name:
            return
            
        product_type = self.product_type_combo.get()
        if not product_type:
            return
            
        db_path = Path("merchand/data/products.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Récupérer le produit sélectionné
        cursor.execute("""
            SELECT product_id, name, duration, price 
            FROM products 
            WHERE product_type = ? AND name = ?
        """, (product_type, product_name.split(" (")[0]))
        product = cursor.fetchone()
        conn.close()
        
        if product:
            self._update_unit_price(product)

    def _update_unit_price(self, product):
        """Met à jour l'affichage du prix unitaire."""
        self.update_price_field(self.price_entry, product[3])
        
        # Mettre à jour les totaux si des articles existent
        if self.items:
            self._update_items_tree()
            self._update_totals()
            
    def _on_discount_changed(self, event):
        """Recalcule les prix quand la réduction change."""
        self._update_items_tree()
        self._update_totals()
        
    def _add_item(self):
        """Ajoute un article à la liste."""
        try:
            product_type = self.product_type_combo.get()
            product_name = self.product_combo.get()
            quantity = int(self.quantity_combo.get())
            discount = int(self.discount_combo.get())
            
            if not product_name:
                messagebox.showerror("Erreur", "Veuillez sélectionner un produit")
                return
                
            # Récupérer les informations du produit
            db_path = Path("merchand/data/products.db")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT product_id, name, duration, price 
                FROM products 
                WHERE product_type = ? AND name = ?
            """, (product_type, product_name.split(" (")[0]))
            selected_product = cursor.fetchone()
            conn.close()
            
            if not selected_product:
                messagebox.showerror("Erreur", "Produit non trouvé")
                return
                
            item_data = {
                'product_id': selected_product[0],
                'name': selected_product[1],
                'duration': selected_product[2],
                'base_price': selected_product[3],
                'quantity': quantity,
                'discount_percent': discount
            }
            
            self.add_item(item_data)
            self._update_items_tree()
            self._update_totals()
            
            # Réinitialiser les champs
            self.quantity_combo.set('1')
            self.discount_combo.set('0')
            
        except Exception as e:
            print(f"Erreur lors de l'ajout de l'article : {e}")
            messagebox.showerror("Erreur", f"Erreur lors de l'ajout de l'article : {e}")
            
    def _update_item(self, index):
        """Met à jour l'article à l'index donné."""
        item = self.items[index]
        
        # Ouvrir une fenêtre de dialogue pour modifier l'article
        dialog = tk.Toplevel(self)
        dialog.title("Modifier l'article")
        dialog.geometry("300x200")
        
        ttk.Label(dialog, text="Quantité:").pack(padx=5, pady=2)
        quantity_spin = ttk.Spinbox(dialog, from_=1, to=100, width=5)
        quantity_spin.set(item['quantity'])
        quantity_spin.pack(padx=5, pady=2)
        
        ttk.Label(dialog, text="Réduction (%):").pack(padx=5, pady=2)
        discount_spin = ttk.Spinbox(dialog, from_=0, to=100, increment=10, width=5)
        discount_spin.set(item['discount_percent'])
        discount_spin.pack(padx=5, pady=2)
        
        def save_changes():
            item['quantity'] = int(quantity_spin.get())
            item['discount_percent'] = int(discount_spin.get())
            self._update_items_tree()
            self._update_totals()
            dialog.destroy()
            
        ttk.Button(dialog, text="Enregistrer", command=save_changes).pack(pady=10)
        
    def _update_totals(self):
        """Met à jour les totaux."""
        subtotal = sum(float(item['base_price']) * item['quantity'] * (1 - item['discount_percent'] / 100) for item in self.items)
        vat = subtotal * 0.20
        total = subtotal + vat
        
        self.subtotal_label.config(text=self.format_currency(subtotal))
        self.vat_label.config(text=self.format_currency(vat))
        self.total_label.config(text=self.format_currency(total))
        
    def _preview_order(self):
        """Prévisualise le bon de commande."""
        if not self._validate_data():
            return
            
        order_data = self._prepare_order_data()
        pdf_path = self.order_generator.generate_order(order_data)
        
        if pdf_path:
            # Ouvrir le PDF avec le visualiseur par défaut
            os.startfile(pdf_path)
            
    def _print_order(self):
        """Imprime le bon de commande."""
        if not self._validate_data():
            return
            
        order_data = self._prepare_order_data()
        pdf_path = self.order_generator.generate_order(order_data)
        
        if pdf_path:
            if self.print_document(pdf_path):
                messagebox.showinfo("Succès", "Impression lancée")
            else:
                messagebox.showerror("Erreur", "Erreur lors de l'impression")
                
    def _validate_data(self):
        """Valide les données du bon de commande."""
        if not self.items:
            messagebox.showerror("Erreur", "Veuillez ajouter au moins un article")
            return False
            
        if not self.client_id_entry.get():
            messagebox.showerror("Erreur", "Veuillez saisir l'ID client")
            return False
            
        if not self.client_email_entry.get():
            messagebox.showerror("Erreur", "Veuillez saisir l'email client")
            return False
            
        return True
        
    def _load_clients(self):
        """Charge la liste des clients depuis la base."""
        db_path = Path("merchand/data/clients.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT client_id, name FROM clients ORDER BY name")
        self.clients_list = cursor.fetchall()
        conn.close()
        self._update_client_combo()

    def _update_client_combo(self, filter_txt=""):
        """Met à jour la liste déroulante des clients selon le filtre."""
        filtered = [f"{name} ({cid})" for cid, name in self.clients_list if filter_txt.lower() in name.lower() or filter_txt.lower() in cid.lower()]
        self.client_combo['values'] = filtered

    def _on_client_filter(self, event):
        filter_txt = self.client_combo_var.get()
        self._update_client_combo(filter_txt)

    def _on_client_selected(self, event):
        """Gère la sélection d'un client dans la combobox."""
        selection = self.client_combo_var.get()
        if not selection:
            return
            
        # Extraire l'ID client
        try:
            if '(' in selection and ')' in selection:
                cid = selection.split('(')[-1].split(')')[0].strip()
            else:
                cid = selection.strip()
                
            self.selected_client_id = cid
            self._fill_client_fields_from_db(cid)
            
        except Exception as e:
            print(f"Erreur lors de la sélection du client : {e}")
            messagebox.showerror("Erreur", f"Erreur lors de la sélection du client : {e}")

    def _fill_client_fields_from_db(self, client_id):
        """Récupère et affiche les données du client depuis la base de données."""
        try:
            db_path = Path("merchand/data/clients.db")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Vérifier si la colonne postal_code existe
            cursor.execute("PRAGMA table_info(clients)")
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'postal_code' not in columns:
                # Ajouter la colonne postal_code
                cursor.execute("ALTER TABLE clients ADD COLUMN postal_code TEXT")
                conn.commit()
            
            # Récupérer les données du client
            cursor.execute("""
                SELECT client_id, name, email, address, postal_code, city, country 
                FROM clients 
                WHERE client_id = ?
            """, (client_id,))
            
            client = cursor.fetchone()
            conn.close()
            
            if client:
                self._fill_client_fields(client)
            else:
                messagebox.showwarning("Attention", f"Client {client_id} non trouvé dans la base de données.")
                
        except Exception as e:
            print(f"Erreur lors de la récupération des données client : {e}")
            messagebox.showerror("Erreur", f"Erreur lors de la récupération des données client : {e}")

    def _fill_client_fields(self, client_tuple):
        """Remplit les champs client avec les données de la base."""
        try:
            # ID client (lecture seule)
            self.client_id_entry.config(state='normal')
            self.client_id_entry.delete(0, tk.END)
            self.client_id_entry.insert(0, client_tuple[0])
            self.client_id_entry.config(state='readonly')
            
            # Autres champs
            self.client_name_entry.delete(0, tk.END)
            self.client_name_entry.insert(0, client_tuple[1] or '')
            
            self.client_email_entry.delete(0, tk.END)
            self.client_email_entry.insert(0, client_tuple[2] or '')
            
            self.client_address_entry.delete(0, tk.END)
            self.client_address_entry.insert(0, client_tuple[3] or '')
            
            self.client_postal_code_entry.delete(0, tk.END)
            self.client_postal_code_entry.insert(0, client_tuple[4] or '')
            
            self.client_city_entry.delete(0, tk.END)
            self.client_city_entry.insert(0, client_tuple[5] or '')
            
            self.client_country_entry.delete(0, tk.END)
            self.client_country_entry.insert(0, client_tuple[6] or '')
            
            # Activer le bouton de sauvegarde
            self.save_client_btn.config(state='normal')
            
        except Exception as e:
            print(f"Erreur lors du remplissage des champs client : {e}")
            messagebox.showerror("Erreur", f"Erreur lors du chargement des données client : {e}")

    def _save_client(self):
        if not self.selected_client_id:
            messagebox.showerror("Erreur", "Aucun client sélectionné.")
            return
        if not messagebox.askyesno("Confirmation", "Voulez-vous vraiment enregistrer les modifications pour ce client ?"):
            return
            
        db_path = Path("merchand/data/clients.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Vérifier si la colonne postal_code existe
        cursor.execute("PRAGMA table_info(clients)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'postal_code' not in columns:
            # Ajouter la colonne postal_code
            cursor.execute("ALTER TABLE clients ADD COLUMN postal_code TEXT")
            conn.commit()
        
        # Mettre à jour les données du client
        cursor.execute("""
            UPDATE clients SET
                name=?, email=?, address=?, city=?, country=?, postal_code=?
            WHERE client_id=?
        """, (
            self.client_name_entry.get(),
            self.client_email_entry.get(),
            self.client_address_entry.get(),
            self.client_city_entry.get(),
            self.client_country_entry.get(),
            self.client_postal_code_entry.get(),
            self.selected_client_id
        ))
        conn.commit()
        conn.close()
        messagebox.showinfo("Succès", "Les données du client ont été mises à jour.")
        self.save_client_btn.config(state='disabled')
        self._load_clients()

    def _reset_grid(self):
        """Réinitialise la grille et les totaux."""
        # Vider la liste des articles
        self.items = []
        
        # Vider la grille
        for item in self.items_tree.get_children():
            self.items_tree.delete(item)
            
        # Réinitialiser les totaux
        self.subtotal_label.config(text="0.00 €")
        self.vat_label.config(text="0.00 €")
        self.total_label.config(text="0.00 €")
        
        # Réinitialiser les champs de produit
        self.quantity_combo.set('1')
        self.discount_combo.set('0')
        self.price_entry.delete(0, tk.END)
        
        # Vider le frame des totaux par type
        for widget in self.type_totals_frame.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    app = OrderEditor()
    app.mainloop() 