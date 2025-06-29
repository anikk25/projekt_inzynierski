from pandas import read_csv, DataFrame
from regex import sub, findall
from typing import Optional

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

def compare_types(letter: str, origin: str, target: str, data: DataFrame) -> int:
    """
    Counts how many times a specific letter appears in the target column
    for rows where the origin column exactly matches that letter.

        Args:
            letter: The letter abbreviation to match (e.g., "P", "E", "H").
            origin: The name of the column to check for an exact match with the letter.
            target: The name of the column to check for the presence of the letter.
            data: A pandas DataFrame containing the data to compare.

        Returns:
            correct_matches: The number of rows where the origin column equals the letter and the target column contains the letter.
    """
    correct_matches = 0
    for _, row in data.iterrows():
        if row[origin] == letter and letter in row[target]:
            correct_matches += 1
    return correct_matches

if __name__ == "__main__":
    df = read_csv("npw_described_products.csv", encoding="utf-8")
    df['pred_type'] = df['pred_type'].apply(correct_type_name)
    df.to_csv("cleaned_npw_described_products.csv", index=False, encoding="utf-8")
    correct_matches = 0
    for _, row in df.iterrows():
        if row['pred_type'] == row['type']:
            correct_matches += 1
    comparision_score = correct_matches/df.shape[0]*100
    df.to_csv("cleaned_npw_described_products.csv", index=False, encoding="utf-8")

    print(f"Skuteczność Gemini w określaniu typów odżywek metodą 1:1 wynosi: {comparision_score:.2f}%")

    npw_P_count = len(df[df['type'] == "P"])
    npw_E_count = len(df[df['type'] == "E"])
    npw_H_count = len(df[df['type'] == "H"])
    ai_P_count = len(df[df['pred_type'] == "P"])
    ai_E_count = len(df[df['pred_type'] == "E"])
    ai_H_count = len(df[df['pred_type'] == "H"])

    npw_P_comparison = compare_types("P", "type", "pred_type", df)
    npw_E_comparison = compare_types("E", "type", "pred_type", df)
    npw_H_comparison = compare_types("H", "type", "pred_type", df)
    ai_P_comparison = compare_types("P", "pred_type", "type", df)
    ai_E_comparison = compare_types("E", "pred_type", "type", df)
    ai_H_comparison = compare_types("H", "pred_type", "type", df)

    accuracy = (npw_P_comparison+npw_E_comparison+npw_H_comparison+ai_P_comparison+ai_E_comparison+ai_H_comparison)/(npw_P_count+npw_E_count+npw_H_count+ai_P_count+ai_E_count+ai_H_count)*100

    print(f"Skuteczność Gemini w określaniu typów odżywek metodą alternatywną wynosi: {accuracy:.2f}%")

# Skuteczność Gemini w określaniu typów odżywek metodą 1:1 wynosi: 58.66%
# Skuteczność Gemini w określaniu typów odżywek metodą alternatywną wynosi: 98.81%