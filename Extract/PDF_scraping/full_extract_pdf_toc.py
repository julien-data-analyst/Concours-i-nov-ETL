##############################-
# Sujet : Extraction complète des données du sommaire + export CSV à nettoyer
# Date : 30/11/2025
#############################-

if __name__=="__main__":

    import download_pdf_files as dpf
    import extract_data_inov_1_6 as inov16
    import extract_data_inov_7_10 as inov710
    import extract_data_inov_11_12 as inov1112
else:
    import Extract.PDF_scraping.download_pdf_files as dpf
    import Extract.PDF_scraping.extract_data_inov_1_6 as inov16
    import Extract.PDF_scraping.extract_data_inov_7_10 as inov710
    import Extract.PDF_scraping.extract_data_inov_11_12 as inov1112

import pandas as pd
import os

def extract_toc():
    # Définition des chemins pour stocker les résulats
    dossier_pdf = "Data/PDF_files"
    data_nettoyer = "Data/ToClean/concours_inov_1_12_toc.csv"

    # 1ère partie : Téléchargement de tous les fichiers PDF
    concours = pd.read_json("Data/concours.jsonl", lines=True)

    for pdf_url in concours["PDF_URL"]:
        dpf.download_pdf_web(pdf_url, "Data/PDF_files")

    # 2ème partie : Extraction du sommaire pour tous les PDF 
    dataset_inov_1_6 = inov16.extract_concours_inov_1_6(dossier_pdf)
    #print(dataset_inov_1_6)
    dataset_inov_7_10 = inov710.extract_concours_inov_7_10(dossier_pdf)
    #print(dataset_inov_7_10)
    dataset_inov_11_12 = inov1112.extract_concours_inov_11_12(dossier_pdf)
    #print(dataset_inov_11_12)

    # 3ème partie : concaténation des trois DataFrames + export CSV
    dataset_inov_global = pd.concat([dataset_inov_1_6, dataset_inov_7_10, dataset_inov_11_12], ignore_index=True)
    #print(dataset_inov_global)
    # export to CSV
    dataset_inov_global.to_csv(data_nettoyer, index=False, sep=";", encoding="utf-8")