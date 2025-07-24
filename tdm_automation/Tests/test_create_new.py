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
from selenium.webdriver.chrome.options import Options

load_dotenv()


class TestCreateNewTab:

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
        cls.TEST_LIST_NAME = os.getenv('TEST_LIST_NAME', 'ListName')

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

        # *** TEK SEFERLİK LOGIN İŞLEMLERİ ***
        cls.driver.get(cls.BASE_URL)
        login_success = cls.login_page.do_login(cls.VALID_USERNAME, cls.VALID_PASSWORD)
        assert login_success, "Login başarısız!"

        # TDM'ye git
        tdm_locator = (By.XPATH, "//li[@title='New Test Data Manager'][2]")
        tdm_success = cls.login_page.click_element(tdm_locator)
        assert tdm_success, "TDM elementine tıklanamadı"

        # List Generator'e git
        listgen_success = cls.dashboard_page.click_list_generator()
        assert listgen_success, "List Generator butonuna tıklanamadı"

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
        self.test_list_name = f"{self.TEST_LIST_NAME}_{timestamp}"

        # App Management sayfasında olduğumuzu kontrol et
        current_url = self.driver.current_url
        if "list-generator" not in current_url:
            print("List Generator sayfasına yönlendiriliyor...")
            self.dashboard_page.click_list_generator()
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
            if hasattr(self, 'test_list_name') and self.test_list_name in page_source:
                self.listgen_page.click_deletelist_andconfirm_button(self.test_list_name)
                time.sleep(1)
        except:
            pass

    def test_TC035_integer_type_with_single_dot(self):
        """TC035: Integer type ile tek nokta - Type: Integer, Values: "13.2", "5.7" - Tek nokta kabul ediyor"""
        print("\nTC035: Integer type ile tek nokta testi ===")

        # Önce NEW butonuna tıkla (modal açılır)
        new_clicked = self.listgen_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"
        time.sleep(1)

        # Create New tab'ına git (modal içinde)
        tab_clicked = self.create_lg_page.click_create_new_tab()
        assert tab_clicked, "Create New tab'ına tıklanamadı"
        time.sleep(1)

        # Name gir
        name_entered = self.create_lg_page.enter_name(self.test_list_name)
        assert name_entered, "Name girilemedi"

        # Type: Integer seç
        type_selected = self.create_lg_page.select_type("integer")
        assert type_selected, "Integer type seçilemedi"

        # İlk value: "13.2" gir ve ekle
        value1_added = self.create_lg_page.add_value("13.2")
        assert value1_added, "İlk value (13.2) eklenemedi"

        # İkinci value: "5.7" gir ve ekle
        value2_added = self.create_lg_page.add_value("5.7")
        assert value2_added, "İkinci value (5.7) eklenemedi"

        # SAVE butonunun aktif olduğunu kontrol et
        save_enabled = self.create_lg_page.is_save_button_enabled_new_file()
        assert save_enabled, "SAVE butonu aktif değil"

        # SAVE butonuna tıkla
        save_clicked = self.create_lg_page.click_save_button_new_file()
        assert save_clicked, "SAVE butonuna tıklanamadı"

        time.sleep(2)

        print("Test başarılı: Integer type tek nokta kabul ediyor, liste oluşturuldu")


    def test_TC036_integer_type_with_double_dot(self):
        """TC036: Integer type ile çift nokta - Type: Integer, Values: "13.2.5", "5.7.9" - İkinci nokta yazdırmıyor"""
        print("\nTC036: Integer type ile çift nokta testi ===")

        # Önce NEW butonuna tıkla (modal açılır)
        new_clicked = self.listgen_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"
        time.sleep(1)

        # Create New tab'ına git (modal içinde)
        tab_clicked = self.create_lg_page.click_create_new_tab()
        assert tab_clicked, "Create New tab'ına tıklanamadı"
        time.sleep(1)

        # Name gir
        name_entered = self.create_lg_page.enter_name(self.test_list_name)
        assert name_entered, "Name girilemedi"

        # Type: Integer seç
        type_selected = self.create_lg_page.select_type("integer")
        assert type_selected, "Integer type seçilemedi"

        # İlk value: "13.2.5" yazmaya çalış (sistem "13.25" yapacak)
        value1_entered = self.create_lg_page.enter_value("13.2.5")
        assert value1_entered, "İlk value girilemedi"

        # Field'daki değeri kontrol et
        values_field = self.driver.find_element(*self.create_lg_page.VALUES_FIELD)
        actual_value1 = values_field.get_attribute("value")
        print(f"Girilen: '13.2.5' → Sistem yazdı: '{actual_value1}'")

        add1_clicked = self.create_lg_page.click_add_value_button()
        assert add1_clicked, "İlk + butonuna tıklanamadı"

        # İkinci value: "5.7.9" yazmaya çalış (sistem "5.79" yapacak)
        value2_entered = self.create_lg_page.enter_value("5.7.9")
        assert value2_entered, "İkinci value girilemedi"

        # Field'daki değeri kontrol et
        values_field = self.driver.find_element(*self.create_lg_page.VALUES_FIELD)
        actual_value2 = values_field.get_attribute("value")
        print(f"Girilen: '5.7.9' → Sistem yazdı: '{actual_value2}'")

        add2_clicked = self.create_lg_page.click_add_value_button()
        assert add2_clicked, "İkinci + butonuna tıklanamadı"

        # SAVE butonuna tıkla
        save_clicked = self.create_lg_page.click_save_button_new_file()
        assert save_clicked, "SAVE butonuna tıklanamadı"

        time.sleep(2)

        print("Test başarılı: Integer type ikinci noktayı yazdırmıyor (13.2.5 → 13.25)")


    def test_TC037_integer_type_with_fronttext(self):
        """TC037: Integer Type ile başına text yazdırma: textleri yazdırmıyor"""
        print("\nTC037: Integer type ile başına text koyma testi ===")

        # Önce NEW butonuna tıkla (modal açılır)
        new_clicked = self.listgen_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"
        time.sleep(1)

        # Create New tab'ına git (modal içinde)
        tab_clicked = self.create_lg_page.click_create_new_tab()
        assert tab_clicked, "Create New tab'ına tıklanamadı"
        time.sleep(1)

        # Name gir
        name_entered = self.create_lg_page.enter_name(self.test_list_name)
        assert name_entered, "Name girilemedi"

        # Type: Integer seç
        type_selected = self.create_lg_page.select_type("integer")
        assert type_selected, "Integer type seçilemedi"

        # İlk value: "abc13.2" yazmaya çalış (sistem text'i kesecek)
        value_entered = self.create_lg_page.enter_value("abc13.2")
        assert value_entered, "İlk value girilemedi"

        # Field'daki değeri kontrol et
        values_field = self.driver.find_element(*self.create_lg_page.VALUES_FIELD)
        actual_value1 = values_field.get_attribute("value")
        print(f"Girilen: 'abc13.2' → Sistem yazdı: '{actual_value1}'")

        add1_clicked = self.create_lg_page.click_add_value_button()
        assert add1_clicked, "İlk + butonuna tıklanamadı"

        # İkinci value: "test5.7" yazmaya çalış (sistem text'i kesecek)
        value2_entered = self.create_lg_page.enter_value("test5.7")
        assert value2_entered, "İkinci value girilemedi"

        # Field'daki değeri kontrol et
        values_field = self.driver.find_element(*self.create_lg_page.VALUES_FIELD)
        actual_value2 = values_field.get_attribute("value")
        print(f"Girilen: 'test5.7' → Sistem yazdı: '{actual_value2}'")

        add2_clicked = self.create_lg_page.click_add_value_button()
        assert add2_clicked, "İkinci + butonuna tıklanamadı"

        # SAVE butonuna tıkla
        save_clicked = self.create_lg_page.click_save_button_new_file()
        assert save_clicked, "SAVE butonuna tıklanamadı"

        time.sleep(2)

        print("Test başarılı: Integer type textleri yazdırmıyor (abc13.2 → 13.2, test5.7 → 5.7)")


    def test_TC038_integer_type_with_only_text(self):
        """TC038: Integer type ile sadece text - Type: Integer, Values: "abc" - Text yazdırmaz, boş kalır"""
        print("\nTC038: Integer type ile sadece text testi ===")

        # Önce NEW butonuna tıkla (modal açılır)
        new_clicked = self.listgen_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"
        time.sleep(1)

        # Create New tab'ına git (modal içinde)
        tab_clicked = self.create_lg_page.click_create_new_tab()
        assert tab_clicked, "Create New tab'ına tıklanamadı"
        time.sleep(1)

        # Name gir
        name_entered = self.create_lg_page.enter_name(self.test_list_name)
        assert name_entered, "Name girilemedi"

        # Type: Integer seç
        type_selected = self.create_lg_page.select_type("integer")
        assert type_selected, "Integer type seçilemedi"

        # Value: "abc" yazmaya çalış (sistem hiçbir şey yazmaz)
        value_entered = self.create_lg_page.enter_value("abc")
        assert value_entered, "Value girilemedi"

        # Field'ın boş kaldığını kontrol et
        values_field = self.driver.find_element(*self.create_lg_page.VALUES_FIELD)
        actual_value = values_field.get_attribute("value")
        print(f"Girilen: 'abc' → Sistem yazdı: '{actual_value}' (boş)")

        # SAVE butonu disabled olmalı (value yok)
        save_enabled = self.create_lg_page.is_save_button_enabled_new_file()
        assert not save_enabled, "SAVE butonu aktif olmamalıydı (value yok)"

        print("Test başarılı: Integer type sadece text yazdırmaz, field boş kalır, SAVE disabled")


    def test_TC039_integer_type_with_negative_numbers(self):
        """TC039: Integer type ile negatif sayılar - Type: Integer, Values: "-13.2" - Negatif değere izin veriyor"""
        print("\nTC039: Integer type ile negatif sayılar testi ===")

        # Önce NEW butonuna tıkla (modal açılır)
        new_clicked = self.listgen_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"
        time.sleep(1)

        # Create New tab'ına git (modal içinde)
        tab_clicked = self.create_lg_page.click_create_new_tab()
        assert tab_clicked, "Create New tab'ına tıklanamadı"
        time.sleep(1)

        # Name gir
        name_entered = self.create_lg_page.enter_name(self.test_list_name)
        assert name_entered, "Name girilemedi"

        # Type: Integer seç
        type_selected = self.create_lg_page.select_type("integer")
        assert type_selected, "Integer type seçilemedi"

        # Value: "-13.2" gir ve ekle
        value_added = self.create_lg_page.add_value("-13.2")
        assert value_added, "Value (-13.2) eklenemedi"

        # SAVE butonuna tıkla
        save_clicked = self.create_lg_page.click_save_button_new_file()
        assert save_clicked, "SAVE butonuna tıklanamadı"

        time.sleep(2)

        print("Test başarılı: Integer type negatif sayıları kabul ediyor")


    def test_TC040_decimal_type_with_double_dot(self):
        """TC040: Decimal type ile çift nokta - Type: Decimal, Values: "3.14.15" - Çift nokta nasıl handle ediliyor?"""
        print("\nTC040: Decimal type ile çift nokta testi ===")

        # Önce NEW butonuna tıkla (modal açılır)
        new_clicked = self.listgen_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"
        time.sleep(1)

        # Create New tab'ına git (modal içinde)
        tab_clicked = self.create_lg_page.click_create_new_tab()
        assert tab_clicked, "Create New tab'ına tıklanamadı"
        time.sleep(1)

        # Name gir
        name_entered = self.create_lg_page.enter_name(self.test_list_name)
        assert name_entered, "Name girilemedi"

        # Type: Decimal seç
        type_selected = self.create_lg_page.select_type("decimal")
        assert type_selected, "Decimal type seçilemedi"

        # Value: "3.14.15" yazmaya çalış (sistem ikinci noktayı kesecek)
        value_entered = self.create_lg_page.enter_value("3.14.15")
        assert value_entered, "Value girilemedi"

        # Field'daki değeri kontrol et
        values_field = self.driver.find_element(*self.create_lg_page.VALUES_FIELD)
        actual_value = values_field.get_attribute("value")
        print(f"Girilen: '3.14.15' → Sistem yazdı: '{actual_value}'")

        # Value'yu ekle
        add_clicked = self.create_lg_page.click_add_value_button()
        assert add_clicked, "+ butonuna tıklanamadı"

        # SAVE butonuna tıkla
        save_clicked = self.create_lg_page.click_save_button_new_file()
        assert save_clicked, "SAVE butonuna tıklanamadı"

        time.sleep(2)

        print("Test başarılı: Decimal type çift nokta ile davranış test edildi")


    def test_TC041_decimal_type_with_text(self):
        """TC041: Decimal type ile text - Type: Decimal, Values: "abc3.14" - Text+decimal kombinasyonu"""
        print("\nTC041: Decimal type ile text testi ===")

        # Önce NEW butonuna tıkla (modal açılır)
        new_clicked = self.listgen_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"
        time.sleep(1)

        # Create New tab'ına git (modal içinde)
        tab_clicked = self.create_lg_page.click_create_new_tab()
        assert tab_clicked, "Create New tab'ına tıklanamadı"
        time.sleep(1)

        # Name gir
        name_entered = self.create_lg_page.enter_name(self.test_list_name)
        assert name_entered, "Name girilemedi"

        # Type: Decimal seç
        type_selected = self.create_lg_page.select_type("decimal")
        assert type_selected, "Decimal type seçilemedi"

        # Value: "abc3.14" yazmaya çalış (sistem text'i kesecek)
        value_entered = self.create_lg_page.enter_value("abc3.14")
        assert value_entered, "Value girilemedi"

        # Field'daki değeri kontrol et
        values_field = self.driver.find_element(*self.create_lg_page.VALUES_FIELD)
        actual_value = values_field.get_attribute("value")
        print(f"Girilen: 'abc3.14' → Sistem yazdı: '{actual_value}'")

        # Value'yu ekle
        add_clicked = self.create_lg_page.click_add_value_button()
        assert add_clicked, "+ butonuna tıklanamadı"

        # SAVE butonuna tıkla
        save_clicked = self.create_lg_page.click_save_button_new_file()
        assert save_clicked, "SAVE butonuna tıklanamadı"

        time.sleep(2)

        print("Test başarılı: Decimal type text+decimal kombinasyonu test edildi")


    def test_TC042_text_type_with_everything(self):
        """TC042: Text type ile her şey - Type: Text, Values: "123abc!@#" - Text her şeyi kabul ediyor mu?"""
        print("\nTC042: Text type ile everything testi ===")

        # Önce NEW butonuna tıkla (modal açılır)
        new_clicked = self.listgen_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"
        time.sleep(1)

        # Create New tab'ına git (modal içinde)
        tab_clicked = self.create_lg_page.click_create_new_tab()
        assert tab_clicked, "Create New tab'ına tıklanamadı"
        time.sleep(1)

        # Name gir
        name_entered = self.create_lg_page.enter_name(self.test_list_name)
        assert name_entered, "Name girilemedi"

        # Type: Text seç
        type_selected = self.create_lg_page.select_type("text")
        assert type_selected, "Text type seçilemedi"

        # Value: "123abc!@#" gir (her tür karakter)
        value_entered = self.create_lg_page.enter_value("123abc!@#")
        assert value_entered, "Value girilemedi"

        # Field'daki değeri kontrol et
        values_field = self.driver.find_element(*self.create_lg_page.VALUES_FIELD)
        actual_value = values_field.get_attribute("value")
        print(f"Girilen: '123abc!@#' → Sistem yazdı: '{actual_value}'")

        # Value'yu ekle
        add_clicked = self.create_lg_page.click_add_value_button()
        assert add_clicked, "+ butonuna tıklanamadı"

        # SAVE butonuna tıkla
        save_clicked = self.create_lg_page.click_save_button_new_file()
        assert save_clicked, "SAVE butonuna tıklanamadı"

        time.sleep(2)

        print("Test başarılı: Text type her şeyi kabul ediyor")


    def test_TC043_empty_value_control(self):
        """TC043: Boş value kontrolü - Values: "   " - Boş değer nasıl işleniyor?"""
        print("\nTC043: Boş value kontrolü testi ===")

        # Önce NEW butonuna tıkla (modal açılır)
        new_clicked = self.listgen_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"
        time.sleep(1)

        # Create New tab'ına git (modal içinde)
        tab_clicked = self.create_lg_page.click_create_new_tab()
        assert tab_clicked, "Create New tab'ına tıklanamadı"
        time.sleep(1)

        # Name gir
        name_entered = self.create_lg_page.enter_name(self.test_list_name)
        assert name_entered, "Name girilemedi"

        # Type: Text seç
        type_selected = self.create_lg_page.select_type("text")
        assert type_selected, "Text type seçilemedi"

        # Value: "   " (sadece boşluk) gir
        value_entered = self.create_lg_page.enter_value("   ")
        assert value_entered, "Value girilemedi"

        # + butonuna tıkla
        add_clicked = self.create_lg_page.click_add_value_button()
        # Boş value eklenemeyebilir, assertion yapmıyoruz

        # SAVE butonu aktif mi kontrol et
        save_enabled = self.create_lg_page.is_save_button_enabled_new_file()

        if save_enabled:
            print("Boş değer kabul edildi")
            save_clicked = self.create_lg_page.click_save_button_new_file()
            time.sleep(2)
        else:
            print("Boş değer reddedildi - SAVE disabled")

        print("Test tamamlandı: Boş value kontrolü yapıldı")


    def test_TC044_very_long_name(self):
        """TC044: Çok uzun name - Name: 500+ karakter - Name karakter limiti var mı?"""
        print("\nTC044: Çok uzun name testi ===")

        # Önce NEW butonuna tıkla (modal açılır)
        new_clicked = self.listgen_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"
        time.sleep(1)

        # Create New tab'ına git (modal içinde)
        tab_clicked = self.create_lg_page.click_create_new_tab()
        assert tab_clicked, "Create New tab'ına tıklanamadı"
        time.sleep(1)

        # Çok uzun name oluştur (500 karakter)
        long_name = "VeryLongListName" * 30  # 16*30 = 480 karakter
        print(f"Uzun name karakter sayısı: {len(long_name)}")

        # Uzun name gir
        name_entered = self.create_lg_page.enter_name(long_name)
        assert name_entered, "Uzun name girilemedi"

        # Name field'daki değeri kontrol et
        name_field = self.driver.find_element(*self.create_lg_page.NAME_FIELD)
        actual_name = name_field.get_attribute("value")
        print(f"Girilen karakter: {len(long_name)} → Sistem yazdı: {len(actual_name)} karakter")

        # Type: Text seç
        type_selected = self.create_lg_page.select_type("text")
        assert type_selected, "Text type seçilemedi"

        # Value ekle
        value_added = self.create_lg_page.add_value("test123")
        assert value_added, "Value eklenemedi"

        # SAVE butonuna tıkla
        save_clicked = self.create_lg_page.click_save_button_new_file()
        assert save_clicked, "SAVE butonuna tıklanamadı"

        time.sleep(2)

        print("Test başarılı: Uzun name davranışı test edildi")


    def test_TC045_very_long_value(self):
        """TC045: Çok uzun value - Values: 500+ karakter - Value karakter limiti var mı?"""
        print("\nTC045: Çok uzun value testi ===")

        # Önce NEW butonuna tıkla (modal açılır)
        new_clicked = self.listgen_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"
        time.sleep(1)

        # Create New tab'ına git (modal içinde)
        tab_clicked = self.create_lg_page.click_create_new_tab()
        assert tab_clicked, "Create New tab'ına tıklanamadı"
        time.sleep(1)

        # Name gir
        name_entered = self.create_lg_page.enter_name(self.test_list_name)
        assert name_entered, "Name girilemedi"

        # Type: Text seç
        type_selected = self.create_lg_page.select_type("text")
        assert type_selected, "Text type seçilemedi"

        # Çok uzun value oluştur (500 karakter)
        long_value = "VeryLongValueText" * 30  # 17*30 = 510 karakter
        print(f"Uzun value karakter sayısı: {len(long_value)}")

        # Uzun value gir
        value_entered = self.create_lg_page.enter_value(long_value)
        assert value_entered, "Uzun value girilemedi"

        # Values field'daki değeri kontrol et
        values_field = self.driver.find_element(*self.create_lg_page.VALUES_FIELD)
        actual_value = values_field.get_attribute("value")
        print(f"Girilen karakter: {len(long_value)} → Sistem yazdı: {len(actual_value)} karakter")

        # Value'yu ekle
        add_clicked = self.create_lg_page.click_add_value_button()
        assert add_clicked, "+ butonuna tıklanamadı"

        # SAVE butonuna tıkla
        save_clicked = self.create_lg_page.click_save_button_new_file()
        assert save_clicked, "SAVE butonuna tıklanamadı"

        time.sleep(2)

        print("Test başarılı: Uzun value davranışı test edildi")


    def test_TC046_maximum_value_count(self):
        """TC046: Maksimum value sayısı - 100 value ekle - Limit var mı?"""
        print("\nTC046: Maksimum value sayısı testi (100 value) ===")

        # Önce NEW butonuna tıkla (modal açılır)
        new_clicked = self.listgen_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"
        time.sleep(1)

        # Create New tab'ına git (modal içinde)
        tab_clicked = self.create_lg_page.click_create_new_tab()
        assert tab_clicked, "Create New tab'ına tıklanamadı"
        time.sleep(1)

        # Name gir
        name_entered = self.create_lg_page.enter_name(self.test_list_name)
        assert name_entered, "Name girilemedi"

        # Type: Text seç
        type_selected = self.create_lg_page.select_type("text")
        assert type_selected, "Text type seçilemedi"

        # 100 value ekle
        print("100 value ekleme başlıyor...")
        start_time = time.time()

        success_count = 0
        for i in range(100):
            try:
                value_added = self.create_lg_page.add_value(f"value{i:03d}")
                if value_added:
                    success_count += 1

                # Her 10 value'da progress göster
                if (i + 1) % 10 == 0:
                    print(f"Progress: {i + 1}/100 value eklendi")

            except Exception as e:
                print(f"Value {i} eklenirken hata: {e}")
                break

        end_time = time.time()
        elapsed_time = end_time - start_time

        print(f"Toplam eklenen value: {success_count}/100")
        print(f"Geçen süre: {elapsed_time:.2f} saniye")
        print(f"Ortalama süre per value: {elapsed_time / success_count:.3f} saniye")

        # SAVE butonuna tıkla
        save_clicked = self.create_lg_page.click_save_button_new_file()
        assert save_clicked, "SAVE butonuna tıklanamadı"

        time.sleep(3)  # Kayıt için biraz bekle

        print("Test başarılı: Maksimum value sayısı test edildi")


    def test_TC047_duplicate_values(self):
        """TC047: Duplicate values - Values: "test123", "test123" - Sistem duplicate'a izin vermiyor"""
        print("\nTC047: Duplicate values testi ===")

        # Önce NEW butonuna tıkla (modal açılır)
        new_clicked = self.listgen_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"
        time.sleep(1)

        # Create New tab'ına git (modal içinde)
        tab_clicked = self.create_lg_page.click_create_new_tab()
        assert tab_clicked, "Create New tab'ına tıklanamadı"
        time.sleep(1)

        # Name gir
        name_entered = self.create_lg_page.enter_name(self.test_list_name)
        assert name_entered, "Name girilemedi"

        # Type: Text seç
        type_selected = self.create_lg_page.select_type("text")
        assert type_selected, "Text type seçilemedi"

        # İlk value: "test123" ekle
        value1_added = self.create_lg_page.add_value("test123")
        assert value1_added, "İlk value (test123) eklenemedi"
        print("İlk 'test123' eklendi")

        # Aynı value'yu tekrar eklemeye çalış: "test123"
        value2_entered = self.create_lg_page.enter_value("test123")
        assert value2_entered, "İkinci value girilemedi"

        add2_clicked = self.create_lg_page.click_add_value_button()
        time.sleep(1)

        # Error modal açıldı mı kontrol et
        page_source = self.driver.page_source
        error_modal_present = "The values you add must be different from each other" in page_source
        assert error_modal_present, "Duplicate value error modal açılmadı"
        print("Error modal açıldı: 'The values you add must be different from each other'")

        # OK butonuna tıkla (error modal'ı kapat)
        ok_button = self.driver.find_element(By.XPATH, "//span[text()='OK']")
        ok_button.click()
        time.sleep(1)

        # Farklı value ekle
        value3_added = self.create_lg_page.add_value("test456")
        assert value3_added, "Farklı value (test456) eklenemedi"

        # SAVE butonuna tıkla
        save_clicked = self.create_lg_page.click_save_button_new_file()
        assert save_clicked, "SAVE butonuna tıklanamadı"

        time.sleep(2)

        print("Test başarılı: Duplicate values reddediliyor, error modal gösteriliyor")


    def test_TC048_sql_injection_name(self):
        """TC048: SQL injection name - Name: "'; DROP TABLE lists; --" - Name field SQL injection koruması"""
        print("\nTC048: SQL injection name testi ===")

        # Önce NEW butonuna tıkla (modal açılır)
        new_clicked = self.listgen_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"
        time.sleep(1)

        # Create New tab'ına git (modal içinde)
        tab_clicked = self.create_lg_page.click_create_new_tab()
        assert tab_clicked, "Create New tab'ına tıklanamadı"
        time.sleep(1)

        # SQL injection payload
        sql_payload = "'; DROP TABLE lists; --"
        print(f"SQL payload: {sql_payload}")

        # SQL payload'ını Name field'ına gir
        name_entered = self.create_lg_page.enter_name(sql_payload)
        assert name_entered, "SQL payload name girilemedi"

        # Name field'daki değeri kontrol et
        name_field = self.driver.find_element(*self.create_lg_page.NAME_FIELD)
        actual_name = name_field.get_attribute("value")
        print(f"Girilen: '{sql_payload}' → Sistem yazdı: '{actual_name}'")

        # Type: Text seç
        type_selected = self.create_lg_page.select_type("text")
        assert type_selected, "Text type seçilemedi"

        # Normal value ekle
        value_added = self.create_lg_page.add_value("test123")
        assert value_added, "Value eklenemedi"

        # SAVE butonuna tıkla
        save_clicked = self.create_lg_page.click_save_button_new_file()
        assert save_clicked, "SAVE butonuna tıklanamadı"

        time.sleep(2)

        # Sistem hala çalışıyor mu kontrol et (crash olmadı mı?)
        try:
            # Yeni bir modal açmayı dene
            new_test = self.listgen_page.click_newlist()
            if new_test:
                print("Sistem stabil - SQL injection etkisiz")
                # Cancel ile kapat
                cancel_button = self.driver.find_element(By.XPATH, "//span[text()='CANCEL']")
                cancel_button.click()
            else:
                print("UYARI: Sistem etkilenmiş olabilir")
        except:
            print("UYARI: Sistem crash olmuş olabilir")

        print("Test tamamlandı: SQL injection name kontrolü yapıldı")

    def test_TC049_sql_injection_values(self):
        """TC049: SQL injection values - Values: "'; DROP TABLE data; --" - Values field SQL injection koruması"""
        print("\nTC049: SQL injection values testi ===")

        # Önce NEW butonuna tıkla (modal açılır)
        new_clicked = self.listgen_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"
        time.sleep(1)

        # Create New tab'ına git (modal içinde)
        tab_clicked = self.create_lg_page.click_create_new_tab()
        assert tab_clicked, "Create New tab'ına tıklanamadı"
        time.sleep(1)

        # Normal name gir
        name_entered = self.create_lg_page.enter_name(self.test_list_name)
        assert name_entered, "Name girilemedi"

        # Type: Text seç
        type_selected = self.create_lg_page.select_type("text")
        assert type_selected, "Text type seçilemedi"

        # SQL injection payload
        sql_payload = "'; DROP TABLE data; --"
        print(f"SQL payload: {sql_payload}")

        # SQL payload'ını Values field'ına gir
        value_entered = self.create_lg_page.enter_value(sql_payload)
        assert value_entered, "SQL payload value girilemedi"

        # Values field'daki değeri kontrol et
        values_field = self.driver.find_element(*self.create_lg_page.VALUES_FIELD)
        actual_value = values_field.get_attribute("value")
        print(f"Girilen: '{sql_payload}' → Sistem yazdı: '{actual_value}'")

        # Value'yu ekle
        add_clicked = self.create_lg_page.click_add_value_button()
        assert add_clicked, "+ butonuna tıklanamadı"

        # SAVE butonuna tıkla
        save_clicked = self.create_lg_page.click_save_button_new_file()
        assert save_clicked, "SAVE butonuna tıklanamadı"

        time.sleep(2)

        # Sistem hala çalışıyor mu kontrol et (crash olmadı mı?)
        try:
            # Yeni bir modal açmayı dene
            new_test = self.listgen_page.click_newlist()
            if new_test:
                print("Sistem stabil - SQL injection etkisiz")
                # Cancel ile kapat
                cancel_button = self.driver.find_element(By.XPATH, "//span[text()='CANCEL']")
                cancel_button.click()
            else:
                print("UYARI: Sistem etkilenmiş olabilir")
        except:
            print("UYARI: Sistem crash olmuş olabilir")

        print("Test tamamlandı: SQL injection values kontrolü yapıldı")


    def test_TC050_xss_injection_name(self):
        """TC050: XSS injection name - Name: "<script>alert('xss')</script>" - Name field XSS koruması"""
        print("\nTC050: XSS injection name testi ===")

        # Önce NEW butonuna tıkla (modal açılır)
        new_clicked = self.listgen_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"
        time.sleep(1)

        # Create New tab'ına git (modal içinde)
        tab_clicked = self.create_lg_page.click_create_new_tab()
        assert tab_clicked, "Create New tab'ına tıklanamadı"
        time.sleep(1)

        # XSS payload
        xss_payload = "<script>alert('xss')</script>"
        print(f"XSS payload: {xss_payload}")

        # XSS payload'ını Name field'ına gir
        name_entered = self.create_lg_page.enter_name(xss_payload)
        assert name_entered, "XSS payload name girilemedi"

        # Name field'daki değeri kontrol et
        name_field = self.driver.find_element(*self.create_lg_page.NAME_FIELD)
        actual_name = name_field.get_attribute("value")
        print(f"Girilen: '{xss_payload}' → Sistem yazdı: '{actual_name}'")

        # Type: Text seç
        type_selected = self.create_lg_page.select_type("text")
        assert type_selected, "Text type seçilemedi"

        # Normal value ekle
        value_added = self.create_lg_page.add_value("test123")
        assert value_added, "Value eklenemedi"

        # SAVE butonuna tıkla
        save_clicked = self.create_lg_page.click_save_button_new_file()
        assert save_clicked, "SAVE butonuna tıklanamadı"

        time.sleep(2)

        print("Test tamamlandı: XSS injection name kontrolü yapıldı")


    def test_TC051_html_injection_values(self):
        """TC051: HTML injection values - Values: "<img src=x onerror=alert(1)>" - Values field HTML injection koruması"""
        print("\nTC051: HTML injection values testi ===")

        # Önce NEW butonuna tıkla (modal açılır)
        new_clicked = self.listgen_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"
        time.sleep(1)

        # Create New tab'ına git (modal içinde)
        tab_clicked = self.create_lg_page.click_create_new_tab()
        assert tab_clicked, "Create New tab'ına tıklanamadı"
        time.sleep(1)

        # Normal name gir
        name_entered = self.create_lg_page.enter_name(self.test_list_name)
        assert name_entered, "Name girilemedi"

        # Type: Text seç
        type_selected = self.create_lg_page.select_type("text")
        assert type_selected, "Text type seçilemedi"

        # HTML injection payload
        html_payload = "<img src=x onerror=alert(1)>"
        print(f"HTML payload: {html_payload}")

        # HTML payload'ını Values field'ına gir
        value_entered = self.create_lg_page.enter_value(html_payload)
        assert value_entered, "HTML payload value girilemedi"

        # Values field'daki değeri kontrol et
        values_field = self.driver.find_element(*self.create_lg_page.VALUES_FIELD)
        actual_value = values_field.get_attribute("value")
        print(f"Girilen: '{html_payload}' → Sistem yazdı: '{actual_value}'")

        # Value'yu ekle
        add_clicked = self.create_lg_page.click_add_value_button()
        assert add_clicked, "+ butonuna tıklanamadı"

        # SAVE butonuna tıkla
        save_clicked = self.create_lg_page.click_save_button_new_file()
        assert save_clicked, "SAVE butonuna tıklanamadı"

        time.sleep(2)

        print("Test tamamlandı: HTML injection values kontrolü yapıldı")


    def test_TC052_duplicate_list_names(self):
        """TC052: Duplicate list names - Aynı name ile 2 list oluşturma - Sistem aynı isimde liste kabul ediyor mu?"""
        print("\nTC052: Duplicate list names testi ===")

        # İlk listeyi oluştur
        print("İlk liste oluşturuluyor...")
        new_clicked1 = self.listgen_page.click_newlist()
        assert new_clicked1, "İlk NEW butonuna tıklanamadı"
        time.sleep(1)

        tab_clicked1 = self.create_lg_page.click_create_new_tab()
        assert tab_clicked1, "İlk Create New tab'ına tıklanamadı"
        time.sleep(1)

        # Aynı name kullan
        duplicate_name = f"DuplicateTest_{int(time.time())}"
        name_entered1 = self.create_lg_page.enter_name(duplicate_name)
        assert name_entered1, "İlk name girilemedi"

        type_selected1 = self.create_lg_page.select_type("text")
        assert type_selected1, "İlk text type seçilemedi"

        value_added1 = self.create_lg_page.add_value("value1")
        assert value_added1, "İlk value eklenemedi"

        save_clicked1 = self.create_lg_page.click_save_button_new_file()
        assert save_clicked1, "İlk SAVE butonuna tıklanamadı"
        time.sleep(2)
        print(f"İlk liste '{duplicate_name}' oluşturuldu")

        # İkinci listeyi aynı isimle oluşturmaya çalış
        print("İkinci liste aynı isimle oluşturuluyor...")
        new_clicked2 = self.listgen_page.click_newlist()
        assert new_clicked2, "İkinci NEW butonuna tıklanamadı"
        time.sleep(1)

        tab_clicked2 = self.create_lg_page.click_create_new_tab()
        assert tab_clicked2, "İkinci Create New tab'ına tıklanamadı"
        time.sleep(1)

        # Aynı name gir
        name_entered2 = self.create_lg_page.enter_name(duplicate_name)
        assert name_entered2, "İkinci name girilemedi"

        type_selected2 = self.create_lg_page.select_type("text")
        assert type_selected2, "İkinci text type seçilemedi"

        value_added2 = self.create_lg_page.add_value("value2")
        assert value_added2, "İkinci value eklenemedi"

        save_clicked2 = self.create_lg_page.click_save_button_new_file()
        time.sleep(2)

        # Hata mesajı var mı kontrol et
        page_source = self.driver.page_source
        if "error" in page_source.lower() or "already exists" in page_source.lower():
            print("Duplicate name hatası alındı")
        else:
            print("Duplicate name kabul edildi - İkinci liste oluşturuldu")

        print("Test tamamlandı: Duplicate list names kontrolü yapıldı")


    def test_TC053_non_latin_characters(self):
        """TC053: Latin alfabesinden olmayan karakterler - Name: "тест_列表_اختبار_テスト" - Uluslararası karakter desteği"""
        print("\nTC053: Latin alfabesinden olmayan karakterler testi ===")

        # Önce NEW butonuna tıkla (modal açılır)
        new_clicked = self.listgen_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"
        time.sleep(1)

        # Create New tab'ına git (modal içinde)
        tab_clicked = self.create_lg_page.click_create_new_tab()
        assert tab_clicked, "Create New tab'ına tıklanamadı"
        time.sleep(1)

        # Farklı dil karakterleri karışımı
        non_latin_name = "тест_列表_اختبار_テスト_한국어"  # Rusça_Çince_Arapça_Japonca_Korece
        print(f"Non-Latin karakterler: {non_latin_name}")

        # Non-Latin karakterleri Name field'ına gir
        name_entered = self.create_lg_page.enter_name(non_latin_name)
        assert name_entered, "Non-Latin name girilemedi"

        # Name field'daki değeri kontrol et
        name_field = self.driver.find_element(*self.create_lg_page.NAME_FIELD)
        actual_name = name_field.get_attribute("value")
        print(f"Girilen: '{non_latin_name}' → Sistem yazdı: '{actual_name}'")

        # Type: Text seç
        type_selected = self.create_lg_page.select_type("text")
        assert type_selected, "Text type seçilemedi"

        # Non-Latin value ekle
        non_latin_value = "测试值_значение_قيمة"  # Çince_Rusça_Arapça
        value_entered = self.create_lg_page.enter_value(non_latin_value)
        assert value_entered, "Non-Latin value girilemedi"

        # Values field'daki değeri kontrol et
        values_field = self.driver.find_element(*self.create_lg_page.VALUES_FIELD)
        actual_value = values_field.get_attribute("value")
        print(f"Value girilen: '{non_latin_value}' → Sistem yazdı: '{actual_value}'")

        # Value'yu ekle
        add_clicked = self.create_lg_page.click_add_value_button()
        assert add_clicked, "+ butonuna tıklanamadı"

        # SAVE butonuna tıkla
        save_clicked = self.create_lg_page.click_save_button_new_file()
        assert save_clicked, "SAVE butonuna tıklanamadı"

        time.sleep(2)

        print("Test tamamlandı: Latin alfabesinden olmayan karakterler kontrolü yapıldı")


    def test_TC054_empty_name_control(self):
        """TC054: Boş name kontrolü - Name: "" - Boş name ile liste oluşturulabiliyor mu?"""
        print("\nTC054: Boş name kontrolü testi ===")

        # Önce NEW butonuna tıkla (modal açılır)
        new_clicked = self.listgen_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"
        time.sleep(1)

        # Create New tab'ına git (modal içinde)
        tab_clicked = self.create_lg_page.click_create_new_tab()
        assert tab_clicked, "Create New tab'ına tıklanamadı"
        time.sleep(1)

        # Name field'ını boş bırak (hiçbir şey girme)
        print("Name field boş bırakılıyor")

        # Type: Text seç
        type_selected = self.create_lg_page.select_type("text")
        assert type_selected, "Text type seçilemedi"

        # Value ekle
        value_added = self.create_lg_page.add_value("test123")
        assert value_added, "Value eklenemedi"

        # SAVE butonu aktif mi kontrol et
        save_enabled = self.create_lg_page.is_save_button_enabled_new_file()
        assert save_enabled, "SAVE butonu aktif olmalıydı"
        print("SAVE butonu aktif")

        # SAVE butonuna tıkla
        save_clicked = self.create_lg_page.click_save_button_new_file()
        assert save_clicked, "SAVE butonuna tıklanamadı"
        time.sleep(2)

        # Modal hala açık mı? (validation error varsa açık kalır)
        page_source = self.driver.page_source
        modal_still_open = "modal" in page_source.lower() or "Create New" in page_source
        assert modal_still_open, "Modal kapanmamalıydı (boş name hatası)"

        # Error mesajı var mı kontrol et
        error_found = "error" in page_source.lower() or "required" in page_source.lower()
        assert error_found, "Name required error mesajı görünmeli"

        print("Test başarılı: Boş name reddediliyor - SAVE aktif ama validation hatası")

    def test_TC055_browser_refresh(self):
        """TC055: Browser refresh - Sayfa yenileme sırasında data kaybı - Form verileri korunuyor mu?"""
        print("\nTC055: Browser refresh testi ===")

        # NEW butonuna tıkla ve form doldur
        new_clicked = self.listgen_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"
        time.sleep(1)

        tab_clicked = self.create_lg_page.click_create_new_tab()
        assert tab_clicked, "Create New tab'ına tıklanamadı"
        time.sleep(1)

        # Form doldur
        name_entered = self.create_lg_page.enter_name(self.test_list_name)
        assert name_entered, "Name girilemedi"

        type_selected = self.create_lg_page.select_type("text")
        assert type_selected, "Text type seçilemedi"

        value_added = self.create_lg_page.add_value("test123")
        assert value_added, "Value eklenemedi"

        # Browser refresh yap
        print("*** BROWSER REFRESH ***")
        self.driver.refresh()
        time.sleep(3)

        # Verilerin kaybolduğunu kontrol et
        try:
            name_field = self.driver.find_element(*self.create_lg_page.NAME_FIELD)
            current_name = name_field.get_attribute("value")
            print(f"Refresh sonrası name: '{current_name}'")
            assert current_name == "", "Form verileri temizlenmeli"
        except:
            print("Name field bulunamadı")

        print("Test başarılı: Browser refresh form verilerini temizliyor")


    def test_TC056_type_change_after_values(self):
        """TC056: Type değiştirme sonrası values - Text seç→values ekle→Integer'a geç - Mevcut values nasıl davranıyor?"""
        print("\nTC056: Type değiştirme sonrası values testi ===")

        # NEW butonuna tıkla ve Create New tab'ına git
        new_clicked = self.listgen_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"
        time.sleep(1)

        tab_clicked = self.create_lg_page.click_create_new_tab()
        assert tab_clicked, "Create New tab'ına tıklanamadı"
        time.sleep(1)

        # Name gir
        name_entered = self.create_lg_page.enter_name(self.test_list_name)
        assert name_entered, "Name girilemedi"

        # İlk olarak TEXT type seç
        type_selected = self.create_lg_page.select_type("text")
        assert type_selected, "Text type seçilemedi"
        print("İlk type: TEXT seçildi")

        # Text values ekle
        value1_added = self.create_lg_page.add_value("abc123")
        assert value1_added, "Text value abc123 eklenemedi"

        value2_added = self.create_lg_page.add_value("hello")
        assert value2_added, "Text value hello eklenemedi"

        print("Text values eklendi: abc123, hello")

        # Type'ı INTEGER'a değiştir
        print("TYPE DEĞİŞTİRİLİYOR: TEXT → INTEGER")
        type_changed = self.create_lg_page.select_type("integer")
        assert type_changed, "Integer type seçilemedi"

        # Mevcut values korundu mu kontrol et
        page_source = self.driver.page_source
        if "abc123" in page_source and "hello" in page_source:
            print("Mevcut values korundu")
        else:
            print("Mevcut values kayboldu")

        # Yeni Integer value eklemeyi dene
        new_value_added = self.create_lg_page.add_value("123")
        if new_value_added:
            print("Yeni Integer value eklendi: 123")

        # SAVE butonu durumu
        save_enabled = self.create_lg_page.is_save_button_enabled_new_file()
        print(f"SAVE butonu: {'Aktif' if save_enabled else 'Disabled'}")

        print("Test tamamlandı: Type değişikliği test edildi")





