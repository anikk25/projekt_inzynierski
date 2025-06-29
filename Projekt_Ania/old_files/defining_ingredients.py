import requests
from typing import Optional
import json
from pandas import read_csv
import time

def scrape_data(ingredient_name: str) -> Optional[dict | None]:
    time.sleep(2)
    url = "https://api.tech.ec.europa.eu/search-api/prod/rest/search"
    params = {
        "apiKey": "285a77fd-1257-4271-8507-f0c6b2961203",
        "text": "*",
        "pageSize": 100,
        "pageNumber": 1
    }
    
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cache-Control": "No-Cache",
        "Connection": "keep-alive",
        "Content-Type": "multipart/form-data; boundary=----WebKitFormBoundaryFt9SVYuX5u995SEk",
        "Origin": "https://ec.europa.eu",
        "Referer": "https://ec.europa.eu/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"'
    }
    
    payload = (
        '------WebKitFormBoundaryFt9SVYuX5u995SEk\r\n'
        'Content-Disposition: form-data; name="query"; filename="blob"\r\n'
        'Content-Type: application/json\r\n\r\n'
        '{"bool":{"must":[{"text":{"query":"'+ingredient_name+'","fields":["inciName.exact","inciUsaName","innName.exact","phEurName","chemicalName","chemicalDescription"],"defaultOperator":"AND"}},{"terms":{"itemType":["ingredient","substance"]}}]}}\r\n'
        '------WebKitFormBoundaryFt9SVYuX5u995SEk--\r\n'
    )
    
    response = requests.post(url, params=params, headers=headers, data=payload)
    
    if response.status_code == 200:
        response_json = response.json()
        try:
            inci_name = response_json["results"][0]["metadata"]["inciName"][0]
        except Exception as e:
            print(f"Dla substancji {ingredient_name} nie znaleziono nazwy INCI.")
            inci_name = None
        try:
            function_names = response_json["results"][0]["metadata"]["functionName"]
        except Exception as e:
            print(f"Dla substancji {ingredient_name} nie znaleziono żadnych funkcji.")
            function_names = []
        return {"original_name": ingredient_name, "inci_name": inci_name, "function_names": function_names}
    else:
        print(f"Request failed with status code {response.status_code}")
        return None


if __name__ == "__main__":
    ingredients = []
    input_data = read_csv("unique_ingredients.csv")
    input_data_series = input_data["ingredient_name"]
    for ingredient in input_data_series:
        ingredients.append(scrape_data(ingredient))
    with open("normalized_ingredients.json", "w+", encoding="utf-8") as f:
        json.dump(ingredients, f, ensure_ascii=False)
