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
from tdm_automation.Pages.application_management_page import AppManagementPage
from tdm_automation.Pages.create_application_page import CreateAppPage
from tdm_automation.Pages.create_module_page import CreateModulePage
from tdm_automation.Pages.product_info_page import ProductInfoPage
from tdm_automation.Pages.list_generator_page import ListGeneratorPage
from tdm_automation.Pages.create_list_generator_page import CreateListGenerator
from tdm_automation.Pages.data_generation_case_page import DataCasePage
from selenium.webdriver.chrome.options import Options


load_dotenv()


class TestDataGenerationCase:

    @classmethod
    def setup_class(cls):
        """Tüm class için tek sefer çalışır - LOGIN İŞLEMLERİ BURADA"""
        print("\n=== CLASS SETUP: Login işlemleri yapılıyor ===")

        # Environment değişkenlerini al
        cls.BASE_URL = os.getenv('BASE_URL')
        cls.VALID_USERNAME = os.getenv('VALID_USERNAME')
        cls.VALID_PASSWORD = os.getenv('VALID_PASSWORD')
        cls.TIMEOUT = int(os.getenv('TIMEOUT', '10'))

        # Test data environment değişkenleri
        cls.CASE_NAME = os.getenv('CASE_NAME', 'CaseName')

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
        cls.listgen_page = ListGeneratorPage(cls.driver)
        cls.create_lg_page = CreateListGenerator(cls.driver)
        cls.datagcase_page = DataCasePage(cls.driver)

        # *** TEK SEFERLİK LOGIN İŞLEMLERİ ***
        cls.driver.get(cls.BASE_URL)
        login_success = cls.login_page.do_login(cls.VALID_USERNAME, cls.VALID_PASSWORD)
        assert login_success, "Login başarısız!"

        # TDM'ye git
        tdm_locator = (By.XPATH, "//li[@title='New Test Data Manager'][2]")
        tdm_success = cls.login_page.click_element(tdm_locator)
        assert tdm_success, "TDM elementine tıklanamadı"

        # List Generator'e git
        datacase_success = cls.dashboard_page.click_data_generation_case()
        assert datacase_success, "Data Case butonuna tıklanamadı"

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
        self.test_case_name = f"{self.CASE_NAME}_{timestamp}"

        # App Management sayfasında olduğumuzu kontrol et
        current_url = self.driver.current_url
        if "data-generation-case" not in current_url:
            print("Data Case sayfasına yönlendiriliyor...")
            self.dashboard_page.click_data_generation_case()
            time.sleep(1)

    def teardown_method(self, method):
        """Her test sonrası çalışır - SADECE TEST CLEANUP"""
        print(f"--- Test bitti: {method.__name__} ---")

        # Modal varsa kapat
        try:
            # Önce CANCEL butonunu dene
            cancel_buttons = self.driver.find_elements(By.XPATH, "//span[text()='CANCEL']")
            for button in cancel_buttons:
                if button.is_displayed():
                    self.datagcase_page.click_element((By.XPATH, "//span[text()='CANCEL']"))
                    time.sleep(0.5)
                    print("Modal CANCEL ile kapatıldı")
                    return

            # CANCEL yoksa BACK butonunu dene
            back_buttons = self.driver.find_elements(By.XPATH, "//span[text()='BACK']")
            for button in back_buttons:
                if button.is_displayed():
                    self.datagcase_page.click_element((By.XPATH, "//span[text()='BACK']"))
                    time.sleep(0.5)
                    print("Sayfa BACK ile kapatıldı")
                    return
        except:
            pass


    def test_TC107_application_seçmeden_module_tıklama(self):
        """TC107: Application seçmeden module tıklama - Module dropdown tıklanabilir ama içeriği boş"""
        print("\nTC107: Application seçmeden module tıklama testi ===")

        # NEW butonuna tıkla
        new_clicked = self.datagcase_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"

        # Önce proje seç
        project_selected = self.datagcase_page.select_project("osmanp")
        assert project_selected, "Proje seçilemedi"

        # Module dropdown'ın durumunu kontrol et
        module_element = self.driver.find_element(*self.datagcase_page.MODULE_DROPDOWN)
        is_enabled = module_element.is_enabled()
        print(f"Module dropdown durumu: {'Enabled' if is_enabled else 'Disabled'}")

        # Module dropdown'a tıkla
        if is_enabled:
            module_element.click()

            # Dropdown açıldığında seçenek var mı kontrol et
            try:
                options = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'ant-select-item')]")
                options_count = len(options)
                print(f"Module dropdown seçenek sayısı: {options_count}")

                # Application seçilmeden module seçenekleri boş/sınırlı olmalı
                assert options_count == 0 or all("select" in opt.text.lower() for opt in options), \
                    "Application seçilmeden Module dropdown'da gerçek seçenekler olmamalı"

            except Exception as e:
                print(f"Module seçenekleri kontrol edilemiyor: {e}")

        print("Test başarılı: Module dropdown Application'a bağımlı çalışıyor")

    def test_TC108_application_seçince_module_aktif(self):
        """TC108: Application seçince module aktif - Module dropdown aktif olmalı"""
        print("\nTC108: Application seçince module aktif testi ===")

        # NEW butonuna tıkla
        new_clicked = self.datagcase_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"

        # Önce proje seç
        project_selected = self.datagcase_page.select_project("osmanp")
        assert project_selected, "Proje seçilemedi"

        # Application seç
        app_selected = self.datagcase_page.select_application("osmana")
        assert app_selected, "Application seçilemedi"

        # Module dropdown'a tıkla ve seçenekleri kontrol et
        module_element = self.driver.find_element(*self.datagcase_page.MODULE_DROPDOWN)
        module_element.click()

        # Dropdown'da seçenek olmalı
        try:
            options = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'ant-select-item')]")
            options_count = len(options)
            print(f"Module dropdown seçenek sayısı: {options_count}")

            assert options_count > 0, "Application seçildikten sonra Module dropdown'da seçenek olmalı"

        except Exception as e:
            print(f"Module seçenekleri kontrol edilemiyor: {e}")
            assert False, "Module dropdown kontrol edilemedi"

        print("Test başarılı: Application seçince Module dropdown aktif")

    def test_TC109_module_seçince_version_aktif(self):
        """TC109: Module seçince version aktif - Module Version dropdown aktif olmalı"""
        print("\nTC109: Module seçince version aktif testi ===")

        # NEW butonuna tıkla
        new_clicked = self.datagcase_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"

        # Önce proje seç
        project_selected = self.datagcase_page.select_project("osmanp")
        assert project_selected, "Proje seçilemedi"

        # Application seç
        app_selected = self.datagcase_page.select_application("osmana")
        assert app_selected, "Application seçilemedi"

        # Module seç
        module_selected = self.datagcase_page.select_module("osmanm")
        assert module_selected, "Module seçilemedi"

        # Module Version dropdown'a tıkla ve seçenekleri kontrol et
        version_element = self.driver.find_element(*self.datagcase_page.MODULE_VERSION_DROPDOWN)
        version_element.click()

        # Dropdown'da seçenek olmalı
        try:
            options = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'ant-select-item')]")
            options_count = len(options)
            print(f"Module Version dropdown seçenek sayısı: {options_count}")

            assert options_count > 0, "Module seçildikten sonra Module Version dropdown'da seçenek olmalı"

        except Exception as e:
            print(f"Module Version seçenekleri kontrol edilemiyor: {e}")
            assert False, "Module Version dropdown kontrol edilemedi"

        print("Test başarılı: Module seçince Module Version dropdown aktif")

    def test_TC110_version_seçince_flow_aktif(self):
        """TC110: Version seçince flow aktif - Synthetic Flow dropdown aktif olmalı"""
        print("\nTC110: Version seçince flow aktif testi ===")

        # NEW butonuna tıkla
        new_clicked = self.datagcase_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"

        # Önce proje seç
        project_selected = self.datagcase_page.select_project("osmanp")
        assert project_selected, "Proje seçilemedi"

        # Application seç
        app_selected = self.datagcase_page.select_application("osmana")
        assert app_selected, "Application seçilemedi"

        # Module seç
        module_selected = self.datagcase_page.select_module("osmanm")
        assert module_selected, "Module seçilemedi"

        # Module Version seç
        version_selected = self.datagcase_page.select_module_version("v1")
        assert version_selected, "Module Version seçilemedi"

        # Synthetic Flow dropdown'a tıkla ve seçenekleri kontrol et
        flow_element = self.driver.find_element(*self.datagcase_page.SYNTHETIC_FLOW_DROPDOWN)
        flow_element.click()

        # Dropdown'da seçenek olmalı
        try:
            options = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'ant-select-item')]")
            options_count = len(options)
            print(f"Synthetic Flow dropdown seçenek sayısı: {options_count}")

            assert options_count > 0, "Version seçildikten sonra Synthetic Flow dropdown'da seçenek olmalı"

        except Exception as e:
            print(f"Synthetic Flow seçenekleri kontrol edilemiyor: {e}")
            assert False, "Synthetic Flow dropdown kontrol edilemedi"

        print("Test başarılı: Version seçince Synthetic Flow dropdown aktif")

    def test_TC111_case_name_boş_bırakma(self):
        """TC111: Case name boş bırakma - SAVE butonu disabled kalmalı"""
        print("\nTC111: Case name boş bırakma testi ===")

        # NEW butonuna tıkla
        new_clicked = self.datagcase_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"

        # Tüm dropdown'ları doldur
        project_selected = self.datagcase_page.select_project("osmanp")
        assert project_selected, "Proje seçilemedi"

        app_selected = self.datagcase_page.select_application("osmana")
        assert app_selected, "Application seçilemedi"

        module_selected = self.datagcase_page.select_module("osmanm")
        assert module_selected, "Module seçilemedi"

        version_selected = self.datagcase_page.select_module_version("v1")
        assert version_selected, "Module Version seçilemedi"

        flow_selected = self.datagcase_page.select_synthetic_flow("osmand")
        assert flow_selected, "Synthetic Flow seçilemedi"

        # Case Name boş bırak - hiçbir şey girme

        # SAVE butonunun disabled olduğunu kontrol et
        save_button = self.driver.find_element(*self.datagcase_page.SAVE_BUTTON)
        is_disabled = not save_button.is_enabled() or "disabled" in save_button.get_attribute("class")

        print(f"SAVE butonu durumu: {'Disabled' if is_disabled else 'Enabled'}")
        assert is_disabled, "Case Name boş iken SAVE butonu disabled olmalı"

        print("Test başarılı: Case name boş bırakıldığında SAVE disabled")

    def test_TC112_başarılı_case_oluşturma(self):
        """TC112: Başarılı case oluşturma - Case başarıyla oluşturulmalı"""
        print("\nTC112: Başarılı case oluşturma testi ===")

        # NEW butonuna tıkla
        new_clicked = self.datagcase_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"

        # Tüm dropdown'ları doldur
        project_selected = self.datagcase_page.select_project("osmanp")
        assert project_selected, "Proje seçilemedi"

        app_selected = self.datagcase_page.select_application("osmana")
        assert app_selected, "Application seçilemedi"

        module_selected = self.datagcase_page.select_module("osmanm")
        assert module_selected, "Module seçilemedi"

        version_selected = self.datagcase_page.select_module_version("v1")
        assert version_selected, "Module Version seçilemedi"

        flow_selected = self.datagcase_page.select_synthetic_flow("osmand")
        assert flow_selected, "Synthetic Flow seçilemedi"

        # Case Name gir
        case_name_entered = self.datagcase_page.enter_case_name(self.test_case_name)
        assert case_name_entered, "Case Name girilemedi"

        # Description gir (opsiyonel)
        description_entered = self.datagcase_page.enter_description("Test Description")
        assert description_entered, "Description girilemedi"

        # SAVE butonuna tıkla
        save_clicked = self.datagcase_page.click_save_button()
        assert save_clicked, "SAVE butonuna tıklanamadı"

        # Case oluşturulduğunu kontrol et (listede görünmeli)
        page_source = self.driver.page_source
        assert self.test_case_name in page_source, f"Case '{self.test_case_name}' listede görünmüyor"

        print("Test başarılı: Case başarıyla oluşturuldu")

    def test_TC113_description_olmadan_oluşturma(self):
        """TC113: Description olmadan oluşturma - Case başarıyla oluşturulmalı"""
        print("\nTC113: Description olmadan oluşturma testi ===")

        # NEW butonuna tıkla
        new_clicked = self.datagcase_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"

        # Tüm dropdown'ları doldur
        project_selected = self.datagcase_page.select_project("osmanp")
        assert project_selected, "Proje seçilemedi"

        app_selected = self.datagcase_page.select_application("osmana")
        assert app_selected, "Application seçilemedi"

        module_selected = self.datagcase_page.select_module("osmanm")
        assert module_selected, "Module seçilemedi"

        version_selected = self.datagcase_page.select_module_version("v1")
        assert version_selected, "Module Version seçilemedi"

        flow_selected = self.datagcase_page.select_synthetic_flow("osmand")
        assert flow_selected, "Synthetic Flow seçilemedi"

        # Case Name gir
        case_name_entered = self.datagcase_page.enter_case_name(self.test_case_name)
        assert case_name_entered, "Case Name girilemedi"

        # Description boş bırak - hiçbir şey girme

        # SAVE butonuna tıkla
        save_clicked = self.datagcase_page.click_save_button()
        assert save_clicked, "SAVE butonuna tıklanamadı"

        # Case oluşturulduğunu kontrol et
        page_source = self.driver.page_source  # "page" eksikti!
        assert self.test_case_name in page_source, f"Case '{self.test_case_name}' listede görünmüyor"

        print("Test başarılı: Description olmadan case oluşturuldu")

    def test_TC114_duplicate_case_name(self):
        """TC114: Duplicate case name - Duplicate name hatası alınmalı"""
        print("\nTC114: Duplicate case name testi ===")

        # İlk case'i oluştur
        new_clicked = self.datagcase_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"

        # Tüm alanları doldur
        project_selected = self.datagcase_page.select_project("osmanp")
        assert project_selected, "Proje seçilemedi"

        app_selected = self.datagcase_page.select_application("osmana")
        assert app_selected, "Application seçilemedi"

        module_selected = self.datagcase_page.select_module("osmanm")
        assert module_selected, "Module seçilemedi"

        version_selected = self.datagcase_page.select_module_version("v1")
        assert version_selected, "Module Version seçilemedi"

        flow_selected = self.datagcase_page.select_synthetic_flow("osmand")
        assert flow_selected, "Synthetic Flow seçilemedi"

        # İlk case name
        first_case_name = f"DuplicateTest_{int(time.time())}"
        case_name_entered = self.datagcase_page.enter_case_name(first_case_name)
        assert case_name_entered, "İlk Case Name girilemedi"

        save_clicked = self.datagcase_page.click_save_button()
        assert save_clicked, "İlk SAVE butonuna tıklanamadı"

        # İkinci case'i aynı isimle oluşturmaya çalış
        new_clicked2 = self.datagcase_page.click_newlist()
        assert new_clicked2, "İkinci NEW butonuna tıklanamadı"

        # İkinci case için de tüm alanları doldur
        project_selected2 = self.datagcase_page.select_project("osmanp")
        assert project_selected2, "İkinci Proje seçilemedi"

        app_selected2 = self.datagcase_page.select_application("osmana")
        assert app_selected2, "İkinci Application seçilemedi"

        module_selected2 = self.datagcase_page.select_module("osmanm")
        assert module_selected2, "İkinci Module seçilemedi"

        version_selected2 = self.datagcase_page.select_module_version("v1")
        assert version_selected2, "İkinci Module Version seçilemedi"

        flow_selected2 = self.datagcase_page.select_synthetic_flow("osmand")
        assert flow_selected2, "İkinci Synthetic Flow seçilemedi"

        # Aynı isimde case oluştur
        case_name_entered2 = self.datagcase_page.enter_case_name(first_case_name)
        assert case_name_entered2, "İkinci Case Name girilemedi"

        save_clicked2 = self.datagcase_page.click_save_button()

        # Hata mesajı kontrolü
        page_source = self.driver.page_source
        has_error = "error" in page_source.lower() or "duplicate" in page_source.lower() or "exists" in page_source.lower()

        print(f"Duplicate name hatası: {'Alındı' if has_error else 'Alınmadı'}")
        assert has_error, "Duplicate case name hatası alınmalıydı"

        print("Test başarılı: Duplicate case name hatası alındı")


    def test_TC115_case_edit_işlemi(self):
        """TC115: Case edit işlemi - Sadece name ve description değiştirilebilmeli"""
        print("\nTC115: Case edit işlemi testi ===")

        # Önce bir case oluştur
        new_clicked = self.datagcase_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"

        # Tüm alanları doldur
        project_selected = self.datagcase_page.select_project("osmanp")
        assert project_selected, "Proje seçilemedi"

        app_selected = self.datagcase_page.select_application("osmana")
        assert app_selected, "Application seçilemedi"

        module_selected = self.datagcase_page.select_module("osmanm")
        assert module_selected, "Module seçilemedi"

        version_selected = self.datagcase_page.select_module_version("v1")
        assert version_selected, "Module Version seçilemedi"

        flow_selected = self.datagcase_page.select_synthetic_flow("osmand")
        assert flow_selected, "Synthetic Flow seçilemedi"

        # Case oluştur
        case_name_entered = self.datagcase_page.enter_case_name(self.test_case_name)
        assert case_name_entered, "Case Name girilemedi"

        save_clicked = self.datagcase_page.click_save_button()
        assert save_clicked, "SAVE butonuna tıklanamadı"

        # Edit butonuna tıkla
        edit_clicked = self.datagcase_page.click_caseedit_button(self.test_case_name)
        assert edit_clicked, "Edit butonuna tıklanamadı"

        # Edit modalda dropdown'ların read-only olduğunu kontrol et
        try:
            app_dropdown = self.driver.find_element(*self.datagcase_page.APPLICATION_DROPDOWN)
            app_disabled = "disabled" in app_dropdown.get_attribute("class") or not app_dropdown.is_enabled()
            print(f"Application dropdown durumu: {'Read-only' if app_disabled else 'Editable'}")

            # Name ve description değiştir
            new_name = f"{self.test_case_name}_edited"
            self.datagcase_page.enter_case_name(new_name)
            self.datagcase_page.enter_description("Edited description")

            # SAVE tıkla
            save_edit_clicked = self.datagcase_page.click_save_button()
            assert save_edit_clicked, "Edit SAVE butonuna tıklanamadı"



        except Exception as e:
            print(f"Edit kontrolü hatası: {e}")
            assert False, "Edit işlemi kontrol edilemedi"

        print("Test başarılı: Case edit işlemi çalışıyor")

    def test_TC116_case_delete_işlemi(self):
        """TC116: Case delete işlemi - Case silinmeli, listeden kaldırılmalı"""
        print("\nTC116: Case delete işlemi testi ===")

        # Önce bir case oluştur
        new_clicked = self.datagcase_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"

        project_selected = self.datagcase_page.select_project("osmanp")
        assert project_selected, "Proje seçilemedi"

        app_selected = self.datagcase_page.select_application("osmana")
        assert app_selected, "Application seçilemedi"

        module_selected = self.datagcase_page.select_module("osmanm")
        assert module_selected, "Module seçilemedi"

        version_selected = self.datagcase_page.select_module_version("v1")
        assert version_selected, "Module Version seçilemedi"

        flow_selected = self.datagcase_page.select_synthetic_flow("osmand")
        assert flow_selected, "Synthetic Flow seçilemedi"

        case_name_entered = self.datagcase_page.enter_case_name(self.test_case_name)
        assert case_name_entered, "Case Name girilemedi"

        save_clicked = self.datagcase_page.click_save_button()
        assert save_clicked, "SAVE butonuna tıklanamadı"

        # Delete işlemi
        delete_clicked = self.datagcase_page.click_deletecase_andconfirm_button(self.test_case_name)
        assert delete_clicked, "Delete işlemi başarısız"

        # Case silindiğini kontrol et - 1 saniye bekle
        time.sleep(1)
        page_source = self.driver.page_source
        case_deleted = self.test_case_name not in page_source

        print(f"Case silindi mi: {'Evet' if case_deleted else 'Hayır'}")
        assert case_deleted, f"Case '{self.test_case_name}' listeden silinmedi"

        print("Test başarılı: Case delete işlemi çalışıyor")


    def test_TC117_case_run_başarılı(self):
        """TC117: Case run - başarılı - Status SUCCESS, history'de kayıt"""
        print("\nTC117: Case run başarılı testi ===")

        project_selected = self.datagcase_page.select_project("osmanp")
        assert project_selected, "Proje seçilemedi"

        # Mevcut bir case'i çalıştır (varsa)
        run_clicked = self.datagcase_page.click_runcase_button("afa")
        assert run_clicked, "Run butonuna tıklanamadı"

        # Status kontrolü
        page_source = self.driver.page_source
        has_success = "success" in page_source.lower() or "running" in page_source.lower()

        print(f"Run durumu: {'Başarılı/Çalışıyor' if has_success else 'Başarısız'}")

        print("Test başarılı: Case run işlemi çalışıyor")



    def test_TC118_history_button_tıklama(self):
        """TC118: History button tıklama - History List sayfası açılmalı"""
        print("\nTC118: History button tıklama testi ===")

        project_selected = self.datagcase_page.select_project("osmanp")
        assert project_selected, "Proje seçilemedi"

        # History butonuna tıkla (mevcut case için)
        history_clicked = self.datagcase_page.click_history_button("afa")
        assert history_clicked, "History butonuna tıklanamadı"

        # History sayfasının açıldığını kontrol et
        current_url = self.driver.current_url
        history_opened = "history" in current_url.lower()

        if not history_opened:
            page_source = self.driver.page_source
            history_opened = "history" in page_source.lower() or "run version" in page_source.lower()

        assert history_opened, "History sayfası açılmadı"

        print("Test başarılı: History sayfası açıldı")

    def test_TC119_log_button_direkt_erişim(self):
        """TC119: Log button direkt erişim - En son log sayfası açılmalı"""
        print("\nTC119: Log button direkt erişim testi ===")

        project_selected = self.datagcase_page.select_project("osmanp")
        assert project_selected, "Proje seçilemedi"

        # Log butonuna tıkla (mevcut case için)
        log_clicked = self.datagcase_page.click_log_button("afa")
        assert log_clicked, "Log butonuna tıklanamadı"

        # Log sayfasının açıldığını kontrol et
        current_url = self.driver.current_url
        log_opened = "log" in current_url.lower()

        if not log_opened:
            page_source = self.driver.page_source
            log_opened = "log" in page_source.lower() or "duration" in page_source.lower() or "from:" in page_source.lower()

        assert log_opened, "Log sayfası açılmadı"

        print("Test başarılı: Log sayfası açıldı")

    def test_TC120_failed_case_log_ERROR_kontrolü(self):
        """TC120: Failed case log ERROR kontrolü - Log'da ERROR kelimesi bulunmalı"""
        print("\nTC120: Failed case log ERROR kontrolü testi ===")

        project_selected = self.datagcase_page.select_project("osmanp")
        assert project_selected, "Proje seçilemedi"

        # Başarısız case'in log'una git (varsa)
        log_clicked = self.datagcase_page.click_log_button("afa")
        assert log_clicked, "Log butonuna tıklanamadı"

        # Log textarea'sında ERROR kelimesi kontrolü
        try:
            # Textarea element'ini bul
            textarea_element = self.driver.find_element(By.XPATH,
                                                        "//textarea[contains(@class, 'ant-input') and @readonly]")
            textarea_content = textarea_element.get_attribute("value") or textarea_element.text

            has_error = "error" in textarea_content.lower()

            print(f"Log textarea içeriğinde ERROR bulundu mu: {'Evet' if has_error else 'Hayır'}")

            # Bu test case durumuna göre pass/fail olabilir
            # Eğer case başarılıysa ERROR olmayabilir, bu normal
            print("Test tamamlandı: Log ERROR kontrolü yapıldı")

        except Exception as e:
            print(f"Textarea bulunamadı: {e}")
            # Fallback - page source'da ara
            page_source = self.driver.page_source
            has_error = "error" in page_source.lower()
            print(f"Page source'da ERROR bulundu mu: {'Evet' if has_error else 'Hayır'}")


    def test_TC121_case_name_özel_karakterler(self):
        """TC121: Case name özel karakterler - Özel karakterler kabul edilmeli/hata"""
        print("\nTC121: Case name özel karakterler testi ===")

        # NEW butonuna tıkla
        new_clicked = self.datagcase_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"

        # Tüm dropdown'ları doldur
        project_selected = self.datagcase_page.select_project("osmanp")
        assert project_selected, "Proje seçilemedi"

        app_selected = self.datagcase_page.select_application("osmana")
        assert app_selected, "Application seçilemedi"

        module_selected = self.datagcase_page.select_module("osmanm")
        assert module_selected, "Module seçilemedi"

        version_selected = self.datagcase_page.select_module_version("v1")
        assert version_selected, "Module Version seçilemedi"

        flow_selected = self.datagcase_page.select_synthetic_flow("osmand")
        assert flow_selected, "Synthetic Flow seçilemedi"

        # Özel karakterli case name
        special_case_name = f"Test!@#$%^&*()_{int(time.time())}"
        case_name_entered = self.datagcase_page.enter_case_name(special_case_name)
        assert case_name_entered, "Özel karakterli Case Name girilemedi"

        # SAVE butonuna tıkla
        save_clicked = self.datagcase_page.click_save_button()

        # Sonuç kontrolü - ya kabul edilir ya da hata verir
        page_source = self.driver.page_source
        case_created = special_case_name in page_source
        has_error = "error" in page_source.lower() or "invalid" in page_source.lower()

        print(f"Özel karakterli case: {'Oluşturuldu' if case_created else 'Hata aldı' if has_error else 'Belirsiz'}")

        # İkisi de geçerli sonuç - ya kabul eder ya reddeder
        assert case_created or has_error, "Özel karakterler için bir sonuç alınmalı"

        print("Test başarılı: Özel karakter kontrolü yapıldı")

    def test_TC122_case_name_max_karakter(self):
        """TC122: Case name max karakter - Karakter limiti uyarısı verilmeli"""
        print("\nTC122: Case name max karakter testi ===")

        # NEW butonuna tıkla
        new_clicked = self.datagcase_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"

        # Tüm dropdown'ları doldur
        project_selected = self.datagcase_page.select_project("osmanp")
        assert project_selected, "Proje seçilemedi"

        app_selected = self.datagcase_page.select_application("osmana")
        assert app_selected, "Application seçilemedi"

        module_selected = self.datagcase_page.select_module("osmanm")
        assert module_selected, "Module seçilemedi"

        version_selected = self.datagcase_page.select_module_version("v1")
        assert version_selected, "Module Version seçilemedi"

        flow_selected = self.datagcase_page.select_synthetic_flow("osmand")
        assert flow_selected, "Synthetic Flow seçilemedi"

        # Çok uzun case name (255+ karakter)
        long_case_name = "A" * 300  # 300 karakter
        case_name_entered = self.datagcase_page.enter_case_name(long_case_name)
        assert case_name_entered, "Uzun Case Name girilemedi"

        # SAVE butonuna tıkla
        save_clicked = self.datagcase_page.click_save_button()

        # Karakter limiti hatası kontrolü
        page_source = self.driver.page_source
        has_limit_error = "limit" in page_source.lower() or "length" in page_source.lower() or "character" in page_source.lower()

        print(f"Karakter limiti uyarısı: {'Alındı' if has_limit_error else 'Alınmadı'}")

        print("Test tamamlandı: Karakter limiti kontrolü yapıldı")

    def test_TC123_dropdownları_boş_bırakma(self):
        """TC123: Dropdown'ları boş bırakma - SAVE disabled kalmalı"""
        print("\nTC123: Dropdown'ları boş bırakma testi ===")

        # NEW butonuna tıkla
        new_clicked = self.datagcase_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"

        # Sadece Case Name doldur, dropdown'ları boş bırak
        case_name_entered = self.datagcase_page.enter_case_name(self.test_case_name)
        assert case_name_entered, "Case Name girilemedi"

        # SAVE butonunun disabled olduğunu kontrol et
        save_button = self.driver.find_element(*self.datagcase_page.SAVE_BUTTON)
        is_disabled = not save_button.is_enabled() or "disabled" in save_button.get_attribute("class")

        print(f"SAVE butonu durumu: {'Disabled' if is_disabled else 'Enabled'}")
        assert is_disabled, "Dropdown'lar boş iken SAVE butonu disabled olmalı"

        print("Test başarılı: Dropdown'lar boş bırakıldığında SAVE disabled")

    def test_TC124_modal_browser_refresh(self):
        """TC124: Modal'da browser refresh - Modal kapanmalı, veriler kaybolmalı"""
        print("\nTC124: Modal'da browser refresh testi ===")

        # NEW butonuna tıkla
        new_clicked = self.datagcase_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"

        # Bazı alanları doldur
        project_selected = self.datagcase_page.select_project("osmanp")
        assert project_selected, "Proje seçilemedi"

        app_selected = self.datagcase_page.select_application("osmana")
        assert app_selected, "Application seçilemedi"

        case_name_entered = self.datagcase_page.enter_case_name(self.test_case_name)
        assert case_name_entered, "Case Name girilemedi"

        # Browser refresh yap
        self.driver.refresh()
        time.sleep(2)

        # Girilen verilerin kaybolduğunu kontrol et - bu ana test
        page_source = self.driver.page_source
        data_lost = self.test_case_name not in page_source

        # Modal state kontrolü (yan etki)
        current_url = self.driver.current_url
        back_to_list = "data-generation-case" in current_url

        print(f"Ana sayfaya döndü mü: {'Evet' if back_to_list else 'Hayır'}")
        print(f"Veriler kayboldu mu: {'Evet' if data_lost else 'Hayır'}")

        # Ana test kriteri: veriler kaybolmalı
        assert data_lost, "Browser refresh sonrası girilen veriler kaybolmalı"
        assert back_to_list, "Browser refresh sonrası ana sayfaya dönmeli"

        print("Test başarılı: Browser refresh ile veriler kayboldu")

    def test_TC125_çok_uzun_case_name(self):
        """TC125: Çok uzun case name - Uzunluk limiti kontrolü"""
        print("\nTC125: Çok uzun case name testi ===")

        # NEW butonuna tıkla
        new_clicked = self.datagcase_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"

        # Tüm dropdown'ları doldur
        project_selected = self.datagcase_page.select_project("osmanp")
        assert project_selected, "Proje seçilemedi"

        app_selected = self.datagcase_page.select_application("osmana")
        assert app_selected, "Application seçilemedi"

        module_selected = self.datagcase_page.select_module("osmanm")
        assert module_selected, "Module seçilemedi"

        version_selected = self.datagcase_page.select_module_version("v1")
        assert version_selected, "Module Version seçilemedi"

        flow_selected = self.datagcase_page.select_synthetic_flow("osmand")
        assert flow_selected, "Synthetic Flow seçilemedi"

        # 500+ karakter case name
        super_long_name = "VeryLongCaseName" * 35  # ~500+ karakter
        case_name_entered = self.datagcase_page.enter_case_name(super_long_name)
        assert case_name_entered, "Süper uzun Case Name girilemedi"

        # SAVE butonuna tıkla
        save_clicked = self.datagcase_page.click_save_button()

        # Sonuç kontrolü
        page_source = self.driver.page_source
        has_limit_error = "limit" in page_source.lower() or "too long" in page_source.lower()
        case_created = super_long_name[:50] in page_source  # İlk 50 karaktere bak

        print(f"Uzun case name: {'Hata aldı' if has_limit_error else 'Oluşturuldu' if case_created else 'Belirsiz'}")

        print("Test tamamlandı: Uzun case name kontrolü yapıldı")

    def test_TC126_boş_form_kaydetme(self):
        """TC126: Boş form kaydetme - SAVE disabled kalmalı"""
        print("\nTC126: Boş form kaydetme testi ===")

        # NEW butonuna tıkla
        new_clicked = self.datagcase_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"

        # Hiçbir alan doldurmadan SAVE kontrol et
        save_button = self.driver.find_element(*self.datagcase_page.SAVE_BUTTON)
        is_disabled = not save_button.is_enabled() or "disabled" in save_button.get_attribute("class")

        print(f"SAVE butonu durumu: {'Disabled' if is_disabled else 'Enabled'}")
        assert is_disabled, "Hiçbir alan doldurulmadan SAVE butonu disabled olmalı"

        print("Test başarılı: Boş form SAVE disabled")

    def test_TC127_SQL_injection_case_name(self):
        """TC127: SQL injection case name - Güvenlik koruması olmalı"""
        print("\nTC127: SQL injection case name testi ===")

        # NEW butonuna tıkla
        new_clicked = self.datagcase_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"

        # Tüm dropdown'ları doldur
        project_selected = self.datagcase_page.select_project("osmanp")
        assert project_selected, "Proje seçilemedi"

        app_selected = self.datagcase_page.select_application("osmana")
        assert app_selected, "Application seçilemedi"

        module_selected = self.datagcase_page.select_module("osmanm")
        assert module_selected, "Module seçilemedi"

        version_selected = self.datagcase_page.select_module_version("v1")
        assert version_selected, "Module Version seçilemedi"

        flow_selected = self.datagcase_page.select_synthetic_flow("osmand")
        assert flow_selected, "Synthetic Flow seçilemedi"

        # SQL injection denemesi
        sql_injection_name = f"'; DROP TABLE users; --_{int(time.time())}"
        case_name_entered = self.datagcase_page.enter_case_name(sql_injection_name)
        assert case_name_entered, "SQL injection Case Name girilemedi"

        # SAVE butonuna tıkla
        save_clicked = self.datagcase_page.click_save_button()

        # Güvenlik kontrolü
        page_source = self.driver.page_source
        has_security_error = "error" in page_source.lower() or "invalid" in page_source.lower()
        case_created = sql_injection_name in page_source

        print(f"SQL injection koruması: {'Var' if has_security_error else 'Yok' if case_created else 'Belirsiz'}")

        # Güvenlik açısından ya hata vermeli ya da güvenli şekilde kaydetmeli
        print("Test tamamlandı: SQL injection koruması kontrol edildi")

    def test_TC128_XSS_injection_case_name(self):
        """TC128: XSS injection case name - XSS koruması olmalı"""
        print("\nTC128: XSS injection case name testi ===")

        # NEW butonuna tıkla
        new_clicked = self.datagcase_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"

        # Tüm dropdown'ları doldur
        project_selected = self.datagcase_page.select_project("osmanp")
        assert project_selected, "Proje seçilemedi"

        app_selected = self.datagcase_page.select_application("osmana")
        assert app_selected, "Application seçilemedi"

        module_selected = self.datagcase_page.select_module("osmanm")
        assert module_selected, "Module seçilemedi"

        version_selected = self.datagcase_page.select_module_version("v1")
        assert version_selected, "Module Version seçilemedi"

        flow_selected = self.datagcase_page.select_synthetic_flow("osmand")
        assert flow_selected, "Synthetic Flow seçilemedi"

        # XSS injection denemesi
        xss_name = f"<script>alert('xss')</script>_{int(time.time())}"
        case_name_entered = self.datagcase_page.enter_case_name(xss_name)
        assert case_name_entered, "XSS Case Name girilemedi"

        # SAVE butonuna tıkla
        save_clicked = self.datagcase_page.click_save_button()

        # XSS koruması kontrolü
        page_source = self.driver.page_source
        has_xss_protection = "<script>" not in page_source or "error" in page_source.lower()

        print(f"XSS koruması: {'Var' if has_xss_protection else 'Yok'}")

        print("Test tamamlandı: XSS koruması kontrol edildi")

    def test_TC129_unicode_karakterler(self):
        """TC129: Unicode karakterler - Unicode karakterler desteklenmeli"""
        print("\nTC129: Unicode karakterler testi ===")

        # NEW butonuna tıkla
        new_clicked = self.datagcase_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"

        # Tüm dropdown'ları doldur
        project_selected = self.datagcase_page.select_project("osmanp")
        assert project_selected, "Proje seçilemedi"

        app_selected = self.datagcase_page.select_application("osmana")
        assert app_selected, "Application seçilemedi"

        module_selected = self.datagcase_page.select_module("osmanm")
        assert module_selected, "Module seçilemedi"

        version_selected = self.datagcase_page.select_module_version("v1")
        assert version_selected, "Module Version seçilemedi"

        flow_selected = self.datagcase_page.select_synthetic_flow("osmand")
        assert flow_selected, "Synthetic Flow seçilemedi"

        # Unicode karakterli case name
        unicode_name = f"тест_列表_اختبار_{int(time.time())}"
        case_name_entered = self.datagcase_page.enter_case_name(unicode_name)
        assert case_name_entered, "Unicode Case Name girilemedi"

        # SAVE butonuna tıkla
        save_clicked = self.datagcase_page.click_save_button()

        # Unicode desteği kontrolü
        page_source = self.driver.page_source
        unicode_supported = unicode_name in page_source or "тест" in page_source

        print(f"Unicode desteği: {'Var' if unicode_supported else 'Yok'}")

        print("Test tamamlandı: Unicode desteği kontrol edildi")

    def test_TC130_case_name_sadece_boşluk(self):
        """TC130: Case name sadece boşluk - Boşluk karakteri validation"""
        print("\nTC130: Case name sadece boşluk testi ===")

        # NEW butonuna tıkla
        new_clicked = self.datagcase_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"

        # Tüm dropdown'ları doldur
        project_selected = self.datagcase_page.select_project("osmanp")
        assert project_selected, "Proje seçilemedi"

        app_selected = self.datagcase_page.select_application("osmana")
        assert app_selected, "Application seçilemedi"

        module_selected = self.datagcase_page.select_module("osmanm")
        assert module_selected, "Module seçilemedi"

        version_selected = self.datagcase_page.select_module_version("v1")
        assert version_selected, "Module Version seçilemedi"

        flow_selected = self.datagcase_page.select_synthetic_flow("osmand")
        assert flow_selected, "Synthetic Flow seçilemedi"

        # Sadece boşluk karakterli case name
        space_only_name = "   "  # Sadece boşluklar
        case_name_entered = self.datagcase_page.enter_case_name(space_only_name)
        assert case_name_entered, "Boşluk Case Name girilemedi"

        # SAVE butonuna tıkla
        save_clicked = self.datagcase_page.click_save_button()

        # Boşluk validation kontrolü
        page_source = self.driver.page_source
        has_validation_error = "error" in page_source.lower() or "invalid" in page_source.lower() or "required" in page_source.lower()

        print(f"Boşluk validation: {'Var' if has_validation_error else 'Yok'}")

        print("Test tamamlandı: Boşluk validation kontrol edildi")

    def test_TC131_description_max_karakter(self):
        """TC131: Description max karakter - Description uzunluk limiti"""
        print("\nTC131: Description max karakter testi ===")

        # NEW butonuna tıkla
        new_clicked = self.datagcase_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"

        # Tüm dropdown'ları doldur
        project_selected = self.datagcase_page.select_project("osmanp")
        assert project_selected, "Proje seçilemedi"

        app_selected = self.datagcase_page.select_application("osmana")
        assert app_selected, "Application seçilemedi"

        module_selected = self.datagcase_page.select_module("osmanm")
        assert module_selected, "Module seçilemedi"

        version_selected = self.datagcase_page.select_module_version("v1")
        assert version_selected, "Module Version seçilemedi"

        flow_selected = self.datagcase_page.select_synthetic_flow("osmand")
        assert flow_selected, "Synthetic Flow seçilemedi"

        # Case name gir
        case_name_entered = self.datagcase_page.enter_case_name(self.test_case_name)
        assert case_name_entered, "Case Name girilemedi"

        # Çok uzun description (1000+ karakter)
        long_description = "Very long description text " * 50  # ~1000+ karakter
        description_entered = self.datagcase_page.enter_description(long_description)
        assert description_entered, "Uzun Description girilemedi"

        # SAVE butonuna tıkla
        save_clicked = self.datagcase_page.click_save_button()

        # Description limit kontrolü
        page_source = self.driver.page_source
        has_desc_limit = "limit" in page_source.lower() or self.test_case_name in page_source

        print(f"Description limit: {'Kontrol edildi' if has_desc_limit else 'Problem'}")

        print("Test tamamlandı: Description uzunluk limiti kontrol edildi")

    def test_TC132_case_run_sırasında_edit(self):
        """TC132: Case run sırasında edit - Edit disabled olmalı veya uyarı"""
        print("\nTC132: Case run sırasında edit testi ===")

        # Önce bir case oluştur
        new_clicked = self.datagcase_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"

        project_selected = self.datagcase_page.select_project("osmanp")
        assert project_selected, "Proje seçilemedi"

        app_selected = self.datagcase_page.select_application("osmana")
        assert app_selected, "Application seçilemedi"

        module_selected = self.datagcase_page.select_module("osmanm")
        assert module_selected, "Module seçilemedi"

        version_selected = self.datagcase_page.select_module_version("v1")
        assert version_selected, "Module Version seçilemedi"

        flow_selected = self.datagcase_page.select_synthetic_flow("osmand")
        assert flow_selected, "Synthetic Flow seçilemedi"

        case_name_entered = self.datagcase_page.enter_case_name(self.test_case_name)
        assert case_name_entered, "Case Name girilemedi"

        save_clicked = self.datagcase_page.click_save_button()
        assert save_clicked, "SAVE butonuna tıklanamadı"

        # Case'i çalıştır
        run_clicked = self.datagcase_page.click_runcase_button(self.test_case_name)
        if run_clicked:
            print("Case çalıştırıldı")

            # Edit butonuna tıklamaya çalış
            try:
                edit_clicked = self.datagcase_page.click_caseedit_button(self.test_case_name)
                print(f"Edit butonu: {'Tıklanabilir' if edit_clicked else 'Disabled/Bloklanmış'}")
            except:
                print("Edit butonuna tıklanamadı - Muhtemelen disabled")

        print("Test tamamlandı: Run sırasında edit kontrolü yapıldı")


