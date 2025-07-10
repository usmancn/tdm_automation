import os
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from .base_page import BasePage

load_dotenv()

class LoginPage(BasePage):
    # Locatorlar
    USERNAME_FIELD = (By.ID, "username")
    PASSWORD_FIELD = (By.ID, "password")
    LOGIN_BUTTON = (By.ID, "submit_login2")

    def __init__(self, driver):
        super().__init__(driver)
        self.base_url = os.getenv('BASE_URL')

    def go_to_login_page(self):
        """Login sayfasına git"""
        self.driver.get(self.base_url)
        return True

    def enter_username(self, username):
        """Kullanıcı adı gir"""
        return self.enter_text(self.USERNAME_FIELD, username)

    def enter_password(self, password):
        """Şifre gir"""
        return self.enter_text(self.PASSWORD_FIELD, password)

    def click_login_button(self):
        """Login butonuna tıkla"""
        return self.click_element(self.LOGIN_BUTTON)

    def do_login(self, username, password):
        """Tam login işlemi"""
        self.enter_username(username)
        self.enter_password(password)
        self.click_login_button()
        return True