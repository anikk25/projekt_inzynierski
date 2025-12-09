from typing import Optional
from pandas import read_csv
import os
import time
from google import genai
import csv

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set. Please set it in your environment variables.")
PROMPT = """Based on the following list of ingredients in a hair conditioner please determine whether the type of this hair conditioner is an emollient, humectant, protein, emollient-humectant, protein-emollient, protein-emollient-humectant, or protein-humectant. Take into account the order of ingredients in the conditioner and their strength. Disregard ingredients of the base used in the hair conditioner.

Return only the type, don't return any additional information."""

def ask_gemini(desc: str) -> Optional[str|None]:
    """
    Uses the Gemini API to classify a hair conditioner based on its ingredients description
    into a specific type (emollient, humectant, protein, or a combination).

        Args:
            desc: A string describing the list of ingredients in the hair conditioner.

        Returns:
            response_text: A string containing the predicted type of hair conditioner.
    
    """
    time.sleep(10)
    question = PROMPT+"\n\n"+desc
    try:
        response = client.models.generate_content(
            model = 'gemini-2.5-flash',
            contents = question,
        )
    except Exception as e:
        print(e)
        return None
    else:
        return response.text


if __name__ == "__main__":
    data = read_csv("products_cleaned.csv")
    data_series = data["description"]

    header = ["URL", "type", "description", "pred_type"]
    csv_file = "npw_described_products.csv"
    with open(csv_file, "w+", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
    print(f"Stworzono lub wyczyszczono plik {csv_file}")
    
    client = genai.Client(api_key = GEMINI_API_KEY,
                      http_options = {'api_version': 'v1alpha'})
    print("Stworzono klienta Gemini.")
    
    data["pred_type"] = [None for _ in range(len(data_series))]
    for idx, description in enumerate(data_series):
        ingredient_type = ask_gemini(description)
        with open(csv_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=header)
            writer.writerow({
                "URL": data.iloc[idx, 0],
                "type": data.iloc[idx, 1],
                "description": data.iloc[idx, 2],
                "pred_type": ingredient_type
            })

    print("Sukces!")

