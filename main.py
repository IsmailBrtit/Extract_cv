import pdfplumber
from pydantic import BaseModel, Field
from typing import List, Optional
import csv
from google import genai
from google.genai import types
import json



class CVPage(BaseModel):
    nom: str
    email: str
    telephone: str
    profil: Optional[str] = Field(None, description="Phrase de présentation")
    competences: List[str] = Field(default_factory=list)
    experiences: List[str] = Field(default_factory=list)


def extract_page_text(path: str) -> str:
    with pdfplumber.open(path) as pdf:
        page = pdf.pages[0]
        #print(page.extract_text())
        return page.extract_text() or ""

def structure_cv_page(raw_text: str) -> CVPage:

    client = genai.Client()

    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=CVPage,
    )

    resp = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=raw_text,
        config=config,
    )

    data = json.loads(resp.text)
    return CVPage.model_validate(data)

def main():
    pdf_path = "ISMAIL-BRTIT-2025.pdf"
    print(f"Extraction de la page 1 de : {pdf_path}")
    raw = extract_page_text(pdf_path)

    print("Structuration via Gemini…")
    try:
        cv_page = structure_cv_page(raw)
    except Exception as e:
        print("Erreur pendant la structuration :", e)
        return



    print("\nCV Page 1 structurée (via json.dumps) :")
    data_dict = cv_page.model_dump()
    print(json.dumps(data_dict, indent=2, ensure_ascii=False))


    data_dict['competences'] = ";".join(data_dict['competences'])
    data_dict['experiences'] = ";".join(data_dict['experiences'])

    with open("cv_csv.csv", "w", encoding="utf-8", newline="") as f:
        champs = ["nom", "email", "telephone", "profil", "competences", "experiences"]
        writer = csv.DictWriter(f, fieldnames=champs)
        writer.writeheader()
        writer.writerow({k: data_dict.get(k, "") for k in champs})

    print("saved in cv_csv.csv")

if __name__ == "__main__":
    main()
