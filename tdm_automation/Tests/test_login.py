import time

import pytest
import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from Pages.login_page import LoginPage

load_dotenv()

class TestLoginScenarios:

    def setup_method(self):
        """Her test öncesi çalışır"""
        # Environment değişkenlerini al
        self.BASE_URL = os.getenv('BASE_URL')
        self.VALID_USERNAME = os.getenv('VALID_USERNAME')
        self.VALID_PASSWORD = os.getenv('VALID_PASSWORD')
        self.INVALID_USERNAME = os.getenv('INVALID_USERNAME')
        self.INVALID_PASSWORD = os.getenv('INVALID_PASSWORD')
        self.TIMEOUT = int(os.getenv('TIMEOUT', '10'))

        # WebDriver kurulumu
        self.service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=self.service)
        self.login_page = LoginPage(self.driver)


    def teardown_method(self):
        """Her test sonrası çalışır"""
        self.driver.quit()

    def test_TC001_login_empty_fields(self):
        """TC_001: Bütün alanlar boş"""
        print("\n TC_001: Bütün alanlar boş ile giriş ===")

        self.driver.get(self.BASE_URL)
        self.login_page.do_login("", "")

        assert self.login_page.wait_for_url_contains("login_error=1"), "Boş alanlar hatası alınmadı"
        print("Test başarılı: Boş alanlarla hata alındı")

    def test_TC002_login_empty_username(self):
        """TC_002: Kullanıcı adı boş"""
        print("\n TC_002: Kullanıcı adı boş ===")

        self.driver.get(self.BASE_URL)
        self.login_page.do_login("", self.VALID_PASSWORD)

        assert self.login_page.wait_for_url_contains("login_error=1"), "Boş kullanıcı adı hatası alınmadı"
        print("Test başarılı: Boş kullanıcı adı hatası alındı")

    def test_TC003_login_empty_password(self):
        """TC_003: Şifre boş"""
        print("\n TC_003: Şifre boş ===")

        self.driver.get(self.BASE_URL)
        self.login_page.do_login(self.VALID_USERNAME, "")

        assert self.login_page.wait_for_url_contains("login_error=1"), "Boş şifre hatası alınmadı"
        print("Test başarılı: Boş şifre hatası alındı")

    def test_TC004_login_invalid_username(self):
        """TC_004: Kullanıcı adı hatalı"""
        print("\n TC_004: Kullanıcı adı hatalı ===")

        self.driver.get(self.BASE_URL)
        self.login_page.do_login(self.INVALID_USERNAME, self.VALID_PASSWORD)

        assert self.login_page.wait_for_url_contains("login_error=1"), "Hatalı kullanıcı adı hatası alınmadı"
        print("Test başarılı: Hatalı kullanıcı adı hatası alındı")

    def test_TC005_login_invalid_password(self):
        """TC_005: Şifre hatalı"""
        print("\n TC_005: Şifre hatalı ===")

        self.driver.get(self.BASE_URL)
        self.login_page.do_login(self.VALID_USERNAME, self.INVALID_PASSWORD)

        assert self.login_page.wait_for_url_contains("login_error=1"), "Hatalı şifre hatası alınmadı"
        print("Test başarılı: Hatalı şifre hatası alındı")

    def test_TC006_login_successful(self):
        """TC_006: Başarılı giriş"""
        print("\n TC_006: Başarılı giriş ===")

        self.driver.get(self.BASE_URL)
        self.login_page.do_login(self.VALID_USERNAME, self.VALID_PASSWORD)

        assert self.login_page.wait_for_url_contains("/WebConsole/"), "Başarılı giriş sonrası ana sayfa açılmadı"

        current_url = self.driver.current_url
        print(f"Gidilen URL: {current_url}")

        assert "login_error" not in current_url, f"Login başarısız: {current_url}"
        assert "/WebConsole/" in current_url, f"Ana sayfaya yönlendirilmedi: {current_url}"

        page_title = self.driver.title
        print(f"Sayfa başlığı: {page_title}")
        print("Test başarılı: Ana sayfaya başarıyla giriş yapıldı")

    def test_TC007_new_test_data_manager(self):
        """TC_007: New Test Data Manager kontrolü ve tıklama"""
        print("\n TC_007: New Test Data Manager ===")

        self.driver.get(self.BASE_URL)
        self.login_page.do_login(self.VALID_USERNAME, self.VALID_PASSWORD)

        assert self.login_page.wait_for_url_contains("/WebConsole/"), "Başarılı login sonrası ana sayfaya gelinmedi"

        page_source = self.driver.page_source.lower()

        if "new test data manager" in page_source:
            print("New Test Data Manager bulundu!")

            tdm_locator = (By.XPATH, "//li[@title='New Test Data Manager'][2]")
            success = self.login_page.click_element(tdm_locator)

            assert success, "TDM elementine tıklanamadı"
            print(f"Tıklandı! Yeni URL: {self.driver.current_url}")
        else:
            assert False, "New Test Data Manager modülü bulunamadı"