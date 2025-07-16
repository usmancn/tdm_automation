
from selenium.webdriver.common.by import By
from .base_page import BasePage





class CreateAppPage(BasePage):


    APPNAME_FIELD = (By.ID, "name")
    VERSION_FIELD = (By.XPATH,"//input[@type='text' and @placeholder='Version']")
    ADD_BUTTON= (By.XPATH,"//span[text()='ADD']")
    SAVE_BUTTON= (By.XPATH,"(//button[contains(@class,'save-btn')])[2]")




    def __init__(self,driver):
        super().__init__(driver)



    def enter_appname(self,appname):
        return self.enter_text(self.APPNAME_FIELD, appname)

    def enter_version(self,version):
        return self.enter_text(self.VERSION_FIELD,version)

    def click_versionadd_button(self):

        """Add butonuna tıkla"""
        print("Add butonuna tıklanıyor")

        success = self.click_element(self.ADD_BUTTON)
        if success:
            print("New butonuna başarıyla tıklandı")
        else:
            print("New butonuna tıklanamadı")
        return success

    def click_save_button(self):

        """Save butonuna tıkla """

        print("Save butonuna tıklanıyor")

        success = self.click_element(self.SAVE_BUTTON)
        if success:
            print("Save butonuna başarıyla tıklandı")
        else:
            print("Save butonuna tıklanamadı")
        return success





