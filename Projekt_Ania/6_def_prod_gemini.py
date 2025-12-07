from typing import Optional
from pandas import read_csv, DataFrame
import os
import time
from google import genai
from regex import sub, findall
import csv


GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set. Please set it in your environment variables.")
PROMPT = """Based on the following list of ingredients in a hair conditioner please determine whether the type of this hair conditioner is an emollient, humectant, protein, emollient-humectant, protein-emollient, protein-emollient-humectant, or protein-humectant. Take into account the order of ingredients in the conditioner and their strength. Disregard ingredients of the base used in the hair conditioner.

Return only the type, don't return any additional information."""


def ask_gemini(desc: str, client) -> Optional[str|None]:
    """
    Uses the Gemini API to classify a hair conditioner based on its ingredients description
    into a specific type (emollient, humectant, protein, or a combination).

        Args:
            desc: A string describing the list of ingredients in the hair conditioner.
            client: Gemini instance

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
        print(response)
        return response.text


def correct_type_name(type_to_correct: str) -> Optional[str]:
    """
    Converts the full name of a hair conditioner type into its letter abbreviation.

        Args:
            type_to_correct: The full name of the hair conditioner type (e.g., "Protein-Emollient-Humectant").

        Returns:
            corrected_type: A string representing the letter abbreviation (e.g., "PEH")

    """

    corrected_type = sub(r'(?i)\A\s*Emollient-Humectant\s*\Z','EH', type_to_correct)
    corrected_type = sub(r'(?i)\A\s*Protein-Emollient\s*\Z','PE', corrected_type)
    corrected_type = sub(r'(?i)\A\s*Protein-Emollient-Humectant\s*\Z','PEH', corrected_type)
    corrected_type = sub(r'(?i)\A\s*Protein-Humectant\s*\Z','PH', corrected_type)
    corrected_type = sub(r'(?i)\A\s*Emollient\s*\Z','E', corrected_type)
    corrected_type = sub(r'(?i)\A\s*Humectant\s*\Z','H', corrected_type)
    corrected_type = sub(r'(?i)\A\s*Protein\s*\Z','P', corrected_type)
    if findall(r'\A\s*[PEH]+\s*\Z', corrected_type):
        return corrected_type.strip()
    else:
        return None
    

if __name__ == "__main__":
    data = read_csv("ross_products.csv")
    data_series = data["ingredients"]

    header = ["URL", "name", "price", "ingredients", "pred_type"]
    csv_file = "ross_described_products.csv"
    with open(csv_file, "w+", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
    print(f"Stworzono lub wyczyszczono plik {csv_file}")
    gemini_client = genai.Client(api_key = GEMINI_API_KEY, http_options = {'api_version': 'v1alpha'})
    print("Stworzono klienta Gemini.")
    data["pred_type"] = [None for _ in range(len(data_series))]
    for idx, ingredients in enumerate(data_series):
        ingredient_type = correct_type_name(ask_gemini(ingredients, gemini_client))
        with open(csv_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=header)
            writer.writerow({
                "URL": data.iloc[idx, 0],
                "name": data.iloc[idx, 1],
                "price": data.iloc[idx, 2],
                "ingredients": data.iloc[idx, 3],
                "pred_type": ingredient_type
            })
    print("Sukces!")