import os
import time

from selenium.webdriver.common.by import By
from .base_page import BasePage





class DataCasePage(BasePage):

    NEW_BUTTON = (By.XPATH,"//span[text()='NEW']")
    PROJECT_DROPDOWN = (By.XPATH, "(//div[contains(@class, 'ant-select-selector')])[1]")
    DATA_GENERATION_SUITES = (By.XPATH, "(//div[contains(@class, 'ant-select-selector')])[2]")
    APPLICATION_DROPDOWN = (By.XPATH, "(//div[contains(@class, 'ant-select-selector')])[3]")
    MODULE_DROPDOWN = (By.XPATH, "(//div[contains(@class, 'ant-select-selector')])[4]")
    MODULE_VERSION_DROPDOWN = (By.XPATH, "(//div[contains(@class, 'ant-select-selector')])[5]")
    TYPE_DROPDOWN = (By.XPATH, "(//div[contains(@class, 'ant-select-selector')])[6]")
    SYNTHETIC_FLOW_DROPDOWN = (By.XPATH, "(//div[contains(@class, 'ant-select-selector')])[7]")

    SAVE_BUTTON = (By.XPATH, "(//button[contains(@class,'save-btn')])[1]")
    CANCEL_BUTTON = (By.XPATH, "//button[text()='CANCEL']")
    BACK_BUTTON = (By.XPATH, "//button[text()='BACK']")

    CASE_NAME_FIELD = (By.XPATH, "//input[@placeholder='Data Generation Case Name']")
    DESCRIPTION_FIELD = (By.XPATH, "//input[@placeholder='Description']")


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

    def click_deletecase_andconfirm_button(self,projectname):

        """ Case'i sonuna kadar sil"""

        print("Delete butonuna tıklanıyor")

        CASEDELETE_BUTTON = (By.XPATH,
                             f"//span[text()='{projectname}']/ancestor::tr//button[contains(@class, 'delete-btn')]")

        success = self.click_element(CASEDELETE_BUTTON)
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

    def click_caseedit_button(self, projectname):
        """Case Edit butonuna tıkla"""
        print("App Edit butonuna tıklanıyor")

        CASEEDITBUTTON = (By.XPATH,f"//span[text()='{projectname}']/ancestor::tr//button[contains(@class, 'edit-btn')]")

        success = self.click_element(CASEEDITBUTTON)
        if success:
            print("List Edit butonuna başarıyla tıklandı")
        else:
            print("List Edit butonuna tıklanamadı")
        return success


    def click_runcase_button(self, projectname):
        """Case Run butonuna tıkla"""
        print("App Edit butonuna tıklanıyor")

        CASERUNBUTTON = (By.XPATH,f"//span[text()='{projectname}']/ancestor::tr//button[contains(@class, 'run-btn')]")

        success = self.click_element(CASERUNBUTTON)
        if success:
            print("Case Run butonuna başarıyla tıklandı")
            RUN_CONFIRM_BUTTON = (By.XPATH, "//span[text()='RUN']")
            confirm_success = self.click_element(RUN_CONFIRM_BUTTON)
            if confirm_success:
                print("Run başarıyla gerçekleştiriliyor")
            else:
                print("Run başarısız run butonuna tıklanamadı")
            return confirm_success

        else:
            print("Case Run butonuna tıklanamadı")
        return success


    def click_schedule_button(self, projectname):
        """Case Schedule butonuna tıkla"""
        print("Schedule butonuna tıklanıyor")

        SCEDULEBUTTON = (By.XPATH,f"//span[text()='{projectname}']/ancestor::tr//button[contains(@class, 'schedule-btn')]")

        success = self.click_element(SCEDULEBUTTON)
        if success:
            print("Schedule butonuna başarıyla tıklandı")
        else:
            print("Schedule butonuna tıklanamadı")
        return success

    def click_history_button(self, projectname):
        """Case History butonuna tıkla"""
        print("Case History butonuna tıklanıyor")

        HISTORYBUTTON = (By.XPATH,f"//span[text()='{projectname}']/ancestor::tr//button[contains(@class, 'history-btn')]")

        success = self.click_element(HISTORYBUTTON)
        if success:
            print("History butonuna başarıyla tıklandı")
        else:
            print("History butonuna tıklanamadı")
        return success

    def click_historylog_button(self, projectname):
        """Case History log butonuna tıkla"""
        print("Case History log butonuna tıklanıyor")

        self.click_history_button(projectname)
        HISTORYLOGBUTTON = (By.XPATH,"//button[contains(@class, 'log-btn')]")
        success = self.click_element(HISTORYLOGBUTTON)
        if success:
            print("History Log butonuna başarıyla tıklandı")
        else:
            print("History Log butonuna tıklanamadı")
        return success


    def click_log_button(self, projectname):
        """Case log butonuna tıkla"""
        print("Case  log butonuna tıklanıyor")

        LOGBUTTON = (By.XPATH,f"//span[text()='{projectname}']/ancestor::tr//button[contains(@class, 'log-btn')]")
        success = self.click_element(LOGBUTTON)
        if success:
            print(" Log butonuna başarıyla tıklandı")
        else:
            print(" Log butonuna tıklanamadı")
        return success



        # Dropdown genel metodları

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


    def select_project(self,project_name):
        """ Projeyi seç"""
        return self.select_dropdown_option(self.PROJECT_DROPDOWN,project_name)

    def select_data_generation_suites(self, suite_name):
        """Data Generation Suites seç"""
        return self.select_dropdown_option(self.DATA_GENERATION_SUITES, suite_name)

    def select_application(self, app_name):
        """Application seç"""
        return self.select_dropdown_option(self.APPLICATION_DROPDOWN, app_name)

    def select_module(self, module_name):
        """Module seç"""
        return self.select_dropdown_option(self.MODULE_DROPDOWN, module_name)

    def select_module_version(self, version):
        """Module Version seç"""
        return self.select_dropdown_option(self.MODULE_VERSION_DROPDOWN, version)

    def select_type(self, type_name):
        """Type seç"""
        return self.select_dropdown_option(self.TYPE_DROPDOWN, type_name)

    def select_synthetic_flow(self, flow_name):
        """Synthetic Flow seç"""
        return self.select_dropdown_option(self.SYNTHETIC_FLOW_DROPDOWN, flow_name)


    def enter_case_name(self,case_name):
        """Case Nmae gir"""
        print(f"Case name '{case_name}' giriliyor")
        return self.enter_text(self.CASE_NAME_FIELD, case_name)

    def enter_description(self,description):
        """Description gir"""
        print(f"Description '{description}' giriliyor")
        return self.enter_text(self.DESCRIPTION_FIELD, description)

    def click_save_button(self):
        """SAVE butonuna tıkla """
        print("SAVE butonuna tıklanıyor ")
        return self.click_element_with_scroll(self.SAVE_BUTTON)

    def click_cancel_button(self):
        """CANCEL butonuna tıkla """
        print("CANCEL butonuna tıklanıyor ")
        return self.click_element_with_scroll(self.CANCEL_BUTTON)


    def click_back_button(self):
        """BACK butonuna tıkla """
        print("BACK butonuna tıklanıyor ")
        return self.click_element_with_scroll(self.BACK_BUTTON)

















