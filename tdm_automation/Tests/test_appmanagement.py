
import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from tdm_automation.Pages.login_page import LoginPage
from tdm_automation.Pages.tdm_dashboard_page import TDMDashboardPage
from tdm_automation.Pages.application_management_page import AppManagementPage
from tdm_automation.Pages.create_application_page import CreateAppPage
from tdm_automation.Pages.create_module_page import CreateModulePage
from tdm_automation.Pages.product_info_page import ProductInfoPage
from selenium.webdriver.chrome.options import Options
import time


load_dotenv()


class TestAppManagement:

    @classmethod
    def setup_class(cls):
        """Tüm class için tek sefer çalışır - LOGIN İŞLEMLERİ BURADA"""
        print("\n=== CLASS SETUP: Login işlemleri yapılıyor ===")

        # Environment değişkenlerini al
        cls.BASE_URL = os.getenv('BASE_URL')
        cls.VALID_USERNAME = os.getenv('VALID_USERNAME')
        cls.VALID_PASSWORD = os.getenv('VALID_PASSWORD')
        cls.TIMEOUT = int(os.getenv('TIMEOUT', '20'))

        # Test data environment değişkenleri
        cls.TEST_APP_NAME = os.getenv('TEST_APP_NAME', 'TestApp')
        cls.TEST_MODULE_NAME = os.getenv('TEST_MODULE_NAME', 'TestModule')
        cls.TEST_VERSION = os.getenv('TEST_VERSION', 'V1')
        cls.TEST_VERSION_2 = os.getenv('TEST_VERSION_2', 'V2')
        cls.TEST_VERSION_3 = os.getenv('TEST_VERSION_3', 'V3')

        # Environment değişkenlerini al
        cls.HEADLESS = os.getenv('HEADLESS', 'false').lower() == 'true'
        cls.DOCKER_MODE = os.getenv('DOCKER_MODE', 'false').lower() == 'true'

        # Chrome options - Docker ve headless için optimize edilmiş
        cls.chrome_options = Options()

        if cls.HEADLESS:
            cls.chrome_options.add_argument("--headless")
            print("HEADLESS modda çalışıyor")

        if cls.DOCKER_MODE:
            # Docker için gerekli argumentlar
            cls.chrome_options.add_argument("--no-sandbox")
            cls.chrome_options.add_argument("--disable-dev-shm-usage")
            cls.chrome_options.add_argument("--disable-gpu")
            cls.chrome_options.add_argument("--remote-debugging-port=9222")
            cls.chrome_options.add_argument("--incognito")
            print("DOCKER modda çalışıyor")
        else:
            # Local development için
            cls.chrome_options.add_argument("--incognito")

        # Genel performans ayarları
        cls.chrome_options.add_argument("--window-size=1920,1080")
        cls.chrome_options.add_argument("--disable-web-security")
        cls.chrome_options.add_argument("--ignore-certificate-errors")

        # WebDriver kurulumu
        cls.service = Service(ChromeDriverManager().install())
        cls.driver = webdriver.Chrome(service=cls.service, options=cls.chrome_options)
        cls.driver.maximize_window()

        # Page object'leri oluştur
        cls.login_page = LoginPage(cls.driver)
        cls.dashboard_page = TDMDashboardPage(cls.driver)
        cls.product_info_page = ProductInfoPage(cls.driver)
        cls.appman_page = AppManagementPage(cls.driver)
        cls.create_app_page = CreateAppPage(cls.driver)
        cls.create_mdl_page = CreateModulePage(cls.driver)

        # *** TEK SEFERLİK LOGIN İŞLEMLERİ ***
        cls.driver.get(cls.BASE_URL)
        login_success = cls.login_page.do_login(cls.VALID_USERNAME, cls.VALID_PASSWORD)
        assert login_success, "Login başarısız!"

        # TDM'ye git
        tdm_locator = (By.XPATH, "//li[@title='New Test Data Manager'][2]")
        tdm_success = cls.login_page.click_element(tdm_locator)
        assert tdm_success, "TDM elementine tıklanamadı"

        # App Management'e git
        appman_success = cls.appman_page.click_appman()
        assert appman_success, "App Management butonuna tıklanamadı"

        print("=== CLASS SETUP TAMAMLANDI: Login ve navigation başarılı ===")

    @classmethod
    def teardown_class(cls):
        """Tüm testler bitince tek sefer çalışır"""
        print("\n=== CLASS TEARDOWN: Driver kapatılıyor ===")
        if hasattr(cls, 'driver'):
            cls.driver.quit()

    def setup_method(self, method):
        """Her test öncesi çalışır - SADECE TEST-SPECIFIC SETUP"""
        print(f"\n--- Test başlıyor: {method.__name__} ---")

        # Test data - her test için unique değerler
        timestamp = int(time.time())
        self.test_app_name = f"{self.TEST_APP_NAME}_{timestamp}"
        self.test_module_name = f"{self.TEST_MODULE_NAME}_{timestamp}"
        self.test_version = self.TEST_VERSION
        self.test_version_2 = self.TEST_VERSION_2
        self.test_version_3 = self.TEST_VERSION_3

        # App Management sayfasında olduğumuzu kontrol et
        current_url = self.driver.current_url
        if "application-management" not in current_url:
            print("App Management sayfasına yönlendiriliyor...")
            self.appman_page.click_appman()
            time.sleep(1)

    def teardown_method(self, method):
        """Her test sonrası çalışır - SADECE TEST CLEANUP"""
        print(f"--- Test bitti: {method.__name__} ---")

        # Modal varsa kapat
        try:
            cancel_buttons = self.driver.find_elements(By.XPATH, "//span[text()='CANCEL']")
            for button in cancel_buttons:
                if button.is_displayed():
                    button.click()
                    time.sleep(0.5)
        except:
            pass

        # Test verilerini temizlemeye çalış (best effort)
        try:
            self._cleanup_test_data()
        except:
            pass  # Cleanup başarısız olsa da test devam etsin

    def _cleanup_test_data(self):
        """Test verilerini temizle"""
        try:
            # Oluşturulan app'i sil
            page_source = self.driver.page_source
            if hasattr(self, 'test_app_name') and self.test_app_name in page_source:
                self.appman_page.click_deleteapp_andconfirm_button(self.test_app_name)
                time.sleep(1)
        except:
            pass

    def _create_test_app(self):
        """Test için gerekli app'i oluştur - Helper method"""
        try:
            # NEW butonuna tıkla
            self.appman_page.click_newapp_button()
            time.sleep(1)

            # App name ve version gir
            self.create_app_page.enter_appname(self.test_app_name)
            self.create_app_page.enter_version(self.test_version)
            self.create_app_page.click_versionadd_button()
            self.create_app_page.click_save_button()
            time.sleep(2)

            print(f"Test app oluşturuldu: {self.test_app_name}")
            return True
        except Exception as e:
            print(f"Test app oluşturulamadı: {e}")
            return False

    def test_TC010_new_button_click_modal_open(self):
        """TC_010: NEW butonuna tıklama ve modal açma"""
        print("\nTC_010: NEW butonuna tıklama ve modal açma ===")

        # NEW butonuna tıkla
        new_button_clicked = self.appman_page.click_newapp_button()
        assert new_button_clicked, "NEW butonuna tıklanamadı"

        # Modal açıldığını kontrol et
        page_source = self.driver.page_source.lower()
        modal_present = "modal" in page_source
        assert modal_present, "Modal açılmadı"

        # Application Name alanının görünür olduğunu kontrol et
        app_name_field = self.create_app_page.find_element(self.create_app_page.APPNAME_FIELD)
        assert app_name_field is not None, "Application Name alanı görünmüyor"

        # Version alanının görünür olduğunu kontrol et
        version_field = self.create_app_page.find_element(self.create_app_page.VERSION_FIELD)
        assert version_field is not None, "Version alanı görünmüyor"

        print("Test başarılı: NEW butonuna tıklandı, modal açıldı ve gerekli alanlar görünür")

    def test_TC011_create_app_with_name_and_version(self):
        """TC_011: Name ve Version girip application oluşturma"""
        print("\nTC_011: Name ve Version girip application oluşturma ===")

        # NEW butonuna tıkla
        new_button_clicked = self.appman_page.click_newapp_button()
        assert new_button_clicked, "NEW butonuna tıklanamadı"

        # Application Name gir
        app_name_entered = self.create_app_page.enter_appname(self.test_app_name)
        assert app_name_entered, "Application Name girilemedi"

        # Version gir
        version_entered = self.create_app_page.enter_version(self.test_version)
        assert version_entered, "Version girilemedi"

        # ADD butonuna tıkla
        add_clicked = self.create_app_page.click_versionadd_button()
        assert add_clicked, "ADD butonuna tıklanamadı"

        # SAVE butonuna tıkla
        save_clicked = self.create_app_page.click_save_button()
        assert save_clicked, "SAVE butonuna tıklanamadı"

        time.sleep(2)

        # Uygulamanın listede görünür olduğunu kontrol et
        page_source = self.driver.page_source
        assert self.test_app_name in page_source, f"Oluşturulan uygulama '{self.test_app_name}' listede görünmüyor"

        print(f"Test başarılı: Uygulama '{self.test_app_name}' başarıyla oluşturuldu ve listede görünüyor")

    def test_TC012_create_app_empty_version(self):
        """TC_012: Name girip Version girmeden application oluşturma"""
        print("\nTC_012: Name girip Version girmeden application oluşturma ===")

        # NEW butonuna tıkla
        new_button_clicked = self.appman_page.click_newapp_button()
        assert new_button_clicked, "NEW butonuna tıklanamadı"

        # Application Name gir
        app_name_entered = self.create_app_page.enter_appname(self.test_app_name)
        assert app_name_entered, "Application Name girilemedi"

        time.sleep(1)

        # SAVE disabled olmalı
        save_button = self.create_app_page.find_element(self.create_app_page.SAVE_BUTTON)
        is_disabled = save_button.get_attribute("disabled") is not None
        assert is_disabled, "SAVE butonu disabled olmalıydı (version eklenmediği için)"

        print("Test başarılı: Version eklenmeden SAVE disabled kaldı")


    def test_TC013_create_app_empty_name(self):
        """TC_013: Name girmeyip Version girip application oluşturma"""
        print("\nTC_013: Name girmeyip Version girip application oluşturma ===")

        # NEW butonuna tıkla
        new_button_clicked = self.appman_page.click_newapp_button()
        assert new_button_clicked, "NEW butonuna tıklanamadı"

        # Application Name boş bırak (hiçbir şey girme)

        # Version gir
        version_entered = self.create_app_page.enter_version(self.test_version)
        assert version_entered, "Version girilemedi"

        # ADD butonuna tıkla
        add_clicked = self.create_app_page.click_versionadd_button()
        assert add_clicked, "ADD butonuna tıklanamadı"

        time.sleep(1)

        # SAVE disabled olmalı (app name olmadığı için)
        save_button = self.create_app_page.find_element(self.create_app_page.SAVE_BUTTON)
        is_disabled = save_button.get_attribute("disabled") is not None
        assert is_disabled, "SAVE butonu disabled olmalıydı (app name girilmediği için)"

        print("Test başarılı: App Name girilmediğinde SAVE disabled kaldı")


    def test_TC014_create_app_both_empty(self):
        """TC_014: İkisini de boş bırakıp application oluşturma"""
        print("\nTC_014: İkisini de boş bırakıp application oluşturma ===")

        # NEW butonuna tıkla
        new_button_clicked = self.appman_page.click_newapp_button()
        assert new_button_clicked, "NEW butonuna tıklanamadı"

        # Her iki alanı da boş bırak (hiçbir şey girme)

        time.sleep(1)

        # SAVE disabled olmalı
        save_button = self.create_app_page.find_element(self.create_app_page.SAVE_BUTTON)
        is_disabled = save_button.get_attribute("disabled") is not None
        assert is_disabled, "SAVE butonu disabled olmalıydı (her iki alan da boş)"

        print("Test başarılı: Her iki alan boş bırakıldığında SAVE disabled kaldı")


    def test_TC015_create_app_multiple_versions(self):
        """TC_015: Name girip birden fazla version ekleyerek application kaydetme"""
        print("\nTC_015: Name girip birden fazla version ekleyerek application kaydetme ===")

        # NEW butonuna tıkla
        new_button_clicked = self.appman_page.click_newapp_button()
        assert new_button_clicked, "NEW butonuna tıklanamadı"

        # Application Name gir
        app_name_entered = self.create_app_page.enter_appname(self.test_app_name)
        assert app_name_entered, "Application Name girilemedi"

        # İlk Version gir
        version1_entered = self.create_app_page.enter_version(self.test_version)
        assert version1_entered, "İlk Version girilemedi"

        # İlk ADD butonuna tıkla
        add1_clicked = self.create_app_page.click_versionadd_button()
        assert add1_clicked, "İlk ADD butonuna tıklanamadı"

        # İkinci Version gir
        version2_entered = self.create_app_page.enter_version(self.test_version_2)
        assert version2_entered, "İkinci Version girilemedi"

        # İkinci ADD butonuna tıkla
        add2_clicked = self.create_app_page.click_versionadd_button()
        assert add2_clicked, "İkinci ADD butonuna tıklanamadı"

        time.sleep(1)

        # SAVE butonuna tıkla
        save_clicked = self.create_app_page.click_save_button()
        assert save_clicked, "SAVE butonuna tıklanamadı"

        time.sleep(2)

        # Uygulamanın listede görünür olduğunu kontrol et
        page_source = self.driver.page_source
        assert self.test_app_name in page_source, f"Çoklu versiyonlu uygulama '{self.test_app_name}' listede görünmüyor"

        print(f"Test başarılı: Çoklu versiyonlu uygulama '{self.test_app_name}' başarıyla oluşturuldu")

    def test_TC016_create_app_duplicate_name(self):
        """TC_016: Tamamen aynı isimde application name ile kaydetme"""
        print("\nTC_016: Tamamen aynı isimde application name ile kaydetme ===")

        # İlk uygulamayı oluştur
        print("İlk uygulamayı oluşturuyor...")

        # NEW butonuna tıkla
        new_button_clicked = self.appman_page.click_newapp_button()
        assert new_button_clicked, "NEW butonuna tıklanamadı"

        # Application Name gir
        app_name_entered = self.create_app_page.enter_appname(self.test_app_name)
        assert app_name_entered, "Application Name girilemedi"

        # Version gir ve ADD
        version_entered = self.create_app_page.enter_version(self.test_version)
        assert version_entered, "Version girilemedi"

        add_clicked = self.create_app_page.click_versionadd_button()
        assert add_clicked, "ADD butonuna tıklanamadı"

        # SAVE butonuna tıkla
        save_clicked = self.create_app_page.click_save_button()
        assert save_clicked, "İlk SAVE butonuna tıklanamadı"

        time.sleep(2)

        # İlk uygulamanın oluşturulduğunu kontrol et
        page_source = self.driver.page_source
        assert self.test_app_name in page_source, "İlk uygulama oluşturulamadı"
        print("İlk uygulama başarıyla oluşturuldu")

        # Şimdi aynı isimde ikinci uygulamayı oluşturmaya çalış
        print("Aynı isimde ikinci uygulamayı oluşturmaya çalışıyor...")

        # Tekrar NEW butonuna tıkla
        new_button_clicked2 = self.appman_page.click_newapp_button()
        assert new_button_clicked2, "İkinci NEW butonuna tıklanamadı"

        # Aynı Application Name gir
        app_name_entered2 = self.create_app_page.enter_appname(self.test_app_name)
        assert app_name_entered2, "İkinci Application Name girilemedi"

        # Version gir ve ADD
        version_entered2 = self.create_app_page.enter_version(self.test_version_2)
        assert version_entered2, "İkinci Version girilemedi"

        add_clicked2 = self.create_app_page.click_versionadd_button()
        assert add_clicked2, "İkinci ADD butonuna tıklanamadı"

        # SAVE butonuna tıkla
        save_clicked2 = self.create_app_page.click_save_button()

        time.sleep(2)

        # Hata mesajı veya modal açık kalmalı
        modal_present = "modal" in self.driver.page_source.lower()
        if modal_present:
            print("Modal açık kaldı - Duplicate name hatası alındı")
        else:
            print("UYARI: Aynı isimde ikinci uygulama oluşturulabildi!")

        print("Test tamamlandı: Duplicate name kontrolü yapıldı")

    def test_TC017_sql_injection_app_name(self):
        """TC_017: SQL cümleciği ile application name oluşturma"""
        print("\nTC_017: SQL cümleciği ile application name oluşturma ===")

        time.sleep(1)

        # NEW butonuna tıkla
        new_button_clicked = self.appman_page.click_newapp_button()
        assert new_button_clicked, "NEW butonuna tıklanamadı"

        # SQL injection payload
        sql_payload = "'; DROP TABLE applications; --"

        # SQL payload'ını Application Name alanına gir
        app_name_entered = self.create_app_page.enter_appname(sql_payload)
        assert app_name_entered, "SQL payload girilemedi"

        # Version gir ve ADD
        version_entered = self.create_app_page.enter_version(self.test_version)
        assert version_entered, "Version girilemedi"

        add_clicked = self.create_app_page.click_versionadd_button()
        assert add_clicked, "ADD butonuna tıklanamadı"

        # SAVE butonuna tıkla
        save_clicked = self.create_app_page.click_save_button()
        time.sleep(2)

        # Sistem hala çalışıyor mu kontrol et
        page_source = self.driver.page_source
        if sql_payload in page_source:
            print("UYARI: SQL kod sisteme kaydedildi")

        # Yeni modal açılabiliyor mu?
        new_test = self.appman_page.click_newapp_button()
        assert new_test, "Sistem zarar görmüş - NEW modal açılmıyor"

        print("Test başarılı: SQL injection sistemi etkilemedi")

    def test_TC018_create_app_different_languages(self):
        """TC_018: Farklı dillerde application name ile kaydetme"""
        print("\nTC_018: Farklı dillerde application name ile kaydetme ===")

        # Farklı dil karakterleri
        language_names = [
            ("Arabic", "تطبيق_اختبار"),
            ("Turkish", "Türkçe_Uygulama_ÇĞİÖŞÜ"),
            ("Chinese", "测试应用程序"),
            ("Russian", "Тестовое_приложение"),
            ("Japanese", "テストアプリケーション"),
        ]

        for lang_name, app_name in language_names:
            print(f"\n{lang_name} karakterleri test ediliyor: {app_name}")

            try:
                # NEW butonuna tıkla
                new_button_clicked = self.appman_page.click_newapp_button()
                assert new_button_clicked, "NEW butonuna tıklanamadı"

                time.sleep(1)

                # Farklı dilde application name gir
                app_name_entered = self.create_app_page.enter_appname(app_name)

                if app_name_entered:
                    # Version gir ve ADD
                    version_entered = self.create_app_page.enter_version(self.test_version)
                    if version_entered:
                        add_clicked = self.create_app_page.click_versionadd_button()
                        if add_clicked:
                            # SAVE butonuna tıkla
                            save_clicked = self.create_app_page.click_save_button()
                            time.sleep(2)

                            # Oluşturuldu mu kontrol et
                            page_source = self.driver.page_source
                            if app_name in page_source:
                                print(f"{lang_name} karakterleri kabul edildi")
                            else:
                                print(f"{lang_name} karakterleri reddedildi")

                # Modal varsa kapat
                try:
                    cancel_button = self.driver.find_element(By.XPATH, "//span[text()='CANCEL']")
                    cancel_button.click()
                    time.sleep(1)
                except:
                    pass

            except Exception as e:
                print(f"{lang_name} test hatası: {e}")

        print("Farklı dil karakterleri testi tamamlandı")


    def test_TC019_create_app_duplicate_versions(self):
        """TC_019: Aynı version adıyla birden fazla version ekleme ve kaydetme"""
        print("\nTC_019: Aynı version adıyla birden fazla version ekleme ===")

        # NEW butonuna tıkla
        new_button_clicked = self.appman_page.click_newapp_button()
        assert new_button_clicked, "NEW butonuna tıklanamadı"

        # Application Name gir
        app_name_entered = self.create_app_page.enter_appname(self.test_app_name)
        assert app_name_entered, "Application Name girilemedi"

        # İlk version gir ve ADD
        version1_entered = self.create_app_page.enter_version(self.test_version)
        assert version1_entered, "İlk Version girilemedi"

        add1_clicked = self.create_app_page.click_versionadd_button()
        assert add1_clicked, "İlk ADD butonuna tıklanamadı"

        # Aynı version'ı tekrar gir ve ADD
        version2_entered = self.create_app_page.enter_version(self.test_version)
        assert version2_entered, "İkinci Version girilemedi"

        add2_clicked = self.create_app_page.click_versionadd_button()
        assert add2_clicked, "İkinci ADD butonuna tıklanamadı"

        # SAVE butonuna tıkla
        save_clicked = self.create_app_page.click_save_button()
        time.sleep(2)

        # Modal hala açık mı (hata varsa açık kalır)
        modal_present = "modal" in self.driver.page_source.lower()
        assert modal_present, "Duplicate version hatası alınmadı"

        print("Test başarılı: Aynı version ile hata alındı")


    def test_TC020_delete_app(self):
        """TC_020: Application'ı silme"""
        print("\nTC_020: Application'ı silme ===")

        # Önce bir app oluştur
        app_created = self._create_test_app()
        assert app_created, "Test app oluşturulamadı"

        # App oluşturulduğunu kontrol et
        page_source = self.driver.page_source
        assert self.test_app_name in page_source, "App oluşturulamadı"
        print("App başarıyla oluşturuldu")

        # Şimdi app'i sil
        delete_success = self.appman_page.click_deleteapp_andconfirm_button(self.test_app_name)
        assert delete_success, "App silinemedi"

        time.sleep(2)

        # App silindiğini kontrol et
        page_source = self.driver.page_source
        assert self.test_app_name not in page_source, "App silinemedi"

        print("Test başarılı: App başarıyla silindi")


    def test_TC021_edit_app(self):
        """TC_021: Application'ı düzenleme"""
        print("\nTC_021: Application'ı düzenleme ===")

        # Önce bir app oluştur
        app_created = self._create_test_app()
        assert app_created, "Test app oluşturulamadı"

        # App oluşturulduğunu kontrol et
        page_source = self.driver.page_source
        assert self.test_app_name in page_source, "App oluşturulamadı"
        print("App başarıyla oluşturuldu")

        # Edit butonuna tıkla
        edit_clicked = self.appman_page.click_appedit_button(self.test_app_name)
        assert edit_clicked, "Edit butonuna tıklanamadı"

        time.sleep(1)

        # Yeni version ekle
        new_version_entered = self.create_app_page.enter_version(self.test_version_2)
        assert new_version_entered, "Yeni version girilemedi"

        add_new_clicked = self.create_app_page.click_versionadd_button()
        assert add_new_clicked, "Yeni version ADD butonuna tıklanamadı"

        # SAVE butonuna tıkla
        save_edit_clicked = self.create_app_page.click_save_button()
        assert save_edit_clicked, "Edit SAVE butonuna tıklanamadı"

        time.sleep(2)

        print("Test başarılı: App başarıyla düzenlendi ve yeni version eklendi")


    def test_TC022_version_list_navigation(self):
        """TC_022: Version List linkine tıklama"""
        print("\nTC_022: Version List linkine tıklama ===")

        # Önce test app oluştur
        app_created = self._create_test_app()
        assert app_created, "Test app oluşturulamadı"

        # Version List linkine tıkla
        version_list_clicked = self.appman_page.click_versionlist_button(self.test_app_name)
        assert version_list_clicked, "Version List linkine tıklanamadı"

        time.sleep(2)

        # Version List sayfasının açıldığını kontrol et
        page_source = self.driver.page_source
        version_list_opened = "version" in page_source.lower()
        assert version_list_opened, "Version List sayfası açılmadı"

        print("Test başarılı: Version List sayfası açıldı")


    def test_TC023_module_list_navigation(self):
        """TC_023: Module List linkine tıklama"""
        print("\nTC_023: Module List linkine tıklama ===")

        # Önce test app oluştur
        app_created = self._create_test_app()
        assert app_created, "Test app oluşturulamadı"

        # Module List linkine tıkla
        module_list_clicked = self.appman_page.click_modulelist_button(self.test_app_name)
        assert module_list_clicked, "Module List linkine tıklanamadı"

        time.sleep(2)

        # Module List sayfasının açıldığını kontrol et
        page_source = self.driver.page_source
        module_list_opened = "module" in page_source.lower()
        assert module_list_opened, "Module List sayfası açılmadı"

        print("Test başarılı: Module List sayfası açıldı")


    def test_TC024_module_creation_modal_open(self):
        """TC_024: Module oluşturma modal'ının açıldığını kontrol etme"""
        print("\nTC_024: Module oluşturma modal'ı açma ===")

        # Önce test app oluştur
        app_created = self._create_test_app()
        assert app_created, "Test app oluşturulamadı"

        # Module List sayfasına git
        self.appman_page.click_modulelist_button(self.test_app_name)
        time.sleep(1)

        # '+' butonuna tıkla
        add_module_clicked = self.appman_page.click_modulelistADD_button(self.test_app_name)
        assert add_module_clicked, "'+' butonuna tıklanamadı"

        time.sleep(1)

        # Modal açıldığını kontrol et
        modal_present = "modal" in self.driver.page_source.lower()
        assert modal_present, "Modal açılmadı"

        # Form alanlarının mevcut olduğunu kontrol et
        module_name_field = self.create_mdl_page.find_element(self.create_mdl_page.MODULENAME_FIELD)
        version_field = self.create_mdl_page.find_element(self.create_mdl_page.VERSION_FIELD)

        assert module_name_field is not None, "Module Name alanı bulunamadı"
        assert version_field is not None, "Version alanı bulunamadı"

        print("Test başarılı: Module oluşturma modal'ı açıldı ve form alanları mevcut")


    def test_TC025_create_module_with_name_and_version(self):
        """TC_025: Module Name ve Version girip module oluşturma"""
        print("\nTC_025: Module Name ve Version girip module oluşturma ===")

        # Önce test app oluştur
        app_created = self._create_test_app()
        assert app_created, "Test app oluşturulamadı"

        # Module List sayfasına git
        self.appman_page.click_modulelist_button(self.test_app_name)
        time.sleep(2)

        add_module_clicked = self.appman_page.click_modulelistADD_button(self.test_app_name)
        assert add_module_clicked, "'+' butonuna tıklanamadı"

        time.sleep(2)

        module_name_entered = self.create_mdl_page.enter_modulename(self.test_module_name)
        assert module_name_entered, "Module name girilemedi"

        version_entered = self.create_mdl_page.enter_version(self.test_version)
        assert version_entered, "Version girilemedi"

        add_clicked = self.create_mdl_page.click_versionadd_button()
        assert add_clicked, "ADD butonuna tıklanamadı"

        save_clicked = self.create_mdl_page.click_save_button()
        assert save_clicked, "SAVE butonuna tıklanamadı"

        time.sleep(2)

        self.appman_page.click_modulelist_button(self.test_app_name)
        time.sleep(2)

        page_source = self.driver.page_source
        module_found = self.test_module_name in page_source
        assert module_found, f"Module '{self.test_module_name}' bulunamadı"

        print(f"Test başarılı: Module '{self.test_module_name}' başarıyla oluşturuldu")


    def test_TC026_create_module_empty_version(self):
        """TC_026: Module Name girip Version girmeden module oluşturma"""
        print("\nTC_026: Module Name girip Version girmeden module oluşturma ===")

        # Önce test app oluştur
        app_created = self._create_test_app()
        assert app_created, "Test app oluşturulamadı"

        # Module List sayfasına git
        self.appman_page.click_modulelist_button(self.test_app_name)
        time.sleep(1)

        add_module_clicked = self.appman_page.click_modulelistADD_button(self.test_app_name)
        assert add_module_clicked, "'+' butonuna tıklanamadı"

        time.sleep(1)

        module_name_entered = self.create_mdl_page.enter_modulename(self.test_module_name)
        assert module_name_entered, "Module name girilemedi"

        save_button = self.create_mdl_page.find_element(self.create_mdl_page.SAVE_BUTTON)
        is_disabled = save_button.get_attribute("disabled") is not None
        assert is_disabled, "SAVE butonu disabled olmalıydı (version eklenmediği için)"

        print("Test başarılı: Version eklenmeden SAVE disabled kaldı")


    def test_TC027_create_module_empty_name(self):
        """TC_027: Module Name girmeden module oluşturma"""
        print("\nTC_027: Module Name girmeden module oluşturma ===")

        # Önce test app oluştur
        app_created = self._create_test_app()
        assert app_created, "Test app oluşturulamadı"

        # Module List sayfasına git
        self.appman_page.click_modulelist_button(self.test_app_name)
        time.sleep(1)

        add_module_clicked = self.appman_page.click_modulelistADD_button(self.test_app_name)
        assert add_module_clicked, "'+' butonuna tıklanamadı"

        time.sleep(1)

        version_entered = self.create_mdl_page.enter_version(self.test_version)
        assert version_entered, "Version girilemedi"

        add_clicked = self.create_mdl_page.click_versionadd_button()
        assert add_clicked, "ADD butonuna tıklanamadı"

        save_button = self.create_mdl_page.find_element(self.create_mdl_page.SAVE_BUTTON)
        is_disabled = save_button.get_attribute("disabled") is not None
        assert is_disabled, "SAVE butonu disabled olmalıydı (module name girilmediği için)"

        print("Test başarılı: Module Name girilmediğinde SAVE disabled kaldı")


    def test_TC028_create_module_both_empty(self):
        """TC_028: İkisini de boş bırakarak module oluşturma"""
        print("\nTC_028: İkisini de boş bırakarak module oluşturma ===")

        # Önce test app oluştur
        app_created = self._create_test_app()
        assert app_created, "Test app oluşturulamadı"

        # Module List sayfasına git
        self.appman_page.click_modulelist_button(self.test_app_name)
        time.sleep(1)

        add_module_clicked = self.appman_page.click_modulelistADD_button(self.test_app_name)
        assert add_module_clicked, "'+' butonuna tıklanamadı"

        time.sleep(1)

        save_button = self.create_mdl_page.find_element(self.create_mdl_page.SAVE_BUTTON)
        is_disabled = save_button.get_attribute("disabled") is not None
        assert is_disabled, "SAVE butonu disabled olmalıydı (her iki alan da boş)"

        print("Test başarılı: Her iki alan boş bırakıldığında SAVE disabled kaldı")


    def test_TC029_create_module_multiple_versions(self):
        """TC_029: Module Name girip birden fazla version ekleyerek module kaydetme"""
        print("\nTC_029: Module Name girip birden fazla version ekleyerek module kaydetme ===")

        # Önce test app oluştur
        app_created = self._create_test_app()
        assert app_created, "Test app oluşturulamadı"

        # Module List sayfasına git
        self.appman_page.click_modulelist_button(self.test_app_name)
        time.sleep(1)

        # '+' butonuna tıkla
        add_module_clicked = self.appman_page.click_modulelistADD_button(self.test_app_name)
        assert add_module_clicked, "'+' butonuna tıklanamadı"

        time.sleep(2)

        # Module Name gir
        module_name_entered = self.create_mdl_page.enter_modulename(self.test_module_name)
        assert module_name_entered, "Module Name girilemedi"

        # İlk Version gir
        version1_entered = self.create_mdl_page.enter_version(self.test_version)
        assert version1_entered, "İlk Version girilemedi"

        # İlk ADD butonuna tıkla
        add1_clicked = self.create_mdl_page.click_versionadd_button()
        assert add1_clicked, "İlk ADD butonuna tıklanamadı"

        # İkinci Version gir
        version2_entered = self.create_mdl_page.enter_version(self.test_version_2)
        assert version2_entered, "İkinci Version girilemedi"

        # İkinci ADD butonuna tıkla
        add2_clicked = self.create_mdl_page.click_versionadd_button()
        assert add2_clicked, "İkinci ADD butonuna tıklanamadı"

        # SAVE butonuna tıkla
        save_clicked = self.create_mdl_page.click_save_button()
        assert save_clicked, "SAVE butonuna tıklanamadı"

        time.sleep(2)

        self.appman_page.click_modulelist_button(self.test_app_name)
        time.sleep(2)

        # Module'ün oluşturulduğunu kontrol et
        page_source = self.driver.page_source
        module_found = self.test_module_name in page_source
        assert module_found, f"Çoklu versiyonlu module '{self.test_module_name}' listede görünmüyor"

        print(f"Test başarılı: Çoklu versiyonlu module '{self.test_module_name}' başarıyla oluşturuldu")



    def test_TC030_create_module_duplicate_name(self):
        """TC_030: Tamamen aynı isimde module name ile kaydetme"""
        print("\nTC_030: Tamamen aynı isimde module name ile kaydetme ===")

        # Önce test app oluştur
        app_created = self._create_test_app()
        assert app_created, "Test app oluşturulamadı"

        # Module List sayfasına git
        self.appman_page.click_modulelist_button(self.test_app_name)
        time.sleep(1)

        # İlk module'ü oluştur
        add_module_clicked = self.appman_page.click_modulelistADD_button(self.test_app_name)
        assert add_module_clicked, "'+' butonuna tıklanamadı"

        time.sleep(1)

        module_name_entered = self.create_mdl_page.enter_modulename(self.test_module_name)
        assert module_name_entered, "Module Name girilemedi"

        version_entered = self.create_mdl_page.enter_version(self.test_version)
        assert version_entered, "Version girilemedi"

        add_clicked = self.create_mdl_page.click_versionadd_button()
        assert add_clicked, "ADD butonuna tıklanamadı"

        save_clicked = self.create_mdl_page.click_save_button()
        assert save_clicked, "SAVE butonuna tıklanamadı"

        time.sleep(2)
        print("İlk module oluşturuldu")

        # Aynı isimde ikinci module oluşturmaya çalış
        add_module_clicked2 = self.appman_page.click_modulelistADD_button(self.test_app_name)
        assert add_module_clicked2, "İkinci '+' butonuna tıklanamadı"

        time.sleep(1)

        # Aynı Module Name gir
        module_name_entered2 = self.create_mdl_page.enter_modulename(self.test_module_name)
        assert module_name_entered2, "İkinci Module Name girilemedi"

        version_entered2 = self.create_mdl_page.enter_version(self.test_version_2)
        assert version_entered2, "İkinci Version girilemedi"

        add_clicked2 = self.create_mdl_page.click_versionadd_button()
        assert add_clicked2, "İkinci ADD butonuna tıklanamadı"

        save_clicked2 = self.create_mdl_page.click_save_button()
        time.sleep(2)

        # Modal hala açık mı? (hata varsa açık kalır)
        modal_present = "modal" in self.driver.page_source.lower()
        if modal_present:
            print("Modal açık kaldı - Duplicate name hatası alındı")
        else:
            print("UYARI: Aynı isimde ikinci module oluşturulabildi!")

        print("Test tamamlandı: Duplicate module name kontrolü yapıldı")


    def test_TC031_create_module_different_languages(self):
        """TC_031: Farklı dillerde module name ile kaydetme"""
        print("\nTC_031: Farklı dillerde module name ile kaydetme ===")

        # Önce test app oluştur
        app_created = self._create_test_app()
        assert app_created, "Test app oluşturulamadı"

        # Module List sayfasına git
        self.appman_page.click_modulelist_button(self.test_app_name)

        # Farklı dil karakterleri
        language_names = [
            ("Arabic", "وحدة_اختبار"),
            ("Turkish", "Türkçe_Modül_ÇĞİÖŞÜ"),
            ("Chinese", "测试模块"),
            ("Russian", "Тестовый_модуль"),
            ("Japanese", "テストモジュール"),
        ]

        for lang_name, module_name in language_names:
            print(f"\n{lang_name} karakterleri test ediliyor: {module_name}")

            try:
                time.sleep(1)

                # '+' butonuna tıkla
                add_module_clicked = self.appman_page.click_modulelistADD_button(self.test_app_name)
                assert add_module_clicked, "'+' butonuna tıklanamadı"

                time.sleep(1)

                # Farklı dilde module name gir
                module_name_entered = self.create_mdl_page.enter_modulename(module_name)

                if module_name_entered:
                    # Version gir ve ADD
                    version_entered = self.create_mdl_page.enter_version(self.test_version)
                    if version_entered:
                        add_clicked = self.create_mdl_page.click_versionadd_button()
                        if add_clicked:
                            # SAVE butonuna tıkla
                            save_clicked = self.create_mdl_page.click_save_button()
                            time.sleep(2)

                            # Oluşturuldu mu kontrol et
                            page_source = self.driver.page_source
                            if module_name in page_source:
                                print(f"{lang_name} karakterleri kabul edildi")
                            else:
                                print(f"{lang_name} karakterleri reddedildi")

                # Modal varsa kapat
                try:
                    cancel_button = self.driver.find_element(By.XPATH, "//span[text()='CANCEL']")
                    cancel_button.click()
                    time.sleep(1)
                except:
                    pass

            except Exception as e:
                print(f"{lang_name} test hatası: {e}")

        print("Farklı dil karakterleri testi tamamlandı")



    def test_TC032_sql_injection_module_name(self):
        """TC_032: SQL cümleciği ile module name oluşturma"""
        print("\nTC_032: SQL cümleciği ile module name oluşturma ===")

        # Önce test app oluştur
        app_created = self._create_test_app()
        assert app_created, "Test app oluşturulamadı"

        # Module List sayfasına git
        self.appman_page.click_modulelist_button(self.test_app_name)
        time.sleep(1)

        # '+' butonuna tıkla
        add_module_clicked = self.appman_page.click_modulelistADD_button(self.test_app_name)
        assert add_module_clicked, "'+' butonuna tıklanamadı"

        time.sleep(1)

        # SQL injection payload
        sql_payload = "'; DROP TABLE modules; --"

        # SQL payload'ını Module Name alanına gir
        module_name_entered = self.create_mdl_page.enter_modulename(sql_payload)
        assert module_name_entered, "SQL payload girilemedi"

        # Version gir ve ADD
        version_entered = self.create_mdl_page.enter_version(self.test_version)
        assert version_entered, "Version girilemedi"

        add_clicked = self.create_mdl_page.click_versionadd_button()
        assert add_clicked, "ADD butonuna tıklanamadı"

        # SAVE butonuna tıkla
        save_clicked = self.create_mdl_page.click_save_button()
        time.sleep(2)

        # Sistem hala çalışıyor mu kontrol et
        new_test = self.appman_page.click_modulelistADD_button(self.test_app_name)
        assert new_test, "Sistem zarar görmüş - Module modal açılmıyor"

        print("Test başarılı: SQL injection sistemi etkilemedi")


    def test_TC033_edit_module(self):
        """TC_033: Module'ü düzenleme"""
        print("\nTC_033: Module'ü düzenleme ===")

        # Önce test app oluştur
        app_created = self._create_test_app()
        assert app_created, "Test app oluşturulamadı"

        # Module List sayfasına git ve module oluştur
        self.appman_page.click_modulelist_button(self.test_app_name)
        time.sleep(1)

        # Önce bir module oluştur
        add_module_clicked = self.appman_page.click_modulelistADD_button(self.test_app_name)
        assert add_module_clicked, "'+' butonuna tıklanamadı"

        module_name_entered = self.create_mdl_page.enter_modulename(self.test_module_name)
        assert module_name_entered, "Module name girilemedi"

        version_entered = self.create_mdl_page.enter_version(self.test_version)
        assert version_entered, "Version girilemedi"

        add_clicked = self.create_mdl_page.click_versionadd_button()
        assert add_clicked, "ADD butonuna tıklanamadı"

        save_clicked = self.create_mdl_page.click_save_button()
        assert save_clicked, "SAVE butonuna tıklanamadı"

        time.sleep(2)
        print("Test module oluşturuldu")

        # Module edit butonuna tıkla
        edit_clicked = self.appman_page.click_editmodule_button(self.test_app_name, self.test_module_name)
        assert edit_clicked, "Module Edit butonuna tıklanamadı"

        time.sleep(1)

        # Yeni version ekle
        new_version_entered = self.create_mdl_page.enter_version(self.test_version_2)
        assert new_version_entered, "Yeni version girilemedi"

        add_new_clicked = self.create_mdl_page.click_versionadd_button()
        assert add_new_clicked, "Yeni version ADD butonuna tıklanamadı"

        # SAVE butonuna tıkla
        save_edit_clicked = self.create_mdl_page.click_save_button()
        assert save_edit_clicked, "Edit SAVE butonuna tıklanamadı"

        time.sleep(2)

        print("Test başarılı: Module başarıyla düzenlendi ve yeni version eklendi")


    def test_TC034_delete_module(self):
        """TC_034: Module'ü silme"""
        print("\nTC_034: Module'ü silme ===")

        # Önce test app oluştur
        app_created = self._create_test_app()
        assert app_created, "Test app oluşturulamadı"

        # Module List sayfasına git ve module oluştur
        self.appman_page.click_modulelist_button(self.test_app_name)
        time.sleep(1)

        # Önce bir module oluştur
        add_module_clicked = self.appman_page.click_modulelistADD_button(self.test_app_name)
        assert add_module_clicked, "'+' butonuna tıklanamadı"

        module_name_entered = self.create_mdl_page.enter_modulename(self.test_module_name)
        assert module_name_entered, "Module name girilemedi"

        version_entered = self.create_mdl_page.enter_version(self.test_version)
        assert version_entered, "Version girilemedi"

        add_clicked = self.create_mdl_page.click_versionadd_button()
        assert add_clicked, "ADD butonuna tıklanamadı"

        save_clicked = self.create_mdl_page.click_save_button()
        assert save_clicked, "SAVE butonuna tıklanamadı"

        time.sleep(2)

        # Module'ü sil
        delete_success = self.appman_page.click_deletemodule_andconfirm_button(self.test_app_name,
                                                                               self.test_module_name)
        assert delete_success, "Module silinemedi"

        time.sleep(2)

        # Module silindiğini kontrol et
        page_source = self.driver.page_source
        assert self.test_module_name not in page_source, "Module silinemedi"

        print("Test başarılı: Module başarıyla silindi")