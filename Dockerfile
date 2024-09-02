# Base image olarak Python 3.10 kullan
FROM python:3.10-slim-buster

# Çalışma dizinini ayarla (Kök dizin olarak ayarlanıyor)
WORKDIR /app

# Gereksinim dosyasını ve diğer gerekli dosyaları kopyala (Kök dizinde)
COPY requirements.txt ./
COPY .env ./
COPY . .

# Gereksinimleri yükle
RUN pip install --no-cache-dir -r requirements.txt

# Çalıştırılacak komut
CMD ["python", "run.py"]
