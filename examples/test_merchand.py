from merchand import ClientManager, InvoiceManager, PaymentManager
from datetime import datetime
import uuid

def test_merchand_system():
    # Initialisation
    client_manager = ClientManager()
    invoice_manager = InvoiceManager()
    payment_manager = PaymentManager()
    
    # Test création client
    test_client = {
        "name": "John Doe",
        "email": "john@example.com",
        "address": "123 Test Street",
        "city": "Paris",
        "country": "France"
    }
    
    test_uuid = str(uuid.uuid4())
    success, referral_code = client_manager.create_client(
        test_client["email"],
        "1990-01-01",
        test_uuid
    )
    
    print(f"✅ Création client : {'Succès' if success else 'Échec'}")
    print(f"📝 Code de parrainage : {referral_code}")
    
    # Test génération facture
    items = [
        {
            "description": "Licence LotoAiPredictor - 1 an",
            "quantity": 1,
            "price": 29.99
        }
    ]
    
    invoice_number = f"INV-{datetime.now().strftime('%Y%m%d')}-001"
    invoice_path = invoice_manager.generate_invoice(
        test_client,
        items,
        invoice_number,
        "Carte bancaire"
    )
    
    print(f"\n📄 Génération facture : {'Succès' if invoice_path else 'Échec'}")
    if invoice_path:
        print(f"Chemin : {invoice_path}")
    
    # Test paiement
    payment_success, payment_info = payment_manager.process_payment(
        test_client,
        items,
        "card",
        invoice_number
    )
    
    print(f"\n💳 Test paiement : {'Succès' if payment_success else 'Échec'}")
    if payment_success:
        print(f"Informations : {payment_info}")
        
        # Vérification du paiement
        verification = payment_manager.verify_payment(payment_info, "card")
        print(f"Vérification : {'Validé' if verification else 'Échec'}")
    
    # Test remboursement
    if payment_success:
        refund_success, refund_id = payment_manager.refund_payment(
            payment_info,
            "card",
            29.99
        )
        print(f"\n💸 Test remboursement : {'Succès' if refund_success else 'Échec'}")
        if refund_success:
            print(f"ID remboursement : {refund_id}")

if __name__ == "__main__":
    test_merchand_system() 