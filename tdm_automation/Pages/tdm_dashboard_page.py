from selenium.webdriver.common.by import By
from .base_page import BasePage

class TDMDashboardPage(BasePage):

    #Locatorlar
    DASHBOARD_HEADER = (By.CSS_SELECTOR,".header-page-title")
    INFO_BUTTON = (By.XPATH,"//button[contains(@class, 'user-icon')][1]")
    APPMAN_BUTTON = (By.XPATH,"//span[text()='APPLICATION MANAGEMENT']")
    FLOWMAN_BUTTON = (By.XPATH,"//span[text()='FLOW MANAGEMENT']")
    LISTGEN_BUTTON = (By.XPATH,"//span[text()='List Generator']")


    def __init__(self,driver):
        super().__init__(driver)

    def is_dashboard_loaded(self):
        """Dashboard'ın yüklendiğini kontrol et"""

        header_element = self.find_element(self.DASHBOARD_HEADER)
        if header_element and "Dashboard" in header_element.text:
            return True
        return False

    def click_info_button(self):
        """Info butonuna tıkla"""
        print("info butonuna tıklanıyor")

        success = self.click_element(self.INFO_BUTTON)
        if success:
             print("Info butonuna başarıyla tıklandı")
        else:
              print("Info butonuna tıklanamadı")
        return success


    def click_application_management(self):
        """ Applicatoin Management'a tıkla"""
        print("App man'a tıklanıyor")

        success = self.click_element((self.APPMAN_BUTTON))
        if success:
             print("App Man butonuna başarıyla tıklandı")
        else:
              print("App Man butonuna tıklanamadı")
        return success

    def click_flow_managemnet(self):

        """ Flow Management'a tıkla"""

        success = self.click_element((self.FLOWMAN_BUTTON))
        if success:
            print("Flow Man butonuna başarıyla tıklandı")
        else:
            print("Flow Man butonuna tıklanamadı")
        return success

    def click_list_generator(self):

        """ List Generator'e tıkla"""

        self.click_flow_managemnet()
        
        success = self.click_element((self.LISTGEN_BUTTON))
        if success:
            print("List Generator butonuna başarıyla tıklandı")
        else:
            print("List Generator butonuna tıklanamadı")
        return success


