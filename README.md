# projekt_inzynierski

1_scraping.py
Program pobierający dane z napieknewlosy.pl o linku, typie i opisie ze strony każdej odżywki, które później zapisuje w pliku csv (npw_products.csv).

2_data_cleaning.ipynb
Program, który na podstawie pobranych danych o typie nadaje odpowiednie im nazwy oraz wyciąga informacje o składnikach z opisów produktów, czyści je z niestandardowych symboli, a także tworzy plik csv (products_cleaned.csv).

3_def_prod_gemini.py
Program, który przy użyciu AI Gemini klasyfikuje odżywki jako emolientowe, humektantowe, proteinowe lub mieszane oraz tworzy plik npw_described_products.csv.

4_comparision.py
Program, który na podstawie danych o typie pochodzących z Gemini poprawia je do postaci literowych skrótów oraz za pomocą dwóch metod sprawdza skuteczność AI w określaniu typów odżywek do włosów, porównując je z typami już zdefiniowanymi na stronie napieknewlosy.pl.

5_scraping.py
Program pobierający dane z rossmann.pl o linku, nazwie, cenie i składnikach ze strony każdej odżywki, które później zapisuje w pliku csv (ross_products.csv).

6_def_prod_gemini.py
Program, który przy użyciu AI Gemini klasyfikuje odżywki jako emolientowe, humektantowe, proteinowe lub mieszane, poprawia je na literowe skróty i tworzy plik ross_described_products.csv.

7_web_app.py
Aplikacja Flask, która rekomenduje użytkownikowi typ odżywki do włosów na podstawie formularza dotyczącego kondycji włosów użytkownika (tabela z książki) wraz z możliwością sortowania wyników względem cen oraz typów odżywek.
