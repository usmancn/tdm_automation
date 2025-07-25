from selenium.webdriver.common.by import By
from .base_page import BasePage





class SyntheticFlowListPage(BasePage):

    NEW_BUTTON = (By.XPATH, "//span[text()='NEW']")

    def __init__(self,driver):
        super().__init__(driver)

    def click_newflow(self):

        """New flow tıkla"""
        print("New Flow butonuna tıklanıyor")

        success = self.click_element(self.NEW_BUTTON)
        if success:
            print("New butonuna başarıyla tıklandı")
        else:
            print("New butonuna tıklanamadı")
        return success

    def click_tableconf(self, projectname):
        """Table Conf butonuna tıkla"""
        print("Table Conf butonuna tıklanıyor")

        TABLECONFBUTTON = (By.XPATH,f"//tr[.//span[text()='{projectname}']]//button[1]")

        success = self.click_element(TABLECONFBUTTON)
        if success:
            print("Table Conf butonuna başarıyla tıklandı")
        else:
            print("Table Conf butonuna tıklanamadı")
        return success

    def click_deleteflow_andconfirm_button(self, projectname):

        """ Flow'u sonuna kadar sil"""

        print("Delete butonuna tıklanıyor")

        FLOWDELETE_BUTTON = (By.XPATH,
                             f"//tr[.//span[text()='{projectname}']]//button[2]")

        success = self.click_element(FLOWDELETE_BUTTON)
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




