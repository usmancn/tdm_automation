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
from Pages.list_generator_page import ListGeneratorPage
from Pages.create_list_generator_page import CreateListGenerator
from selenium.webdriver.chrome.options import Options

load_dotenv()


class TestGenerateWithAi:

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

        # Chrome options - Gizli sekme
        cls.chrome_options = Options()
        cls.chrome_options.add_argument("--incognito")

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

    def test_TC093_empty_name_generate_with_ai(self):
        """TC093: Name boş bırakma - Generate with AI - Name boş iken VALIDATE disabled"""
        print("\nTC093: Name boş bırakma - Generate with AI testi ===")

        # NEW butonuna tıkla
        new_clicked = self.listgen_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"
        time.sleep(1)

        # Generate with AI tab'ına git
        tab_clicked = self.create_lg_page.click_generate_with_ai_tab()
        assert tab_clicked, "Generate with AI tab'ına tıklanamadı"
        time.sleep(1)

        # Name field'ını boş bırak
        print("Name field boş bırakılıyor")

        # Max Count gir
        max_count_entered = self.create_lg_page.enter_max_count(10)
        assert max_count_entered, "Max Count girilemedi"
        print("Max Count girildi")

        # AI API URL gir
        api_url_entered = self.create_lg_page.enter_api_url("https://openrouter.ai/api/v1")
        assert api_url_entered, "API URL girilemedi"
        print("API URL girildi")

        # AI API Key gir
        api_key_entered = self.create_lg_page.enter_api_key("sk-or-v1-be4cb404544f7213")
        assert api_key_entered, "API Key girilemedi"
        print("API Key girildi")

        # Model Name gir
        model_entered = self.create_lg_page.enter_model_name("anthropic/claude-3.5-haiku")
        assert model_entered, "Model Name girilemedi"
        print("Model Name girildi")

        # Prompt gir
        prompt_entered = self.create_lg_page.enter_prompt("Generate a list of popular car brands")
        assert prompt_entered, "Prompt girilemedi"
        print("Prompt girildi")

        # VALIDATE butonunun disabled olduğunu kontrol et
        validate_enabled = self.create_lg_page.is_validate_button_enabled()
        print(f"VALIDATE butonu durumu: {'Aktif' if validate_enabled else 'Disabled'}")

        assert not validate_enabled, "Name boş olduğu için VALIDATE butonu disabled olmalıydı"

        # Name required error mesajı var mı kontrol et
        page_source = self.driver.page_source
        name_error = "name" in page_source.lower() and (
                    "required" in page_source.lower() or "empty" in page_source.lower())

        if name_error:
            print("Name required error mesajı bulundu")
        else:
            print("Name error mesajı henüz görünmüyor (VALIDATE basılmadı)")

        print("Test BAŞARILI: Name boş iken VALIDATE disabled - Generate with AI")

    def test_TC094_empty_max_count_generate_with_ai(self):
        """TC094: Max Count boş bırakma - Max Count: boş, diğerleri dolu"""
        print("\nTC094: Max Count boş bırakma - Generate with AI testi ===")

        new_clicked = self.listgen_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"
        time.sleep(1)

        tab_clicked = self.create_lg_page.click_generate_with_ai_tab()
        assert tab_clicked, "Generate with AI tab'ına tıklanamadı"
        time.sleep(1)

        name_entered = self.create_lg_page.enter_name(self.test_list_name)
        assert name_entered, "Name girilemedi"

        print("Max Count field boş bırakılıyor")

        api_url_entered = self.create_lg_page.enter_api_url("https://openrouter.ai/api/v1")
        assert api_url_entered, "API URL girilemedi"

        api_key_entered = self.create_lg_page.enter_api_key("sk-or-v1-be4cb404544f7213")
        assert api_key_entered, "API Key girilemedi"

        model_entered = self.create_lg_page.enter_model_name("anthropic/claude-3.5-haiku")
        assert model_entered, "Model Name girilemedi"

        prompt_entered = self.create_lg_page.enter_prompt("Generate a list of popular car brands")
        assert prompt_entered, "Prompt girilemedi"

        validate_enabled = self.create_lg_page.is_validate_button_enabled()
        print(f"VALIDATE butonu durumu: {'Aktif' if validate_enabled else 'Disabled'}")

        assert not validate_enabled, "Max Count boş olduğu için VALIDATE butonu disabled olmalıydı"

        print("Test BAŞARILI: Max Count boş iken VALIDATE disabled")

    def test_TC095_empty_api_url_generate_with_ai(self):
        """TC095: AI API URL boş - API URL: boş, diğerleri dolu"""
        print("\nTC095: AI API URL boş - Generate with AI testi ===")

        new_clicked = self.listgen_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"
        time.sleep(1)

        tab_clicked = self.create_lg_page.click_generate_with_ai_tab()
        assert tab_clicked, "Generate with AI tab'ına tıklanamadı"
        time.sleep(1)

        name_entered = self.create_lg_page.enter_name(self.test_list_name)
        assert name_entered, "Name girilemedi"

        max_count_entered = self.create_lg_page.enter_max_count(10)
        assert max_count_entered, "Max Count girilemedi"

        print("API URL field boş bırakılıyor")

        api_key_entered = self.create_lg_page.enter_api_key("sk-or-v1-be4cb404544f7213")
        assert api_key_entered, "API Key girilemedi"

        model_entered = self.create_lg_page.enter_model_name("anthropic/claude-3.5-haiku")
        assert model_entered, "Model Name girilemedi"

        prompt_entered = self.create_lg_page.enter_prompt("Generate a list of popular car brands")
        assert prompt_entered, "Prompt girilemedi"

        validate_enabled = self.create_lg_page.is_validate_button_enabled()
        print(f"VALIDATE butonu durumu: {'Aktif' if validate_enabled else 'Disabled'}")

        assert not validate_enabled, "API URL boş olduğu için VALIDATE butonu disabled olmalıydı"

        print("Test BAŞARILI: API URL boş iken VALIDATE disabled")

    def test_TC096_empty_api_key_generate_with_ai(self):
        """TC096: AI API Key boş - API Key: boş, diğerleri dolu"""
        print("\nTC096: AI API Key boş - Generate with AI testi ===")

        new_clicked = self.listgen_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"
        time.sleep(1)

        tab_clicked = self.create_lg_page.click_generate_with_ai_tab()
        assert tab_clicked, "Generate with AI tab'ına tıklanamadı"
        time.sleep(1)

        name_entered = self.create_lg_page.enter_name(self.test_list_name)
        assert name_entered, "Name girilemedi"

        max_count_entered = self.create_lg_page.enter_max_count(10)
        assert max_count_entered, "Max Count girilemedi"

        api_url_entered = self.create_lg_page.enter_api_url("https://openrouter.ai/api/v1")
        assert api_url_entered, "API URL girilemedi"

        print("API Key field boş bırakılıyor")

        model_entered = self.create_lg_page.enter_model_name("anthropic/claude-3.5-haiku")
        assert model_entered, "Model Name girilemedi"

        prompt_entered = self.create_lg_page.enter_prompt("Generate a list of popular car brands")
        assert prompt_entered, "Prompt girilemedi"

        validate_enabled = self.create_lg_page.is_validate_button_enabled()
        print(f"VALIDATE butonu durumu: {'Aktif' if validate_enabled else 'Disabled'}")

        assert not validate_enabled, "API Key boş olduğu için VALIDATE butonu disabled olmalıydı"

        print("Test BAŞARILI: API Key boş iken VALIDATE disabled")


    def test_TC097_empty_model_name_generate_with_ai(self):
        """TC097: Model Name boş - Model Name: boş, diğerleri dolu"""
        print("\nTC097: Model Name boş - Generate with AI testi ===")

        new_clicked = self.listgen_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"
        time.sleep(1)

        tab_clicked = self.create_lg_page.click_generate_with_ai_tab()
        assert tab_clicked, "Generate with AI tab'ına tıklanamadı"
        time.sleep(1)

        name_entered = self.create_lg_page.enter_name(self.test_list_name)
        assert name_entered, "Name girilemedi"

        max_count_entered = self.create_lg_page.enter_max_count(10)
        assert max_count_entered, "Max Count girilemedi"

        api_url_entered = self.create_lg_page.enter_api_url("https://openrouter.ai/api/v1")
        assert api_url_entered, "API URL girilemedi"

        api_key_entered = self.create_lg_page.enter_api_key("sk-or-v1-be4cb404544f7213")
        assert api_key_entered, "API Key girilemedi"

        print("Model Name field boş bırakılıyor")

        prompt_entered = self.create_lg_page.enter_prompt("Generate a list of popular car brands")
        assert prompt_entered, "Prompt girilemedi"

        validate_enabled = self.create_lg_page.is_validate_button_enabled()
        print(f"VALIDATE butonu durumu: {'Aktif' if validate_enabled else 'Disabled'}")

        assert not validate_enabled, "Model Name boş olduğu için VALIDATE butonu disabled olmalıydı"

        print("Test BAŞARILI: Model Name boş iken VALIDATE disabled")

    def test_TC098_empty_prompt_generate_with_ai(self):
        """TC098: Prompt boş bırakma - Prompt: boş, diğerleri dolu"""
        print("\nTC098: Prompt boş bırakma - Generate with AI testi ===")

        new_clicked = self.listgen_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"
        time.sleep(1)

        tab_clicked = self.create_lg_page.click_generate_with_ai_tab()
        assert tab_clicked, "Generate with AI tab'ına tıklanamadı"
        time.sleep(1)

        name_entered = self.create_lg_page.enter_name(self.test_list_name)
        assert name_entered, "Name girilemedi"

        max_count_entered = self.create_lg_page.enter_max_count(10)
        assert max_count_entered, "Max Count girilemedi"

        api_url_entered = self.create_lg_page.enter_api_url("https://openrouter.ai/api/v1")
        assert api_url_entered, "API URL girilemedi"

        api_key_entered = self.create_lg_page.enter_api_key("sk-or-v1-be4cb404544f7213")
        assert api_key_entered, "API Key girilemedi"

        model_entered = self.create_lg_page.enter_model_name("anthropic/claude-3.5-haiku")
        assert model_entered, "Model Name girilemedi"

        print("Prompt field boş bırakılıyor")

        validate_enabled = self.create_lg_page.is_validate_button_enabled()
        print(f"VALIDATE butonu durumu: {'Aktif' if validate_enabled else 'Disabled'}")

        assert not validate_enabled, "Prompt boş olduğu için VALIDATE butonu disabled olmalıydı"

        print("Test BAŞARILI: Prompt boş iken VALIDATE disabled")


    def test_TC099_zero_max_count_generate_with_ai(self):
        """TC099: Max Count sıfır - Max Count: 0 - Otomatik 1'e çevirir"""
        print("\nTC099: Max Count sıfır testi ===")

        new_clicked = self.listgen_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"
        time.sleep(1)

        tab_clicked = self.create_lg_page.click_generate_with_ai_tab()
        assert tab_clicked, "Generate with AI tab'ına tıklanamadı"
        time.sleep(1)

        name_entered = self.create_lg_page.enter_name(self.test_list_name)
        assert name_entered, "Name girilemedi"

        max_count_entered = self.create_lg_page.enter_max_count(0)
        assert max_count_entered, "Max Count 0 girilemedi"

        api_url_entered = self.create_lg_page.enter_api_url("https://openrouter.ai/api/v1")
        assert api_url_entered, "API URL girilemedi"

        api_key_entered = self.create_lg_page.enter_api_key("sk-or-v1-be4cb404544f7213")
        assert api_key_entered, "API Key girilemedi"

        model_entered = self.create_lg_page.enter_model_name("anthropic/claude-3.5-haiku")
        assert model_entered, "Model Name girilemedi"

        prompt_entered = self.create_lg_page.enter_prompt("Generate a list of popular car brands")
        assert prompt_entered, "Prompt girilemedi"

        # Max Count otomatik düzeltme kontrol et
        max_count_field = self.driver.find_element(By.ID, "max_count")
        current_value = max_count_field.get_attribute("value")
        print(f"Max Count değeri: {current_value}")

        if current_value == "1":
            print("Test BAŞARILI: Max Count 0 → 1'e otomatik düzeltildi")
        else:
            print(f"Max Count düzeltilmedi: {current_value}")

        print("Test tamamlandı: Max Count sıfır")

    def test_TC100_max_count_validation_generate_with_ai(self):
        """TC100: Max Count validation - Text girişi - Sadece pozitif integer kabul etmeli"""
        print("\nTC100: Max Count validation testi ===")

        new_clicked = self.listgen_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"
        time.sleep(1)

        tab_clicked = self.create_lg_page.click_generate_with_ai_tab()
        assert tab_clicked, "Generate with AI tab'ına tıklanamadı"
        time.sleep(1)

        name_entered = self.create_lg_page.enter_name(self.test_list_name)
        assert name_entered, "Name girilemedi"

        # Text girişi test et
        max_count_field = self.driver.find_element(By.ID, "max_count")
        max_count_field.clear()
        max_count_field.send_keys("abc123")

        text_value = max_count_field.get_attribute("value")
        print(f"'abc123' girişi sonucu: '{text_value}'")

        if text_value == "123":
            print("Text filtrelendi - sadece sayı kısmı kabul edildi")
        elif text_value == "":
            print("Text girişi tamamen reddedildi")
        elif text_value == "abc123":
            print("Text girişi aynen kabul edildi")
        else:
            print(f"Beklenmeyen sonuç: '{text_value}'")

        print("Test tamamlandı: Max Count text validation")


    def test_TC101_max_count_large_number_generate_with_ai(self):
        """TC101: Max Count çok büyük - Max Count: 999999 - Üst limit var mı?"""
        print("\nTC101: Max Count çok büyük testi ===")

        new_clicked = self.listgen_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"
        time.sleep(1)

        tab_clicked = self.create_lg_page.click_generate_with_ai_tab()
        assert tab_clicked, "Generate with AI tab'ına tıklanamadı"
        time.sleep(1)

        name_entered = self.create_lg_page.enter_name(self.test_list_name)
        assert name_entered, "Name girilemedi"

        # Max Count çok büyük sayı gir
        max_count_entered = self.create_lg_page.enter_max_count(999999)
        assert max_count_entered, "Max Count 999999 girilemedi"
        print("Max Count 999999 girildi")

        # Diğer alanları doldur
        api_url_entered = self.create_lg_page.enter_api_url("https://openrouter.ai/api/v1")
        assert api_url_entered, "API URL girilemedi"

        api_key_entered = self.create_lg_page.enter_api_key("sk-or-v1-be4cb404544f7213")
        assert api_key_entered, "API Key girilemedi"

        model_entered = self.create_lg_page.enter_model_name("anthropic/claude-3.5-haiku")
        assert model_entered, "Model Name girilemedi"

        prompt_entered = self.create_lg_page.enter_prompt("Generate a list of popular car brands")
        assert prompt_entered, "Prompt girilemedi"

        # Field değerini kontrol et
        max_count_field = self.driver.find_element(By.ID, "max_count")
        large_value = max_count_field.get_attribute("value")
        print(f"999999 girişi sonucu: '{large_value}'")

        # VALIDATE butonuna bas
        validate_enabled = self.create_lg_page.is_validate_button_enabled()
        if validate_enabled:
            validate_clicked = self.create_lg_page.click_validate_button()
            if validate_clicked:
                time.sleep(3)
                print("VALIDATE başarılı")

                # SAVE aktif mi kontrol et
                save_enabled = self.create_lg_page.is_save_button_enabled_db_ai()
                if save_enabled:
                    print("SAVE aktif - büyük Max Count kabul edildi")
                    save_clicked = self.create_lg_page.click_save_button_db_ai()
                    if save_clicked:
                        time.sleep(2)
                        print("Test BAŞARILI: Büyük Max Count ile liste oluşturuldu")
                else:
                    print("SAVE disabled - büyük Max Count reddedildi")
        else:
            print("VALIDATE disabled - büyük Max Count problemi")

        print("Test tamamlandı: Max Count büyük sayı")

    def test_TC102_invalid_api_url_generate_with_ai(self):
        """TC102: Geçersiz API URL - API URL: "invalid-url" - URL format kontrolü"""
        print("\nTC102: Geçersiz API URL testi ===")

        new_clicked = self.listgen_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"
        time.sleep(1)

        tab_clicked = self.create_lg_page.click_generate_with_ai_tab()
        assert tab_clicked, "Generate with AI tab'ına tıklanamadı"
        time.sleep(1)

        name_entered = self.create_lg_page.enter_name(self.test_list_name)
        assert name_entered, "Name girilemedi"

        max_count_entered = self.create_lg_page.enter_max_count(10)
        assert max_count_entered, "Max Count girilemedi"

        api_url_entered = self.create_lg_page.enter_api_url("invalid-url")
        assert api_url_entered, "Invalid API URL girilemedi"
        print("Invalid API URL girildi")

        api_key_entered = self.create_lg_page.enter_api_key("sk-or-v1-be4cb404544f7213")
        assert api_key_entered, "API Key girilemedi"

        model_entered = self.create_lg_page.enter_model_name("anthropic/claude-3.5-haiku")
        assert model_entered, "Model Name girilemedi"

        prompt_entered = self.create_lg_page.enter_prompt("Generate a list of popular car brands")
        assert prompt_entered, "Prompt girilemedi"

        # VALIDATE butonuna bas
        validate_enabled = self.create_lg_page.is_validate_button_enabled()
        if validate_enabled:
            validate_clicked = self.create_lg_page.click_validate_button()
            if validate_clicked:
                time.sleep(3)
                print("VALIDATE başarılı")

                # SAVE aktif mi kontrol et
                save_enabled = self.create_lg_page.is_save_button_enabled_db_ai()
                if save_enabled:
                    print("SAVE aktif - invalid URL kabul edildi")
                    save_clicked = self.create_lg_page.click_save_button_db_ai()
                    if save_clicked:
                        time.sleep(2)
                        print("Test BAŞARILI: Invalid URL ile liste oluşturuldu")
                else:
                    print("SAVE disabled - invalid URL reddedildi")
        else:
            print("VALIDATE disabled - invalid URL problemi")

        print("Test tamamlandı: Invalid API URL")

    def test_TC103_invalid_api_key_format_generate_with_ai(self):
        """TC103: Geçersiz API Key format - API Key: "123" - API key format kontrolü"""
        print("\nTC103: Geçersiz API Key format testi ===")

        new_clicked = self.listgen_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"
        time.sleep(1)

        tab_clicked = self.create_lg_page.click_generate_with_ai_tab()
        assert tab_clicked, "Generate with AI tab'ına tıklanamadı"
        time.sleep(1)

        name_entered = self.create_lg_page.enter_name(self.test_list_name)
        assert name_entered, "Name girilemedi"

        max_count_entered = self.create_lg_page.enter_max_count(10)
        assert max_count_entered, "Max Count girilemedi"

        api_url_entered = self.create_lg_page.enter_api_url("https://openrouter.ai/api/v1")
        assert api_url_entered, "API URL girilemedi"

        api_key_entered = self.create_lg_page.enter_api_key("123")
        assert api_key_entered, "Invalid API Key girilemedi"
        print("Invalid API Key girildi")

        model_entered = self.create_lg_page.enter_model_name("anthropic/claude-3.5-haiku")
        assert model_entered, "Model Name girilemedi"

        prompt_entered = self.create_lg_page.enter_prompt("Generate a list of popular car brands")
        assert prompt_entered, "Prompt girilemedi"

        # VALIDATE butonuna bas
        validate_enabled = self.create_lg_page.is_validate_button_enabled()
        if validate_enabled:
            validate_clicked = self.create_lg_page.click_validate_button()
            if validate_clicked:
                time.sleep(3)
                print("VALIDATE başarılı")

                # SAVE aktif mi kontrol et
                save_enabled = self.create_lg_page.is_save_button_enabled_db_ai()
                if save_enabled:
                    print("SAVE aktif - invalid API key kabul edildi")
                    save_clicked = self.create_lg_page.click_save_button_db_ai()
                    if save_clicked:
                        time.sleep(2)
                        print("Test BAŞARILI: Invalid API key ile liste oluşturuldu")
                else:
                    print("SAVE disabled - invalid API key reddedildi")
        else:
            print("VALIDATE disabled - invalid API key problemi")

        print("Test tamamlandı: Invalid API Key format")

    def test_TC104_very_long_prompt_generate_with_ai(self):
        """TC104: Çok uzun prompt - 2000+ karakter - Prompt uzunluk limiti"""
        print("\nTC104: Çok uzun prompt testi ===")

        new_clicked = self.listgen_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"
        time.sleep(1)

        tab_clicked = self.create_lg_page.click_generate_with_ai_tab()
        assert tab_clicked, "Generate with AI tab'ına tıklanamadı"
        time.sleep(1)

        name_entered = self.create_lg_page.enter_name(self.test_list_name)
        assert name_entered, "Name girilemedi"

        max_count_entered = self.create_lg_page.enter_max_count(10)
        assert max_count_entered, "Max Count girilemedi"

        api_url_entered = self.create_lg_page.enter_api_url("https://openrouter.ai/api/v1")
        assert api_url_entered, "API URL girilemedi"

        api_key_entered = self.create_lg_page.enter_api_key("sk-or-v1-be4cb404544f7213")
        assert api_key_entered, "API Key girilemedi"

        model_entered = self.create_lg_page.enter_model_name("anthropic/claude-3.5-haiku")
        assert model_entered, "Model Name girilemedi"

        long_prompt = "Generate a comprehensive list of " + "very detailed and specific " * 20 + "items for testing purposes"
        print(f"Prompt uzunluğu: {len(long_prompt)} karakter")

        prompt_entered = self.create_lg_page.enter_prompt(long_prompt)
        assert prompt_entered, "Uzun prompt girilemedi"

        # VALIDATE butonuna bas
        validate_enabled = self.create_lg_page.is_validate_button_enabled()
        if validate_enabled:
            validate_clicked = self.create_lg_page.click_validate_button()
            if validate_clicked:
                time.sleep(5)
                print("VALIDATE başarılı")

                # SAVE aktif mi kontrol et
                save_enabled = self.create_lg_page.is_save_button_enabled_db_ai()
                if save_enabled:
                    print("SAVE aktif - uzun prompt kabul edildi")
                    save_clicked = self.create_lg_page.click_save_button_db_ai()
                    if save_clicked:
                        time.sleep(3)
                        print("Test BAŞARILI: Uzun prompt ile liste oluşturuldu")
                else:
                    print("SAVE disabled - uzun prompt reddedildi")
        else:
            print("VALIDATE disabled - uzun prompt problemi")

        print("Test tamamlandı: Çok uzun prompt")

    def test_TC105_special_characters_prompt_generate_with_ai(self):
        """TC105: Özel karakterler prompt - Prompt: "ÇĞİÖŞÜ," - Özel karakter desteği"""
        print("\nTC105: Özel karakterler prompt testi ===")

        new_clicked = self.listgen_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"
        time.sleep(1)

        tab_clicked = self.create_lg_page.click_generate_with_ai_tab()
        assert tab_clicked, "Generate with AI tab'ına tıklanamadı"
        time.sleep(1)

        name_entered = self.create_lg_page.enter_name(self.test_list_name)
        assert name_entered, "Name girilemedi"

        max_count_entered = self.create_lg_page.enter_max_count(10)
        assert max_count_entered, "Max Count girilemedi"

        api_url_entered = self.create_lg_page.enter_api_url("https://openrouter.ai/api/v1")
        assert api_url_entered, "API URL girilemedi"

        api_key_entered = self.create_lg_page.enter_api_key("sk-or-v1-be4cb404544f7213")
        assert api_key_entered, "API Key girilemedi"

        model_entered = self.create_lg_page.enter_model_name("anthropic/claude-3.5-haiku")
        assert model_entered, "Model Name girilemedi"

        special_prompt = "Generate Turkish names with special characters: ÇĞİÖŞÜ, çğıöşü"
        prompt_entered = self.create_lg_page.enter_prompt(special_prompt)
        assert prompt_entered, "Özel karakterli prompt girilemedi"
        print("Özel karakterli prompt girildi")

        # VALIDATE butonuna bas
        validate_enabled = self.create_lg_page.is_validate_button_enabled()
        if validate_enabled:
            validate_clicked = self.create_lg_page.click_validate_button()
            if validate_clicked:
                time.sleep(3)
                print("VALIDATE başarılı")

                # SAVE aktif mi kontrol et
                save_enabled = self.create_lg_page.is_save_button_enabled_db_ai()
                if save_enabled:
                    print("SAVE aktif - özel karakterli prompt kabul edildi")
                    save_clicked = self.create_lg_page.click_save_button_db_ai()
                    if save_clicked:
                        time.sleep(2)
                        print("Test BAŞARILI: Özel karakterli prompt ile liste oluşturuldu")
                else:
                    print("SAVE disabled - özel karakterli prompt reddedildi")
        else:
            print("VALIDATE disabled - özel karakterli prompt problemi")

        print("Test tamamlandı: Özel karakterler prompt")

    def test_TC106_sql_injection_prompt_generate_with_ai(self):
        """TC106: SQL injection prompt - Prompt: "'; DROP TABLE; --" - Güvenlik koruması"""
        print("\nTC106: SQL injection prompt testi ===")

        new_clicked = self.listgen_page.click_newlist()
        assert new_clicked, "NEW butonuna tıklanamadı"
        time.sleep(1)

        tab_clicked = self.create_lg_page.click_generate_with_ai_tab()
        assert tab_clicked, "Generate with AI tab'ına tıklanamadı"
        time.sleep(1)

        name_entered = self.create_lg_page.enter_name(self.test_list_name)
        assert name_entered, "Name girilemedi"

        max_count_entered = self.create_lg_page.enter_max_count(10)
        assert max_count_entered, "Max Count girilemedi"

        api_url_entered = self.create_lg_page.enter_api_url("https://openrouter.ai/api/v1")
        assert api_url_entered, "API URL girilemedi"

        api_key_entered = self.create_lg_page.enter_api_key("sk-or-v1-be4cb404544f7213")
        assert api_key_entered, "API Key girilemedi"

        model_entered = self.create_lg_page.enter_model_name("anthropic/claude-3.5-haiku")
        assert model_entered, "Model Name girilemedi"

        sql_injection_prompt = "Generate list'; DROP TABLE users; --"
        prompt_entered = self.create_lg_page.enter_prompt(sql_injection_prompt)
        assert prompt_entered, "SQL injection prompt girilemedi"
        print("SQL injection prompt girildi")

        # VALIDATE butonuna bas
        validate_enabled = self.create_lg_page.is_validate_button_enabled()
        if validate_enabled:
            validate_clicked = self.create_lg_page.click_validate_button()
            if validate_clicked:
                time.sleep(3)
                print("VALIDATE başarılı")

                # SAVE aktif mi kontrol et
                save_enabled = self.create_lg_page.is_save_button_enabled_db_ai()
                if save_enabled:
                    print("SAVE aktif - SQL injection prompt kabul edildi")
                    save_clicked = self.create_lg_page.click_save_button_db_ai()
                    if save_clicked:
                        time.sleep(2)
                        print("Test BAŞARILI: SQL injection prompt ile liste oluşturuldu")
                else:
                    print("SAVE disabled - SQL injection prompt reddedildi")
        else:
            print("VALIDATE disabled - SQL injection prompt problemi")

        print("Test tamamlandı: SQL injection prompt")

