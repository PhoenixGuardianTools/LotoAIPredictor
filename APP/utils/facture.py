from fpdf import FPDF
import datetime
import os

def generer_facture(nom_client, duree, date):
    try:
        dossier = "FACTURES"
        os.makedirs(dossier, exist_ok=True)

        tva_txt = "Non applicable"
        prix_base = 15
        duree_map = {
            "1 mois": 15,
            "3 mois": 40,
            "6 mois": 75,
            "1 an": 120
        }
        total = duree_map.get(duree, 15)

        nom_fichier = f"{dossier}/facture_{nom_client}_{date}.pdf"
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        pdf.cell(200, 10, txt="Facture LotoAiPredictor", ln=True, align="C")
        pdf.cell(200, 10, txt=f"Client : {nom_client}", ln=True)
        pdf.cell(200, 10, txt=f"Durée : {duree}", ln=True)
        pdf.cell(200, 10, txt=f"Date : {date}", ln=True)
        pdf.cell(200, 10, txt=f"Montant : {total} € TTC", ln=True)
        pdf.cell(200, 10, txt=f"TVA : {tva_txt}", ln=True)
        pdf.cell(200, 10, txt="Entreprise : ProjetPhoenix SASU", ln=True)

        pdf.output(nom_fichier)

        # Optionnel : envoi mail + ajout CRM
        with open("DATABASE/clients.csv", "a", encoding="utf-8") as f:
            f.write(f"{nom_client},{duree},{date},{total}€\n")

        return True
    except Exception as e:
        print("Erreur facture:", e)
        return False
