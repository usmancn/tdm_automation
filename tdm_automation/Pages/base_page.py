import os
from dotenv import load_dotenv
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

load_dotenv()

class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.timeout = int(os.getenv('TIMEOUT', '10'))
        self.wait = WebDriverWait(driver, self.timeout)

    def find_element(self, locator):
        """Element bul"""
        try:
            return self.wait.until(EC.presence_of_element_located(locator))
        except TimeoutException:
            print(f"Element bulunamadı: {locator}")
            return None

    def click_element(self, locator):
        """Element'e tıkla"""
        try:
            element = self.wait.until(EC.element_to_be_clickable(locator))
            element.click()
            return True
        except TimeoutException:
            print(f"Element tıklanamadı: {locator}")
            return False

    def enter_text(self, locator, text):
        """Text gir"""
        try:
            element = self.wait.until(EC.element_to_be_clickable(locator))
            element.clear()
            element.send_keys(text)
            return True
        except Exception as e:
            print(f"Text giriş hatası: {e}")
            return False

    def get_text(self, locator):
        """Element'in text'ini al"""
        element = self.find_element(locator)
        return element.text if element else ""

    def wait_for_url_contains(self, text, timeout=None):
        """URL belirli bir metni içerene kadar bekle"""
        timeout = timeout or self.timeout
        try:
            return WebDriverWait(self.driver, timeout).until(EC.url_contains(text))
        except TimeoutException:
            print(f"URL '{text}' içermiyor. Mevcut URL: {self.driver.current_url}")
            return False