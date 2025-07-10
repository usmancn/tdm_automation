import time
import pytest
import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from Pages.login_page import LoginPage
from Pages.tdm_dashboard_page import TDMDashboardPage
from Pages.product_info_page import ProductInfoPage

load_dotenv()

class TestTDMVersionControl:

    def setup_method(self):
       """Her test öncesi çalışır"""

       # Environment değişkenlerini al
       self.BASE_URL = os.getenv('BASE_URL')
       self.VALID_USERNAME = os.getenv('VALID_USERNAME')
       self.VALID_PASSWORD = os.getenv('VALID_PASSWORD')
       self.TIMEOUT = int(os.getenv('TIMEOUT', '10'))

       # WebDriver kurulumu
       self.service = Service(ChromeDriverManager().install())
       self.driver = webdriver.Chrome(service=self.service)
       self.login_page = LoginPage(self.driver)
       self.dashboard_page = TDMDashboardPage(self.driver)
       self.product_info_page = ProductInfoPage(self.driver)

    def teardown_method(self):
        """Her test sonrası çalışır"""
        self.driver.quit()

    def navigate_to_product_info(self):
        """Product Info sayfasına git - ortak işlem"""
        # Login
        self.driver.get(self.BASE_URL)
        self.login_page.do_login(self.VALID_USERNAME, self.VALID_PASSWORD)

        # TDM'ye git
        tdm_locator = (By.XPATH, "//li[@title='New Test Data Manager'][2]")
        success = self.login_page.click_element(tdm_locator)
        assert success, "TDM elementine tıklanamadı"

        # Info butonuna tıkla
        time.sleep(3)
        info_button_clicked = self.dashboard_page.click_info_button()
        assert info_button_clicked, "Info butonuna tıklanamadı"

        time.sleep(2)

    def test_TC008_dashboard_info_button(self):
        """TC_008: Dashboard navigation"""
        print("\n TC_008: Dashboard Info Button ===")

        self.navigate_to_product_info()

        # Sadece navigation kontrolü
        assert "/product-info" in self.driver.current_url, "Product Info sayfasına gidilmedi"
        print("Navigation başarılı")

    def test_TC009_version_information(self):
        """TC_009: Version bilgisi"""
        print("\n TC_009: Version Information ===")

        self.navigate_to_product_info()

        # Sadece version kontrolü
        page_loaded = self.product_info_page.is_product_info_loaded()
        assert page_loaded, "Product Info sayfası yüklenmedi"

        version_info = self.product_info_page.get_version()
        assert version_info, "Version bilgisi alınamadı"

        print(f"Version: {version_info}")
