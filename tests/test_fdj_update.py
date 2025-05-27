from core.database import update_fdj_data, get_recent_draws
from core.regles import GAMES
import traceback

def test_fdj_update():
    """
    Teste la mise à jour des données FDJ pour tous les jeux.
    """
    print("\n🔄 Test de mise à jour des données FDJ...")
    
    # Mise à jour des données
    success = update_fdj_data()
    
    if success:
        print("\n✅ Mise à jour réussie !")
        
        # Affichage des derniers tirages pour chaque jeu
        for game_name in GAMES.keys():
            print(f"\n📊 Derniers tirages pour {game_name}:")
            recent_draws = get_recent_draws(game_name, limit=5)
            
            for date, numbers, special in recent_draws:
                print(f"Date: {date}")
                print(f"Numéros: {numbers}")
                print(f"Spéciaux: {special}")
                print("-" * 30)
    else:
        print("\n❌ Échec de la mise à jour")

if __name__ == "__main__":
    try:
        test_fdj_update()
    except Exception as e:
        print("\n❌ Exception attrapée lors du test :")
        traceback.print_exc() 