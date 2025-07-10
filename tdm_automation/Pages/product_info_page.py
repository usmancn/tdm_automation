from selenium.webdriver.common.by import By

from .base_page import BasePage


class ProductInfoPage(BasePage):

    #Locatorlar
    PRODUCT_INFO_CONTAINER = (By.CSS_SELECTOR, ".product-info")
    VERSION_VALUE = (By.XPATH, "//tr[@data-row-key='2']//td[2]")

    def __init__(self, driver):
        super().__init__(driver)

    def is_product_info_loaded(self):
        """Product Info sayfasının yüklenip yüklenmediğini kontrol et"""
        container = self.find_element(self.PRODUCT_INFO_CONTAINER)
        return container is not None

    def get_version(self):
        """Version değerini al"""
        version_element = self.find_element(self.VERSION_VALUE)
        if version_element:
            return version_element.text.strip()
        return None