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
from tdm_automation.Pages.list_generator_page import ListGeneratorPage
from tdm_automation.Pages.create_list_generator_page import CreateListGenerator
from selenium.webdriver.chrome.options import Options

load_dotenv()


class TestCreateFromDbTab:

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

        # List Generator sayfasında olduğumuzu kontrol et
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
            # Oluşturulan liste'yi sil
            page_source = self.driver.page_source
            if hasattr(self, 'test_list_name') and self.test_list_name in page_source:
                self.listgen_page.click_deletelist_andconfirm_button(self.test_list_name)
                time.sleep(1)
        except:
            pass

    def test_TC077_empty_name_with_sql_query(self):
        """TC077: Name boş bırakma - SAVE button disabled olmalı"""
        print("\nTC077: Name boş bırakma testi ===")

        new_clicked = self.listgen_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"
        time.sleep(1)

        tab_clicked = self.create_lg_page.click_create_from_db_tab()
        assert tab_clicked, "Create From DB tab'ına tıklanamadı"
        time.sleep(1)

        print("Name field boş bırakılıyor")

        environment_selected = self.create_lg_page.select_environment_postgres()
        assert environment_selected, "AAAdene environment seçilemedi"

        sql_query = "SELECT first_name FROM schema_1.table_1"
        query_entered = self.create_lg_page.enter_sql_query(sql_query)
        assert query_entered, "SQL query girilemedi"

        validate_clicked = self.create_lg_page.click_validate_button()
        assert validate_clicked, "VALIDATE butonuna tıklanamadı"
        time.sleep(3)

        # SAVE button disabled olmalı (name boş olduğu için)
        save_enabled = self.create_lg_page.is_save_button_enabled_db_ai()
        print(f"SAVE butonu durumu: {'Aktif' if save_enabled else 'Disabled'}")

        assert not save_enabled, "Name boş olduğu için SAVE butonu disabled olmalıydı"

        print(" Test BAŞARILI: Name boş iken SAVE disabled")

    def test_TC078_no_environment_selected(self):
        """TC078: Environment seçmeme - Environment boş bırak, name + SQL doldur"""
        print("\nTC078: Environment seçmeme testi ===")

        # NEW butonuna tıkla
        new_clicked = self.listgen_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"
        time.sleep(1)

        # Create From DB tab'ına git
        tab_clicked = self.create_lg_page.click_create_from_db_tab()
        assert tab_clicked, "Create From DB tab'ına tıklanamadı"
        time.sleep(1)

        # Name gir
        name_entered = self.create_lg_page.enter_name(self.test_list_name)
        assert name_entered, "Name girilemedi"
        print("Name girildi")

        # Environment seçme (boş bırak)
        print("Environment seçilmiyor - boş bırakılıyor")

        # SQL query gir
        sql_query = "SELECT first_name FROM schema_1.table_1"
        query_entered = self.create_lg_page.enter_sql_query(sql_query)
        assert query_entered, "SQL query girilemedi"
        print("SQL query girildi")

        # VALIDATE butonuna tıkla
        validate_clicked = self.create_lg_page.click_validate_button()
        assert validate_clicked, "VALIDATE butonuna tıklanamadı"
        time.sleep(3)

        # SAVE button disabled olmalı (environment seçilmedi)
        save_enabled = self.create_lg_page.is_save_button_enabled_db_ai()
        print(f"SAVE butonu durumu: {'Aktif' if save_enabled else 'Disabled'}")

        assert not save_enabled, "Environment seçilmediği için SAVE butonu disabled olmalıydı"

        print(" Test BAŞARILI: Environment seçmeden SAVE disabled")

    def test_TC079_empty_sql_query(self):
        """TC079: Boş SQL query - Name + Environment doldur, SQL boş bırak"""
        print("\nTC079: Boş SQL query testi ===")

        # NEW butonuna tıkla
        new_clicked = self.listgen_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"
        time.sleep(1)

        # Create From DB tab'ına git
        tab_clicked = self.create_lg_page.click_create_from_db_tab()
        assert tab_clicked, "Create From DB tab'ına tıklanamadı"
        time.sleep(1)

        # Name gir
        name_entered = self.create_lg_page.enter_name(self.test_list_name)
        assert name_entered, "Name girilemedi"
        print("Name girildi")

        # AAAdene environment seç
        environment_selected = self.create_lg_page.select_environment_postgres()
        assert environment_selected, "AAAdene environment seçilemedi"
        print("AAAdene environment seçildi")

        # SQL query'yi boş bırak
        print("SQL query boş bırakılıyor")

        # VALIDATE butonuna tıkla
        validate_clicked = self.create_lg_page.click_validate_button()
        assert validate_clicked, "VALIDATE butonuna tıklanamadı"
        time.sleep(3)

        # SAVE button disabled olmalı (SQL query boş)
        save_enabled = self.create_lg_page.is_save_button_enabled_db_ai()
        print(f"SAVE butonu durumu: {'Aktif' if save_enabled else 'Disabled'}")

        assert not save_enabled, "SQL query boş olduğu için SAVE butonu disabled olmalıydı"

        print("Test BAŞARILI: SQL query boş iken SAVE disabled")

    def test_TC080_valid_single_column_select(self):
        """TC080: Geçerli tek sütun SELECT - Name + Environment + SQL: SELECT first_name FROM schema_1.table_1"""
        print("\nTC080: Geçerli tek sütun SELECT testi ===")

        # NEW butonuna tıkla
        new_clicked = self.listgen_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"
        time.sleep(1)

        # Create From DB tab'ına git
        tab_clicked = self.create_lg_page.click_create_from_db_tab()
        assert tab_clicked, "Create From DB tab'ına tıklanamadı"
        time.sleep(1)

        # Name gir
        name_entered = self.create_lg_page.enter_name(self.test_list_name)
        assert name_entered, "Name girilemedi"
        print("Name girildi")

        # AAAdene environment seç
        environment_selected = self.create_lg_page.select_environment_postgres()
        assert environment_selected, "AAAdene environment seçilemedi"
        print("AAAdene environment seçildi")

        # Valid SQL query gir
        sql_query = "SELECT first_name FROM schema_1.table_1"
        query_entered = self.create_lg_page.enter_sql_query(sql_query)
        assert query_entered, "SQL query girilemedi"
        print("Valid SQL query girildi")

        # VALIDATE butonuna tıkla
        validate_clicked = self.create_lg_page.click_validate_button()
        assert validate_clicked, "VALIDATE butonuna tıklanamadı"
        time.sleep(3)

        # SAVE button aktif olmalı
        save_enabled = self.create_lg_page.is_save_button_enabled_db_ai()
        print(f"SAVE butonu durumu: {'Aktif' if save_enabled else 'Disabled'}")
        assert save_enabled, "SAVE butonu aktif olmalıydı"

        # SAVE butonuna bas
        save_clicked = self.create_lg_page.click_save_button_db_ai()
        assert save_clicked, "SAVE butonuna tıklanamadı"
        time.sleep(2)
        print("SAVE butonuna tıklandı")

        # Liste oluşturuldu mu kontrol et (modal kapandı mı?)
        current_url = self.driver.current_url
        if "create" not in current_url:
            print("Liste başarıyla oluşturuldu - ana sayfaya yönlendirildi")
        else:
            print("Modal hala açık - liste oluşturulamadı veya hata var")

        print("Test tamamlandı: Valid SQL ile liste oluşturma")

    def test_TC081_multiple_column_select(self):
        """TC081: Çoklu sütun SELECT - Sistem çoklu sütunu reddediyor, SAVE disabled olmalı"""
        print("\nTC081: Çoklu sütun SELECT testi ===")

        # NEW butonuna tıkla
        new_clicked = self.listgen_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"
        time.sleep(1)

        # Create From DB tab'ına git
        tab_clicked = self.create_lg_page.click_create_from_db_tab()
        assert tab_clicked, "Create From DB tab'ına tıklanamadı"
        time.sleep(1)

        # Name gir
        name_entered = self.create_lg_page.enter_name(self.test_list_name)
        assert name_entered, "Name girilemedi"
        print("Name girildi")

        # AAAdene environment seç
        environment_selected = self.create_lg_page.select_environment_postgres()
        assert environment_selected, "AAAdene environment seçilemedi"
        print("AAAdene environment seçildi")

        # Çoklu sütun SQL query gir
        sql_query = "SELECT first_name, last_name FROM schema_1.table_1"
        query_entered = self.create_lg_page.enter_sql_query(sql_query)
        assert query_entered, "SQL query girilemedi"
        print("Çoklu sütun SQL query girildi")

        # VALIDATE butonuna tıkla
        validate_clicked = self.create_lg_page.click_validate_button()
        assert validate_clicked, "VALIDATE butonuna tıklanamadı"
        time.sleep(3)

        # SAVE button disabled olmalı (çoklu sütun reddedildi)
        save_enabled = self.create_lg_page.is_save_button_enabled_db_ai()
        print(f"SAVE butonu durumu: {'Aktif' if save_enabled else 'Disabled'}")

        assert not save_enabled, "Çoklu sütun SELECT reddedildiği için SAVE butonu disabled olmalıydı"

        print("Test BAŞARILI: Sistem çoklu sütun SELECT'i reddediyor")

    def test_TC082_insert_query_validation(self):
        """TC082: INSERT INTO query - INSERT INTO schema_1.table_1... - INSERT sorgusu reddedilmeli"""
        print("\nTC082: INSERT INTO query testi ===")

        # NEW butonuna tıkla
        new_clicked = self.listgen_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"
        time.sleep(1)

        # Create From DB tab'ına git
        tab_clicked = self.create_lg_page.click_create_from_db_tab()
        assert tab_clicked, "Create From DB tab'ına tıklanamadı"
        time.sleep(1)

        # Name gir
        name_entered = self.create_lg_page.enter_name(self.test_list_name)
        assert name_entered, "Name girilemedi"
        print("Name girildi")

        # AAAdene environment seç
        environment_selected = self.create_lg_page.select_environment_postgres()
        assert environment_selected, "AAAdene environment seçilemedi"
        print("AAAdene environment seçildi")

        # INSERT query gir
        sql_query = "INSERT INTO schema_1.table_1 (first_name, last_name) VALUES ('Test', 'User')"
        query_entered = self.create_lg_page.enter_sql_query(sql_query)
        assert query_entered, "SQL query girilemedi"
        print("INSERT query girildi")

        # VALIDATE butonuna tıkla
        validate_clicked = self.create_lg_page.click_validate_button()
        assert validate_clicked, "VALIDATE butonuna tıklanamadı"
        time.sleep(3)

        # SAVE button disabled olmalı (INSERT sorgusu reddedildi)
        save_enabled = self.create_lg_page.is_save_button_enabled_db_ai()
        print(f"SAVE butonu durumu: {'Aktif' if save_enabled else 'Disabled'}")

        assert not save_enabled, "INSERT sorgusu reddedildiği için SAVE butonu disabled olmalıydı"

        print("Test BAŞARILI: Sistem INSERT query'sini reddediyor")

    def test_TC083_drop_create_query_validation(self):
        """TC083: DROP/CREATE query - DROP TABLE schema_1.table_1 - Tehlikeli DDL sorguları reddedilmeli"""
        print("\nTC083: DROP/CREATE query testi ===")

        # NEW butonuna tıkla
        new_clicked = self.listgen_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"
        time.sleep(1)

        # Create From DB tab'ına git
        tab_clicked = self.create_lg_page.click_create_from_db_tab()
        assert tab_clicked, "Create From DB tab'ına tıklanamadı"
        time.sleep(1)

        # Name gir
        name_entered = self.create_lg_page.enter_name(self.test_list_name)
        assert name_entered, "Name girilemedi"
        print("Name girildi")

        # AAAdene environment seç
        environment_selected = self.create_lg_page.select_environment_postgres()
        assert environment_selected, "AAAdene environment seçilemedi"
        print("AAAdene environment seçildi")

        # DROP query gir (tehlikeli)
        sql_query = "DROP TABLE schema_1.table_1"
        query_entered = self.create_lg_page.enter_sql_query(sql_query)
        assert query_entered, "SQL query girilemedi"
        print("DROP query girildi")

        # VALIDATE butonuna tıkla
        validate_clicked = self.create_lg_page.click_validate_button()
        assert validate_clicked, "VALIDATE butonuna tıklanamadı"
        time.sleep(3)

        # SAVE button disabled olmalı (DROP sorgusu reddedildi)
        save_enabled = self.create_lg_page.is_save_button_enabled_db_ai()
        print(f"SAVE butonu durumu: {'Aktif' if save_enabled else 'Disabled'}")

        assert not save_enabled, "DROP sorgusu reddedildiği için SAVE butonu disabled olmalıydı"

        print("Test BAŞARILI: Sistem DROP query'sini reddediyor - Güvenlik koruması")

    def test_TC084_sql_injection_query(self):
        """TC084: SQL injection - SELECT * FROM schema_1.table_1; DROP TABLE users; - SQL injection reddedilmeli"""
        print("\nTC084: SQL injection query testi ===")

        new_clicked = self.listgen_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"
        time.sleep(1)

        tab_clicked = self.create_lg_page.click_create_from_db_tab()
        assert tab_clicked, "Create From DB tab'ına tıklanamadı"
        time.sleep(1)

        name_entered = self.create_lg_page.enter_name(self.test_list_name)
        assert name_entered, "Name girilemedi"

        environment_selected = self.create_lg_page.select_environment_postgres()
        assert environment_selected, "AAAdene environment seçilemedi"

        # SQL injection attempt
        sql_query = "SELECT * FROM schema_1.table_1; DROP TABLE users;"
        query_entered = self.create_lg_page.enter_sql_query(sql_query)
        assert query_entered, "SQL query girilemedi"
        print("SQL injection query girildi")

        validate_clicked = self.create_lg_page.click_validate_button()
        assert validate_clicked, "VALIDATE butonuna tıklanamadı"
        time.sleep(3)

        save_enabled = self.create_lg_page.is_save_button_enabled_db_ai()
        print(f"SAVE butonu durumu: {'Aktif' if save_enabled else 'Disabled'}")

        assert not save_enabled, "SQL injection reddedildiği için SAVE butonu disabled olmalıydı"

        print("Test BAŞARILI: SQL injection reddediliyor")

    def test_TC085_invalid_sql_syntax(self):
        """TC085: Geçersiz SQL syntax - SELCT frist_nam FOMR schema_1.table_1 - Syntax hatası reddedilmeli"""
        print("\nTC085: Geçersiz SQL syntax testi ===")

        new_clicked = self.listgen_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"
        time.sleep(1)

        tab_clicked = self.create_lg_page.click_create_from_db_tab()
        assert tab_clicked, "Create From DB tab'ına tıklanamadı"
        time.sleep(1)

        name_entered = self.create_lg_page.enter_name(self.test_list_name)
        assert name_entered, "Name girilemedi"

        environment_selected = self.create_lg_page.select_environment_postgres()
        assert environment_selected, "AAAdene environment seçilemedi"

        # Invalid syntax query
        sql_query = "SELCT frist_nam FOMR schema_1.table_1"
        query_entered = self.create_lg_page.enter_sql_query(sql_query)
        assert query_entered, "SQL query girilemedi"
        print("Invalid syntax query girildi")

        validate_clicked = self.create_lg_page.click_validate_button()
        assert validate_clicked, "VALIDATE butonuna tıklanamadı"
        time.sleep(3)

        save_enabled = self.create_lg_page.is_save_button_enabled_db_ai()
        print(f"SAVE butonu durumu: {'Aktif' if save_enabled else 'Disabled'}")

        assert not save_enabled, "Invalid syntax reddedildiği için SAVE butonu disabled olmalıydı"

        print("Test BAŞARILI: Invalid SQL syntax reddediliyor")


    def test_TC086_nonexistent_table(self):
        """TC086: Var olmayan tablo - SELECT name FROM nonexistent_table - Olmayan tablo reddedilmeli"""
        print("\nTC086: Var olmayan tablo testi ===")

        new_clicked = self.listgen_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"
        time.sleep(1)

        tab_clicked = self.create_lg_page.click_create_from_db_tab()
        assert tab_clicked, "Create From DB tab'ına tıklanamadı"
        time.sleep(1)

        name_entered = self.create_lg_page.enter_name(self.test_list_name)
        assert name_entered, "Name girilemedi"

        environment_selected = self.create_lg_page.select_environment_postgres()
        assert environment_selected, "AAAdene environment seçilemedi"

        # Nonexistent table query
        sql_query = "SELECT name FROM nonexistent_table"
        query_entered = self.create_lg_page.enter_sql_query(sql_query)
        assert query_entered, "SQL query girilemedi"
        print("Nonexistent table query girildi")

        validate_clicked = self.create_lg_page.click_validate_button()
        assert validate_clicked, "VALIDATE butonuna tıklanamadı"
        time.sleep(3)

        save_enabled = self.create_lg_page.is_save_button_enabled_db_ai()
        print(f"SAVE butonu durumu: {'Aktif' if save_enabled else 'Disabled'}")

        assert not save_enabled, "Var olmayan tablo reddedildiği için SAVE butonu disabled olmalıydı"

        print("Test BAŞARILI: Var olmayan tablo reddediliyor")


    def test_TC087_nonexistent_column(self):
        """TC087: Var olmayan sütun - SELECT nonexistent_column FROM schema_1.table_1 - Olmayan sütun reddedilmeli"""
        print("\nTC087: Var olmayan sütun testi ===")

        new_clicked = self.listgen_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"
        time.sleep(1)

        tab_clicked = self.create_lg_page.click_create_from_db_tab()
        assert tab_clicked, "Create From DB tab'ına tıklanamadı"
        time.sleep(1)

        name_entered = self.create_lg_page.enter_name(self.test_list_name)
        assert name_entered, "Name girilemedi"

        environment_selected = self.create_lg_page.select_environment_postgres()
        assert environment_selected, "AAAdene environment seçilemedi"

        # Nonexistent column query
        sql_query = "SELECT nonexistent_column FROM schema_1.table_1"
        query_entered = self.create_lg_page.enter_sql_query(sql_query)
        assert query_entered, "SQL query girilemedi"
        print("Nonexistent column query girildi")

        validate_clicked = self.create_lg_page.click_validate_button()
        assert validate_clicked, "VALIDATE butonuna tıklanamadı"
        time.sleep(3)

        save_enabled = self.create_lg_page.is_save_button_enabled_db_ai()
        print(f"SAVE butonu durumu: {'Aktif' if save_enabled else 'Disabled'}")

        assert not save_enabled, "Var olmayan sütun reddedildiği için SAVE butonu disabled olmalıydı"

        print("Test BAŞARILI: Var olmayan sütun reddediliyor")

    def test_TC088_very_long_sql_query(self):
        """TC088: Çok uzun SQL query - 1000+ karakter SQL - Uzun query limit kontrolü"""
        print("\nTC088: Çok uzun SQL query testi ===")

        new_clicked = self.listgen_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"
        time.sleep(1)

        tab_clicked = self.create_lg_page.click_create_from_db_tab()
        assert tab_clicked, "Create From DB tab'ına tıklanamadı"
        time.sleep(1)

        name_entered = self.create_lg_page.enter_name(self.test_list_name)
        assert name_entered, "Name girilemedi"

        environment_selected = self.create_lg_page.select_environment_postgres()
        assert environment_selected, "AAAdene environment seçilemedi"

        # Very long SQL query (1000+ characters)
        long_query = "SELECT first_name FROM schema_1.table_1 WHERE " + " OR ".join([f"id = {i}" for i in range(100)])
        print(f"Query length: {len(long_query)} characters")

        query_entered = self.create_lg_page.enter_sql_query(long_query)
        assert query_entered, "SQL query girilemedi"
        print("Very long query girildi")

        validate_clicked = self.create_lg_page.click_validate_button()
        assert validate_clicked, "VALIDATE butonuna tıklanamadı"
        time.sleep(3)

        save_enabled = self.create_lg_page.is_save_button_enabled_db_ai()
        print(f"SAVE butonu durumu: {'Aktif' if save_enabled else 'Disabled'}")

        if save_enabled:
            print("Uzun query kabul edildi - SAVE basılıyor")
            save_clicked = self.create_lg_page.click_save_button_db_ai()
            assert save_clicked, "SAVE butonuna tıklanamadı"
            time.sleep(2)

            # Sonucu kontrol et
            current_url = self.driver.current_url
            if "create" not in current_url:
                print("Uzun query ile liste başarıyla oluşturuldu")
            else:
                print("Modal hala açık - uzun query error olabilir")
        else:
            print("Uzun query reddedildi - karakter limiti var")

        print("Test tamamlandı: Uzun SQL query limit kontrolü")

    def test_TC089_query_with_where_condition(self):
        """TC089: WHERE koşulu ile - SELECT city FROM schema_1.table_1 WHERE age > 25"""
        print("\nTC089: WHERE koşulu ile query testi ===")

        new_clicked = self.listgen_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"
        time.sleep(1)

        tab_clicked = self.create_lg_page.click_create_from_db_tab()
        assert tab_clicked, "Create From DB tab'ına tıklanamadı"
        time.sleep(1)

        name_entered = self.create_lg_page.enter_name(self.test_list_name)
        assert name_entered, "Name girilemedi"

        environment_selected = self.create_lg_page.select_environment_postgres()
        assert environment_selected, "AAAdene environment seçilemedi"

        # WHERE condition query
        sql_query = "SELECT city FROM schema_1.table_1 WHERE age > 25"
        query_entered = self.create_lg_page.enter_sql_query(sql_query)
        assert query_entered, "SQL query girilemedi"
        print("WHERE condition query girildi")

        validate_clicked = self.create_lg_page.click_validate_button()
        assert validate_clicked, "VALIDATE butonuna tıklanamadı"
        time.sleep(3)

        save_enabled = self.create_lg_page.is_save_button_enabled_db_ai()
        print(f"SAVE butonu durumu: {'Aktif' if save_enabled else 'Disabled'}")

        if save_enabled:
            print("WHERE condition kabul edildi - SAVE basılıyor")
            save_clicked = self.create_lg_page.click_save_button_db_ai()
            assert save_clicked, "SAVE butonuna tıklanamadı"
            time.sleep(2)

            current_url = self.driver.current_url
            if "create" not in current_url:
                print("WHERE condition ile liste başarıyla oluşturuldu")
        else:
            print("WHERE condition reddedildi")

        print("Test tamamlandı: WHERE condition testi")

    def test_TC090_query_with_order_by(self):
        """TC090: ORDER BY ile - SELECT first_name FROM schema_1.table_1 ORDER BY age"""
        print("\nTC090: ORDER BY ile query testi ===")

        new_clicked = self.listgen_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"
        time.sleep(1)

        tab_clicked = self.create_lg_page.click_create_from_db_tab()
        assert tab_clicked, "Create From DB tab'ına tıklanamadı"
        time.sleep(1)

        name_entered = self.create_lg_page.enter_name(self.test_list_name)
        assert name_entered, "Name girilemedi"

        environment_selected = self.create_lg_page.select_environment_postgres()
        assert environment_selected, "AAAdene environment seçilemedi"

        # ORDER BY query
        sql_query = "SELECT first_name FROM schema_1.table_1 ORDER BY age"
        query_entered = self.create_lg_page.enter_sql_query(sql_query)
        assert query_entered, "SQL query girilemedi"
        print("ORDER BY query girildi")

        validate_clicked = self.create_lg_page.click_validate_button()
        assert validate_clicked, "VALIDATE butonuna tıklanamadı"
        time.sleep(3)

        save_enabled = self.create_lg_page.is_save_button_enabled_db_ai()
        print(f"SAVE butonu durumu: {'Aktif' if save_enabled else 'Disabled'}")

        if save_enabled:
            print("ORDER BY kabul edildi - SAVE basılıyor")
            save_clicked = self.create_lg_page.click_save_button_db_ai()
            assert save_clicked, "SAVE butonuna tıklanamadı"
            time.sleep(2)

            current_url = self.driver.current_url
            if "create" not in current_url:
                print("ORDER BY ile liste başarıyla oluşturuldu")
        else:
            print("ORDER BY reddedildi")

        print("Test tamamlandı: ORDER BY testi")

    def test_TC091_query_with_limit(self):
        """TC091: LIMIT ile - SELECT email FROM schema_1.table_1 LIMIT 10"""
        print("\nTC091: LIMIT ile query testi ===")

        new_clicked = self.listgen_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"
        time.sleep(1)

        tab_clicked = self.create_lg_page.click_create_from_db_tab()
        assert tab_clicked, "Create From DB tab'ına tıklanamadı"
        time.sleep(1)

        name_entered = self.create_lg_page.enter_name(self.test_list_name)
        assert name_entered, "Name girilemedi"

        environment_selected = self.create_lg_page.select_environment_postgres()
        assert environment_selected, "AAAdene environment seçilemedi"

        # LIMIT query
        sql_query = "SELECT email FROM schema_1.table_1 LIMIT 10"
        query_entered = self.create_lg_page.enter_sql_query(sql_query)
        assert query_entered, "SQL query girilemedi"
        print("LIMIT query girildi")

        validate_clicked = self.create_lg_page.click_validate_button()
        assert validate_clicked, "VALIDATE butonuna tıklanamadı"
        time.sleep(3)

        save_enabled = self.create_lg_page.is_save_button_enabled_db_ai()
        print(f"SAVE butonu durumu: {'Aktif' if save_enabled else 'Disabled'}")

        if save_enabled:
            print("LIMIT kabul edildi - SAVE basılıyor")
            save_clicked = self.create_lg_page.click_save_button_db_ai()
            assert save_clicked, "SAVE butonuna tıklanamadı"
            time.sleep(2)

            current_url = self.driver.current_url
            if "create" not in current_url:
                print("LIMIT ile liste başarıyla oluşturuldu")
        else:
            print("LIMIT reddedildi")

        print("Test tamamlandı: LIMIT testi")

    def test_TC092_duplicate_list_name(self):
        """TC092: Duplicate list name - Var olan name ile DB'den liste oluşturma"""
        print("\nTC092: Duplicate list name testi ===")

        # Önce bir liste oluştur
        print("İlk liste oluşturuluyor...")
        new_clicked1 = self.listgen_page.click_newlist()
        assert new_clicked1, "İlk NEW butonuna tıklanamadı"
        time.sleep(1)

        tab_clicked1 = self.create_lg_page.click_create_from_db_tab()
        assert tab_clicked1, "İlk Create From DB tab'ına tıklanamadı"
        time.sleep(1)

        # Aynı name'i kullan
        duplicate_name = f"DuplicateDBTest_{int(time.time())}"
        name_entered1 = self.create_lg_page.enter_name(duplicate_name)
        assert name_entered1, "İlk name girilemedi"

        environment_selected1 = self.create_lg_page.select_environment_postgres()
        assert environment_selected1, "İlk environment seçilemedi"

        sql_query1 = "SELECT first_name FROM schema_1.table_1"
        query_entered1 = self.create_lg_page.enter_sql_query(sql_query1)
        assert query_entered1, "İlk SQL query girilemedi"

        validate_clicked1 = self.create_lg_page.click_validate_button()
        assert validate_clicked1, "İlk VALIDATE butonuna tıklanamadı"
        time.sleep(3)

        save_enabled1 = self.create_lg_page.is_save_button_enabled_db_ai()
        if save_enabled1:
            save_clicked1 = self.create_lg_page.click_save_button_db_ai()
            time.sleep(2)
            print(f"İlk liste '{duplicate_name}' oluşturuldu")
        else:
            print("İlk liste oluşturulamadı - test iptal")
            return

        # İkinci listeyi aynı isimle oluşturmaya çalış
        print("İkinci liste aynı isimle oluşturuluyor...")
        new_clicked2 = self.listgen_page.click_newlist()
        assert new_clicked2, "İkinci NEW butonuna tıklanamadı"
        time.sleep(1)

        tab_clicked2 = self.create_lg_page.click_create_from_db_tab()
        assert tab_clicked2, "İkinci Create From DB tab'ına tıklanamadı"
        time.sleep(1)

        # Aynı name gir
        name_entered2 = self.create_lg_page.enter_name(duplicate_name)
        assert name_entered2, "İkinci name girilemedi"

        environment_selected2 = self.create_lg_page.select_environment_postgres()
        assert environment_selected2, "İkinci environment seçilemedi"

        sql_query2 = "SELECT last_name FROM schema_1.table_1"
        query_entered2 = self.create_lg_page.enter_sql_query(sql_query2)
        assert query_entered2, "İkinci SQL query girilemedi"

        validate_clicked2 = self.create_lg_page.click_validate_button()
        assert validate_clicked2, "İkinci VALIDATE butonuna tıklanamadı"
        time.sleep(3)

        save_enabled2 = self.create_lg_page.is_save_button_enabled_db_ai()
        if save_enabled2:
            save_clicked2 = self.create_lg_page.click_save_button_db_ai()
            time.sleep(2)

            # Duplicate name error kontrol et
            page_source = self.driver.page_source
            if "error" in page_source.lower() or "exists" in page_source.lower():
                print("Duplicate name hatası alındı")
            else:
                print("Duplicate name kabul edildi - ikinci liste oluşturuldu")
        else:
            print("İkinci liste için SAVE disabled - duplicate name reddedildi")

        print("Test tamamlandı: Duplicate list name kontrolü")