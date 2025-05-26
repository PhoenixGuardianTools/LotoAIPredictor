import tkinter as tk
from tkinter import messagebox
from core.mailer import send_email
from datetime import datetime

class FeedbackTab(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack(fill="both", expand=True)

        tk.Label(self, text="💬 Envoyer un message à l'équipe").pack(anchor="w", padx=5, pady=5)

        self.subject = tk.Entry(self)
        self.subject.insert(0, "Sujet")
        self.subject.pack(fill="x", padx=5, pady=2)

        self.message = tk.Text(self, height=8, wrap="word")
        self.message.insert("1.0", "Votre message...")
        self.message.pack(fill="x", padx=5, pady=2)

        send_btn = tk.Button(self, text="Envoyer", command=self.send)
        send_btn.pack(padx=5, pady=10)

    def send(self):
        """Envoie le feedback par email"""
        subject = self.subject.get().strip()
        message = self.message.get("1.0", "end").strip()
        
        if not subject or not message.strip():
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs")
            return
        
        body = f"""
        Nouveau feedback reçu :
        
        Sujet : {subject}
        Date : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        Message :
        {message}
        """
        
        if send_email(subject, body):
            messagebox.showinfo("Succès", "Votre message a été envoyé avec succès")
            self.subject.delete(0, tk.END)
            self.message.delete("1.0", tk.END)
        else:
            messagebox.showerror("Erreur", "L'envoi du message a échoué")
