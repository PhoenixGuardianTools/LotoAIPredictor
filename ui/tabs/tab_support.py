import tkinter as tk
from tkinter import ttk, messagebox
from core.encryption import decrypt_ini
from email.mime.text import MIMEText
import smtplib

class SupportTab(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack(fill="both", expand=True)

        tk.Label(self, text="Sujet :").pack(anchor="w", padx=5, pady=2)
        self.subject_selector = ttk.Combobox(self, values=["Message", "Remerciement", "Bug", "Demande d'évolution"], state="readonly")
        self.subject_selector.current(0)
        self.subject_selector.pack(fill="x", padx=5, pady=2)

        tk.Label(self, text="Email :").pack(anchor="w", padx=5, pady=2)
        self.email_field = tk.Entry(self)
        self.email_field.insert(0, "Votre adresse email")
        self.email_field.pack(fill="x", padx=5, pady=2)

        tk.Label(self, text="Message :").pack(anchor="w", padx=5, pady=2)
        self.msg_box = tk.Text(self, height=6, wrap="word")
        self.msg_box.insert("1.0", "Votre message (500 caractères max)")
        self.msg_box.pack(fill="x", padx=5, pady=2)

        send_btn = tk.Button(self, text="📤 Envoyer au support", command=self.send)
        send_btn.pack(padx=5, pady=10)

    def send(self):
        sujet = self.subject_selector.get()
        message = self.msg_box.get("1.0", "end").strip()[:500]
        user_email = self.email_field.get().strip()

        if not user_email or not message or user_email == "Votre adresse email" or message == "Votre message (500 caractères max)":
            messagebox.showwarning(self, "Erreur", "Veuillez remplir tous les champs.")
            return

        try:
            conf = decrypt_ini("SECURITY/config_admin.ini.enc")
            msg = MIMEText(message)
            msg["Subject"] = f"[{sujet}] - Demande utilisateur"
            msg["From"] = conf["email"]
            msg["To"] = conf["support"]
            msg["Cc"] = user_email

            with smtplib.SMTP_SSL(conf["smtp_host"], int(conf["smtp_port"])) as server:
                server.login(conf["email"], conf["token"])
                server.send_message(msg)

            messagebox.showinfo("Envoyé", "Votre message a bien été transmis.")
            self.msg_box.delete("1.0", "end")
        except Exception as e:
            messagebox.showerror("Erreur SMTP", str(e))
