import time

from selenium.webdriver.common.by import By
from .base_page import BasePage
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By





class ListGeneratorPage(BasePage):

    NEW_BUTTON = (By.XPATH, "//span[text()='NEW']")

    def __init__(self,driver):
        super().__init__(driver)

    def click_newlist(self):
        try:
            wait = WebDriverWait(self.driver, 10)

            # === Eğer modal varsa kapat ===
            try:
                modal_close = WebDriverWait(self.driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'modal-close')]"))
                )
                print("Modal bulundu, kapatılıyor.")
                modal_close.click()
                time.sleep(1)
            except:
                print("Modal bulunamadı, devam ediliyor.")

            # === Canvas ya da benzeri engelleyici varsa gizlenmesini bekle ===
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.invisibility_of_element_located((By.CSS_SELECTOR, "canvas"))
                )
            except:
                print("Canvas görünür olabilir ama devam ediliyor.")

            # === NEW butonunu al ===
            new_button = wait.until(
                EC.presence_of_element_located((By.XPATH, "//span[text()='NEW']"))
            )

            # === Görünür hale getir ===
            self.driver.execute_script("arguments[0].scrollIntoView(true);", new_button)
            time.sleep(0.5)

            # === JavaScript ile zorla tıkla ===
            self.driver.execute_script("arguments[0].click();", new_button)
            print("NEW butonuna JavaScript ile tıklandı.")
            return True

        except Exception as e:
            print(f"NEW butonuna tıklama başarısız: {e}")
            return False

    def click_deletelist_andconfirm_button(self,projectname):

        """ List'i sonuna kadar sil"""

        print("Delete butonuna tıklanıyor")

        APPDELETE_BUTTON = (By.XPATH,
                             f"//span[text()='{projectname}']/ancestor::tr//button[contains(@class, 'delete-btn')]")

        success = self.click_element(APPDELETE_BUTTON)
        if success:
            print("DELETE butonuna başarıyla tıklandı")
            DELETE_CONFIRM_BUTTON = (By.XPATH, "//span[text()='DELETE']")
            confirm_success = self.click_element(DELETE_CONFIRM_BUTTON)
            if confirm_success:
                print("Delete confirmation butonuna başarıyla tıklandı")
            else:
                print("Delete confirmation butonuna tıklanamadı")

            return confirm_success
        else:
            print("DELETE butonuna tıklanamadı")
        return success

    def click_appedit_button(self, projectname):
        """List Edit butonuna tıkla"""
        print("App Edit butonuna tıklanıyor")

        APPEDITBUTTON = (By.XPATH,f"//span[text()='{projectname}']/ancestor::tr//button[contains(@class, 'edit-btn')]")

        success = self.click_element(APPEDITBUTTON)
        if success:
            print("List Edit butonuna başarıyla tıklandı")
        else:
            print("List Edit butonuna tıklanamadı")
        return success

