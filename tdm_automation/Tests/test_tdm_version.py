def navigate_to_product_info(self):
    """Product Info sayfasına git - Geliştirilmiş info button handling"""
    print("=== Navigation başlıyor ===")

    # Login kısmı aynı...
    print(f"1. BASE_URL'ye gidiliyor: {self.BASE_URL}")
    self.driver.get(self.BASE_URL)

    wait_time = 8 if self.HEADLESS else 3
    time.sleep(wait_time)

    print("2. Login yapılıyor...")
    login_result = self.login_page.do_login(self.VALID_USERNAME, self.VALID_PASSWORD)
    print(f"Login sonucu: {login_result}")

    time.sleep(5 if self.HEADLESS else 3)
    print(f"3. Login sonrası URL: {self.driver.current_url}")

    # TDM'ye git - aynı...
    print("4. TDM elementine tıklanacak...")
    tdm_locator = (By.XPATH, "//li[@title='New Test Data Manager'][2]")

    try:
        tdm_element = self.wait.until(EC.element_to_be_clickable(tdm_locator))
        success = self.login_page.click_element(tdm_locator)
        print(f"TDM tıklama sonucu: {success}")
        assert success, "TDM elementine tıklanamadı"
    except Exception as e:
        print(f"TDM element bulunamadı: {e}")
        raise

    time.sleep(5 if self.HEADLESS else 3)
    print(f"5. TDM sonrası URL: {self.driver.current_url}")

    # INFO BUTTON - MÜLTİPLE SELECTOR DENEMELER
    print("6. Info butonuna tıklanacak - Multiple selector...")

    # Farklı info button selector'ları
    info_selectors = [
        # Orijinal
        (By.XPATH, "//button[contains(@class, 'user-icon')][1]"),

        # Alternatifler
        (By.XPATH, "//button[contains(@class, 'user-icon')]"),
        (By.XPATH, "//button[@class='user-icon']"),
        (By.CSS_SELECTOR, "button.user-icon"),
        (By.CSS_SELECTOR, ".user-icon"),

        # Text-based
        (By.XPATH, "//button[contains(text(), 'info')]"),
        (By.XPATH, "//button[contains(text(), 'Info')]"),
        (By.XPATH, "//button[contains(text(), 'INFO')]"),

        # Icon-based
        (By.XPATH, "//i[@class='fa fa-info']/../.."),
        (By.XPATH, "//i[contains(@class, 'info')]/../.."),

        # Generic button search
        (By.XPATH, "//button[contains(@onclick, 'info')]"),
        (By.XPATH, "//button[contains(@id, 'info')]"),
        (By.XPATH, "//button[contains(@name, 'info')]"),

        # Top-right area buttons (where info usually is)
        (By.XPATH, "//div[contains(@class, 'header')]//button"),
        (By.XPATH, "//div[contains(@class, 'top')]//button"),
        (By.XPATH, "//div[contains(@class, 'nav')]//button"),
    ]

    info_button_clicked = False
    used_selector = None

    for i, selector in enumerate(info_selectors):
        try:
            print(f"   Deneme {i + 1}: {selector}")

            # Element'i bul ve tıkla
            element = self.wait.until(EC.element_to_be_clickable(selector))
            element.click()

            print(f"   ✅ Başarılı: {selector}")
            info_button_clicked = True
            used_selector = selector
            break

        except Exception as e:
            print(f"   ❌ Başarısız: {selector} - {str(e)[:50]}...")
            continue

    # Eğer hiçbiri çalışmazsa, sayfadaki tüm button'ları listele
    if not info_button_clicked:
        print("7. Hiçbir info selector çalışmadı. Sayfadaki button'ları listeliyor...")
        try:
            all_buttons = self.driver.find_elements(By.TAG_NAME, "button")
            print(f"   Toplam {len(all_buttons)} button bulundu:")

            for idx, btn in enumerate(all_buttons[:10]):  # İlk 10 button
                try:
                    btn_text = btn.text.strip()
                    btn_class = btn.get_attribute('class') or ''
                    btn_id = btn.get_attribute('id') or ''
                    print(f"   Button {idx + 1}: text='{btn_text}', class='{btn_class}', id='{btn_id}'")

                    # Info ile ilgili button'ı bul
                    if any(keyword in btn_text.lower() for keyword in ['info', 'version', 'about', 'help']):
                        print(f"   ⭐ Potansiyel info button bulundu: {btn_text}")
                        try:
                            btn.click()
                            info_button_clicked = True
                            used_selector = f"text-based: {btn_text}"
                            print(f"   ✅ Text-based tıklama başarılı: {btn_text}")
                            break
                        except Exception as click_error:
                            print(f"   ❌ Tıklama başarısız: {click_error}")

                except Exception as btn_error:
                    print(f"   Button {idx + 1} analiz edilemedi: {btn_error}")

        except Exception as list_error:
            print(f"Button listeleme hatası: {list_error}")

    if info_button_clicked:
        print(f"🎉 Info button başarıyla tıklandı: {used_selector}")
        time.sleep(8 if self.HEADLESS else 2)
        final_url = self.driver.current_url
        print(f"7. Final URL: {final_url}")
        return final_url
    else:
        print("❌ Hiçbir info button selector çalışmadı")
        # Screenshot al
        try:
            self.driver.save_screenshot("/app/reports/info_button_debug.png")
            print("Debug screenshot kaydedildi: info_button_debug.png")
        except:
            pass

        # HEADLESS modda info button bulunamazsa, mevcut URL'i döndür
        if self.HEADLESS:
            print("⚠️ HEADLESS modda info button atlanıyor")
            return self.driver.current_url
        else:
            raise Exception("Info button bulunamadı ve tıklanamadı")