@echo off
:: Masaüstündeki proje klasörüne git
cd /d "C:\Users\irfan\OneDrive\Masaüstü\vera_ai"

:: Streamlit uygulamasını başlat
streamlit run app.py

:: Hata durumunda pencerenin hemen kapanmaması için ekledim
pause