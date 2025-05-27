from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# URLs des pages de résultats FDJ
FDJ_URLS = {
    'LOTO': 'https://www.fdj.fr/jeux-de-tirage/loto/resultats',
    'EUROMILLIONS': 'https://www.fdj.fr/jeux-de-tirage/euromillions-my-million/resultats',
    'KENO': 'https://www.fdj.fr/jeux-de-tirage/keno/resultats',
    'EURODREAMS': 'https://www.fdj.fr/jeux-de-tirage/eurodreams/resultats',
}

def extract_loto(driver):
    print("\n--- LOTO ---")
    driver.get(FDJ_URLS['LOTO'])
    time.sleep(5)  # Augmentation du temps d'attente
    
    # Sauvegarder le HTML pour debug
    with open("loto_debug.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print("HTML Loto sauvegardé dans loto_debug.html")
    
    try:
        # Attendre que les éléments soient présents
        wait = WebDriverWait(driver, 10)
        
        # Numéros principaux
        numbers = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.number, .boule, .numero')))
        numbers = [elem.text for elem in numbers][:5]
        
        # Numéro chance
        chance = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.chance, .lucky, .numero-chance'))).text
        
        # Date
        date = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.date, .date-tirage, .date-resultat'))).text
        
        print(f"Date : {date}")
        print(f"Numéros : {numbers}")
        print(f"Chance : {chance}")
    except Exception as e:
        print(f"Erreur extraction LOTO : {e}")

def extract_euromillions(driver):
    print("\n--- EUROMILLIONS ---")
    driver.get(FDJ_URLS['EUROMILLIONS'])
    time.sleep(5)
    
    # Sauvegarder le HTML pour debug
    with open("euromillions_debug.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print("HTML Euromillions sauvegardé dans euromillions_debug.html")
    
    try:
        wait = WebDriverWait(driver, 10)
        
        numbers = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.number, .boule, .numero')))
        numbers = [elem.text for elem in numbers][:5]
        
        stars = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.star, .etoile, .numero-etoile')))
        stars = [elem.text for elem in stars][:2]
        
        date = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.date, .date-tirage, .date-resultat'))).text
        
        print(f"Date : {date}")
        print(f"Numéros : {numbers}")
        print(f"Étoiles : {stars}")
    except Exception as e:
        print(f"Erreur extraction EUROMILLIONS : {e}")

def extract_keno(driver):
    print("\n--- KENO ---")
    driver.get(FDJ_URLS['KENO'])
    time.sleep(5)
    
    # Sauvegarder le HTML pour debug
    with open("keno_debug.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print("HTML Keno sauvegardé dans keno_debug.html")
    
    try:
        wait = WebDriverWait(driver, 10)
        
        numbers = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.number, .boule, .numero')))
        numbers = [elem.text for elem in numbers][:20]
        
        date = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.date, .date-tirage, .date-resultat'))).text
        
        print(f"Date : {date}")
        print(f"Numéros : {numbers}")
    except Exception as e:
        print(f"Erreur extraction KENO : {e}")

def extract_eurodreams(driver):
    print("\n--- EURODREAMS ---")
    driver.get(FDJ_URLS['EURODREAMS'])
    time.sleep(5)
    
    # Sauvegarder le HTML pour debug
    with open("eurodreams_debug.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print("HTML EuroDreams sauvegardé dans eurodreams_debug.html")
    
    try:
        wait = WebDriverWait(driver, 10)
        
        numbers = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.number, .boule, .numero')))
        numbers = [elem.text for elem in numbers][:6]
        
        dream = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.dream, .numero-dream, .numero-special'))).text
        
        date = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.date, .date-tirage, .date-resultat'))).text
        
        print(f"Date : {date}")
        print(f"Numéros : {numbers}")
        print(f"Dream : {dream}")
    except Exception as e:
        print(f"Erreur extraction EURODREAMS : {e}")

def main():
    # Lancement du navigateur Chrome en mode headless
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    try:
        extract_loto(driver)
        extract_euromillions(driver)
        extract_keno(driver)
        extract_eurodreams(driver)
    finally:
        driver.quit()

if __name__ == "__main__":
    main() 