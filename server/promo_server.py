from flask import Flask, jsonify, request
import json
import hashlib
from datetime import datetime
from pathlib import Path

app = Flask(__name__)

# Chemins des fichiers
PROMO_PATH = Path("PROMOTIONS/promo_templates.json")
BANDEAU_PATH = Path("PROMOTIONS/bandeau_default.json")

def get_promo_hash():
    """Calcule le hash des fichiers de promotion."""
    hashes = {}
    if PROMO_PATH.exists():
        with open(PROMO_PATH, 'rb') as f:
            hashes['promo'] = hashlib.md5(f.read()).hexdigest()
    if BANDEAU_PATH.exists():
        with open(BANDEAU_PATH, 'rb') as f:
            hashes['bandeau'] = hashlib.md5(f.read()).hexdigest()
    return hashes

@app.route('/promos/hash', methods=['GET'])
def get_hash():
    """Endpoint pour récupérer le hash des promotions."""
    return jsonify(get_promo_hash())

@app.route('/promos/data', methods=['GET'])
def get_data():
    """Endpoint pour récupérer les données des promotions."""
    data = {
        'promo': {},
        'bandeau': {},
        'hash': get_promo_hash()
    }
    
    if PROMO_PATH.exists():
        with open(PROMO_PATH, 'r') as f:
            data['promo'] = json.load(f)
            
    if BANDEAU_PATH.exists():
        with open(BANDEAU_PATH, 'r') as f:
            data['bandeau'] = json.load(f)
            
    return jsonify(data)

@app.route('/promos/update', methods=['POST'])
def update_promos():
    """Endpoint pour mettre à jour les promotions (admin uniquement)."""
    # Vérification de l'authentification admin
    auth = request.headers.get('Authorization')
    if not auth or not verify_admin_token(auth):
        return jsonify({'error': 'Non autorisé'}), 401
        
    try:
        data = request.json
        
        # Mise à jour des fichiers
        with open(PROMO_PATH, 'w') as f:
            json.dump(data['promo'], f, indent=2)
            
        with open(BANDEAU_PATH, 'w') as f:
            json.dump(data['bandeau'], f, indent=2)
            
        return jsonify({
            'success': True,
            'message': 'Promotions mises à jour',
            'hash': get_promo_hash()
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

def verify_admin_token(token):
    """Vérifie le token d'authentification admin."""
    # À implémenter selon votre système d'authentification
    return True

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 