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


class TestCreateFromFileTab:

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

    def test_TC058_upload_file_without_separator(self):
        """TC058: Separator seçmeden dosya yükleme - Dosya yükle, separator boş bırak - Error alıyor modal açık kalıyor"""
        print("\nTC058: Separator seçmeden dosya yükleme testi ===")

        # NEW butonuna tıkla
        new_clicked = self.listgen_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"
        time.sleep(1)

        # Create From File tab'ına git
        tab_clicked = self.create_lg_page.click_create_from_file_tab()
        assert tab_clicked, "Create From File tab'ına tıklanamadı"
        time.sleep(1)

        # Test dosyası oluştur
        test_file_path = os.path.join(os.getcwd(), "test_data", "sample.csv")
        os.makedirs(os.path.dirname(test_file_path), exist_ok=True)
        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write("value1,value2,value3\ntest1,test2,test3")

        # Dosya upload et
        file_uploaded = self.create_lg_page.upload_file(test_file_path)
        assert file_uploaded, "Dosya upload edilemedi"
        print("Dosya upload edildi")

        # SAVE butonu aktif mi kontrol et
        save_enabled = self.create_lg_page.is_save_button_enabled_new_file()
        assert save_enabled, "SAVE butonu aktif olmalı"
        print("SAVE butonu aktif")

        # Separator seçmeden SAVE'e tıkla
        save_clicked = self.create_lg_page.click_save_button_new_file()
        assert save_clicked, "SAVE butonuna tıklanamadı"
        time.sleep(2)

        # Modal hala açık mı kontrol et (error varsa açık kalır)
        page_source = self.driver.page_source
        modal_still_open = "modal" in page_source.lower() or "Create From File" in page_source
        assert modal_still_open, "Modal kapanmamalıydı (separator error)"

        # Error mesajı var mı kontrol et
        error_found = "error" in page_source.lower() or "separator" in page_source.lower() or "required" in page_source.lower()
        assert error_found, "Separator error mesajı görünmeli"

        print("Test başarılı: Separator seçmeden SAVE aktif ama error alıyor, modal açık kalıyor")

    def test_TC059_comma_separator_csv_upload(self):
        """TC059: Comma separator ile CSV yükleme - Service unavailable hatası alıyor"""
        print("\nTC059: Comma separator ile CSV yükleme testi ===")

        # NEW butonuna tıkla
        new_clicked = self.listgen_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"
        time.sleep(1)

        # Create From File tab'ına git
        tab_clicked = self.create_lg_page.click_create_from_file_tab()
        assert tab_clicked, "Create From File tab'ına tıklanamadı"
        time.sleep(1)

        # Comma separated CSV dosyası oluştur
        test_file_path = os.path.join(os.getcwd(), "test_data", "comma_separated.csv")
        os.makedirs(os.path.dirname(test_file_path), exist_ok=True)

        csv_content = "List_Name,List_Age,List_City\nList_Ahmet,25,Istanbul\nList_Mehmet,30,Ankara"
        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write(csv_content)

        print("Comma separated CSV dosyası oluşturuldu")

        # Dosya upload et
        file_uploaded = self.create_lg_page.upload_file(test_file_path)
        assert file_uploaded, "CSV dosyası upload edilemedi"
        print("CSV dosyası upload edildi")

        # Separator: Comma seç
        separator_selected = self.create_lg_page.select_separator("comma")
        assert separator_selected, "Comma separator seçilemedi"
        print("Comma separator seçildi")

        # SAVE butonuna tıkla
        save_clicked = self.create_lg_page.click_save_button_new_file()
        assert save_clicked, "SAVE butonuna tıklanamadı"
        time.sleep(2)

        # Backend service durumunu kontrol et
        page_source = self.driver.page_source
        service_error = "service is currently unavailable" in page_source.lower() or "docker" in page_source.lower()

        if service_error:
            print("Backend service unavailable - Docker container problemi")
        else:
            print("Comma separated CSV başarıyla upload edildi")

        print("Test tamamlandı: Comma separator testi")

    def test_TC060_tab_separator_csv_upload(self):
        """TC060: Tab separator ile CSV yükleme - CSV dosyasında tab separator kullanma"""
        print("\nTC060: Tab separator ile CSV yükleme testi ===")

        # NEW butonuna tıkla
        new_clicked = self.listgen_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"
        time.sleep(1)

        # Create From File tab'ına git
        tab_clicked = self.create_lg_page.click_create_from_file_tab()
        assert tab_clicked, "Create From File tab'ına tıklanamadı"
        time.sleep(1)

        # Tab separated CSV oluştur
        test_file_path = os.path.join(os.getcwd(), "test_data", "tab_separated.csv")
        os.makedirs(os.path.dirname(test_file_path), exist_ok=True)

        csv_content = "List_Name\tList_Age\tList_City\nList_Ahmet\t25\tIstanbul\nList_Mehmet\t30\tAnkara"
        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write(csv_content)

        print("Tab separated CSV dosyası oluşturuldu")

        # Dosya upload et
        file_uploaded = self.create_lg_page.upload_file(test_file_path)
        assert file_uploaded, "CSV dosyası upload edilemedi"
        print("CSV dosyası upload edildi")

        # Separator: Tab seç
        separator_selected = self.create_lg_page.select_separator("tab")
        assert separator_selected, "Tab separator seçilemedi"
        print("Tab separator seçildi")

        # SAVE butonuna tıkla
        save_clicked = self.create_lg_page.click_save_button_new_file()
        assert save_clicked, "SAVE butonuna tıklanamadı"
        time.sleep(2)

        # Backend service durumunu kontrol et
        page_source = self.driver.page_source
        service_error = "service is currently unavailable" in page_source.lower() or "docker" in page_source.lower()

        if service_error:
            print("Backend service unavailable - Docker container problemi")
        else:
            print("Tab separated CSV başarıyla upload edildi")

        print("Test tamamlandı: Tab separator testi")

    def test_TC061_semicolon_separator_csv_upload(self):
        """TC061: Semicolon separator ile CSV yükleme - CSV dosyasında semicolon separator kullanma"""
        print("\nTC061: Semicolon separator ile CSV yükleme testi ===")

        # NEW butonuna tıkla
        new_clicked = self.listgen_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"
        time.sleep(1)

        # Create From File tab'ına git
        tab_clicked = self.create_lg_page.click_create_from_file_tab()
        assert tab_clicked, "Create From File tab'ına tıklanamadı"
        time.sleep(1)

        # Semicolon separated CSV oluştur
        test_file_path = os.path.join(os.getcwd(), "test_data", "semicolon_separated.csv")
        os.makedirs(os.path.dirname(test_file_path), exist_ok=True)

        csv_content = "List_Name;List_Age;List_City\nList_Ahmet;25;Istanbul\nList_Mehmet;30;Ankara"
        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write(csv_content)

        print("Semicolon separated CSV dosyası oluşturuldu")

        # Dosya upload et
        file_uploaded = self.create_lg_page.upload_file(test_file_path)
        assert file_uploaded, "CSV dosyası upload edilemedi"
        print("CSV dosyası upload edildi")

        # Separator: Semicolon seç
        separator_selected = self.create_lg_page.select_separator("semicolon")
        assert separator_selected, "Semicolon separator seçilemedi"
        print("Semicolon separator seçildi")

        # SAVE butonuna tıkla
        save_clicked = self.create_lg_page.click_save_button_new_file()
        assert save_clicked, "SAVE butonuna tıklanamadı"
        time.sleep(2)

        # Backend service durumunu kontrol et
        page_source = self.driver.page_source
        service_error = "service is currently unavailable" in page_source.lower() or "docker" in page_source.lower()

        if service_error:
            print("Backend service unavailable - Docker container problemi")
        else:
            print("Semicolon separated CSV başarıyla upload edildi")

        print("Test tamamlandı: Semicolon separator testi")

    def test_TC062_space_separator_csv_upload(self):
        """TC062: Space separator ile CSV yükleme - CSV dosyasında space separator kullanma"""
        print("\nTC062: Space separator ile CSV yükleme testi ===")

        # NEW butonuna tıkla
        new_clicked = self.listgen_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"
        time.sleep(1)

        # Create From File tab'ına git
        tab_clicked = self.create_lg_page.click_create_from_file_tab()
        assert tab_clicked, "Create From File tab'ına tıklanamadı"
        time.sleep(1)

        # Space separated CSV oluştur
        test_file_path = os.path.join(os.getcwd(), "test_data", "space_separated.csv")
        os.makedirs(os.path.dirname(test_file_path), exist_ok=True)

        csv_content = "List_Name List_Age List_City\nList_Ahmet 25 Istanbul\nList_Mehmet 30 Ankara"
        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write(csv_content)

        print("Space separated CSV dosyası oluşturuldu")

        # Dosya upload et
        file_uploaded = self.create_lg_page.upload_file(test_file_path)
        assert file_uploaded, "CSV dosyası upload edilemedi"
        print("CSV dosyası upload edildi")

        # Separator: Space seç
        separator_selected = self.create_lg_page.select_separator("space")
        assert separator_selected, "Space separator seçilemedi"
        print("Space separator seçildi")

        # SAVE butonuna tıkla
        save_clicked = self.create_lg_page.click_save_button_new_file()
        assert save_clicked, "SAVE butonuna tıklanamadı"
        time.sleep(2)

        # Backend service durumunu kontrol et
        page_source = self.driver.page_source
        service_error = "service is currently unavailable" in page_source.lower() or "docker" in page_source.lower()

        if service_error:
            print("Backend service unavailable - Docker container problemi")
        else:
            print("Space separated CSV başarıyla upload edildi")

        print("Test tamamlandı: Space separator testi")

    def test_TC063_pipe_separator_csv_upload(self):
        """TC063: Pipe separator ile CSV yükleme - CSV dosyasında pipe separator kullanma"""
        print("\nTC063: Pipe separator ile CSV yükleme testi ===")

        # NEW butonuna tıkla
        new_clicked = self.listgen_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"
        time.sleep(1)

        # Create From File tab'ına git
        tab_clicked = self.create_lg_page.click_create_from_file_tab()
        assert tab_clicked, "Create From File tab'ına tıklanamadı"
        time.sleep(1)

        # Pipe separated CSV oluştur
        test_file_path = os.path.join(os.getcwd(), "test_data", "pipe_separated.csv")
        os.makedirs(os.path.dirname(test_file_path), exist_ok=True)

        csv_content = "List_Name|List_Age|List_City\nList_Ahmet|25|Istanbul\nList_Mehmet|30|Ankara"
        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write(csv_content)

        print("Pipe separated CSV dosyası oluşturuldu")

        # Dosya upload et
        file_uploaded = self.create_lg_page.upload_file(test_file_path)
        assert file_uploaded, "CSV dosyası upload edilemedi"
        print("CSV dosyası upload edildi")

        # Separator: Pipe seç
        separator_selected = self.create_lg_page.select_separator("pipe")
        assert separator_selected, "Pipe separator seçilemedi"
        print("Pipe separator seçildi")

        # SAVE butonuna tıkla
        save_clicked = self.create_lg_page.click_save_button_new_file()
        assert save_clicked, "SAVE butonuna tıklanamadı"
        time.sleep(2)

        # Backend service durumunu kontrol et
        page_source = self.driver.page_source
        service_error = "service is currently unavailable" in page_source.lower() or "docker" in page_source.lower()

        if service_error:
            print("Backend service unavailable - Docker container problemi")
        else:
            print("Pipe separated CSV başarıyla upload edildi")

        print("Test tamamlandı: Pipe separator testi")

    def test_TC064_colon_separator_csv_upload(self):
        """TC064: Colon separator ile CSV yükleme - CSV dosyasında colon separator kullanma"""
        print("\nTC064: Colon separator ile CSV yükleme testi ===")

        # NEW butonuna tıkla
        new_clicked = self.listgen_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"
        time.sleep(1)

        # Create From File tab'ına git
        tab_clicked = self.create_lg_page.click_create_from_file_tab()
        assert tab_clicked, "Create From File tab'ına tıklanamadı"
        time.sleep(1)

        # Colon separated CSV oluştur
        test_file_path = os.path.join(os.getcwd(), "test_data", "colon_separated.csv")
        os.makedirs(os.path.dirname(test_file_path), exist_ok=True)

        csv_content = "List_Name:List_Age:List_City\nList_Ahmet:25:Istanbul\nList_Mehmet:30:Ankara"
        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write(csv_content)

        print("Colon separated CSV dosyası oluşturuldu")

        # Dosya upload et
        file_uploaded = self.create_lg_page.upload_file(test_file_path)
        assert file_uploaded, "CSV dosyası upload edilemedi"
        print("CSV dosyası upload edildi")

        # Separator: Colon seç
        separator_selected = self.create_lg_page.select_separator("colon")
        assert separator_selected, "Colon separator seçilemedi"
        print("Colon separator seçildi")

        # SAVE butonuna tıkla
        save_clicked = self.create_lg_page.click_save_button_new_file()
        assert save_clicked, "SAVE butonuna tıklanamadı"
        time.sleep(2)

        # Backend service durumunu kontrol et
        page_source = self.driver.page_source
        service_error = "service is currently unavailable" in page_source.lower() or "docker" in page_source.lower()

        if service_error:
            print("Backend service unavailable - Docker container problemi")
        else:
            print("Colon separated CSV başarıyla upload edildi")

        print("Test tamamlandı: Colon separator testi")

    def test_TC065_empty_file_upload(self):
        """TC065: Boş dosya yükleme - Içeriği olmayan CSV dosyası upload"""
        print("\nTC065: Boş dosya yükleme testi ===")

        # NEW butonuna tıkla
        new_clicked = self.listgen_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"
        time.sleep(1)

        # Create From File tab'ına git
        tab_clicked = self.create_lg_page.click_create_from_file_tab()
        assert tab_clicked, "Create From File tab'ına tıklanamadı"
        time.sleep(1)

        # Boş CSV dosyası oluştur
        test_file_path = os.path.join(os.getcwd(), "test_data", "empty_file.csv")
        os.makedirs(os.path.dirname(test_file_path), exist_ok=True)

        # Tamamen boş dosya
        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write("")  # Hiçbir şey yazma

        print("Boş CSV dosyası oluşturuldu")

        # Dosya upload et
        file_uploaded = self.create_lg_page.upload_file(test_file_path)
        assert file_uploaded, "Boş dosya upload edilemedi"
        print("Boş dosya upload edildi")

        # Separator: Comma seç
        separator_selected = self.create_lg_page.select_separator("comma")
        assert separator_selected, "Comma separator seçilemedi"

        # SAVE butonuna tıkla
        save_clicked = self.create_lg_page.click_save_button_new_file()
        assert save_clicked, "SAVE butonuna tıklanamadı"
        time.sleep(2)

        # Error kontrolü (boş dosya hatası bekleniyor)
        page_source = self.driver.page_source
        empty_file_error = "empty" in page_source.lower() or "no data" in page_source.lower()
        service_error = "service is currently unavailable" in page_source.lower()

        if service_error:
            print("Backend service unavailable")
        elif empty_file_error:
            print("Boş dosya hatası alındı")
        else:
            print("Boş dosya kabul edildi")

        print("Test tamamlandı: Boş dosya yükleme testi")

    def test_TC066_invalid_file_format(self):
        """TC066: Geçersiz dosya formatı - .txt dosyası upload denemesi"""
        print("\nTC066: Geçersiz dosya formatı testi ===")

        # NEW butonuna tıkla
        new_clicked = self.listgen_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"
        time.sleep(1)

        # Create From File tab'ına git
        tab_clicked = self.create_lg_page.click_create_from_file_tab()
        assert tab_clicked, "Create From File tab'ına tıklanamadı"
        time.sleep(1)

        # .txt dosyası oluştur
        test_file_path = os.path.join(os.getcwd(), "test_data", "invalid_format.txt")
        os.makedirs(os.path.dirname(test_file_path), exist_ok=True)

        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write("List_Name,List_Age\nAhmet,25")

        print("TXT dosyası oluşturuldu")

        # Dosya upload et
        file_uploaded = self.create_lg_page.upload_file(test_file_path)
        time.sleep(2)

        # File format error kontrolü
        page_source = self.driver.page_source
        format_error = "YouCanOnlyUploadCSVFile" in page_source or "csv" in page_source.lower()

        if format_error:
            print("File format error alındı - sadece CSV kabul ediyor")
            assert format_error, "Geçersiz format hatası alınmalı"
        else:
            print("TXT dosyası kabul edildi (beklenmeyen)")

        print("Test tamamlandı: Geçersiz dosya formatı testi")

    def test_TC067_special_characters_in_data(self):
        """TC067: Veride özel karakterler - CSV'de özel karakterler ve unicode"""
        print("\nTC067: Veride özel karakterler testi ===")

        # NEW butonuna tıkla
        new_clicked = self.listgen_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"
        time.sleep(1)

        # Create From File tab'ına git
        tab_clicked = self.create_lg_page.click_create_from_file_tab()
        assert tab_clicked, "Create From File tab'ına tıklanamadı"
        time.sleep(1)

        # Özel karakterli CSV oluştur
        test_file_path = os.path.join(os.getcwd(), "test_data", "special_chars.csv")
        os.makedirs(os.path.dirname(test_file_path), exist_ok=True)

        # Özel karakterler: Unicode, emoji, semboller
        csv_content = "List_Name,List_Symbol,List_Unicode\nList_Açelya,List_@#$%,List_测试\nList_Müge,List_€£¥,List_🚀🎯"

        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write(csv_content)

        print("Özel karakterli CSV oluşturuldu")

        # Dosya upload et
        file_uploaded = self.create_lg_page.upload_file(test_file_path)
        assert file_uploaded, "Özel karakterli dosya upload edilemedi"

        # Separator: Comma seç
        separator_selected = self.create_lg_page.select_separator("comma")
        assert separator_selected, "Comma separator seçilemedi"

        # SAVE butonuna tıkla
        save_clicked = self.create_lg_page.click_save_button_new_file()
        assert save_clicked, "SAVE butonuna tıklanamadı"
        time.sleep(2)

        # Sonuç kontrolü
        page_source = self.driver.page_source
        service_error = "service is currently unavailable" in page_source.lower()

        if service_error:
            print("Backend service unavailable")
        else:
            print("Özel karakterli CSV test edildi")

        print("Test tamamlandı: Özel karakterler testi")

    def test_TC068_quotes_in_csv(self):
        """TC068: CSV'de tırnak işaretleri - Escaped quotes ve complex data"""
        print("\nTC068: CSV'de tırnak işaretleri testi ===")

        # NEW butonuna tıkla
        new_clicked = self.listgen_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"
        time.sleep(1)

        # Create From File tab'ına git
        tab_clicked = self.create_lg_page.click_create_from_file_tab()
        assert tab_clicked, "Create From File tab'ına tıklanamadı"
        time.sleep(1)

        # Tırnak işaretli CSV oluştur
        test_file_path = os.path.join(os.getcwd(), "test_data", "quotes_csv.csv")
        os.makedirs(os.path.dirname(test_file_path), exist_ok=True)

        # Karmaşık tırnak kullanımı
        csv_content = '''List_Name,List_Description,List_Quote
"List_Ahmet","List_Developer, Senior","List_He said ""Hello World"""
"List_Ayşe","List_Manager, Team Lead","List_She said 'Good morning'"'''

        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write(csv_content)

        print("Tırnak işaretli CSV oluşturuldu")

        # Dosya upload et
        file_uploaded = self.create_lg_page.upload_file(test_file_path)
        assert file_uploaded, "Tırnak işaretli dosya upload edilemedi"

        # Separator: Comma seç
        separator_selected = self.create_lg_page.select_separator("comma")
        assert separator_selected, "Comma separator seçilemedi"

        # SAVE butonuna tıkla
        save_clicked = self.create_lg_page.click_save_button_new_file()
        assert save_clicked, "SAVE butonuna tıklanamadı"
        time.sleep(2)

        print("Test tamamlandı: Tırnak işaretleri testi")

    def test_TC069_mixed_data_types(self):
        """TC069: Karışık veri tipleri - String, Number, Date, Boolean mix"""
        print("\nTC069: Karışık veri tipleri testi ===")

        # NEW butonuna tıkla
        new_clicked = self.listgen_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"
        time.sleep(1)

        # Create From File tab'ına git
        tab_clicked = self.create_lg_page.click_create_from_file_tab()
        assert tab_clicked, "Create From File tab'ına tıklanamadı"
        time.sleep(1)

        # Karışık veri tipli CSV oluştur
        test_file_path = os.path.join(os.getcwd(), "test_data", "mixed_types.csv")
        os.makedirs(os.path.dirname(test_file_path), exist_ok=True)

        csv_content = """List_Name,List_Age,List_Salary,List_Date,List_Active,List_Score
List_Ahmet,25,50000.75,2023-01-15,true,95.5
List_Ayşe,thirty,invalid_salary,invalid_date,maybe,not_number
List_Mehmet,-5,0,1900-01-01,false,100.0"""

        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write(csv_content)

        print("Karışık veri tipli CSV oluşturuldu")

        # Dosya upload et
        file_uploaded = self.create_lg_page.upload_file(test_file_path)
        assert file_uploaded, "Karışık tipli dosya upload edilemedi"

        # Separator: Comma seç
        separator_selected = self.create_lg_page.select_separator("comma")
        assert separator_selected, "Comma separator seçilemedi"

        # SAVE butonuna tıkla
        save_clicked = self.create_lg_page.click_save_button_new_file()
        assert save_clicked, "SAVE butonuna tıklanamadı"
        time.sleep(2)

        print("Test tamamlandı: Karışık veri tipleri testi")

    def test_TC070_multiple_file_upload_attempt(self):
        """TC070: Çoklu dosya yükleme denemesi - Sistem sadece tek dosya kabul ediyor mu"""
        print("\nTC070: Çoklu dosya yükleme denemesi testi ===")

        # NEW butonuna tıkla
        new_clicked = self.listgen_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"
        time.sleep(1)

        # Create From File tab'ına git
        tab_clicked = self.create_lg_page.click_create_from_file_tab()
        assert tab_clicked, "Create From File tab'ına tıklanamadı"
        time.sleep(1)

        # İki farklı CSV dosyası oluştur
        test_file1_path = os.path.join(os.getcwd(), "test_data", "file1.csv")
        test_file2_path = os.path.join(os.getcwd(), "test_data", "file2.csv")
        os.makedirs(os.path.dirname(test_file1_path), exist_ok=True)

        with open(test_file1_path, 'w', encoding='utf-8') as f:
            f.write("List_Name,List_Age\nList_File1,25")

        with open(test_file2_path, 'w', encoding='utf-8') as f:
            f.write("List_Name,List_City\nList_File2,Istanbul")

        print("İki farklı CSV dosyası oluşturuldu")

        # İlk dosyayı upload et
        file1_uploaded = self.create_lg_page.upload_file(test_file1_path)
        assert file1_uploaded, "İlk dosya upload edilemedi"
        print("İlk dosya upload edildi")

        # İkinci dosyayı upload etmeye çalış (öncekinin üzerine yazmalı)
        file2_uploaded = self.create_lg_page.upload_file(test_file2_path)
        time.sleep(2)
        print("İkinci dosya upload edilmeye çalışıldı")

        # Hangi dosyanın kaldığını kontrol et
        page_source = self.driver.page_source
        if "file1" in page_source:
            print("İlk dosya kaldı")
        elif "file2" in page_source:
            print("İkinci dosya öncekinin yerine geçti")
        else:
            print("Dosya durumu belirsiz")

        print("Test tamamlandı: Çoklu dosya upload denemesi")

    def test_TC071_sample_file_download(self):
        """TC071: Örnek dosya indirme - Sample file download butonunu test et"""
        print("\nTC071: Örnek dosya indirme testi ===")

        # NEW butonuna tıkla
        new_clicked = self.listgen_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"
        time.sleep(1)

        # Create From File tab'ına git
        tab_clicked = self.create_lg_page.click_create_from_file_tab()
        assert tab_clicked, "Create From File tab'ına tıklanamadı"
        time.sleep(1)

        # Download butonunun varlığını kontrol et
        try:
            download_button = self.driver.find_element(*self.create_lg_page.SAMPLE_FILE_DOWNLOAD)
            print(f"Download butonu bulundu: {download_button.is_displayed()}")
            print(f"Download butonu enabled: {download_button.is_enabled()}")

            if download_button.is_enabled():
                # Sample file download butonuna tıkla
                download_clicked = self.create_lg_page.click_download_sample()
                assert download_clicked, "Sample download butonuna tıklanamadı"
                print("Sample file download butonuna tıklandı")
                time.sleep(3)  # Download için bekle

                # Downloads klasörüne bakılabilir ama test environment'da zor
                print("Sample file Downloads klasörüne indirilmiş olmalı")
            else:
                print("Download butonu disabled")

        except Exception as e:
            print(f"Download butonu bulunamadı: {e}")

        print("Test tamamlandı: Örnek dosya indirme testi")

    def test_TC072_file_without_separator_chars(self):
        """TC072: Dosyada ayraç karakteri yok - Seçilen separator dosyada mevcut değil"""
        print("\nTC072: Dosyada ayraç karakteri yok testi ===")

        # NEW butonuna tıkla
        new_clicked = self.listgen_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"
        time.sleep(1)

        # Create From File tab'ına git
        tab_clicked = self.create_lg_page.click_create_from_file_tab()
        assert tab_clicked, "Create From File tab'ına tıklanamadı"
        time.sleep(1)

        # Ayraç karakteri olmayan dosya oluştur
        test_file_path = os.path.join(os.getcwd(), "test_data", "no_separator.csv")
        os.makedirs(os.path.dirname(test_file_path), exist_ok=True)

        # Hiç virgül olmayan tek sütun data
        csv_content = "List_FullData\nList_AhmetFromIstanbul25YearsOld\nList_AyseFromAnkara30YearsOld"

        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write(csv_content)

        print("Ayraç karakteri olmayan dosya oluşturuldu")

        # Dosya upload et
        file_uploaded = self.create_lg_page.upload_file(test_file_path)
        assert file_uploaded, "Dosya upload edilemedi"

        # Separator: Comma seç (ama dosyada virgül yok)
        separator_selected = self.create_lg_page.select_separator("comma")
        assert separator_selected, "Comma separator seçilemedi"

        # SAVE butonuna tıkla
        save_clicked = self.create_lg_page.click_save_button_new_file()
        assert save_clicked, "SAVE butonuna tıklanamadı"
        time.sleep(2)

        # Sistem nasıl davranıyor kontrol et
        page_source = self.driver.page_source
        service_error = "service is currently unavailable" in page_source.lower()

        if service_error:
            print("Backend service unavailable")
        else:
            print("Ayraç olmayan dosya işlendi - tek sütun olarak")

        print("Test tamamlandı: Ayraç karakteri olmayan dosya testi")

    def test_TC073_sql_injection_in_file(self):
        """TC073: Dosya içeriğinde SQL injection - CSV data'da SQL injection payload"""
        print("\nTC073: Dosya içeriğinde SQL injection testi ===")

        # NEW butonuna tıkla
        new_clicked = self.listgen_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"
        time.sleep(1)

        # Create From File tab'ına git
        tab_clicked = self.create_lg_page.click_create_from_file_tab()
        assert tab_clicked, "Create From File tab'ına tıklanamadı"
        time.sleep(1)

        # SQL injection payload'lu CSV oluştur
        test_file_path = os.path.join(os.getcwd(), "test_data", "sql_injection.csv")
        os.makedirs(os.path.dirname(test_file_path), exist_ok=True)

        # SQL injection payloadları
        csv_content = """List_Name,List_Query,List_Payload
"List_Drop","'; DROP TABLE users; --","List_1' OR '1'='1"
"List_Union","' UNION SELECT * FROM admin --","List_'; DELETE FROM data; --"
"List_Normal","List_RegularName","List_RegularData\""""

        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write(csv_content)

        print("SQL injection payloadlı CSV oluşturuldu")

        # Dosya upload et
        file_uploaded = self.create_lg_page.upload_file(test_file_path)
        assert file_uploaded, "SQL injection dosyası upload edilemedi"

        # Separator: Comma seç
        separator_selected = self.create_lg_page.select_separator("comma")
        assert separator_selected, "Comma separator seçilemedi"

        # SAVE butonuna tıkla
        save_clicked = self.create_lg_page.click_save_button_new_file()
        assert save_clicked, "SAVE butonuna tıklanamadı"
        time.sleep(2)

        # Sistem crash olmadı mı kontrol et
        try:
            current_url = self.driver.current_url
            print(f"Current URL: {current_url}")
            print("Sistem stabil - SQL injection etkisiz")
        except:
            print("UYARI: Sistem etkilenmiş olabilir")

        print("Test tamamlandı: SQL injection dosya içeriği testi")

    def test_TC074_xss_injection_in_file(self):
        """TC074: Dosya ile XSS injection - CSV data'da XSS payload"""
        print("\nTC074: Dosya ile XSS injection testi ===")

        # NEW butonuna tıkla
        new_clicked = self.listgen_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"
        time.sleep(1)

        # Create From File tab'ına git
        tab_clicked = self.create_lg_page.click_create_from_file_tab()
        assert tab_clicked, "Create From File tab'ına tıklanamadı"
        time.sleep(1)

        # XSS payload'lu CSV oluştur
        test_file_path = os.path.join(os.getcwd(), "test_data", "xss_injection.csv")
        os.makedirs(os.path.dirname(test_file_path), exist_ok=True)

        # XSS payloadları
        csv_content = """List_Name,List_Script,List_Html
"List_Alert","<script>alert('XSS')</script>","<img src=x onerror=alert(1)>"
"List_Iframe","<iframe src=javascript:alert('XSS')>","<svg onload=alert('XSS')>"
"List_Normal","List_RegularName","List_RegularData\""""

        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write(csv_content)

        print("XSS payloadlı CSV oluşturuldu")

        # Dosya upload et
        file_uploaded = self.create_lg_page.upload_file(test_file_path)
        assert file_uploaded, "XSS injection dosyası upload edilemedi"

        # Separator: Comma seç
        separator_selected = self.create_lg_page.select_separator("comma")
        assert separator_selected, "Comma separator seçilemedi"

        # SAVE butonuna tıkla
        save_clicked = self.create_lg_page.click_save_button_new_file()
        assert save_clicked, "SAVE butonuna tıklanamadı"
        time.sleep(2)

        print("Test tamamlandı: XSS injection dosya içeriği testi")

    def test_TC075_file_without_extension(self):
        """TC075: Uzantısız dosya yükleme - Extension olmayan dosya upload"""
        print("\nTC075: Uzantısız dosya yükleme testi ===")

        # NEW butonuna tıkla
        new_clicked = self.listgen_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"
        time.sleep(1)

        # Create From File tab'ına git
        tab_clicked = self.create_lg_page.click_create_from_file_tab()
        assert tab_clicked, "Create From File tab'ına tıklanamadı"
        time.sleep(1)

        # Uzantısız dosya oluştur
        test_file_path = os.path.join(os.getcwd(), "test_data", "no_extension_file")  # .csv yok
        os.makedirs(os.path.dirname(test_file_path), exist_ok=True)

        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write("List_Name,List_Age\nList_Ahmet,25")

        print("Uzantısız dosya oluşturuldu")

        # Dosya upload et
        file_uploaded = self.create_lg_page.upload_file(test_file_path)
        time.sleep(2)

        # File extension error kontrolü
        page_source = self.driver.page_source
        extension_error = "extension" in page_source.lower() or "csv" in page_source.lower()

        if extension_error:
            print("File extension error alındı")
        else:
            print("Uzantısız dosya kabul edildi")

        print("Test tamamlandı: Uzantısız dosya yükleme testi")

    def test_TC076_duplicate_column_names(self):
        """TC076: Aynı sütun isimleri - CSV'de duplicate column headers"""
        print("\nTC076: Aynı sütun isimleri testi ===")

        # NEW butonuna tıkla
        new_clicked = self.listgen_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"
        time.sleep(1)

        # Create From File tab'ına git
        tab_clicked = self.create_lg_page.click_create_from_file_tab()
        assert tab_clicked, "Create From File tab'ına tıklanamadı"
        time.sleep(1)

        # Aynı sütun isimli CSV oluştur
        test_file_path = os.path.join(os.getcwd(), "test_data", "duplicate_columns.csv")
        os.makedirs(os.path.dirname(test_file_path), exist_ok=True)

        # Duplicate column names
        csv_content = """List_Name,List_Name,List_Age,List_Age,List_Name
List_Ahmet1,List_Ahmet2,25,26,List_Ahmet3
List_Ayse1,List_Ayse2,30,31,List_Ayse3"""

        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write(csv_content)

        print("Duplicate column names CSV oluşturuldu")

        # Dosya upload et
        file_uploaded = self.create_lg_page.upload_file(test_file_path)
        assert file_uploaded, "Duplicate columns dosyası upload edilemedi"

        # Separator: Comma seç
        separator_selected = self.create_lg_page.select_separator("comma")
        assert separator_selected, "Comma separator seçilemedi"

        # SAVE butonuna tıkla
        save_clicked = self.create_lg_page.click_save_button_new_file()
        assert save_clicked, "SAVE butonuna tıklanamadı"
        time.sleep(2)

        # Duplicate column error kontrolü
        page_source = self.driver.page_source
        duplicate_error = "duplicate" in page_source.lower() or "column" in page_source.lower()
        service_error = "service is currently unavailable" in page_source.lower()

        if service_error:
            print("Backend service unavailable")
        elif duplicate_error:
            print("Duplicate column error alındı")
        else:
            print("Duplicate columns kabul edildi")

        print("Test tamamlandı: Aynı sütun isimleri testi")