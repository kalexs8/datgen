SET /p url_target="Masukkan Soal URL: "

py scraper_soal.py %url_target%

rm requirements.txt