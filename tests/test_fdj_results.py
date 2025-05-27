import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.fdj_data_manager import FDJDataManager

def test_latest_results():
    manager = FDJDataManager()
    
    # Test pour chaque jeu
    games = ['LOTO', 'EUROMILLIONS', 'KENO', 'EURODREAMS']
    
    for game in games:
        print(f"\nTest des résultats pour {game}:")
        result = manager.get_latest_results(game)
        
        if result:
            print(f"Date du tirage: {result['date']}")
            print(f"Numéros: {result['numbers']}")
            print(f"Numéros spéciaux: {result['special_numbers']}")
            print(f"Jackpot: {result['jackpot']}")
        else:
            print(f"Aucun résultat trouvé pour {game}")

if __name__ == "__main__":
    test_latest_results() 