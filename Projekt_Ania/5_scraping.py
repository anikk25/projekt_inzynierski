import time
import random
import csv
from urllib.parse import urljoin
from math import ceil
import regex
import requests
import json

EMPTY_SYMBOLS = "[\u200E\u0008\u001A\u200B\u2028\u202A\u202C\uFEFF\u0001\u000E\u0013\u0014\u0019\u001c\u001d\uF0FC\u200B\u0002\u00AD]+"
SPACES = "[\u00A0\u2009\u2002\u2003\u3000\u202F]+"


def parse_product_data(product_data: str, product_url: str) -> dict:
    """
    Gets url, product ingredients, name and product's price.

        Args:
            product_data: content of a product page
            product_url: link for the product page

        Returns:
            product_data: dictionary with product information

    """

    name_list = regex.findall(r'"metatags"[^\}]*?"title"\s*:\s*"\s*([^"]*?)\s*[\|"]', product_data, regex.DOTALL)
    if name_list != []:
        name = name_list[0]
        name = regex.sub(r'\\u003c/?\w+\\u003e', '', name)
        name = regex.sub(r'\\u0026', '&', name)
        name = regex.sub(rf'{EMPTY_SYMBOLS}', '', name)
        name = regex.sub(rf'{SPACES}', ' ', name)
        name = regex.sub(r'\s+', ' ', name)
        name = regex.sub(r'\A\s*|\s*\Z', '', name)
    else:
        name = None
        print(f"Nie znaleziono informacji o nazwie produktu: {product_url}")

    price_list = regex.findall(r'"offers"[^\}]*?"price"\s*:\s*([^,]*?)\s*,', product_data, regex.DOTALL)
    if price_list != []:
        price = price_list[0]
        price = regex.sub(r'\\u003c/?\w+\\u003e', '', price)
        price = regex.sub(rf'{EMPTY_SYMBOLS}', '', price)
        price = regex.sub(rf'{SPACES}', ' ', price)
        price = regex.sub(r'\s+', ' ', price)
        price = regex.sub(r'\A\s*|\s*\Z', '', price)
    else:
        price = None
        print(f"Nie znaleziono informacji o cenie produktu: {product_url}")

    ingredients_list = regex.findall(r'"CharacterComponents"\s*,\s*"html"\s*:\s*"\s*(.*?)\s*"\s*\}', product_data, regex.DOTALL)
    if ingredients_list != []:
        ingredients = ingredients_list[0]
        ingredients = regex.sub(r'\\u003c/?\w+\\u003e', '', ingredients)
        ingredients = regex.sub(r'\\u003c.*?\\u003e', '', ingredients)
        ingredients = regex.sub(r'(?i)\A(?:.*?:)?\s*(?:Składniki\s*/?\s*(?:Ingredients|aktywne)?|Ingredients)\s*:?\s*', '', ingredients)
        ingredients = regex.sub(r'(?i)\..*?\b(?:Shampoo|Szampon)\b.*?:\s*.*', '', ingredients)
        ingredients = regex.sub(r'(?i)\A.*?Mask.*?:\s*', '', ingredients)
        ingredients = regex.sub(r'\\n|\\t', ' ', ingredients)
        ingredients = regex.sub(rf'{EMPTY_SYMBOLS}', '', ingredients)
        ingredients = regex.sub(rf'{SPACES}', ' ', ingredients)
        ingredients = regex.sub(r'\s+', ' ', ingredients)
        ingredients = regex.sub(r'\A\s*|\s*\Z', '', ingredients)
    else:
        ingredients = None
        print(f"Nie znaleziono informacji o składnikach produktu: {product_url}")

    product_data: dict = {
        "url": product_url,
        "name": name,
        "price": price,
        "ingredients": ingredients
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

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
    }

    all_data: list = []  # data container

    first_page: dict = json.loads(requests.get(base_url.format(1)).text)
    total_count: int = first_page["data"]['totalCount']

    for p in range(ceil(total_count/items_per_page)):
        time.sleep(random.uniform(min_delay,max_delay))
        page: dict = json.loads(requests.get(base_url.format(p+1)).text)
        product_links: list = [page["data"]["items"][i]['navigateUrl'] for i in range(len(page["data"]["items"]))]
        for product_link in product_links:
            time.sleep(random.uniform(min_delay,max_delay))
            product_url: str = urljoin(base_url, product_link)
            product_content: str = requests.get(product_url, headers=headers).text
            all_data.append(parse_product_data(product_content, product_url))
    return all_data

    


if __name__ == '__main__':

    URL = "https://www.rossmann.pl/products/v4/api/Products?categoryId=13183&page={}&pageSize=24&search=&sortOrder=default"
    data = scrape_all_pages(URL, 3, 4, 24)

    csv_file = "ross_products.csv"

    with open(csv_file, mode='w+', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["URL", "name", "price", "ingredients"])
        writer.writeheader()
        for product in data:
            if product["ingredients"] == None:
                pass
            else:
                writer.writerow({
                    "URL": product["url"],
                    "name": product["name"],
                    "price": product["price"],
                    "ingredients": product["ingredients"]
                })


    print(f"Dane zostały zapisane do pliku {csv_file}")
