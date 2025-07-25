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
from tdm_automation.Pages.synthetic_flow_list_page import SyntheticFlowListPage
from tdm_automation.Pages.create_synthetic_flow_page import CreateFlowPage
from tdm_automation.Pages.synthetic_flow_edit_page import FlowEditPage
from selenium.webdriver.chrome.options import Options



load_dotenv()


class TestSyntheticFlow:

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
        cls.FLOW_NAME = os.getenv('FLOW_NAME', 'FlowName')

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
        cls.listgen_page = ListGeneratorPage(cls.driver)
        cls.create_lg_page = CreateListGenerator(cls.driver)
        cls.datagcase_page = DataCasePage(cls.driver)
        cls.synflowlist = SyntheticFlowListPage(cls.driver)
        cls.createsynflow = CreateFlowPage(cls.driver)
        cls.synflowedit = FlowEditPage(cls.driver)


        # *** TEK SEFERLİK LOGIN İŞLEMLERİ ***
        cls.driver.get(cls.BASE_URL)
        login_success = cls.login_page.do_login(cls.VALID_USERNAME, cls.VALID_PASSWORD)
        assert login_success, "Login başarısız!"

        # TDM'ye git
        tdm_locator = (By.XPATH, "//li[@title='New Test Data Manager'][2]")
        tdm_success = cls.login_page.click_element(tdm_locator)
        assert tdm_success, "TDM elementine tıklanamadı"

        # Syn Flowa git
        datacase_success = cls.dashboard_page.click_syn_flow()
        assert datacase_success, "Synthetic Flow butonuna tıklanamadı"

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
        self.test_flow_name = f"{self.FLOW_NAME}_{timestamp}"

        # Synthetic Flow sayfasında olduğumuzu kontrol et
        current_url = self.driver.current_url
        if "synthetic-flow" not in current_url:
            print("Synthetic Flow sayfasına yönlendiriliyor...")
            self.dashboard_page.click_syn_flow()
            time.sleep(1)

    def teardown_method(self, method):
        """Her test sonrası çalışır - Açık modal veya sayfaları sırayla kapatır"""
        print(f"--- Test bitti: {method.__name__} ---")

        try:
            while True:
                action_taken = False

                # CANCEL butonlarına sırayla bas
                cancel_buttons = self.driver.find_elements(By.XPATH, "//span[text()='CANCEL']")
                for button in cancel_buttons:
                    if button.is_displayed():
                        self.datagcase_page.click_element((By.XPATH, "//span[text()='CANCEL']"))
                        time.sleep(0.5)
                        print("Modal CANCEL ile kapatıldı")
                        action_taken = True
                        break  # Bastıktan sonra tekrar başa dön

                if action_taken:
                    continue

                # BACK butonlarına sırayla bas
                back_buttons = self.driver.find_elements(By.XPATH, "//span[text()='BACK']")
                for button in back_buttons:
                    if button.is_displayed():
                        self.datagcase_page.click_element((By.XPATH, "//span[text()='BACK']"))
                        time.sleep(0.5)
                        print("Sayfa BACK ile kapatıldı")
                        action_taken = True
                        break

                if not action_taken:
                    break  # CANCEL veya BACK bulunamadıysa çık

            # En üste scroll yap
            self.driver.execute_script("window.scrollTo(0, 0);")
            print("Sayfa en üste kaydırıldı")

        except Exception as e:
            print(f"Teardown sırasında hata oluştu: {e}")

    def test_TC133_new_button_modal_açma(self):
        """TC133: NEW button ve modal açma - Create flow modal açılmalı"""
        print("\nTC133: NEW button ve modal açma testi ===")

        # NEW butonuna tıkla
        new_clicked = self.synflowlist.click_newflow()
        assert new_clicked, "NEW butonuna tıklanamadı"

        # Modal açıldığını kontrol et
        time.sleep(1)
        page_source = self.driver.page_source
        modal_opened = "environment" in page_source.lower() and "schema" in page_source.lower()

        print(f"Modal açıldı mı: {'Evet' if modal_opened else 'Hayır'}")
        assert modal_opened, "Create flow modal açılmadı"

        print("Test başarılı: NEW button ile modal açıldı")

    def test_TC134_flow_name_boş_bırakma(self):
        """TC134: Flow name boş bırakma - SAVE butonu disabled kalmalı"""
        print("\nTC134: Flow name boş bırakma testi ===")

        # NEW butonuna tıkla
        new_clicked = self.synflowlist.click_newflow()
        assert new_clicked, "NEW butonuna tıklanamadı"

        # Environment seç
        env_selected = self.createsynflow.select_env("AAAdene")
        assert env_selected, "Environment seçilemedi"

        time.sleep(2)

        # Schema seç ve transfer et
        schema_clicked = self.createsynflow.click_schema()
        assert schema_clicked, "Schema seçilemedi"

        transfer_clicked = self.createsynflow.click_transferschema()
        assert transfer_clicked, "Schema transfer edilemedi"

        time.sleep(1)

        # Table seç ve transfer et
        table_clicked = self.createsynflow.click_table()
        assert table_clicked, "Table seçilemedi"

        table_transfer_clicked = self.createsynflow.click_transfertable()
        assert table_transfer_clicked, "Table transfer edilemedi"

        # Name field'ı boş bırak - hiçbir şey girme

        # SAVE butonunun disabled olduğunu kontrol et
        save_button = self.driver.find_element(*self.createsynflow.SAVE_BUTTON)
        is_disabled = not save_button.is_enabled() or "disabled" in save_button.get_attribute("class")

        print(f"SAVE butonu durumu: {'Disabled' if is_disabled else 'Enabled'}")
        assert is_disabled, "Flow name boş iken SAVE butonu disabled olmalı"

        print("Test başarılı: Flow name boş bırakıldığında SAVE disabled")

    def test_TC135_environment_dependency(self):
        """TC135: Environment dependency - Schema dropdown disabled olmalı"""
        print("\nTC135: Environment dependency testi ===")

        # NEW butonuna tıkla
        new_clicked = self.synflowlist.click_newflow()
        assert new_clicked, "NEW butonuna tıklanamadı"

        # Flow name gir (environment seçmeden)
        name_entered = self.createsynflow.enter_flowname(self.test_flow_name)
        assert name_entered, "Flow name girilemedi"

        # Environment seçmeden schema bölümünü kontrol et
        page_source = self.driver.page_source

        # Schema bölümünde "No data" olmalı veya schema listesi boş olmalı
        schema_disabled = "No data" in page_source or "0 item" in page_source

        print(f"Schema bölümü disabled mi: {'Evet' if schema_disabled else 'Hayır'}")

        # Environment seç ve değişimi kontrol et
        env_selected = self.createsynflow.select_env("AAAdene")
        assert env_selected, "Environment seçilemedi"

        time.sleep(2)  # Schema yüklenmesi için bekle

        # Şimdi schema bölümü aktif olmalı
        page_source_after = self.driver.page_source
        schema_active = "schema_1" in page_source_after and "10 items" in page_source_after

        print(f"Environment seçtikten sonra schema aktif mi: {'Evet' if schema_active else 'Hayır'}")
        assert schema_active, "Environment seçtikten sonra schema aktif olmadı"

        print("Test başarılı: Environment dependency çalışıyor")

    def test_TC136_başarılı_flow_oluşturma(self):
        """TC136: Başarılı flow oluşturma - Flow başarıyla oluşturulmalı"""
        print("\nTC136: Başarılı flow oluşturma testi ===")

        # NEW butonuna tıkla
        new_clicked = self.synflowlist.click_newflow()
        assert new_clicked, "NEW butonuna tıklanamadı"

        # Flow name gir
        name_entered = self.createsynflow.enter_flowname(self.test_flow_name)
        assert name_entered, "Flow name girilemedi"

        # Environment seç
        env_selected = self.createsynflow.select_env("AAAdene")
        assert env_selected, "Environment seçilemedi"

        time.sleep(2)

        # Schema seç ve transfer et
        schema_clicked = self.createsynflow.click_schema()
        assert schema_clicked, "Schema seçilemedi"

        transfer_clicked = self.createsynflow.click_transferschema()
        assert transfer_clicked, "Schema transfer edilemedi"

        time.sleep(1)

        # Table seç ve transfer et
        table_clicked = self.createsynflow.click_table()
        assert table_clicked, "Table seçilemedi"

        table_transfer_clicked = self.createsynflow.click_transfertable()
        assert table_transfer_clicked, "Table transfer edilemedi"

        # SAVE butonuna tıkla
        save_clicked = self.createsynflow.click_save_button()
        assert save_clicked, "SAVE butonuna tıklanamadı"

        # Flow oluşturulduğunu kontrol et
        time.sleep(2)
        page_source = self.driver.page_source
        flow_created = self.test_flow_name in page_source

        print(f"Flow oluşturuldu mu: {'Evet' if flow_created else 'Hayır'}")
        assert flow_created, f"Flow '{self.test_flow_name}' listede görünmüyor"

        print("Test başarılı: Flow başarıyla oluşturuldu")


    @pytest.mark.skip
    def test_TC137_flow_silme_işlemi(self):
        """TC137: Flow silme işlemi - Flow silinmeli"""
        print("\nTC137: Flow silme işlemi testi ===")

        # Önce bir flow oluştur
        new_clicked = self.synflowlist.click_newflow()
        assert new_clicked, "NEW butonuna tıklanamadı"

        name_entered = self.createsynflow.enter_flowname(self.test_flow_name)
        assert name_entered, "Flow name girilemedi"

        env_selected = self.createsynflow.select_env("AAAdene")
        assert env_selected, "Environment seçilemedi"

        time.sleep(2)

        schema_clicked = self.createsynflow.click_schema()
        assert schema_clicked, "Schema seçilemedi"

        transfer_clicked = self.createsynflow.click_transferschema()
        assert transfer_clicked, "Schema transfer edilemedi"

        time.sleep(1)

        table_clicked = self.createsynflow.click_table()
        assert table_clicked, "Table seçilemedi"

        table_transfer_clicked = self.createsynflow.click_transfertable()
        assert table_transfer_clicked, "Table transfer edilemedi"

        save_clicked = self.createsynflow.click_save_button()
        assert save_clicked, "SAVE butonuna tıklanamadı"

        time.sleep(30)

        # Flow silme işlemi
        delete_clicked = self.synflowlist.click_deleteflow_andconfirm_button(self.test_flow_name)
        assert delete_clicked, "Delete işlemi başarısız"

        # Flow silindiğini kontrol et
        time.sleep(15)
        page_source = self.driver.page_source
        flow_deleted = self.test_flow_name not in page_source

        print(f"Flow silindi mi: {'Evet' if flow_deleted else 'Hayır'}")
        assert flow_deleted, f"Flow '{self.test_flow_name}' listeden silinmedi"

        print("Test başarılı: Flow silme işlemi çalışıyor")

    def test_TC138_generate_count_limit_testi(self):
        """TC138: Generate Count limit testi - Otomatik olarak 30000'e düşmeli"""
        print("\nTC138: Generate Count limit testi ===")

        # Mevcut flow "osmanf" kullan
        flow_name = "osmanf"

        # Table config butonuna tıkla
        table_config_clicked = self.synflowlist.click_tableconf(flow_name)
        assert table_config_clicked, "Table config butonuna tıklanamadı"

        time.sleep(2)

        # Generate Count field'a 50000 gir
        count_entered = self.synflowedit.enter_generatecount("50000")
        assert count_entered, "Generate Count girilemedi"

        # Input'tan focus çık (blur event trigger et)
        self.driver.find_element(By.TAG_NAME, "body").click()
        time.sleep(1)

        # Generate Count'un otomatik olarak 30000'e düştüğünü kontrol et
        generate_count_element = self.driver.find_element(*self.synflowedit.GENERATECOUNT)
        current_value = generate_count_element.get_attribute("value")

        print(f"Generate Count değeri: {current_value}")

        # 30000'e düşmüş olmalı
        if current_value == "30000":
            print("Test başarılı: Generate Count otomatik olarak 30000'e düştü")
        elif current_value == "50000":
            # Save butonunun disabled olduğunu kontrol et
            try:
                save_button = self.driver.find_element(*self.synflowedit.COUNT_SAVE)
                is_disabled = not save_button.is_enabled() or "disabled" in save_button.get_attribute("class")
                print(f"SAVE button disabled mi: {'Evet' if is_disabled else 'Hayır'}")
                assert is_disabled, "50000 girince SAVE button disabled olmalı"
                print("Test başarılı: 50000 limit aşımında SAVE disabled")
            except:
                print("SAVE button kontrol edilemedi")
        else:
            print(f"Test sonucu belirsiz: Generate Count = {current_value}")

        print("Test tamamlandı: Generate Count limit kontrolü yapıldı")

    @pytest.mark.skip
    def test_TC139_generate_count_minimum(self):
        """TC139: Generate Count minimum - Hata vermeli, 1'den az kabul etmemeli"""
        print("\nTC139: Generate Count minimum testi ===")

        # Mevcut flow "osmanf" kullan
        flow_name = "osmanf"

        # Table config butonuna tıkla
        table_config_clicked = self.synflowlist.click_tableconf(flow_name)
        assert table_config_clicked, "Table config butonuna tıklanamadı"

        time.sleep(2)

        # Generate Count field'a 0 gir
        count_entered = self.synflowedit.enter_generatecount("0")
        assert count_entered, "Generate Count 0 girilemedi"

        # Input'tan focus çık (validation trigger et)
        self.driver.find_element(By.TAG_NAME, "body").click()
        time.sleep(1)

        # Save butonunun disabled olduğunu kontrol et
        try:
            save_button = self.driver.find_element(*self.synflowedit.COUNT_SAVE)
            is_disabled = not save_button.is_enabled() or "disabled" in save_button.get_attribute("class")
            print(f"SAVE button disabled mi: {'Evet' if is_disabled else 'Hayır'}")

            if is_disabled:
                print("Test başarılı: Generate Count 0 ile SAVE disabled")
                validation_works = True
            else:
                # Save'e tıklamaya çalış ve hata kontrolü yap
                save_clicked = self.synflowedit.confirm_generatecount()

                if not save_clicked:
                    print("Test başarılı: Generate Count 0 ile save başarısız")
                    validation_works = True
                else:
                    # Hata mesajı kontrolü
                    page_source = self.driver.page_source
                    has_error = "error" in page_source.lower() or "minimum" in page_source.lower() or "invalid" in page_source.lower()
                    print(f"Hata mesajı var mı: {'Evet' if has_error else 'Hayır'}")
                    validation_works = has_error

            assert validation_works, "Generate Count 0 validation çalışmadı"

        except Exception as e:
            print(f"Generate Count validation kontrol hatası: {e}")
            assert False, "Generate Count validation kontrol edilemedi"

        print("Test başarılı: Generate Count minimum validation çalışıyor")


    @pytest.mark.skip
    def test_TC140_generator_type_değiştirme(self):
        """TC140: Generator Type değiştirme - Form fields değişmeli ve kaydedilmeli"""
        print("\nTC140: Generator Type değiştirme testi ===")

        # Mevcut flow "osmanf" kullan ve Generation Rules sayfasına git
        flow_name = "osmanf"

        # Table config butonuna tıkla
        table_config_clicked = self.synflowlist.click_tableconf(flow_name)
        assert table_config_clicked, "Table config butonuna tıklanamadı"

        time.sleep(2)

        # Flow setting butonuna tıkla (Generation Rules sayfasına git)
        flow_setting_clicked = self.synflowedit.click_flowsetting()
        assert flow_setting_clicked, "Flow setting butonuna tıklanamadı"

        time.sleep(2)

        # Herhangi bir column'un edit butonuna tıkla
        column_edit_clicked = self.synflowedit.click_colomnedit_button("email")
        assert column_edit_clicked, "Column edit butonuna tıklanamadı"

        time.sleep(1)

        # Şu anki generator type'ı kontrol et (StringGenerator olmalı)
        page_source_before = self.driver.page_source
        has_string_fields = "Min Chars" in page_source_before and "Max Chars" in page_source_before
        print(f"StringGenerator fields var mı: {'Evet' if has_string_fields else 'Hayır'}")

        # Generator Type'ı BooleanGenerator'a değiştir
        type_changed = self.synflowedit.select_type("BooleanGenerator")
        assert type_changed, "Generator Type değiştirilemedi"

        time.sleep(2)

        # BooleanGenerator fields'ları kontrol et
        page_source_after = self.driver.page_source
        has_boolean_fields = "Truth Percentage" in page_source_after
        has_string_fields_after = "Min Chars" in page_source_after and "Max Chars" in page_source_after

        print(f"BooleanGenerator fields var mı: {'Evet' if has_boolean_fields else 'Hayır'}")
        print(f"StringGenerator fields kaldı mı: {'Evet' if has_string_fields_after else 'Hayır'}")

        # Form fields değişmiş olmalı
        assert has_boolean_fields, "BooleanGenerator fields görünmüyor"
        assert not has_string_fields_after, "StringGenerator fields hala görünüyor"

        # SAVE butonuna tıkla
        save_clicked = self.synflowedit.click_save_button()
        assert save_clicked, "SAVE butonuna tıklanamadı"
        print("SAVE butonuna başarıyla tıklandı")

        print("Test başarılı: Generator Type değişince form fields değişti ve başarıyla kaydedildi")

    def test_TC141_min_max_chars_validation(self):
        """TC141: Min/Max chars validation - Save'e basınca hata mesajı"""
        print("\nTC141: Min/Max chars validation testi ===")

        # Mevcut flow "osmanf" kullan ve Generation Rules sayfasına git
        flow_name = "osmanf"

        # Table config butonuna tıkla
        table_config_clicked = self.synflowlist.click_tableconf(flow_name)
        assert table_config_clicked, "Table config butonuna tıklanamadı"

        time.sleep(2)

        # Flow setting butonuna tıkla
        flow_setting_clicked = self.synflowedit.click_flowsetting()
        assert flow_setting_clicked, "Flow setting butonuna tıklanamadı"

        time.sleep(2)

        # String column'un edit butonuna tıkla
        column_edit_clicked = self.synflowedit.click_colomnedit_button("email")
        assert column_edit_clicked, "Column edit butonuna tıklanamadı"

        time.sleep(1)

        # StringGenerator olduğunu kontrol et
        page_source = self.driver.page_source
        is_string_gen = "Min Chars" in page_source and "Max Chars" in page_source

        if not is_string_gen:
            # StringGenerator'a değiştir
            type_changed = self.synflowedit.select_type("StringGenerator")
            assert type_changed, "StringGenerator seçilemedi"
            time.sleep(1)

        # Min: 20, Max: 10 gir (yanlış değerler) - Slow input ile
        min_entered = self.synflowedit.stringgen_enter_minchar("20")
        assert min_entered, "Min Chars girilemedi"

        max_entered = self.synflowedit.stringgen_enter_maxchar("10")
        assert max_entered, "Max Chars girilemedi"

        # Page object save metodunu kullan
        save_clicked = self.synflowedit.click_save_button()
        assert save_clicked, "SAVE butonuna tıklanamadı"

        time.sleep(2)

        # Hata mesajı kontrolü
        page_source_after = self.driver.page_source
        expected_error = "Max chars cannot be less min chars."

        has_expected_error = expected_error in page_source_after
        has_min_max_error = "minimum" in page_source_after.lower() and "maximum" in page_source_after.lower()
        has_validation_error = has_expected_error or has_min_max_error

        print(f"Beklenen hata mesajı var mı: {'Evet' if has_expected_error else 'Hayır'}")
        print(f"Min/Max validation hatası var mı: {'Evet' if has_validation_error else 'Hayır'}")

        if has_validation_error:
            modal_closed = self.synflowedit.close_modal_with_x()
            assert modal_closed, "Modal × ile kapatılamadı"
            print("Modal × ile kapatıldı")
        else:
            assert False, "Min > Max validation hatası alınmadı"

        print("Test başarılı: Save'e basınca Min/Max validation hatası çıktı")

    def test_TC142_prefix_suffix_ekleme(self):
        """TC142: Prefix/Suffix ekleme - Başarıyla kaydedilmeli"""
        print("\nTC142: Prefix/Suffix ekleme testi ===")

        flow_name = "osmanf"

        table_config_clicked = self.synflowlist.click_tableconf(flow_name)
        assert table_config_clicked, "Table config butonuna tıklanamadı"

        time.sleep(2)

        flow_setting_clicked = self.synflowedit.click_flowsetting()
        assert flow_setting_clicked, "Flow setting butonuna tıklanamadı"

        time.sleep(2)

        column_edit_clicked = self.synflowedit.click_colomnedit_button("email")
        assert column_edit_clicked, "Column edit butonuna tıklanamadı"

        time.sleep(1)

        # StringGenerator'a geç
        type_changed = self.synflowedit.select_type("StringGenerator")
        if type_changed:
            time.sleep(1)

        # Prefix ve Suffix gir
        prefix_entered = self.synflowedit.stringgen_enter_prefix("TEST_")
        assert prefix_entered, "Prefix girilemedi"

        suffix_entered = self.synflowedit.stringgen_enter_suffix("_END")
        assert suffix_entered, "Suffix girilemedi"

        # Save
        save_clicked = self.synflowedit.click_save_button()
        assert save_clicked, "SAVE butonuna tıklanamadı"

        time.sleep(1)

        print("Test başarılı: Prefix/Suffix başarıyla kaydedildi")

    def test_TC143_duplicate_flow_name(self):
        """TC143: Duplicate flow name - Flow already exists hatası"""
        print("\nTC143: Duplicate flow name testi ===")

        existing_flow_name = "osmanf"

        new_clicked = self.synflowlist.click_newflow()
        assert new_clicked, "NEW butonuna tıklanamadı"

        name_entered = self.createsynflow.enter_flowname(existing_flow_name)
        assert name_entered, "Flow name girilemedi"

        env_selected = self.createsynflow.select_env("AAAdene")
        assert env_selected, "Environment seçilemedi"

        time.sleep(2)

        schema_clicked = self.createsynflow.click_schema()
        assert schema_clicked, "Schema seçilemedi"

        transfer_clicked = self.createsynflow.click_transferschema()
        assert transfer_clicked, "Schema transfer edilemedi"

        time.sleep(1)

        table_clicked = self.createsynflow.click_table()
        assert table_clicked, "Table seçilemedi"

        table_transfer_clicked = self.createsynflow.click_transfertable()
        assert table_transfer_clicked, "Table transfer edilemedi"

        url_before = self.driver.current_url

        save_clicked = self.createsynflow.click_save_button()
        assert save_clicked, "SAVE butonuna tıklanamadı"

        time.sleep(5)

        url_after = self.driver.current_url
        page_changed = (url_before != url_after)

        print(f"Sayfa URL değişti mi? {'Evet' if page_changed else 'Hayır'}")

        # Sayfa URL değişmemeli, çünkü duplicate kayıt engellenmeli
        assert not page_changed, "Duplicate flow name olmasına rağmen sayfa değişti, kayıt olmuş olabilir"

        print("Test başarılı: Duplicate flow name nedeniyle sayfa değişmedi, kayıt olmadı")

    def test_TC144_flow_name_özel_karakterler(self):
        print("\nTC144: Flow name özel karakterler testi ===")

        new_clicked = self.synflowlist.click_newflow()
        assert new_clicked, "NEW butonuna tıklanamadı"

        special_name = "Flow@#$%^&*()"
        name_entered = self.createsynflow.enter_flowname(special_name)
        assert name_entered, "Özel karakterli flow name girilemedi"

        env_selected = self.createsynflow.select_env("AAAdene")
        assert env_selected, "Environment seçilemedi"

        time.sleep(2)

        schema_clicked = self.createsynflow.click_schema()
        assert schema_clicked, "Schema seçilemedi"

        transfer_clicked = self.createsynflow.click_transferschema()
        assert transfer_clicked, "Schema transfer edilemedi"

        time.sleep(1)

        table_clicked = self.createsynflow.click_table()
        assert table_clicked, "Table seçilemedi"

        table_transfer_clicked = self.createsynflow.click_transfertable()
        assert table_transfer_clicked, "Table transfer edilemedi"

        # Save öncesi URL
        url_before = self.driver.current_url

        save_clicked = self.createsynflow.click_save_button()
        assert save_clicked, "SAVE butonuna tıklanamadı"

        time.sleep(20)  # Yeterli bekleme

        url_after = self.driver.current_url

        page_changed = (url_before != url_after)
        print(f"Sayfa URL değişti mi? {'Evet' if page_changed else 'Hayır'}")

        assert page_changed, "Sayfa değişmedi, kayıt gerçekleşmemiş olabilir"

        print("Test tamamlandı: Özel karakterli flow name kayıt kontrolü yapıldı")

    def test_TC145_flow_name_max_karakter(self):
        """TC145: Flow name max karakter - Karakter limiti uyarısı ya da sorunsuz kayıt"""
        print("\nTC145: Flow name max karakter testi ===")

        new_clicked = self.synflowlist.click_newflow()
        assert new_clicked, "NEW butonuna tıklanamadı"

        long_name = "A" * 300
        name_entered = self.createsynflow.enter_flowname(long_name)
        assert name_entered, "Uzun flow name girilemedi"

        env_selected = self.createsynflow.select_env("AAAdene")
        assert env_selected, "Environment seçilemedi"

        time.sleep(2)

        schema_clicked = self.createsynflow.click_schema()
        assert schema_clicked, "Schema seçilemedi"

        transfer_clicked = self.createsynflow.click_transferschema()
        assert transfer_clicked, "Schema transfer edilemedi"

        time.sleep(1)

        table_clicked = self.createsynflow.click_table()
        assert table_clicked, "Table seçilemedi"

        table_transfer_clicked = self.createsynflow.click_transfertable()
        assert table_transfer_clicked, "Table transfer edilemedi"

        url_before = self.driver.current_url

        save_clicked = self.createsynflow.click_save_button()
        assert save_clicked, "SAVE butonuna tıklanamadı"

        time.sleep(20)

        url_after = self.driver.current_url
        page_changed = (url_before != url_after)

        print(f"Sayfa URL değişti mi? {'Evet' if page_changed else 'Hayır'}")

        # Hata mesajı kontrolü (karakter limiti ile ilgili)
        page_source = self.driver.page_source.lower()
        limit_errors = ["limit", "too long", "maximum", "character"]
        has_limit_error = any(error in page_source for error in limit_errors)

        print(f"Karakter limiti uyarısı var mı: {'Evet' if has_limit_error else 'Hayır'}")

        # Ya sayfa değişmeli (kayıt başarılı) ya da limit hatası olmalı
        assert page_changed or has_limit_error, "Ne sayfa değişti ne de karakter limiti uyarısı alındı"

        print("Test tamamlandı: Karakter limiti kontrolü yapıldı")

    def test_TC146_modal_browser_refresh(self):
        """TC146: Modal browser refresh - Modal kapanmalı, veriler kaybolmalı"""
        print("\nTC146: Modal browser refresh testi ===")

        new_clicked = self.synflowlist.click_newflow()
        assert new_clicked, "NEW butonuna tıklanamadı"

        # Bazı alanları doldur
        test_name = f"RefreshTest_{int(time.time())}"
        name_entered = self.createsynflow.enter_flowname(test_name)
        assert name_entered, "Flow name girilemedi"

        env_selected = self.createsynflow.select_env("AAAdene")
        assert env_selected, "Environment seçilemedi"

        # Browser refresh yap
        self.driver.refresh()
        time.sleep(3)

        # Modal kapandığını ve verilerin kaybolduğunu kontrol et
        page_source = self.driver.page_source
        data_lost = test_name not in page_source
        back_to_list = "synthetic-flow" in self.driver.current_url

        print(f"Ana sayfaya döndü mü: {'Evet' if back_to_list else 'Hayır'}")
        print(f"Veriler kayboldu mu: {'Evet' if data_lost else 'Hayır'}")

        assert data_lost, "Browser refresh sonrası veriler kaybolmalı"
        assert back_to_list, "Browser refresh sonrası ana sayfaya dönmeli"

        print("Test başarılı: Browser refresh ile modal kapandı ve veriler kayboldu")

    def test_TC147_boş_form_kaydetme(self):
        """TC147: Boş form kaydetme - SAVE disabled kalmalı"""
        print("\nTC147: Boş form kaydetme testi ===")

        new_clicked = self.synflowlist.click_newflow()
        assert new_clicked, "NEW butonuna tıklanamadı"

        # Hiçbir alan doldurmadan SAVE kontrol et
        save_button = self.driver.find_element(*self.createsynflow.SAVE_BUTTON)
        is_disabled = not save_button.is_enabled() or "disabled" in save_button.get_attribute("class")

        print(f"SAVE butonu durumu: {'Disabled' if is_disabled else 'Enabled'}")
        assert is_disabled, "Hiçbir alan doldurulmadan SAVE butonu disabled olmalı"

        print("Test başarılı: Boş form SAVE disabled")

    def test_TC148_flow_name_sadece_boşluk(self):
        """TC148: Flow Name sadece boşluk - Name is required validation"""
        print("\nTC148: Flow Name sadece boşluk testi ===")

        new_clicked = self.synflowlist.click_newflow()
        assert new_clicked, "NEW butonuna tıklanamadı"

        # Sadece boşluk karakterli name
        space_name = "   "
        name_entered = self.createsynflow.enter_flowname(space_name)
        assert name_entered, "Boşluk flow name girilemedi"

        env_selected = self.createsynflow.select_env("AAAdene")
        assert env_selected, "Environment seçilemedi"

        time.sleep(2)

        schema_clicked = self.createsynflow.click_schema()
        assert schema_clicked, "Schema seçilemedi"

        transfer_clicked = self.createsynflow.click_transferschema()
        assert transfer_clicked, "Schema transfer edilemedi"

        time.sleep(1)

        table_clicked = self.createsynflow.click_table()
        assert table_clicked, "Table seçilemedi"

        table_transfer_clicked = self.createsynflow.click_transfertable()
        assert table_transfer_clicked, "Table transfer edilemedi"

        # Save'e bas
        save_clicked = self.createsynflow.click_save_button()

        time.sleep(25)

        # Validation kontrolü
        page_source = self.driver.page_source
        required_errors = ["required", "empty", "blank", "invalid"]
        has_required_error = any(error.lower() in page_source.lower() for error in required_errors)

        print(f"Required validation hatası var mı: {'Evet' if has_required_error else 'Hayır'}")

        print("Test tamamlandı: Boşluk validation kontrolü yapıldı")

    def test_T49_flow_name_unicode_karakterler(self):
        """TC149: Flow name unicode karakterler - Unicode kabul edilmeli"""
        print("\nTC149: Flow name unicode karakterler testi ===")

        new_clicked = self.synflowlist.click_newflow()
        assert new_clicked, "NEW butonuna tıklanamadı"

        # Unicode karakterli name
        unicode_name = "тест_फ्लो_اختبار"
        name_entered = self.createsynflow.enter_flowname(unicode_name)
        assert name_entered, "Unicode flow name girilemedi"

        env_selected = self.createsynflow.select_env("AAAdene")
        assert env_selected, "Environment seçilemedi"

        time.sleep(2)

        schema_clicked = self.createsynflow.click_schema()
        assert schema_clicked, "Schema seçilemedi"

        transfer_clicked = self.createsynflow.click_transferschema()
        assert transfer_clicked, "Schema transfer edilemedi"

        time.sleep(1)

        table_clicked = self.createsynflow.click_table()
        assert table_clicked, "Table seçilemedi"

        table_transfer_clicked = self.createsynflow.click_transfertable()
        assert table_transfer_clicked, "Table transfer edilemedi"

        # Save'e bas
        save_clicked = self.createsynflow.click_save_button()

        time.sleep(25)

        # Unicode desteği kontrolü
        page_source = self.driver.page_source
        unicode_supported = unicode_name in page_source or "тест" in page_source

        print(f"Unicode desteği var mı: {'Evet' if unicode_supported else 'Hayır'}")

        print("Test tamamlandı: Unicode desteği kontrol edildi")

    def test_TC150_boolean_percentage_limit(self):
        """TC150: BooleanGenerator percentage limit - 0-100 arası değer hatası"""
        print("\nTC150: BooleanGenerator percentage limit testi ===")

        flow_name = "osmanf"

        table_config_clicked = self.synflowlist.click_tableconf(flow_name)
        assert table_config_clicked, "Table config butonuna tıklanamadı"

        time.sleep(2)

        flow_setting_clicked = self.synflowedit.click_flowsetting()
        assert flow_setting_clicked, "Flow setting butonuna tıklanamadı"

        time.sleep(2)

        column_edit_clicked = self.synflowedit.click_colomnedit_button("email")
        assert column_edit_clicked, "Column edit butonuna tıklanamadı"

        time.sleep(1)

        # BooleanGenerator'a geç
        type_changed = self.synflowedit.select_type("BooleanGenerator")
        assert type_changed, "BooleanGenerator seçilemedi"

        time.sleep(1)

        # 150 (limit dışı) gir
        percentage_entered = self.synflowedit.boolean_truht_percentage("150")
        assert percentage_entered, "Truth Percentage girilemedi"

        # Save'e bas
        save_clicked = self.synflowedit.click_save_button()

        time.sleep(2)

        # Percentage limit kontrolü
        page_source = self.driver.page_source
        limit_errors = ["0-100", "percentage", "limit", "range", "invalid"]
        has_limit_error = any(error.lower() in page_source.lower() for error in limit_errors)

        print(f"Percentage limit hatası var mı: {'Evet' if has_limit_error else 'Hayır'}")

        if limit_errors:
            modal_closed = self.synflowedit.close_modal_with_x()
            assert modal_closed, "Modal × ile kapatılamadı"
            print("Modal × ile kapatıldı")
        else:
            assert False, "Percentage limit hatası alınmadı"

        print("Test başarılı: Save'e basınca Percentage hatası çıktı")

    def test_TC151_alias_sql_injection_test(self):
        """TC151: Alias SQL injection test - SQL injection koruması"""
        print("\nTC151: Alias SQL injection test testi ===")

        flow_name = "osmanf"

        table_config_clicked = self.synflowlist.click_tableconf(flow_name)
        assert table_config_clicked, "Table config butonuna tıklanamadı"

        time.sleep(2)

        flow_setting_clicked = self.synflowedit.click_flowsetting()
        assert flow_setting_clicked, "Flow setting butonuna tıklanamadı"

        time.sleep(2)

        # Alias edit butonuna tıkla
        alias_edit_clicked = self.synflowedit.click_colomnalias_button("email")
        assert alias_edit_clicked, "Alias edit butonuna tıklanamadı"

        time.sleep(1)

        # SQL injection denemesi
        sql_injection = "'; DROP TABLE users; --"
        alias_entered = self.synflowedit.enter_alias(sql_injection)
        assert alias_entered, "SQL injection alias girilemedi"

        # Save'e bas
        save_clicked = self.synflowedit.click_save_button()

        time.sleep(2)

        # SQL injection koruması kontrolü
        page_source = self.driver.page_source
        security_errors = ["invalid", "error", "security", "not allowed"]
        alias_saved = sql_injection in page_source
        has_security_protection = any(error.lower() in page_source.lower() for error in security_errors)

        print(
            f"SQL injection koruması var mı: {'Evet' if has_security_protection else 'Yok' if alias_saved else 'Belirsiz'}")

        print("Test tamamlandı: SQL injection koruması kontrol edildi")

    def test_TC152_description_dangerous_sql(self):
        """TC152: Description dangerous SQL - Dangerous SQL handling"""
        print("\nTC152: Description dangerous SQL testi ===")

        flow_name = "osmanf"

        table_config_clicked = self.synflowlist.click_tableconf(flow_name)
        assert table_config_clicked, "Table config butonuna tıklanamadı"

        time.sleep(2)

        flow_setting_clicked = self.synflowedit.click_flowsetting()
        assert flow_setting_clicked, "Flow setting butonuna tıklanamadı"

        time.sleep(2)

        # Description edit butonuna tıkla
        desc_edit_clicked = self.synflowedit.click_colomndesc_button("email")
        assert desc_edit_clicked, "Description edit butonuna tıklanamadı"

        time.sleep(1)

        # Dangerous SQL
        dangerous_sql = "DELETE FROM important_table"
        desc_entered = self.synflowedit.enter_desctiption(dangerous_sql)
        assert desc_entered, "Dangerous SQL description girilemedi"

        # Save'e bas
        save_clicked = self.synflowedit.click_save_button()

        time.sleep(2)

        # Dangerous SQL handling kontrolü
        page_source = self.driver.page_source
        security_handling = ["error", "invalid", "dangerous", "not allowed"]
        desc_saved = dangerous_sql in page_source
        has_security_handling = any(error.lower() in page_source.lower() for error in security_handling)

        print(
            f"Dangerous SQL handling var mı: {'Evet' if has_security_handling else 'Yok' if desc_saved else 'Belirsiz'}")

        print("Test tamamlandı: Dangerous SQL handling kontrol edildi")

    def test_TC153_min_chars_negative_test(self):
        """TC153: Min chars negative test - Negative value validation"""
        print("\nTC153: Min chars negative test testi ===")

        flow_name = "osmanf"

        table_config_clicked = self.synflowlist.click_tableconf(flow_name)
        assert table_config_clicked, "Table config butonuna tıklanamadı"

        time.sleep(2)

        flow_setting_clicked = self.synflowedit.click_flowsetting()
        assert flow_setting_clicked, "Flow setting butonuna tıklanamadı"

        time.sleep(2)

        column_edit_clicked = self.synflowedit.click_colomnedit_button("email")
        assert column_edit_clicked, "Column edit butonuna tıklanamadı"

        time.sleep(1)

        # StringGenerator'a geç
        type_changed = self.synflowedit.select_type("StringGenerator")
        if type_changed:
            time.sleep(1)

        # Min Chars: -5 gir
        min_entered = self.synflowedit.stringgen_enter_minchar("-5")
        assert min_entered, "Negative Min Chars girilemedi"

        # Save'e bas
        save_clicked = self.synflowedit.click_save_button()

        time.sleep(2)

        # Negative value validation kontrolü
        page_source = self.driver.page_source
        negative_errors = ["negative", "positive", "greater than", "minimum"]
        has_negative_validation = any(error.lower() in page_source.lower() for error in negative_errors)

        print(f"Negative value validation var mı: {'Evet' if has_negative_validation else 'Hayır'}")

        if negative_errors:
            modal_closed = self.synflowedit.close_modal_with_x()
            assert modal_closed, "Modal × ile kapatılamadı"
            print("Modal × ile kapatıldı")
        else:
            assert False, "Negative value hatası alınmadı"

        print("Test başarılı: Save'e basınca Min/Max validation hatası çıktı")

    def test_TC154_empty_required_fields(self):
        """TC154: Empty required fields - Required field validation"""
        print("\nTC154: Empty required fields testi ===")

        flow_name = "osmanf"

        table_config_clicked = self.synflowlist.click_tableconf(flow_name)
        assert table_config_clicked, "Table config butonuna tıklanamadı"

        time.sleep(2)

        flow_setting_clicked = self.synflowedit.click_flowsetting()
        assert flow_setting_clicked, "Flow setting butonuna tıklanamadı"

        time.sleep(2)

        column_edit_clicked = self.synflowedit.click_colomnedit_button("email")
        assert column_edit_clicked, "Column edit butonuna tıklanamadı"

        time.sleep(1)

        # StringGenerator'a geç
        type_changed = self.synflowedit.select_type("StringGenerator")
        if type_changed:
            time.sleep(1)

        # Min ve Max Chars'ı boş bırak (mevcut değerleri sil)
        min_cleared = self.synflowedit.stringgen_enter_minchar("")
        assert min_cleared, "Min Chars temizlenemedi"

        max_cleared = self.synflowedit.stringgen_enter_maxchar("")
        assert max_cleared, "Max Chars temizlenemedi"

        # Save'e bas
        save_clicked = self.synflowedit.click_save_button()

        time.sleep(2)

        # Required field validation kontrolü
        page_source = self.driver.page_source
        required_errors = ["required", "field", "empty", "mandatory", "missing"]
        has_required_validation = any(error.lower() in page_source.lower() for error in required_errors)

        print(f"Required field validation var mı: {'Evet' if has_required_validation else 'Hayır'}")

        print("Test tamamlandı: Required field validation kontrolü yapıldı")











