from selenium.webdriver.common.by import By
from .base_page import BasePage
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC





class AppManagementPage(BasePage):


    DASHBOARD_HEADER = (By.CSS_SELECTOR,".header-page-title")
    NEW_BUTTON = (By.XPATH,"//span[text()='NEW']")
    APPMAN_BUTTON = (By.XPATH,"//span[text()='APPLICATION MANAGEMENT']")



    def __init__(self,driver):
        super().__init__(driver)

    from selenium.webdriver.common.by import By

    def click_appman(self):
        """App Management sayfasına geç"""
        print("app man sayfasına geçiliyor")

        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(self.APPMAN_BUTTON)
            )
            element = self.driver.find_element(*self.APPMAN_BUTTON)

            # Footer'ı görünmez yap
            self.driver.execute_script("""
                let footer = document.querySelector('.sdm-footer');
                if (footer) {
                    footer.style.display = 'none';
                    console.log('Footer gizlendi');
                }
            """)

            # Scroll + JS click
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(1)
            try:
                element.click()
            except Exception as e:
                print(f"Normal click başarısız: {e} - JS click deneniyor")
                self.driver.execute_script("arguments[0].click();", element)

            print("app man sayfasına başarıyla geçildi")
            return True

        except Exception as e:
            print(f"app man sayfasına geçilemedi: {e}")
            return False

    def is_appman_loaded(self):
        """App Man'in yüklendiğini kontrol et"""

        header_element = self.find_element(self.DASHBOARD_HEADER)
        if header_element and "Application Management List" in header_element.text:
            return True
        return False


    def click_newapp_button(self):
        """New butonuna tıkla"""
        print("New App butonuna tıklanıyor")

        success = self.click_element(self.NEW_BUTTON)
        if success:
             print("New butonuna başarıyla tıklandı")
        else:
              print("New butonuna tıklanamadı")
        return success

    def click_versionlist_button(self, projectname):
        """Version List butonuna tıkla"""
        print("Version List butonuna tıklanıyor")

        VERSIONLIST_BUTTON = (By.XPATH,f"//span[text()='{projectname}']/ancestor::tr//button[contains(@class, 'ant-btn')]//div[text()='Version List']")

        success = self.click_element(VERSIONLIST_BUTTON)
        if success:
            print("Version List butonuna başarıyla tıklandı")
        else:
            print("Version List butonuna tıklanamadı")
        return success


    def click_modulelist_button(self,projectname):
        """Module List butonuna tıkla"""
        print("Module List butonuna tıklanıyor")

        MODULELIST_BUTTON = (By.XPATH,f"//span[text()='{projectname}']/ancestor::tr//button[contains(@class, 'ant-btn')]//div[text()='Module List']")

        success = self.click_element(MODULELIST_BUTTON)
        if success:
             print("Module List butonuna başarıyla tıklandı")
        else:
              print("Module List butonuna tıklanamadı")
        return success

    def click_modulelistADD_button(self, projectname):
        """Module List ekleme butonuna tıkla"""
        print("Module List ekleme butonuna tıklanıyor")

        try:
            # İlk önce proje ismini bul
            project_span = self.driver.find_element(By.XPATH, f"//span[text()='{projectname}']")

            # Parent tr'yi bul
            parent_tr = project_span.find_element(By.XPATH, "./ancestor::tr")

            # SVG elementini bul ve tıkla (Path yerine SVG)
            MODULEADD_BUTTON = parent_tr.find_element(By.CSS_SELECTOR, "svg[viewBox='0 0 1536 1536']")
            MODULEADD_BUTTON.click()
            success = True

        except Exception as e:
            print(f"SVG click başarısız, alternatif deneniyor: {e}")
            try:
                # Alternatif: JavaScript ile tıkla
                svg_element = parent_tr.find_element(By.CSS_SELECTOR, "svg[viewBox='0 0 1536 1536']")
                self.driver.execute_script("arguments[0].click();", svg_element)
                success = True
            except Exception as e2:
                print(f"Hata: {e2}")
                success = False

        if success:
            print("Module List ekleme butonuna başarıyla tıklandı")
        else:
            print("Module List ekleme butonuna tıklanamadı")
        return success

    def click_deleteapp_andconfirm_button(self,projectname):

        """ App' sonuna kadar sil"""

        print("Delete butonuna tıklanıyor")

        APPDELETE_BUTTON = (By.XPATH,
                             f"//span[text()='{projectname}']/ancestor::tr//button[contains(@class, 'delete-btn')]")

        success = self.click_element(APPDELETE_BUTTON)
        if success:
            print("DELETE butonuna başarıyla tıklandı")
            DELETE_CONFIRM_BUTTON = (By.XPATH, "//span[text()='DELETE']")
            confirm_success = self.click_element(DELETE_CONFIRM_BUTTON)
            if confirm_success:
                print("Delete confirmation butonuna başarıyla tıklandı")
            else:
                print("Delete confirmation butonuna tıklanamadı")

            return confirm_success
        else:
            print("DELETE butonuna tıklanamadı")
        return success

    def click_appedit_button(self, projectname):
        """App Edit butonuna tıkla"""
        print("App Edit butonuna tıklanıyor")

        APPEDITBUTTON = (By.XPATH,f"//span[text()='{projectname}']/ancestor::tr//button[contains(@class, 'edit-btn')]")

        success = self.click_element(APPEDITBUTTON)
        if success:
            print("App Edit butonuna başarıyla tıklandı")
        else:
            print("App Edit butonuna tıklanamadı")
        return success

    def click_moduleversionlist_button(self,projectname,modulename):
        """Module Version List butonuna tıkla"""
        print("Module Version List butonuna tıklanıyor")

        self.click_modulelist_button(projectname)

        MODULEVERSIONLIST_BUTTON = (By.XPATH,f"//span[text()='{modulename}']/ancestor::tr//button[contains(@class, 'ant-btn')]//div[text()='Version List']")

        success = self.click_element(MODULEVERSIONLIST_BUTTON)
        if success:
            print("Module Version List butonuna başarıyla tıklandı")
        else:
            print("Module Version List butonuna tıklanamadı")
        return success

    def click_deletemodule_andconfirm_button(self,projectname,modulename):

        """ Modulu' sonuna kadar sil"""

        self.click_modulelist_button(projectname)

        print("Delete butonuna tıklanıyor")

        MODULEDELETE_BUTTON = (By.XPATH,
                             f"//span[text()='{modulename}']/ancestor::tr//button[contains(@class, 'delete-btn')]")

        success = self.click_element(MODULEDELETE_BUTTON)
        if success:
            print("DELETE butonuna başarıyla tıklandı")
            DELETE_CONFIRM_BUTTON = (By.XPATH, "//span[text()='DELETE']")
            confirm_success = self.click_element(DELETE_CONFIRM_BUTTON)
            if confirm_success:
                print("Delete confirmation butonuna başarıyla tıklandı")
            else:
                print("Delete confirmation butonuna tıklanamadı")

            return confirm_success
        else:
            print("DELETE butonuna tıklanamadı")
        return success

    def click_editmodule_button(self, projectname, modulename):

        """ Modul edit sayafasını açar"""

        self.click_modulelist_button(projectname)

        print("Edit butonuna tıklanıyor")

        MODULEEDIT_BUTTON = (By.XPATH,
                               f"//span[text()='{modulename}']/ancestor::tr//button[contains(@class, 'edit-btn')]")

        success = self.click_element(MODULEEDIT_BUTTON)

        if success:
            print("Module Edit butonuna başarıyla tıklandı")
        else:
            print("Module Edit butonuna tıklanamadı")
        return success









