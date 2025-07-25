import time

from selenium.webdriver.common.by import By
from .base_page import BasePage
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class FlowEditPage(BasePage):
    GENERATECOUNT = (By.XPATH, "(//input[contains(@class, 'generate-count-input')])[1]")
    COUNT_SAVE = (By.XPATH, "(//button[contains(@class, 'generate-count-save-button')])[1]")
    FLOWSETTING = (By.XPATH, "//tr[.//span[text()='schema_1.table_1']]//button[contains(@class, 'setting-button')]")
    DESC_AREA = (By.XPATH, "//textarea[contains(@class, 'custom-text-area')]")
    ALIAS_AREA = (By.XPATH, "(//input[contains(@class, 'ant-input') and @type='text'])[3]")
    TYPE_DROPDOWN = (By.XPATH, "(//div[contains(@class, 'ant-select-selector')])[3]")
    STRINGMINCHAR = (By.XPATH, "//label[text()='Min Chars']/ancestor::div[contains(@class, 'ant-form-item')]//input")
    STRINGMAXCHAR = (By.XPATH, "//label[text()='Max Chars']/ancestor::div[contains(@class, 'ant-form-item')]//input")
    STRINGPREFIX = (By.XPATH, "//label[text()='Prefix']/ancestor::div[contains(@class, 'ant-form-item')]//input")
    STRINGSUFFIX = (By.XPATH, "//label[text()='Suffix']/ancestor::div[contains(@class, 'ant-form-item')]//input")
    BOOLEANPER = (By.XPATH,
                  "//label[text()='Truth Percentage']/ancestor::div[contains(@class, 'ant-form-item')]//input")
    SAVE_BUTTON = (By.XPATH, "(//button[contains(@class,'save-btn')])[1]")

    MODAL_CLOSE_X = (By.XPATH, "//*[text()='×']")



    def __init__(self, driver):
        super().__init__(driver)

    def enter_generatecount(self, count):
        return self.enter_text(self.GENERATECOUNT, count)

    def confirm_generatecount(self):
        """Generate Counta girilen değeri savele"""
        print("Generate Count save ediliyor")
        success = self.click_element(self.COUNT_SAVE)
        if success:
            print("count başarıyla save e basıldı")
        else:
            print("count savelenemedi")
        return success

    def click_flowsetting(self):
        "Flow Setting butonuna basılıyor"
        print("Flow Setting butonuna tıklanıyor")
        success = self.click_element(self.FLOWSETTING)
        if success:
            print("flow settingse başarıyla basıldı")
        else:
            print("flow settingse girilemedi")
        return success

    def click_colomndesc_button(self, colomnname):
        """Colomn Description butonuna tıkla"""
        print("Colomn Desc butonuna tıklanıyor")
        COLOMNDESCBUTTON = (By.XPATH,
                            f"(//tr[.//span[text()='{colomnname}']]//button[contains(@class, 'edit-btn')])[1]")
        success = self.click_element(COLOMNDESCBUTTON)
        if success:
            print("Colomn Desc butonuna başarıyla tıklandı")
        else:
            print("Colomn desc butonuna tıklanamadı")
        return success

    def enter_desctiption(self, desc):
        """Description gir"""
        return self.enter_text(self.DESC_AREA, desc)

    def click_colomnalias_button(self, colomnname):
        """Colomn Alias butonuna tıkla"""
        print("Colomn Alias butonuna tıklanıyor")
        COLOMNALIASBUTTON = (By.XPATH,
                             f"(//tr[.//span[text()='{colomnname}']]//button[contains(@class, 'edit-btn')])[3]")
        success = self.click_element(COLOMNALIASBUTTON)
        if success:
            print("Colomn Alias butonuna başarıyla tıklandı")
        else:
            print("Colomn alias butonuna tıklanamadı")
        return success

    def enter_alias(self, alias):
        """Alias gir"""
        return self.enter_text(self.ALIAS_AREA, alias)

    def click_colomnedit_button(self, colomnname):
        """Colomn edit butonuna tıkla"""
        print("Colomn edit butonuna tıklanıyor")
        COLOMNEDITBUTTON = (By.XPATH,
                            f"(//tr[.//span[text()='{colomnname}']]//button[contains(@class, 'edit-btn')])[2]")
        success = self.click_element(COLOMNEDITBUTTON)
        if success:
            print("Colomn edit butonuna başarıyla tıklandı")
        else:
            print("Colomn edit butonuna tıklanamadı")
        return success

    def open_dropdown(self, dropdown_locator):
        """Herhangi bir dropdown'ı aç"""
        try:
            success = self.click_element(dropdown_locator)
            if success:
                time.sleep(1)  # Dropdown açılması için bekle
                print("Dropdown açıldı")
            return success
        except Exception as e:
            print(f"Dropdown açma hatası: {e}")
            return False

    def select_dropdown_option(self, dropdown_locator, option_text):
        """Dropdown aç ve seçenek seç - Sadece Arrow Down"""
        try:
            # Dropdown'ı aç
            if not self.open_dropdown(dropdown_locator):
                return False

            print(f"{option_text} aranıyor...")
            time.sleep(1)

            # Dropdown input'a focus yap
            try:
                dropdown_input = self.driver.find_element(By.XPATH,
                                                          "//input[contains(@class, 'ant-select-selection-search-input')]")
                dropdown_input.click()
                time.sleep(0.5)
            except:
                print("Dropdown input bulunamadı, devam ediliyor...")

            # Arrow Down ile aşağı in ve seçeneği ara
            option_xpath = f"//div[contains(@class, 'ant-select-item') and contains(text(), '{option_text}')]"

            max_attempts = 50  # Daha fazla deneme
            for i in range(max_attempts):
                print(f"Arrow Down {i + 1}...")

                # Arrow Down gönder
                focused_elem = self.driver.switch_to.active_element
                focused_elem.send_keys(Keys.ARROW_DOWN)
                time.sleep(0.2)

                # Her arrow down'dan sonra seçeneği ara
                try:
                    element = self.driver.find_element(By.XPATH, option_xpath)
                    if element.is_displayed():
                        element.click()
                        print(f"Seçenek {i + 1}. arrow down'da bulundu: {option_text}")
                        return True
                except:
                    # Bulunamadı, devam et
                    continue

            print(f"50 arrow down sonrası seçenek bulunamadı: {option_text}")
            return False

        except Exception as e:
            print(f"Dropdown seçim hatası: {e}")
            return False

    def select_type(self, type):
        return self.select_dropdown_option(self.TYPE_DROPDOWN, type)

    def stringgen_enter_prefix(self, prefix):
        return self.enter_text(self.STRINGPREFIX, prefix)

    def stringgen_enter_suffix(self, suffix):
        return self.enter_text(self.STRINGSUFFIX, suffix)



    def stringgen_enter_minchar(self, minchar):
        """Min Chars gir - Slow input yöntemi"""
        return self.overwrite_input_slowly(self.driver, self.STRINGMINCHAR[1], minchar)

    def stringgen_enter_maxchar(self, maxchar):
        """Max Chars gir - Slow input yöntemi"""
        return self.overwrite_input_slowly(self.driver, self.STRINGMAXCHAR[1], maxchar)

    def overwrite_input_slowly(self, driver, xpath, value):
        """Zorlu inputlar için tek tek silip tekrar yazma yöntemi"""
        try:
            input_field = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            input_field.click()
            time.sleep(0.2)

            # Önce sona git ve tüm karakterleri sil
            input_text = input_field.get_attribute("value")
            for _ in range(len(input_text)):
                input_field.send_keys(Keys.BACKSPACE)
                time.sleep(0.05)

            # Ardından yeni değeri karakter karakter yaz
            for char in value:
                input_field.send_keys(char)
                time.sleep(0.05)

            input_field.send_keys(Keys.TAB)
            time.sleep(0.2)
            return True

        except Exception as e:
            print(f"[overwrite_input_slowly] Hata: {e}")
            return False

    def click_save_button(self):
        """SAVE butonuna tıkla """
        print("SAVE butonuna tıklanıyor ")
        return self.click_element_with_scroll(self.SAVE_BUTTON)

    def boolean_truht_percentage(self, percantage):
        return self.overwrite_input_slowly(self.driver,self.BOOLEANPER[1], percantage)

    def close_modal_with_x(self):
        """× (times) sembolü ile modal kapat"""
        try:
            print("Modal × butonu ile kapatılıyor...")
            close_button = self.driver.find_element(*self.MODAL_CLOSE_X)
            if close_button.is_displayed():
                close_button.click()
                time.sleep(1)
                print("Modal × butonu ile başarıyla kapatıldı")
                return True
            else:
                print("× butonu görünmüyor")
                return False
        except Exception as e:
            print(f"× butonu ile modal kapatma hatası: {e}")
            return False