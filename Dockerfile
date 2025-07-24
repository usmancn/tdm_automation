# Python 3.13 imajını kullan (sizin Python versiyonunuz)
FROM python:3.13-slim

# Sistem paketlerini güncelle ve gerekli paketleri yükle
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg \
    unzip \
    xvfb \
    xauth \
    dbus-x11 \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libxss1 \
    libnss3 \
    && rm -rf /var/lib/apt/lists/*

# Google Chrome repository ekle
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list

# Google Chrome yükle
RUN apt-get update && apt-get install -y \
    google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# ChromeDriver yükle - Yeni API kullanarak
RUN CHROME_VERSION=$(google-chrome --version | cut -d " " -f3 | cut -d "." -f1) && \
    echo "Chrome version: $CHROME_VERSION" && \
    if [ "$CHROME_VERSION" -ge "115" ]; then \
        # Chrome 115+ için yeni API
        CHROMEDRIVER_VERSION=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_STABLE") && \
        wget -O /tmp/chromedriver.zip "https://storage.googleapis.com/chrome-for-testing-public/${CHROMEDRIVER_VERSION}/linux64/chromedriver-linux64.zip" && \
        unzip /tmp/chromedriver.zip -d /tmp && \
        mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver; \
    else \
        # Eski Chrome sürümleri için eski API
        CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION}") && \
        wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip" && \
        unzip /tmp/chromedriver.zip -d /tmp && \
        mv /tmp/chromedriver /usr/local/bin/chromedriver; \
    fi && \
    chmod +x /usr/local/bin/chromedriver && \
    rm -rf /tmp/chromedriver* && \
    echo "ChromeDriver installed successfully"

# Çalışma dizini oluştur
WORKDIR /app

# Python requirements dosyasını kopyala ve paketleri yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Proje dosyalarını kopyala
COPY . .

# Python path'i ayarla - Bu çok önemli!
ENV PYTHONPATH=/app
ENV DISPLAY=:99

# __init__.py dosyalarını oluştur (Python package yapısı için)
RUN touch /app/__init__.py && \
    touch /app/tdm_automation/__init__.py && \
    touch /app/tdm_automation/Pages/__init__.py && \
    touch /app/tdm_automation/Tests/__init__.py

# Test kullanıcısı oluştur (güvenlik için)
RUN useradd -m testuser && chown -R testuser:testuser /app
# USER testuser

# Reports dizinini oluştur
RUN mkdir -p /app/reports && chown -R testuser:testuser /app/reports

# Login testini önce, diğerlerini sonra çalıştır
CMD ["pytest",
     "tdm_automation/Tests/test_login.py",
     "tdm_automation/Tests/test_tdm_version.py",
     "tdm_automation/Tests/test_appmanagement.py",
     "tdm_automation/Tests/test_create_new.py",
     "tdm_automation/Tests/test_create_from_db.py",
     "tdm_automation/Tests/test_create_from_file.py",
     "tdm_automation/Tests/test_data_generation_case.py",
     "tdm_automation/Tests/test_generate_with_ai.py",
     "--html=reports/report.html",
     "--self-contained-html",
     "-v",
     "--tb=short"]