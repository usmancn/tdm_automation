import time

from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.common.by import By
from .base_page import BasePage


class CreateListGenerator(BasePage):
    # Tab butonları
    CFROMFILE_BUTTON = (By.XPATH, "//div[contains(text(), 'Create From File')]")
    CFROMDB_BUTTON = (By.XPATH, "//div[contains(text(), 'Create From DB')]")
    GWITHAI_BUTTON = (By.XPATH, "//div[contains(text(), 'Generate with AI')]")
    CNEW_BUTTON = (By.XPATH, "//div[contains(text(), 'Create New')]")

    # Ortak elementler (tüm tab'larda kullanılır)
    NAME_FIELD = (By.ID, "name")
    TYPE_DROPDOWN = (By.XPATH, "(//div[contains(@class, 'ant-select-selector')])[2]")
    TYPE_TEXT_OPTION = (By.XPATH, "//div[text()='Text']")
    TYPE_INTEGER_OPTION = (By.XPATH, "//div[text()='Integer']")
    TYPE_DECIMAL_OPTION = (By.XPATH, "//div[text()='Decimal']")

    CANCEL_BUTTON = (By.XPATH, "//button[text()='CANCEL']")
    VALIDATE_BUTTON = (By.XPATH, "(//button[contains(@class,'save-btn')])[1]")

    # SAVE buttonlar (farklı index'ler)
    SAVE_BUTTON_NEW_FILE = (By.XPATH, "(//button[contains(@class,'save-btn')])[1]")  # Create New + From File
    SAVE_BUTTON_DB_AI = (By.XPATH, "(//button[contains(@class,'save-btn')])[2]")     # DB + AI

    # Create New Tab elementleri
    VALUES_FIELD = (By.ID, "values")
    VALUES_ADD_BUTTON = (By.XPATH,
                         "//input[@placeholder='Values']/following::button[@class='ant-btn ant-btn-default ant-btn-color-default ant-btn-variant-outlined'][1]")

    # Create From File Tab elementleri
    SEPARATOR_DROPDOWN = (By.XPATH, "(//div[contains(@class, 'ant-select-selector')])[2]")
    SEPARATOR_COMMA = (By.XPATH, "//div[text()='Comma']")
    SEPARATOR_TAB = (By.XPATH, "//div[text()='Tab']")
    SEPARATOR_SEMICOLON = (By.XPATH, "//div[text()='Semicolon']")
    SEPARATOR_SPACE = (By.XPATH, "//div[text()='Space']")
    SEPARATOR_PIPE = (By.XPATH, "//div[text()='Pipe']")
    SEPARATOR_COLON = (By.XPATH, "//div[text()='Colon']")

    SAMPLE_FILE_DOWNLOAD = (By.XPATH, "//button//span[text()='Download']")
    FILE_UPLOAD_AREA = (By.XPATH, "//p[contains(text(), 'Click or drag file to this area to upload')]")
    FILE_INPUT = (By.XPATH, "//input[@type='file']")

    # Create From DB Tab elementleri
    ENVIRONMENT_DROPDOWN = (By.XPATH, "(//div[contains(@class, 'ant-select-selector')])[2]")
    ENVIRONMENT_POSTGRES = (By.XPATH, "//div[text()='AAAdene']")
    SQL_QUERY_TEXTAREA = (By.CSS_SELECTOR, ".w-tc-editor-text")

    # Generate with AI Tab elementleri
    AI_MAX_COUNT_FIELD = (By.ID, "max_count")
    AI_API_URL_FIELD = (By.ID, "base_url")
    AI_API_KEY_FIELD = (By.ID, "api_key")
    AI_MODEL_NAME_FIELD = (By.ID, "modal_name")
    AI_PROMPT_TEXTAREA = (By.ID, "prompt")

    # =============== TAB NAVIGATION METHODS ===============
    def click_create_new_tab(self):
        """Create New tab'ına tıkla"""
        print("Create New tab'ına tıklanıyor")
        return self.click_element(self.CNEW_BUTTON)

    def click_create_from_file_tab(self):
        """Create From File tab'ına tıkla"""
        print("Create From File tab'ına tıklanıyor")
        return self.click_element(self.CFROMFILE_BUTTON)

    def click_create_from_db_tab(self):
        """Create From DB tab'ına tıkla"""
        print("Create From DB tab'ına tıklanıyor")
        return self.click_element(self.CFROMDB_BUTTON)

    def click_generate_with_ai_tab(self):
        """Generate with AI tab'ına tıkla"""
        print("Generate with AI tab'ına tıklanıyor")
        return self.click_element(self.GWITHAI_BUTTON)

    # =============== ORTAK METHODS ===============
    def enter_name(self, name):
        """Name field'ına text gir (tüm tab'lar için)"""
        print(f"Name field'ına '{name}' giriliyor")
        return self.enter_text(self.NAME_FIELD, name)

    def click_type_dropdown(self):
        """Type dropdown'ını aç"""
        print("Type dropdown açılıyor")
        return self.click_element(self.TYPE_DROPDOWN)

    def select_type(self, type_name):
        """Type seç (Text, Integer, Decimal)"""
        print(f"Type '{type_name}' seçiliyor")

        if not self.click_type_dropdown():
            return False

        if type_name.lower() == "text":
            return self.click_element(self.TYPE_TEXT_OPTION)
        elif type_name.lower() == "integer":
            return self.click_element(self.TYPE_INTEGER_OPTION)
        elif type_name.lower() == "decimal":
            return self.click_element(self.TYPE_DECIMAL_OPTION)
        else:
            print(f"Geçersiz type: {type_name}")
            return False

    def click_save_button_new_file(self):
        """SAVE butonuna tıkla (Create New ve From File için)"""
        print("SAVE butonuna tıklanıyor (New/File)")
        return self.click_element_with_scroll(self.SAVE_BUTTON_NEW_FILE)

    def click_save_button_db_ai(self):
        """SAVE butonuna tıkla (DB ve AI için)"""
        print("SAVE butonuna tıklanıyor (DB/AI)")
        return self.click_element_with_scroll(self.SAVE_BUTTON_DB_AI)

    def click_cancel_button(self):
        """CANCEL butonuna tıkla (tüm tab'lar için)"""
        print("CANCEL butonuna tıklanıyor")
        return self.click_element_with_scroll(self.CANCEL_BUTTON)

    def click_validate_button(self):
        """VALIDATE butonuna tıkla (DB ve AI tab'ları için)"""
        print("VALIDATE butonuna tıklanıyor")
        return self.click_element_with_scroll(self.VALIDATE_BUTTON)

    def is_save_button_enabled_new_file(self):
        """SAVE butonu aktif mi (Create New/From File)"""
        try:
            save_button = self.driver.find_element(*self.SAVE_BUTTON_NEW_FILE)
            return save_button.is_enabled()
        except:
            return False

    def is_save_button_enabled_db_ai(self):
        """SAVE butonu aktif mi (DB/AI)"""
        try:
            save_button = self.driver.find_element(*self.SAVE_BUTTON_DB_AI)
            return save_button.is_enabled()
        except:
            return False

    def is_validate_button_enabled(self):
        """VALIDATE butonu aktif mi kontrol et"""
        try:
            validate_button = self.driver.find_element(*self.VALIDATE_BUTTON)
            return validate_button.is_enabled()
        except:
            return False

    # =============== CREATE NEW TAB METHODS ===============
    def enter_value(self, value):
        """Values field'ına değer gir"""
        print(f"Values field'ına '{value}' giriliyor")
        return self.enter_text(self.VALUES_FIELD, value)

    def click_add_value_button(self):
        """+ butonuna tıklayarak value ekle"""
        print("+ butonuna tıklanıyor")
        return self.click_element(self.VALUES_ADD_BUTTON)

    def add_value(self, value):
        """Value gir ve ekle"""
        print(f"Value '{value}' ekleniyor")
        if self.enter_value(value):
            return self.click_add_value_button()
        return False

    # =============== CREATE FROM FILE TAB METHODS ===============
    def click_separator_dropdown(self):
        """Separator dropdown'ını aç"""
        print("Separator dropdown açılıyor")
        return self.click_element(self.SEPARATOR_DROPDOWN)

    def select_separator(self, separator_type):
        """Separator type seç (Comma, Tab, Semicolon, Space, Pipe, Colon)"""
        print(f"Separator '{separator_type}' seçiliyor")

        if not self.click_separator_dropdown():
            return False

        separators = {
            "comma": self.SEPARATOR_COMMA,
            "tab": self.SEPARATOR_TAB,
            "semicolon": self.SEPARATOR_SEMICOLON,
            "space": self.SEPARATOR_SPACE,
            "pipe": self.SEPARATOR_PIPE,
            "colon": self.SEPARATOR_COLON
        }

        separator_element = separators.get(separator_type.lower())
        if separator_element:
            return self.click_element(separator_element)
        return False

    def click_upload_area(self):
        """Upload area'ya tıklayarak file dialog aç"""
        print("Upload area'ya tıklanıyor")
        return self.click_element(self.FILE_UPLOAD_AREA)

    def upload_file(self, file_path):
        """Dosya upload et"""
        print(f"Dosya upload ediliyor: {file_path}")
        try:
            file_input = self.driver.find_element(*self.FILE_INPUT)
            file_input.send_keys(file_path)
            return True
        except Exception as e:
            print(f"Dosya upload hatası: {e}")
            return False

    def click_download_sample(self):
        """Sample file download butonuna tıkla"""
        print("Sample file download edilıyor")
        return self.click_element(self.SAMPLE_FILE_DOWNLOAD)

    # =============== CREATE FROM DB TAB METHODS ===============
    def click_environment_dropdown(self):
        """Environment dropdown'ını aç"""
        print("Environment dropdown açılıyor")
        return self.click_element(self.ENVIRONMENT_DROPDOWN)

    def select_environment_postgres(self):
        """AAAdene environment'ını seç - Arrow keys + Doğru text okuma"""
        print("AAAdene environment seçiliyor")
        if self.click_environment_dropdown():
            try:
                print("Environment dropdown açılıyor")
                dropdown_input = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH,
                                                    "//div[contains(@class, 'ant-select-dropdown')]//div[contains(@class, 'ant-select-item')]"))
                )
                dropdown_input.click()
                time.sleep(0.5)

                found = False
                max_attempts = 60
                for i in range(max_attempts):
                    focused_elem = self.driver.switch_to.active_element
                    focused_elem.send_keys(Keys.ARROW_DOWN)

                    try:
                        current_item = self.driver.find_element(By.XPATH,
                                                                "//div[contains(@class, 'ant-select-item-option-active') or contains(@class, 'ant-select-item-option-selected')]")
                        text = current_item.text.strip()
                        if "AAAdene" in text:
                            print("AAAdene bulundu! Tıklanıyor...")
                            current_item.click()  # Direkt item'a tıkla
                            found = True
                            break

                    except Exception as text_error:
                        # Text okunamazsa sadece devam et
                        print(f"{i + 1}. odak: [text okunamadı]")
                        continue

                if not found:
                    raise Exception("AAAdene bulunamadı")
                return True

            except Exception as e:
                print(f"Environment seçim hatası: {e}")
                return False
        return False

    def enter_sql_query(self, sql_query):
        """SQL query text area'ya kod gir"""
        print(f"SQL query giriliyor: {sql_query}")
        return self.enter_text(self.SQL_QUERY_TEXTAREA, sql_query)

    # =============== GENERATE WITH AI TAB METHODS ===============
    def enter_max_count(self, count):
        """Max Count field'ına sayı gır"""
        print(f"Max Count field'ına '{count}' giriliyor")
        return self.enter_text(self.AI_MAX_COUNT_FIELD, str(count))

    def enter_api_url(self, url):
        """AI API URL field'ına URL gir"""
        print(f"API URL field'ına '{url}' giriliyor")
        return self.enter_text(self.AI_API_URL_FIELD, url)

    def enter_api_key(self, key):
        """AI API Key field'ına key gir"""
        print(f"API Key field'ına key giriliyor")
        return self.enter_text(self.AI_API_KEY_FIELD, key)

    def enter_model_name(self, model):
        """Model Name field'ına model gir"""
        print(f"Model Name field'ına '{model}' giriliyor")
        return self.enter_text(self.AI_MODEL_NAME_FIELD, model)

    def enter_prompt(self, prompt):
        """Prompt textarea'ya prompt gir"""
        print(f"Prompt giriliyor: {prompt}")
        return self.enter_text(self.AI_PROMPT_TEXTAREA, prompt)