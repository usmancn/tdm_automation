import time

from selenium.webdriver.common.by import By
from .base_page import BasePage



class CreateFlowPage(BasePage):


    FLOWNAME_FIELD = (By.ID, "name")
    ENV_DROPDOWN = (By.XPATH,"//div[contains(@class, 'ant-select-selector') and .//input[@id='db_id']]")
    SCHEMA_CHECKBOX= (By.XPATH, "//tr[@data-row-key='schema_1']//span[contains(@class, 'ant-checkbox')]")
    TABLE_CHECKBOX= (By.XPATH, "//tr[@data-row-key='schema_1.table_1']//span[contains(@class, 'ant-checkbox')]")
    SCHEMA_TRANFER=(By.XPATH,"(//button[contains(@class, 'ant-btn-primary')])[1]")
    TABLE_TRANFER = (By.XPATH, "(//button[contains(@class, 'ant-btn-primary')])[3]")
    SAVE_BUTTON = (By.XPATH, "(//button[contains(@class,'save-btn')])[1]")
    CANCEL_BUTTON = (By.XPATH, "//button[text()='CANCEL']")








    def __init__(self,driver):
        super().__init__(driver)


    def enter_flowname(self,appname):
        return self.enter_text(self.FLOWNAME_FIELD, appname)


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
        """Dropdown aç ve seçenek seç"""
        try:
            # Dropdown'ı aç
            if not self.open_dropdown(dropdown_locator):
                return False

            # Seçeneği bul ve tıkla
            option_locator = (By.XPATH,
                              f"//div[contains(@class, 'ant-select-item') and contains(text(), '{option_text}')]")
            success = self.click_element(option_locator)

            if success:
                print(f"Seçenek seçildi: {option_text}")
            return success

        except Exception as e:
            print(f"Dropdown seçim hatası: {e}")
            return False


    def select_env(self,env_name):
        """ env seç"""
        return self.select_dropdown_option(self.ENV_DROPDOWN,env_name)

    def click_schema(self):

        """Schema checkboxa tıkla"""
        print("Şema seçiliyor")

        success = self.click_element(self.SCHEMA_CHECKBOX)
        if success:
            print("Şema başarıyla seçildi")
        else:
            print("Şema seçilemedi")
        return success

    def click_table(self):

        """ Table chechboxa tıkla"""
        print("Table seçiliyor")

        success= self.click_element_with_scroll(self.TABLE_CHECKBOX)
        if success:
            print("Table başarıyla seçildi")
        else:
            print("Table seçilemedi")
        return success

    def click_transferschema(self):
        """Schemayı tranfer et"""
        print("Schema transfer ediliyor")
        success = self.click_element(self.SCHEMA_TRANFER)
        if success:
            print("Başarıyla transfer oldu")
        else:
            print("Schema transfer olamadı")
        return success

    def click_transfertable(self):
        """Table tranfer et"""
        print("Table transfer ediliyor")
        success = self.click_element_with_scroll(self.TABLE_TRANFER)
        if success:
            print("Başarıyla transfer oldu")
        else:
            print("Table transfer olamadı")
        return success


    def click_save_button(self):
        """SAVE butonuna tıkla """
        print("SAVE butonuna tıklanıyor ")
        return self.click_element_with_scroll(self.SAVE_BUTTON)

    def click_cancel_button(self):
        """CANCEL butonuna tıkla (tüm tab'lar için)"""
        print("CANCEL butonuna tıklanıyor")
        return self.click_element_with_scroll(self.CANCEL_BUTTON)




