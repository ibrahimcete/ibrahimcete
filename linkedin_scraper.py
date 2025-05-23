# linkedin_scraper.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import os

def get_linkedin_contact_info(linkedin_url, linkedin_email, linkedin_pass, screenshot_path="linkedin_contact.png"):
    """
    LinkedIn profilinde giriş yapar, Contact Info ekranını açar ve ekran görüntüsü alır.
    """
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--window-size=1280,900")
    # Oturum cookie dosyası eklemek istersen, buraya eklersin.

    driver = webdriver.Chrome(options=options)
    try:
        # LinkedIn login
        driver.get("https://www.linkedin.com/login")
        time.sleep(2)
        driver.find_element(By.ID, "username").send_keys(linkedin_email)
        driver.find_element(By.ID, "password").send_keys(linkedin_pass)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        time.sleep(4)

        # Profile open
        driver.get(linkedin_url)
        time.sleep(4)

        # "Contact Info" butonunu bul ve tıkla
        contact_info_btn = None
        try:
            contact_info_btn = driver.find_element(By.XPATH, "//a[contains(@href,'contact-info')]")
            contact_info_btn.click()
            time.sleep(2)
        except Exception:
            print("[INFO] Contact Info butonu bulunamadı veya profil herkese açık değil.")

        # Ekran görüntüsü al
        driver.save_screenshot(screenshot_path)
        print(f"[OK] LinkedIn Contact Info ekran görüntüsü: {screenshot_path}")

    except Exception as e:
        print(f"[ERROR] LinkedIn scraping error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    # Test amaçlı:
    LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL", "seninmailin@domain.com")
    LINKEDIN_PASS = os.getenv("LINKEDIN_PASS", "şifren")
    TEST_LINK = "https://www.linkedin.com/in/.../"  # Gerçek profil linkini yaz!
    get_linkedin_contact_info(TEST_LINK, LINKEDIN_EMAIL, LINKEDIN_PASS)
