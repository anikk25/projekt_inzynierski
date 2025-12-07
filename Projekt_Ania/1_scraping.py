import time
import random
import csv
from math import ceil
from regex import findall
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


def scrape_product_data(product_url: str) -> dict:
    """
    Gets url, product description and product tag.

        Args:
            product_url: link to a product page

        Returns:
            product_data: dictionary with product information

    """
    driver.get(product_url)

    # Waiting for the tag with class photoswipe__image to load
    try:
        element_data_label = WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.CSS_SELECTOR, 
            '.pl-container.pl-product'))
        )
        data_label_text: str = element_data_label.get_attribute('innerHTML')
    except Exception as e:
        print(f"""Wystąpił błąd w zbieraniu informacji o typie odżywki.
Url: {product_url}
Error: {e}""")
        data_label_text: str = "Brak danych"

    # Waiting for the tag with attribute "rte" to load
    try:
        element_rte = driver.find_element(By.CLASS_NAME, "rte")
        rte_text: str = element_rte.text
    except Exception as e:
        print(f"""Wystąpił błąd w zbieraniu opisu odżywki.
Url: {product_url}
Error: {e}""")
        rte_text: str = "Brak danych"

    current_url: str = driver.current_url

    product_data: dict = {
        "url": current_url,
        "type": data_label_text,
        "description": rte_text
    }

    return product_data


def scrape_all_pages(base_url: str, min_delay: int, max_delay: int, items_per_page: int) -> list:
    """
    Gathering information about all products.

        Args:
            base_url: initial link
            min_delay: minimum delay (in seconds)
            max_delay: maximum delay (in seconds)
            items_per_page: number of items per page

        Returns:
            all_data: information about products

    """
    all_data: list = []  # data container

    try:
        driver.get(base_url.format(1))
        item_count_tag = WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.CSS_SELECTOR, '.collection-filter__item--count'))
        )
        item_count: int = int(findall(r'\d+', item_count_tag.text)[0])
    except Exception as e:
        print(f"Nie znaleziono liczby produktów. Error:\n{e}")
        return []
    else:
        print(f"Liczba produktów: {item_count}")
        page_count: int = ceil(item_count / items_per_page)
        for i in range(page_count):
            formatted_url: str = base_url.format(i+1)
            print(f"Adres URL strony: {formatted_url}")
            driver.get(formatted_url)
            time.sleep(random.uniform(min_delay, max_delay))  # Random delay in a specified range
            # Find all product links
            try:
                collection_grid = driver.find_element(By.CSS_SELECTOR, '.collection-grid')
                product_tags = collection_grid.find_elements(By.CSS_SELECTOR, '.grid-item__link')
                product_urls: list = [product_tag.get_attribute("href")
                                      for product_tag in product_tags]
            except Exception as e:
                print(f"Wystąpił błąd w zbieraniu linków.\nUrl: {base_url.format(i+1)}\nError:\n{e}")
                return []
            else:
                for product_url in product_urls:
                    # Gathering products' data
                    product_data = scrape_product_data(product_url)
                    print(product_data)
                    all_data.append(product_data)
                    # Applying delay before next product
                    time.sleep(random.uniform(min_delay, max_delay))
        return all_data


if __name__ == '__main__':
    # Request headers simulation
    options = Options()
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 "
        "Safari/537.36")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])

    # Driver initialization
    driver = webdriver.Chrome(options=options)

    # Collecting the data
    URL = "https://napieknewlosy.pl/collections/odzywki?page={}"
    data = scrape_all_pages(URL, 3, 4, 40)

    # Save to file
    csv_file = "npw_products.csv"

    with open(csv_file, mode='w+', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["URL", "type", "description"])
        writer.writeheader()
        for product in data:
            writer.writerow({
                "URL": product["url"],
                "type": product["type"],
                "description": product["description"]
            })

    print(f"Dane zostały zapisane do pliku {csv_file}")

    # Closing the driver
    driver.quit()
