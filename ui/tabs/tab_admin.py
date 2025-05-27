import tkinter as tk
from tkinter import ttk, messagebox
from core.predictor import set_active_model
from utils.smtp_handler import test_smtp_connection
from core.encryption import update_config_admin, decrypt_ini
import smtplib
from email.mime.text import MIMEText
from subprocess import run

class AdminTab(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack(fill="both", expand=True)

        # Modèle de prédiction
        tk.Label(self, text="🎯 Modèle actif :").pack(anchor="w", padx=5, pady=2)
        self.model_selector = ttk.Combobox(self, values=["Modèle A (standard)", "Modèle B (optimisé)"], state="readonly")
        self.model_selector.current(0)
        self.model_selector.pack(fill="x", padx=5, pady=2)
        self.model_selector.bind("<<ComboboxSelected>>", lambda e: self.set_model())

        # SMTP
        smtp_frame = tk.LabelFrame(self, text="📡 Configuration SMTP")
        smtp_frame.pack(fill="x", padx=5, pady=5)
        tk.Label(smtp_frame, text="Serveur SMTP :").pack(anchor="w", padx=5, pady=2)
        self.smtp_host = tk.Entry(smtp_frame)
        self.smtp_host.pack(fill="x", padx=5, pady=2)
        tk.Label(smtp_frame, text="Port :").pack(anchor="w", padx=5, pady=2)
        self.smtp_port = tk.Entry(smtp_frame)
        self.smtp_port.pack(fill="x", padx=5, pady=2)
        smtp_test = tk.Button(smtp_frame, text="Tester la connexion", command=self.test_smtp)
        smtp_test.pack(padx=5, pady=5)

        # Entreprise
        ent_frame = tk.LabelFrame(self, text="🏢 Informations entreprise")
        ent_frame.pack(fill="x", padx=5, pady=5)
        tk.Label(ent_frame, text="Nom entreprise :").pack(anchor="w", padx=5, pady=2)
        self.nom_entreprise = tk.Entry(ent_frame)
        self.nom_entreprise.pack(fill="x", padx=5, pady=2)
        tk.Label(ent_frame, text="SIRET (optionnel) :").pack(anchor="w", padx=5, pady=2)
        self.siret = tk.Entry(ent_frame)
        self.siret.pack(fill="x", padx=5, pady=2)
        tk.Label(ent_frame, text="Site web :").pack(anchor="w", padx=5, pady=2)
        self.site_web = tk.Entry(ent_frame)
        self.site_web.pack(fill="x", padx=5, pady=2)
        save_btn = tk.Button(ent_frame, text="💾 Sauvegarder", command=self.save_config)
        save_btn.pack(padx=5, pady=5)

        # Feedback
        fb_frame = tk.LabelFrame(self, text="📬 Contact support")
        fb_frame.pack(fill="x", padx=5, pady=5)
        self.fb_subject = tk.Entry(fb_frame)
        self.fb_subject.insert(0, "Sujet")
        self.fb_subject.pack(fill="x", padx=5, pady=2)
        self.fb_message = tk.Text(fb_frame, height=4)
        self.fb_message.insert("1.0", "Votre message...")
        self.fb_message.pack(fill="x", padx=5, pady=2)
        fb_btn = tk.Button(fb_frame, text="Envoyer", command=self.send_feedback)
        fb_btn.pack(padx=5, pady=5)

        # Statistiques web
        web_btn = tk.Button(self, text="🌐 Publier les statistiques web", command=self.publish_web)
        web_btn.pack(fill="x", padx=5, pady=10)

    def set_model(self):
        model = "A" if self.model_selector.current() == 0 else "B"
        set_active_model(model)
        messagebox.showinfo("Succès", f"Modèle {model} activé.")

    def test_smtp(self):
        try:
            test_smtp_connection(self.smtp_host.get(), int(self.smtp_port.get()))
            messagebox.showinfo("Succès", "Connexion SMTP valide.")
        except Exception as e:
            messagebox.showerror("Erreur SMTP", str(e))

    def save_config(self):
        data = {
            "smtp_host": self.smtp_host.get(),
            "smtp_port": self.smtp_port.get(),
            "entreprise": self.nom_entreprise.get(),
            "siret": self.siret.get(),
            "site": self.site_web.get()
        }
        update_config_admin(data)
        messagebox.showinfo("Sauvegardé", "Configuration enregistrée.")

    def send_feedback(self):
        subject = self.fb_subject.get().strip()
        message = self.fb_message.get("1.0", "end").strip()
        if not message:
            messagebox.showwarning("Erreur", "Message vide.")
            return

        try:
            config = decrypt_ini("SECURITY/config_admin.ini.enc")
            msg = MIMEText(message)
            msg["Subject"] = subject or "Feedback Admin"
            msg["From"] = config["email"]
            msg["To"] = "contact@phoenixproject.onmicrosoft.com"

            with smtplib.SMTP_SSL(config["smtp_host"], int(config["smtp_port"])) as server:
                server.login(config["email"], config["token"])
                server.send_message(msg)

            messagebox.showinfo("Envoyé", "Message transmis avec succès.")
            self.fb_subject.delete(0, tk.END)
            self.fb_message.delete("1.0", tk.END)
        except Exception as e:
            messagebox.showerror("Erreur", f"Envoi échoué : {e}")

    def publish_web(self):
        try:
            run(["python", "TOOLS/export_web_data.py"], check=True)
            run(["cmd", "/c", "start", "ADMIN_TOOLS/web_push.bat"])
            messagebox.showinfo("Publication", "Statistiques web publiées avec succès.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Publication échouée : {e}")
