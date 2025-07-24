import time
import pytest
import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from tdm_automation.Pages.login_page import LoginPage
from tdm_automation.Pages.tdm_dashboard_page import TDMDashboardPage
from tdm_automation.Pages.product_info_page import ProductInfoPage
from selenium.webdriver.chrome.options import Options


load_dotenv()

class TestTDMVersionControl:

    def setup_method(self):
       """Her test öncesi çalışır"""

       # Environment değişkenlerini al
       self.BASE_URL = os.getenv('BASE_URL')
       self.VALID_USERNAME = os.getenv('VALID_USERNAME')
       self.VALID_PASSWORD = os.getenv('VALID_PASSWORD')
       self.TIMEOUT = int(os.getenv('TIMEOUT', '10'))

       # Environment değişkenlerini al
       self.HEADLESS = os.getenv('HEADLESS', 'false').lower() == 'true'
       self.DOCKER_MODE = os.getenv('DOCKER_MODE', 'false').lower() == 'true'

       # Chrome options - Docker ve headless için optimize edilmiş
       self.chrome_options = Options()

       if self.HEADLESS:
           self.chrome_options.add_argument("--headless")
           print("HEADLESS modda çalışıyor")

       if self.DOCKER_MODE:
           # Docker için gerekli argumentlar
           self.chrome_options.add_argument("--no-sandbox")
           self.chrome_options.add_argument("--disable-dev-shm-usage")
           self.chrome_options.add_argument("--disable-gpu")
           self.chrome_options.add_argument("--remote-debugging-port=9222")
           self.chrome_options.add_argument("--incognito")
           print("DOCKER modda çalışıyor")
       else:
           # Local development için
           self.chrome_options.add_argument("--incognito")

       # Genel performans ayarları
       self.chrome_options.add_argument("--window-size=1920,1080")
       self.chrome_options.add_argument("--disable-web-security")
       self.chrome_options.add_argument("--ignore-certificate-errors")

       # WebDriver kurulumu
       self.service = Service(ChromeDriverManager().install())
       self.driver = webdriver.Chrome(service=self.service, options=self.chrome_options)
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