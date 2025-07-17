from selenium.webdriver.common.by import By
from .base_page import BasePage





class ListGeneratorPage(BasePage):

    NEW_BUTTON = (By.XPATH, "//span[text()='NEW']")

    def __init__(self,driver):
        super().__init__(driver)


    def click_newlist(self):

        """New butonuna tıkla"""
        print("New List Generator butonuna tıklanıyor")

        success = self.click_element(self.NEW_BUTTON)
        if success:
            print("New butonuna başarıyla tıklandı")
        else:
            print("New butonuna tıklanamadı")
        return success

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

